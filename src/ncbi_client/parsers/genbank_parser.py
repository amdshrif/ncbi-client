"""
GenBank format parsing utilities.

Handles parsing of GenBank flat file format.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from ncbi_client.core.exceptions import ParseError


@dataclass
class GenBankFeature:
    """Represents a GenBank feature."""
    key: str
    location: str
    qualifiers: Dict[str, str]


@dataclass 
class GenBankRecord:
    """Represents a complete GenBank record."""
    locus: str
    definition: str
    accession: str
    version: str
    keywords: str
    source: str
    organism: str
    references: List[Dict[str, str]]
    features: List[GenBankFeature]
    origin: str
    
    @property
    def length(self) -> int:
        """Get sequence length."""
        return len(self.origin.replace(' ', '').replace('\n', ''))
    
    @property
    def sequence(self) -> str:
        """Get clean sequence without spaces and numbers."""
        # Remove spaces, numbers, and newlines
        return re.sub(r'[\s\d]', '', self.origin)


class GenBankParser:
    """
    Parser for GenBank flat file format.
    
    Handles both single records and multi-record files.
    """
    
    @staticmethod
    def parse(genbank_content: str) -> List[GenBankRecord]:
        """
        Parse GenBank content into records.
        
        Args:
            genbank_content: GenBank formatted string
            
        Returns:
            List of GenBankRecord objects
            
        Raises:
            ParseError: If GenBank parsing fails
        """
        try:
            records = []
            
            # Split into individual records (separated by //)
            record_texts = genbank_content.split('//\n')
            
            for record_text in record_texts:
                record_text = record_text.strip()
                if record_text:
                    record = GenBankParser._parse_single_record(record_text)
                    if record:
                        records.append(record)
            
            return records
            
        except Exception as e:
            raise ParseError(f"Failed to parse GenBank: {str(e)}")
    
    @staticmethod
    def _parse_single_record(record_text: str) -> Optional[GenBankRecord]:
        """
        Parse a single GenBank record.
        
        Args:
            record_text: Single record text
            
        Returns:
            GenBankRecord object or None if parsing fails
        """
        lines = record_text.split('\n')
        
        # Initialize record fields
        locus = ""
        definition = ""
        accession = ""
        version = ""
        keywords = ""
        source = ""
        organism = ""
        references = []
        features = []
        origin = ""
        
        current_section = None
        current_feature = None
        continuation_line = ""
        
        for line in lines:
            # Handle continuation lines (lines starting with spaces)
            if line.startswith(' ') and current_section:
                continuation_line += " " + line.strip()
                continue
            else:
                # Process previous continuation line
                if continuation_line and current_section:
                    GenBankParser._process_line(
                        current_section, continuation_line, 
                        locals(), current_feature
                    )
                    continuation_line = ""
            
            # Parse line header
            if len(line) >= 12:
                header = line[:12].strip()
                content = line[12:].strip()
                
                if header:
                    current_section = header
                    continuation_line = content
                else:
                    continuation_line += " " + content
        
        # Process final continuation line
        if continuation_line and current_section:
            GenBankParser._process_line(
                current_section, continuation_line,
                locals(), current_feature
            )
        
        # Create record
        return GenBankRecord(
            locus=locus,
            definition=definition,
            accession=accession,
            version=version,
            keywords=keywords,
            source=source,
            organism=organism,
            references=references,
            features=features,
            origin=origin
        )
    
    @staticmethod
    def _process_line(section: str, content: str, record_vars: Dict[str, Any], 
                     current_feature: Optional[GenBankFeature]) -> Optional[GenBankFeature]:
        """
        Process a single GenBank line.
        
        Args:
            section: Section header
            content: Line content
            record_vars: Record variables dictionary
            current_feature: Current feature being processed
            
        Returns:
            Updated current feature
        """
        if section == "LOCUS":
            record_vars['locus'] = content
        
        elif section == "DEFINITION":
            if record_vars['definition']:
                record_vars['definition'] += " " + content
            else:
                record_vars['definition'] = content
        
        elif section == "ACCESSION":
            record_vars['accession'] = content.split()[0]  # First accession
        
        elif section == "VERSION":
            record_vars['version'] = content
        
        elif section == "KEYWORDS":
            record_vars['keywords'] = content
        
        elif section == "SOURCE":
            record_vars['source'] = content
        
        elif section == "ORGANISM":
            record_vars['organism'] = content
        
        elif section == "REFERENCE":
            # Parse reference (simplified)
            ref_match = re.match(r'(\d+)', content)
            if ref_match:
                record_vars['references'].append({
                    'number': ref_match.group(1),
                    'citation': content
                })
        
        elif section == "FEATURES":
            # Parse features section
            if content.strip():
                current_feature = GenBankParser._parse_feature_line(
                    content, record_vars['features'], current_feature
                )
        
        elif section == "ORIGIN":
            record_vars['origin'] += content
        
        return current_feature
    
    @staticmethod
    def _parse_feature_line(line: str, features: List[GenBankFeature], 
                           current_feature: Optional[GenBankFeature]) -> Optional[GenBankFeature]:
        """
        Parse a feature line.
        
        Args:
            line: Feature line content
            features: List to append features to
            current_feature: Current feature being processed
            
        Returns:
            Updated current feature
        """
        # Check if this is a new feature (starts with non-space)
        feature_match = re.match(r'^(\w+)\s+(.+)', line.strip())
        if feature_match:
            # Save previous feature
            if current_feature:
                features.append(current_feature)
            
            # Start new feature
            key = feature_match.group(1)
            location = feature_match.group(2)
            current_feature = GenBankFeature(
                key=key,
                location=location,
                qualifiers={}
            )
        
        elif current_feature and line.strip().startswith('/'):
            # Parse qualifier
            qual_match = re.match(r'/([^=]+)=?"?([^"]*)"?', line.strip())
            if qual_match:
                qual_name = qual_match.group(1)
                qual_value = qual_match.group(2)
                current_feature.qualifiers[qual_name] = qual_value
        
        return current_feature
    
    @staticmethod
    def parse_file(file_path: str) -> List[GenBankRecord]:
        """
        Parse GenBank file.
        
        Args:
            file_path: Path to GenBank file
            
        Returns:
            List of GenBankRecord objects
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return GenBankParser.parse(content)
        except IOError as e:
            raise ParseError(f"Cannot read GenBank file {file_path}: {str(e)}")
    
    @staticmethod
    def to_fasta(record: GenBankRecord) -> str:
        """
        Convert GenBank record to FASTA format.
        
        Args:
            record: GenBankRecord to convert
            
        Returns:
            FASTA formatted string
        """
        header = f">{record.accession} {record.definition}"
        sequence = record.sequence
        
        # Break sequence into 70-character lines
        lines = [header]
        for i in range(0, len(sequence), 70):
            lines.append(sequence[i:i+70])
        
        return '\n'.join(lines)
    
    @staticmethod
    def extract_cds_features(record: GenBankRecord) -> List[GenBankFeature]:
        """
        Extract CDS (coding sequence) features from record.
        
        Args:
            record: GenBankRecord to extract from
            
        Returns:
            List of CDS features
        """
        return [feature for feature in record.features if feature.key == "CDS"]
    
    @staticmethod
    def extract_gene_features(record: GenBankRecord) -> List[GenBankFeature]:
        """
        Extract gene features from record.
        
        Args:
            record: GenBankRecord to extract from
            
        Returns:
            List of gene features
        """
        return [feature for feature in record.features if feature.key == "gene"]
    
    @staticmethod
    def get_feature_by_qualifier(record: GenBankRecord, qualifier: str, 
                                value: str) -> List[GenBankFeature]:
        """
        Find features by qualifier value.
        
        Args:
            record: GenBankRecord to search
            qualifier: Qualifier name to match
            value: Qualifier value to match
            
        Returns:
            List of matching features
        """
        matches = []
        for feature in record.features:
            if qualifier in feature.qualifiers:
                if value.lower() in feature.qualifiers[qualifier].lower():
                    matches.append(feature)
        return matches
