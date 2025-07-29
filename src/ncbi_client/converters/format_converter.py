"""
Format conversion utilities for biological data.

Provides conversion between different biological data formats.
"""

from typing import List, Dict, Any, Optional
from ncbi_client.parsers.fasta_parser import FASTARecord, FASTAParser
from ncbi_client.parsers.genbank_parser import GenBankRecord, GenBankParser
from ncbi_client.parsers.xml_parser import XMLParser
from ncbi_client.core.exceptions import ParseError


class FormatConverter:
    """
    Utilities for converting between biological data formats.
    """
    
    @staticmethod
    def xml_to_fasta(xml_content: str) -> str:
        """
        Convert XML sequence data to FASTA format.
        
        Args:
            xml_content: XML content containing sequence data
            
        Returns:
            FASTA formatted string
        """
        try:
            # Parse GenBank XML format
            records = XMLParser.parse_genbank_set(xml_content)
            
            fasta_lines = []
            for record in records:
                if record.get('accession') and record.get('sequence'):
                    header = f">{record['accession']}"
                    if record.get('definition'):
                        header += f" {record['definition']}"
                    
                    sequence = record['sequence']
                    
                    # Add header
                    fasta_lines.append(header)
                    
                    # Add sequence in 70-character lines
                    for i in range(0, len(sequence), 70):
                        fasta_lines.append(sequence[i:i+70])
            
            return '\n'.join(fasta_lines)
            
        except Exception as e:
            raise ParseError(f"Failed to convert XML to FASTA: {str(e)}")
    
    @staticmethod
    def genbank_to_fasta(genbank_content: str) -> str:
        """
        Convert GenBank format to FASTA.
        
        Args:
            genbank_content: GenBank formatted content
            
        Returns:
            FASTA formatted string
        """
        try:
            records = GenBankParser.parse(genbank_content)
            fasta_parts = []
            
            for record in records:
                fasta_parts.append(GenBankParser.to_fasta(record))
            
            return '\n'.join(fasta_parts)
            
        except Exception as e:
            raise ParseError(f"Failed to convert GenBank to FASTA: {str(e)}")
    
    @staticmethod
    def fasta_to_genbank_minimal(fasta_content: str, source_organism: str = "Unknown") -> str:
        """
        Convert FASTA to minimal GenBank format.
        
        Args:
            fasta_content: FASTA formatted content
            source_organism: Source organism name
            
        Returns:
            GenBank formatted string
        """
        try:
            records = FASTAParser.parse(fasta_content)
            genbank_parts = []
            
            for i, record in enumerate(records):
                # Create minimal GenBank record
                accession = record.accession or f"UNKNOWN_{i+1}"
                length = record.length
                
                genbank_text = f"""LOCUS       {accession:<16} {length:>8} bp    DNA     linear   UNK 01-JAN-1980
DEFINITION  {record.description or "No description available"}
ACCESSION   {accession}
VERSION     {accession}.1
KEYWORDS    .
SOURCE      {source_organism}
  ORGANISM  {source_organism}
            Unclassified.
FEATURES             Location/Qualifiers
     source          1..{length}
                     /organism="{source_organism}"
ORIGIN      
"""
                
                # Add sequence with numbering
                sequence = record.sequence.lower()
                for i in range(0, len(sequence), 60):
                    line_start = i + 1
                    line_seq = sequence[i:i+60]
                    
                    # Format sequence in groups of 10
                    formatted_seq = ' '.join([line_seq[j:j+10] for j in range(0, len(line_seq), 10)])
                    genbank_text += f"{line_start:>9} {formatted_seq}\n"
                
                genbank_text += "//\n"
                genbank_parts.append(genbank_text)
            
            return '\n'.join(genbank_parts)
            
        except Exception as e:
            raise ParseError(f"Failed to convert FASTA to GenBank: {str(e)}")
    
    @staticmethod
    def detect_format(content: str) -> str:
        """
        Automatically detect biological data format.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected format ('fasta', 'genbank', 'xml', 'unknown')
        """
        content = content.strip()
        
        # Check for FASTA
        if content.startswith('>'):
            return 'fasta'
        
        # Check for XML
        if content.startswith('<?xml') or content.startswith('<'):
            return 'xml'
        
        # Check for GenBank
        if content.startswith('LOCUS'):
            return 'genbank'
        
        # Check for common GenBank keywords
        genbank_keywords = ['DEFINITION', 'ACCESSION', 'VERSION', 'SOURCE', 'FEATURES', 'ORIGIN']
        if any(keyword in content[:1000] for keyword in genbank_keywords):
            return 'genbank'
        
        return 'unknown'
    
    @staticmethod
    def convert_format(content: str, from_format: str, to_format: str, **kwargs) -> str:
        """
        Convert between formats.
        
        Args:
            content: Input content
            from_format: Source format
            to_format: Target format
            **kwargs: Additional conversion parameters
            
        Returns:
            Converted content
        """
        # Auto-detect source format if not specified
        if from_format == 'auto':
            from_format = FormatConverter.detect_format(content)
        
        # Conversion matrix
        if from_format == 'xml' and to_format == 'fasta':
            return FormatConverter.xml_to_fasta(content)
        
        elif from_format == 'genbank' and to_format == 'fasta':
            return FormatConverter.genbank_to_fasta(content)
        
        elif from_format == 'fasta' and to_format == 'genbank':
            organism = kwargs.get('organism', 'Unknown')
            return FormatConverter.fasta_to_genbank_minimal(content, organism)
        
        elif from_format == to_format:
            return content  # No conversion needed
        
        else:
            raise ParseError(f"Conversion from {from_format} to {to_format} not supported")
    
    @staticmethod
    def extract_sequences_from_xml(xml_content: str) -> List[Dict[str, str]]:
        """
        Extract sequence information from XML.
        
        Args:
            xml_content: XML content
            
        Returns:
            List of sequence dictionaries
        """
        try:
            records = XMLParser.parse_genbank_set(xml_content)
            sequences = []
            
            for record in records:
                seq_info = {
                    'accession': record.get('accession', ''),
                    'definition': record.get('definition', ''),
                    'organism': record.get('organism', ''),
                    'length': record.get('length', 0),
                    'sequence': record.get('sequence', '')
                }
                sequences.append(seq_info)
            
            return sequences
            
        except Exception as e:
            raise ParseError(f"Failed to extract sequences from XML: {str(e)}")
    
    @staticmethod
    def create_blast_database_fasta(records: List[FASTARecord]) -> str:
        """
        Format FASTA records for BLAST database creation.
        
        Args:
            records: List of FASTA records
            
        Returns:
            BLAST-formatted FASTA string
        """
        blast_lines = []
        
        for record in records:
            # BLAST prefers specific header format
            header = f">{record.accession}"
            if record.gi:
                header = f">gi|{record.gi}|ref|{record.accession}|"
            if record.description:
                header += f" {record.description}"
            
            blast_lines.append(header)
            
            # Add sequence in 80-character lines (BLAST standard)
            sequence = record.sequence
            for i in range(0, len(sequence), 80):
                blast_lines.append(sequence[i:i+80])
        
        return '\n'.join(blast_lines)
    
    @staticmethod
    def split_multifasta(fasta_content: str, max_records_per_file: int = 1000) -> List[str]:
        """
        Split large FASTA file into smaller chunks.
        
        Args:
            fasta_content: FASTA content to split
            max_records_per_file: Maximum records per chunk
            
        Returns:
            List of FASTA chunks
        """
        records = FASTAParser.parse(fasta_content)
        chunks = []
        
        for i in range(0, len(records), max_records_per_file):
            chunk_records = records[i:i + max_records_per_file]
            chunk_lines = []
            
            for record in chunk_records:
                chunk_lines.append(record.to_fasta())
            
            chunks.append('\n'.join(chunk_lines))
        
        return chunks
