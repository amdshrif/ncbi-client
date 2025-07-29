"""
FASTA format parsing utilities.

Handles parsing and manipulation of FASTA sequence files.
"""

import re
from typing import Dict, List, Iterator, Optional, Tuple
from io import StringIO

from ncbi_client.core.exceptions import ParseError


class FASTARecord:
    """
    Represents a single FASTA record.
    """
    
    def __init__(self, header: str, sequence: str):
        """
        Initialize FASTA record.
        
        Args:
            header: FASTA header line (without >)
            sequence: Sequence data
        """
        self.header = header.strip()
        self.sequence = sequence.strip().replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Parse common header formats
        self._parse_header()
    
    def _parse_header(self):
        """Parse common FASTA header formats."""
        # NCBI format: >gi|number|ref|accession|description
        ncbi_match = re.match(r'gi\|(\d+)\|(\w+)\|([^|]+)\|?(.*)', self.header)
        if ncbi_match:
            self.gi = ncbi_match.group(1)
            self.database = ncbi_match.group(2)
            self.accession = ncbi_match.group(3)
            self.description = ncbi_match.group(4).strip()
        else:
            # Simple format: >accession description
            parts = self.header.split(' ', 1)
            self.accession = parts[0]
            self.description = parts[1] if len(parts) > 1 else ''
            self.gi = None
            self.database = None
    
    @property
    def length(self) -> int:
        """Get sequence length."""
        return len(self.sequence)
    
    @property
    def gc_content(self) -> float:
        """Calculate GC content for DNA sequences."""
        if not self.sequence:
            return 0.0
        
        gc_count = self.sequence.upper().count('G') + self.sequence.upper().count('C')
        return (gc_count / len(self.sequence)) * 100
    
    def reverse_complement(self) -> str:
        """
        Get reverse complement of DNA sequence.
        
        Returns:
            Reverse complement sequence
        """
        complement = {
            'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
            'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
            'N': 'N', 'n': 'n'
        }
        
        return ''.join(complement.get(base, base) for base in reversed(self.sequence))
    
    def translate(self, genetic_code: int = 1) -> str:
        """
        Translate DNA sequence to protein.
        
        Args:
            genetic_code: Genetic code table number (default: 1 = standard)
            
        Returns:
            Translated protein sequence
        """
        # Standard genetic code
        codon_table = {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
        
        protein = []
        sequence = self.sequence.upper()
        
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            amino_acid = codon_table.get(codon, 'X')  # X for unknown
            protein.append(amino_acid)
            if amino_acid == '*':  # Stop codon
                break
        
        return ''.join(protein)
    
    def to_fasta(self, line_length: int = 70) -> str:
        """
        Convert record back to FASTA format.
        
        Args:
            line_length: Maximum line length for sequence
            
        Returns:
            FASTA formatted string
        """
        lines = [f'>{self.header}']
        
        # Break sequence into lines
        sequence = self.sequence
        for i in range(0, len(sequence), line_length):
            lines.append(sequence[i:i+line_length])
        
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        """String representation."""
        return f"FASTARecord(accession={self.accession}, length={self.length})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"FASTARecord(header='{self.header[:50]}...', "
                f"length={self.length}, sequence='{self.sequence[:20]}...')")


class FASTAParser:
    """
    Parser for FASTA format files and strings.
    """
    
    @staticmethod
    def parse(fasta_content: str) -> List[FASTARecord]:
        """
        Parse FASTA content into records.
        
        Args:
            fasta_content: FASTA formatted string
            
        Returns:
            List of FASTARecord objects
            
        Raises:
            ParseError: If FASTA parsing fails
        """
        try:
            records = []
            current_header = None
            current_sequence = []
            
            for line in fasta_content.split('\n'):
                line = line.strip()
                
                if line.startswith('>'):
                    # Save previous record
                    if current_header is not None:
                        sequence = ''.join(current_sequence)
                        records.append(FASTARecord(current_header, sequence))
                    
                    # Start new record
                    current_header = line[1:]  # Remove >
                    current_sequence = []
                
                elif line and current_header is not None:
                    # Add sequence line
                    current_sequence.append(line)
            
            # Save last record
            if current_header is not None:
                sequence = ''.join(current_sequence)
                records.append(FASTARecord(current_header, sequence))
            
            return records
            
        except Exception as e:
            raise ParseError(f"Failed to parse FASTA: {str(e)}")
    
    @staticmethod
    def parse_file(file_path: str) -> List[FASTARecord]:
        """
        Parse FASTA file.
        
        Args:
            file_path: Path to FASTA file
            
        Returns:
            List of FASTARecord objects
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return FASTAParser.parse(content)
        except IOError as e:
            raise ParseError(f"Cannot read FASTA file {file_path}: {str(e)}")
    
    @staticmethod
    def parse_iterator(fasta_content: str) -> Iterator[FASTARecord]:
        """
        Parse FASTA content as iterator for large files.
        
        Args:
            fasta_content: FASTA formatted string
            
        Yields:
            FASTARecord objects
        """
        current_header = None
        current_sequence = []
        
        for line in fasta_content.split('\n'):
            line = line.strip()
            
            if line.startswith('>'):
                # Yield previous record
                if current_header is not None:
                    sequence = ''.join(current_sequence)
                    yield FASTARecord(current_header, sequence)
                
                # Start new record
                current_header = line[1:]
                current_sequence = []
            
            elif line and current_header is not None:
                current_sequence.append(line)
        
        # Yield last record
        if current_header is not None:
            sequence = ''.join(current_sequence)
            yield FASTARecord(current_header, sequence)
    
    @staticmethod
    def write_records(records: List[FASTARecord], file_path: str, line_length: int = 70):
        """
        Write FASTA records to file.
        
        Args:
            records: List of FASTARecord objects
            file_path: Output file path
            line_length: Maximum line length for sequences
        """
        try:
            with open(file_path, 'w') as f:
                for record in records:
                    f.write(record.to_fasta(line_length) + '\n')
        except IOError as e:
            raise ParseError(f"Cannot write FASTA file {file_path}: {str(e)}")
    
    @staticmethod
    def filter_by_length(records: List[FASTARecord], min_length: int = 0, 
                        max_length: Optional[int] = None) -> List[FASTARecord]:
        """
        Filter records by sequence length.
        
        Args:
            records: List of FASTARecord objects
            min_length: Minimum sequence length
            max_length: Maximum sequence length (None for no limit)
            
        Returns:
            Filtered list of records
        """
        filtered = []
        for record in records:
            if record.length >= min_length:
                if max_length is None or record.length <= max_length:
                    filtered.append(record)
        return filtered
    
    @staticmethod
    def get_statistics(records: List[FASTARecord]) -> Dict[str, float]:
        """
        Calculate statistics for FASTA records.
        
        Args:
            records: List of FASTARecord objects
            
        Returns:
            Dictionary with statistics
        """
        if not records:
            return {}
        
        lengths = [record.length for record in records]
        
        return {
            'count': len(records),
            'total_length': sum(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'mean_length': sum(lengths) / len(lengths),
            'median_length': sorted(lengths)[len(lengths) // 2]
        }
