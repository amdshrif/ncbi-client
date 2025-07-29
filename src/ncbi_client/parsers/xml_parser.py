"""
XML parsing utilities for NCBI responses.

Provides robust XML parsing with error handling and format detection.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Union
from io import StringIO

from ncbi_client.core.exceptions import ParseError


class XMLParser:
    """
    Enhanced XML parser for NCBI E-utilities responses.
    
    Handles various XML formats returned by different E-utilities
    and provides convenient methods for extracting data.
    """
    
    @staticmethod
    def parse(xml_content: str) -> ET.Element:
        """
        Parse XML content with error handling.
        
        Args:
            xml_content: XML string to parse
            
        Returns:
            Root element of parsed XML
            
        Raises:
            ParseError: If XML parsing fails
        """
        try:
            # Handle BOM and encoding issues
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]
            
            return ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse XML: {str(e)}")
        except Exception as e:
            raise ParseError(f"Unexpected error parsing XML: {str(e)}")
    
    @staticmethod
    def parse_esearch_result(xml_content: str) -> Dict[str, Any]:
        """
        Parse ESearch XML response.
        
        Args:
            xml_content: ESearch XML response
            
        Returns:
            Parsed search results
        """
        root = XMLParser.parse(xml_content)
        
        result = {
            'count': int(root.findtext('Count', '0')),
            'retmax': int(root.findtext('RetMax', '0')),
            'retstart': int(root.findtext('RetStart', '0')),
            'id_list': []
        }
        
        # Extract ID list
        id_list = root.find('IdList')
        if id_list is not None:
            result['id_list'] = [id_elem.text for id_elem in id_list.findall('Id')]
        
        # Extract history information
        webenv = root.findtext('WebEnv')
        query_key = root.findtext('QueryKey')
        if webenv:
            result['webenv'] = webenv
        if query_key:
            result['query_key'] = int(query_key)
        
        # Extract translation set
        translation_set = root.find('TranslationSet')
        if translation_set is not None:
            translations = []
            for trans in translation_set.findall('Translation'):
                translations.append({
                    'from': trans.findtext('From'),
                    'to': trans.findtext('To')
                })
            result['translations'] = translations
        
        return result
    
    @staticmethod
    def parse_pubmed_article(article_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a PubMed article element.
        
        Args:
            article_element: XML element containing article data
            
        Returns:
            Parsed article information
        """
        article = {}
        
        # Basic article info
        medline_citation = article_element.find('MedlineCitation')
        if medline_citation is not None:
            pmid_elem = medline_citation.find('PMID')
            if pmid_elem is not None:
                article['pmid'] = pmid_elem.text
            
            # Article details
            article_elem = medline_citation.find('Article')
            if article_elem is not None:
                # Title
                title_elem = article_elem.find('ArticleTitle')
                if title_elem is not None:
                    article['title'] = title_elem.text
                
                # Abstract
                abstract_elem = article_elem.find('Abstract/AbstractText')
                if abstract_elem is not None:
                    article['abstract'] = abstract_elem.text
                
                # Journal
                journal_elem = article_elem.find('Journal')
                if journal_elem is not None:
                    journal_title = journal_elem.findtext('Title')
                    if journal_title:
                        article['journal'] = journal_title
                
                # Authors
                author_list = article_elem.find('AuthorList')
                if author_list is not None:
                    authors = []
                    for author in author_list.findall('Author'):
                        last_name = author.findtext('LastName', '')
                        fore_name = author.findtext('ForeName', '')
                        if last_name:
                            authors.append(f"{last_name}, {fore_name}".strip(', '))
                    article['authors'] = authors
        
        return article
    
    @staticmethod
    def parse_genbank_set(xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse GenBank XML format.
        
        Args:
            xml_content: GenBank XML content
            
        Returns:
            List of parsed GenBank records
        """
        root = XMLParser.parse(xml_content)
        records = []
        
        # Handle both single records and sets
        gb_seqs = root.findall('.//GBSeq')
        if not gb_seqs:
            gb_seqs = [root] if root.tag == 'GBSeq' else []
        
        for gb_seq in gb_seqs:
            record = {
                'accession': gb_seq.findtext('GBSeq_primary-accession'),
                'definition': gb_seq.findtext('GBSeq_definition'),
                'length': int(gb_seq.findtext('GBSeq_length', '0')),
                'organism': gb_seq.findtext('GBSeq_organism'),
                'sequence': gb_seq.findtext('GBSeq_sequence'),
                'features': []
            }
            
            # Parse features
            feature_table = gb_seq.find('GBSeq_feature-table')
            if feature_table is not None:
                for feature in feature_table.findall('GBFeature'):
                    feat_data = {
                        'key': feature.findtext('GBFeature_key'),
                        'location': feature.findtext('GBFeature_location'),
                        'qualifiers': {}
                    }
                    
                    # Parse qualifiers
                    quals = feature.find('GBFeature_quals')
                    if quals is not None:
                        for qual in quals.findall('GBQualifier'):
                            name = qual.findtext('GBQualifier_name')
                            value = qual.findtext('GBQualifier_value')
                            if name:
                                feat_data['qualifiers'][name] = value
                    
                    record['features'].append(feat_data)
            
            records.append(record)
        
        return records
    
    @staticmethod
    def extract_error_messages(xml_content: str) -> List[str]:
        """
        Extract error messages from XML response.
        
        Args:
            xml_content: XML content that may contain errors
            
        Returns:
            List of error messages
        """
        try:
            root = XMLParser.parse(xml_content)
            errors = []
            
            # Check for various error formats
            error_elem = root.find('ERROR')
            if error_elem is not None:
                errors.append(error_elem.text)
            
            error_list = root.find('ErrorList')
            if error_list is not None:
                for error in error_list.findall('PhraseNotFound'):
                    errors.append(f"Phrase not found: {error.text}")
            
            return errors
        except ParseError:
            return []
    
    @staticmethod
    def to_dict(element: ET.Element, include_attributes: bool = True) -> Dict[str, Any]:
        """
        Convert XML element to dictionary.
        
        Args:
            element: XML element to convert
            include_attributes: Whether to include element attributes
            
        Returns:
            Dictionary representation of XML
        """
        result = {}
        
        # Add attributes if requested
        if include_attributes and element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text
            result['#text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = XMLParser.to_dict(child, include_attributes)
            
            if child.tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
