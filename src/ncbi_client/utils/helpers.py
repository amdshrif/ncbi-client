"""
Helper utilities for NCBI client.

Provides various utility functions for data processing,
validation, and common operations.
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Union, Tuple
from urllib.parse import urlencode, quote
from datetime import datetime, timedelta


class ValidationHelpers:
    """
    Validation utilities for NCBI data.
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_pubmed_id(pmid: Union[str, int]) -> bool:
        """
        Validate PubMed ID format.
        
        Args:
            pmid: PubMed ID to validate
            
        Returns:
            True if valid PMID format
        """
        try:
            pmid_int = int(pmid)
            return pmid_int > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_nucleotide_accession(accession: str) -> bool:
        """
        Validate nucleotide accession number format.
        
        Args:
            accession: Accession number to validate
            
        Returns:
            True if valid accession format
        """
        patterns = [
            r'^[A-Z]{1,2}_?\d{6,8}(\.\d+)?$',  # RefSeq
            r'^[A-Z]{2}\d{6,8}(\.\d+)?$',      # GenBank
            r'^[A-Z]{4}\d{8,10}(\.\d+)?$'      # WGS
        ]
        
        return any(re.match(pattern, accession.upper()) for pattern in patterns)
    
    @staticmethod
    def validate_protein_accession(accession: str) -> bool:
        """
        Validate protein accession number format.
        
        Args:
            accession: Accession number to validate
            
        Returns:
            True if valid accession format
        """
        patterns = [
            r'^[A-Z]{2,3}_?\d{6,8}(\.\d+)?$',  # RefSeq
            r'^[A-Z]{3}\d{5,8}(\.\d+)?$'       # GenBank
        ]
        
        return any(re.match(pattern, accession.upper()) for pattern in patterns)


class FormatHelpers:
    """
    Formatting utilities for NCBI data.
    """
    
    @staticmethod
    def format_date_range(start_date: str, end_date: str) -> str:
        """
        Format date range for NCBI queries.
        
        Args:
            start_date: Start date (YYYY/MM/DD or YYYY)
            end_date: End date (YYYY/MM/DD or YYYY)
            
        Returns:
            Formatted date range string
        """
        return f"{start_date}:{end_date}[pdat]"
    
    @staticmethod
    def format_author_search(author: str) -> str:
        """
        Format author name for search.
        
        Args:
            author: Author name
            
        Returns:
            Formatted author search string
        """
        return f"{author}[author]"
    
    @staticmethod
    def format_journal_search(journal: str) -> str:
        """
        Format journal name for search.
        
        Args:
            journal: Journal name
            
        Returns:
            Formatted journal search string
        """
        return f"{journal}[journal]"
    
    @staticmethod
    def format_mesh_term(term: str) -> str:
        """
        Format MeSH term for search.
        
        Args:
            term: MeSH term
            
        Returns:
            Formatted MeSH search string
        """
        return f"{term}[mesh]"
    
    @staticmethod
    def build_complex_query(terms: List[str], operator: str = "AND") -> str:
        """
        Build complex search query from terms.
        
        Args:
            terms: List of search terms
            operator: Boolean operator (AND, OR, NOT)
            
        Returns:
            Combined search query
        """
        if not terms:
            return ""
        
        return f" {operator} ".join(f"({term})" for term in terms)
    
    @staticmethod
    def escape_search_term(term: str) -> str:
        """
        Escape special characters in search term.
        
        Args:
            term: Search term to escape
            
        Returns:
            Escaped search term
        """
        special_chars = ['[', ']', '(', ')', '"', "'"]
        escaped_term = term
        
        for char in special_chars:
            escaped_term = escaped_term.replace(char, f'\\{char}')
        
        return escaped_term


