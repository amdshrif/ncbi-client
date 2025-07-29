#!/usr/bin/env python3
"""
Basic usage example for NCBI Client.

This example demonstrates the core functionality of the NCBI client,
including searching, fetching, and linking operations.
"""

import os
from ncbi_client import NCBIClient


def main():
    """Run basic examples."""
    
    # Initialize client
    # You can set NCBI_API_KEY environment variable or pass it directly
    api_key = os.environ.get('NCBI_API_KEY')
    client = NCBIClient(
        api_key=api_key,
        email="your@email.com",  # Replace with your email
        tool="ncbi-client-example"
    )
    
    print("NCBI Client Example")
    print("=" * 50)
    
    # Example 1: Search PubMed for COVID-19 articles
    print("\n1. Searching PubMed for COVID-19 articles...")
    search_results = client.esearch.search(
        db="pubmed",
        term="COVID-19[title] AND vaccine",
        retmax=10
    )
    
    print(f"Found {search_results['count']} articles")
    print(f"Showing first {len(search_results['id_list'])} PMIDs:")
    for pmid in search_results['id_list']:
        print(f"  - {pmid}")
    
    # Example 2: Get article summaries
    if search_results['id_list']:
        print("\n2. Getting article summaries...")
        summaries = client.esummary.summary(
            db="pubmed",
            id_list=search_results['id_list'][:3]
        )
        
        for docsum in summaries['docsums']:
            title = docsum.get('Title', 'No title')
            authors = docsum.get('AuthorList', 'No authors')
            print(f"  - {title}")
            print(f"    Authors: {authors}")
    
    # Example 3: Search nucleotide database
    print("\n3. Searching nucleotide database...")
    nuc_search = client.esearch.search(
        db="nucleotide",
        term="insulin[gene] AND human[organism]",
        retmax=5
    )
    
    print(f"Found {nuc_search['count']} nucleotide records")
    
    # Example 4: Get sequence data in FASTA format
    if nuc_search['id_list']:
        print("\n4. Fetching sequences in FASTA format...")
        sequences = client.efetch.fetch(
            db="nucleotide",
            id_list=nuc_search['id_list'][:2],
            rettype="fasta",
            retmode="text"
        )
        
        # Show first few lines of FASTA output
        lines = sequences.split('\n')[:10]
        for line in lines:
            print(f"  {line}")
        if len(sequences.split('\n')) > 10:
            print("  ...")
    
    # Example 5: Find related articles
    if search_results['id_list']:
        print("\n5. Finding related articles...")
        related = client.elink.link(
            dbfrom="pubmed",
            db="pubmed",
            id_list=[search_results['id_list'][0]]
        )
        
        if related['linksets']:
            linkset = related['linksets'][0]
            if linkset['linksetdbs']:
                related_ids = linkset['linksetdbs'][0]['links'][:5]
                print(f"Found {len(related_ids)} related articles (showing first 5):")
                for rid in related_ids:
                    print(f"  - {rid}")
    
    # Example 6: Global search across databases
    print("\n6. Global search across all databases...")
    global_search = client.egquery.global_search("insulin")
    
    print("Database hit counts:")
    for db_result in global_search['databases'][:10]:  # Show first 10
        db_name = db_result['dbname']
        count = db_result['count']
        print(f"  {db_name}: {count:,} hits")
    
    # Example 7: Get database information
    print("\n7. Getting database information...")
    db_info = client.einfo.get_database_info("pubmed")
    
    print(f"PubMed database info:")
    print(f"  Description: {db_info['description']}")
    print(f"  Record count: {db_info['count']:,}")
    print(f"  Last update: {db_info['lastupdate']}")
    
    # Show some search fields
    fields = db_info['fields'][:5]  # First 5 fields
    print(f"  Available search fields (showing first 5):")
    for field in fields:
        print(f"    - {field['name']}: {field['description']}")
    
    print("\n" + "=" * 50)
    print("Example completed!")


if __name__ == "__main__":
    main()
