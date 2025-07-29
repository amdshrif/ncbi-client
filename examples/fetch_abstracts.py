#!/usr/bin/env python3
"""
Advanced CLI example: Fetch article abstracts and save to file.

This example demonstrates:
1. Searching for articles
2. Fetching abstracts
3. Saving results to a file
4. Error handling
"""

import sys
import json
import argparse
from pathlib import Path
from ncbi_client import NCBIClient


def fetch_abstracts(query, max_results=10, output_file=None, api_key=None, email=None, verify_ssl=True):
    """
    Search PubMed and fetch abstracts for the results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to fetch
        output_file: Optional output file path
        api_key: Optional NCBI API key
        email: Email for identification
        verify_ssl: Whether to verify SSL certificates
    """
    # Initialize client
    client = NCBIClient(api_key=api_key, email=email, verify_ssl=verify_ssl)
    
    print(f"Searching PubMed for: {query}")
    
    # Search for articles
    search_results = client.esearch.search(
        db="pubmed",
        term=query,
        retmax=max_results,
        sort="pub_date"  # Sort by publication date
    )
    
    total_found = search_results['count']
    id_list = search_results['id_list']
    
    print(f"Found {total_found} total results, fetching {len(id_list)} abstracts...")
    
    if not id_list:
        print("No results found.")
        return
    
    # Fetch abstracts
    abstracts = client.efetch.fetch(
        db="pubmed",
        id_list=id_list,
        rettype="abstract",
        retmode="xml"
    )
    
    # Also get summaries for metadata
    summaries = client.esummary.summary(
        db="pubmed",
        id_list=id_list,
        version="2.0"
    )
    
    # Combine data
    results = {
        'query': query,
        'total_found': total_found,
        'retrieved': len(id_list),
        'abstracts_xml': abstracts,
        'summaries': summaries
    }
    
    # Save or print results
    if output_file:
        output_path = Path(output_file)
        
        if output_path.suffix.lower() == '.json':
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_path}")
            
        elif output_path.suffix.lower() == '.xml':
            # Save just the XML abstracts
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(abstracts)
            print(f"Abstract XML saved to {output_path}")
            
        else:
            # Save as text summary
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Search Query: {query}\n")
                f.write(f"Total Found: {total_found}\n")
                f.write(f"Retrieved: {len(id_list)}\n\n")
                
                f.write("Article IDs:\n")
                for pmid in id_list:
                    f.write(f"  PMID:{pmid}\n")
                
                f.write(f"\nFull XML abstracts:\n{abstracts}\n")
            print(f"Results saved to {output_path}")
    else:
        # Print summary to stdout
        print(f"\nResults for '{query}':")
        print(f"Total articles found: {total_found}")
        print(f"Retrieved: {len(id_list)}")
        print("\nPubMed IDs:")
        for pmid in id_list:
            print(f"  PMID:{pmid}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch PubMed abstracts for a search query',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python fetch_abstracts.py "COVID-19 vaccine" --max-results 20
  python fetch_abstracts.py "machine learning" --output ml_abstracts.json
  python fetch_abstracts.py "CRISPR" --max-results 50 --output crispr.xml --api-key YOUR_KEY
        '''
    )
    
    parser.add_argument('query', help='Search query for PubMed')
    parser.add_argument('--max-results', type=int, default=10,
                       help='Maximum number of results to fetch (default: 10)')
    parser.add_argument('--output', '-o', help='Output file (JSON, XML, or text)')
    parser.add_argument('--api-key', help='NCBI API key for higher rate limits')
    parser.add_argument('--email', help='Email address for identification')
    parser.add_argument('--no-ssl-verify', action='store_true',
                       help='Disable SSL certificate verification')
    
    args = parser.parse_args()
    
    try:
        fetch_abstracts(
            query=args.query,
            max_results=args.max_results,
            output_file=args.output,
            api_key=args.api_key,
            email=args.email,
            verify_ssl=not args.no_ssl_verify
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