class XMLHelpers:
    """
    XML processing utilities.
    """
    
    @staticmethod
    def safe_xml_parse(xml_string: str) -> Optional[ET.Element]:
        """
        Safely parse XML string.
        
        Args:
            xml_string: XML string to parse
            
        Returns:
            Parsed XML root element or None if parsing fails
        """
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError:
            return None
    
    @staticmethod
    def get_text_content(element: ET.Element, xpath: str, default: str = "") -> str:
        """
        Get text content from XML element using XPath.
        
        Args:
            element: XML element
            xpath: XPath expression
            default: Default value if not found
            
        Returns:
            Text content or default value
        """
        try:
            found = element.find(xpath)
            return found.text if found is not None and found.text else default
        except Exception:
            return default
    
    @staticmethod
    def get_all_text_content(element: ET.Element, xpath: str) -> List[str]:
        """
        Get all text content from XML elements using XPath.
        
        Args:
            element: XML element
            xpath: XPath expression
            
        Returns:
            List of text content
        """
        try:
            elements = element.findall(xpath)
            return [elem.text for elem in elements if elem.text]
        except Exception:
            return []
    
    @staticmethod
    def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary.
        
        Args:
            element: XML element
            
        Returns:
            Dictionary representation
        """
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_dict = XMLHelpers.xml_to_dict(child)
            
            if child.tag in result:
                # Handle multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        
        return result


class URLHelpers:
    """
    URL construction and manipulation utilities.
    """
    
    @staticmethod
    def build_query_string(params: Dict[str, Any]) -> str:
        """
        Build URL query string from parameters.
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            URL-encoded query string
        """
        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}
        return urlencode(filtered_params)
    
    @staticmethod
    def safe_url_encode(value: str) -> str:
        """
        Safely URL encode a value.
        
        Args:
            value: String to encode
            
        Returns:
            URL-encoded string
        """
        return quote(str(value), safe='')
    
    @staticmethod
    def join_url_parts(*parts: str) -> str:
        """
        Join URL parts with proper separators.
        
        Args:
            parts: URL parts to join
            
        Returns:
            Complete URL
        """
        # Remove leading/trailing slashes and join with single slash
        clean_parts = [part.strip('/') for part in parts if part]
        return '/'.join(clean_parts)


class DataHelpers:
    """
    Data processing and manipulation utilities.
    """
    
    @staticmethod
    def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Split list into chunks of specified size.
        
        Args:
            data: List to chunk
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    @staticmethod
    def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
        """
        Flatten nested list structure.
        
        Args:
            nested_list: Nested list to flatten
            
        Returns:
            Flattened list
        """
        return [item for sublist in nested_list for item in sublist]
    
    @staticmethod
    def remove_duplicates(data: List[Any], key_func: Optional[callable] = None) -> List[Any]:
        """
        Remove duplicates from list while preserving order.
        
        Args:
            data: List with potential duplicates
            key_func: Optional function to extract comparison key
            
        Returns:
            List without duplicates
        """
        seen = set()
        result = []
        
        for item in data:
            key = key_func(item) if key_func else item
            
            if key not in seen:
                seen.add(key)
                result.append(item)
        
        return result
    
    @staticmethod
    def safe_int_convert(value: Any, default: int = 0) -> int:
        """
        Safely convert value to integer.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Integer value or default
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float_convert(value: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Float value or default
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


class DateHelpers:
    """
    Date and time utilities.
    """
    
    @staticmethod
    def parse_pubmed_date(date_str: str) -> Optional[datetime]:
        """
        Parse PubMed date string to datetime.
        
        Args:
            date_str: Date string from PubMed
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        formats = [
            '%Y/%m/%d',
            '%Y/%m',
            '%Y',
            '%Y %b %d',
            '%Y %b',
            '%b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def format_date_for_query(date: datetime) -> str:
        """
        Format datetime for NCBI query.
        
        Args:
            date: Datetime to format
            
        Returns:
            Formatted date string
        """
        return date.strftime('%Y/%m/%d')
    
    @staticmethod
    def get_date_range(days_back: int) -> Tuple[str, str]:
        """
        Get date range for recent publications.
        
        Args:
            days_back: Number of days to go back
            
        Returns:
            Tuple of (start_date, end_date) strings
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return (
            DateHelpers.format_date_for_query(start_date),
            DateHelpers.format_date_for_query(end_date)
        )


class ErrorHelpers:
    """
    Error handling and reporting utilities.
    """
    
    @staticmethod
    def extract_error_info(response_text: str) -> Dict[str, str]:
        """
        Extract error information from API response.
        
        Args:
            response_text: API response text
            
        Returns:
            Dictionary with error details
        """
        error_info = {
            'message': 'Unknown error',
            'type': 'API Error',
            'details': response_text[:500]  # Limit details length
        }
        
        # Try to parse XML error response
        root = XMLHelpers.safe_xml_parse(response_text)
        if root is not None:
            error_msg = XMLHelpers.get_text_content(root, './/ErrorList/PhraseNotFound')
            if error_msg:
                error_info['message'] = error_msg
                error_info['type'] = 'Search Error'
        
        return error_info
    
    @staticmethod
    def format_error_message(error_info: Dict[str, str], context: str = "") -> str:
        """
        Format error message for display.
        
        Args:
            error_info: Error information dictionary
            context: Additional context information
            
        Returns:
            Formatted error message
        """
        message = f"{error_info['type']}: {error_info['message']}"
        
        if context:
            message = f"{context} - {message}"
        
        return message
