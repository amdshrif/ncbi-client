"""
Comprehensive example demonstrating NCBI client capabilities.

This example shows how to use the various components of the ncbi-client package
to search, fetch, and analyze biological data from NCBI databases.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ncbi_client import (
    NCBIClient, 
    ValidationHelpers, FormatHelpers, DataHelpers,
    SequenceTools, FormatConverter,
    DatasetsAPI, PubChemAPI,
    CacheManager
)


def main():
    """Main example function."""
    
    # Initialize NCBI client
    print("=== NCBI Client Example ===\n")
    
    # Configure with your email (required by NCBI)
    client = NCBIClient(email="your.email@example.com", api_key="your_api_key_if_available")
    
    print("1. PubMed Search Example")
    print("-" * 30)
    
    # Search PubMed for COVID-19 papers
    search_results = client.esearch.search(
        db="pubmed",
        term="COVID-19 AND vaccine",
        retmax=5,
        sort="pub_date"
    )
    
    print(f"Found {search_results.get('count', 0)} papers")
    
    if search_results.get('idlist'):
        # Fetch detailed information for first few papers
        pmids = search_results['idlist'][:3]
        
        fetch_results = client.efetch.fetch(
            db="pubmed",
            id=pmids,
            rettype="xml"
        )
        
        print(f"Fetched details for {len(pmids)} papers")
        print("Sample paper titles:")
        
        # Parse XML to extract titles (simplified)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(fetch_results)
        
        for article in root.findall('.//Article'):
            title_elem = article.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                print(f"- {title_elem.text[:80]}...")
    
    print("\n2. Nucleotide Database Example")
    print("-" * 30)
    
    # Search for SARS-CoV-2 sequences
    nucl_search = client.esearch.search(
        db="nucleotide",
        term="SARS-CoV-2[Organism] AND complete genome",
        retmax=3
    )
    
    if nucl_search.get('idlist'):
        # Fetch FASTA sequences
        sequences = client.efetch.fetch(
            db="nucleotide",
            id=nucl_search['idlist'][:2],
            rettype="fasta"
        )
        
        print("Retrieved FASTA sequences:")
        # Parse FASTA
        from ncbi_client.parsers.fasta_parser import FASTAParser
        
        fasta_records = FASTAParser.parse_string(sequences)
        for record in fasta_records[:1]:  # Show first record
            print(f"ID: {record.id}")
            print(f"Description: {record.description[:80]}...")
            print(f"Length: {len(record.sequence)} bp")
            
            # Analyze sequence composition
            composition = SequenceTools.analyze_composition(record.sequence)
            print(f"GC Content: {composition.get('GC_percent', 0):.1f}%")
    
    print("\n3. Sequence Analysis Example")
    print("-" * 30)
    
    # Example DNA sequence for analysis
    dna_sequence = "ATGAAGTGCAACATCGAGGTGAAGATCTCCTTCCGCAAGCTGAAGGACTACGAGTAG"
    
    print(f"Original sequence: {dna_sequence}")
    print(f"Reverse complement: {SequenceTools.reverse_complement(dna_sequence)}")
    
    # Translate to protein
    protein = SequenceTools.translate(dna_sequence)
    print(f"Translated protein: {protein}")
    
    # Calculate melting temperature
    tm = SequenceTools.calculate_melting_temperature(dna_sequence)
    print(f"Melting temperature: {tm:.1f}°C")
    
    print("\n4. Format Conversion Example")
    print("-" * 30)
    
    # Convert formats (using mock XML data)
    mock_xml = """<?xml version="1.0"?>
    <GBSet>
        <GBSeq>
            <GBSeq_accession-version>NC_045512.2</GBSeq_accession-version>
            <GBSeq_definition>SARS-CoV-2 complete genome</GBSeq_definition>
            <GBSeq_sequence>ATGAAGTGCAACATCGAGGTG</GBSeq_sequence>
        </GBSeq>
    </GBSet>"""
    
    try:
        fasta_output = FormatConverter.xml_to_fasta(mock_xml)
        print("Converted XML to FASTA:")
        print(fasta_output[:100] + "..." if len(fasta_output) > 100 else fasta_output)
    except Exception as e:
        print(f"Format conversion error: {e}")
    
    print("\n5. Validation Examples")
    print("-" * 30)
    
    # Test various validations
    test_email = "user@example.com"
    test_pmid = "12345678"
    test_accession = "NC_045512.2"
    
    print(f"Email '{test_email}' valid: {ValidationHelpers.validate_email(test_email)}")
    print(f"PMID '{test_pmid}' valid: {ValidationHelpers.validate_pubmed_id(test_pmid)}")
    print(f"Accession '{test_accession}' valid: {ValidationHelpers.validate_nucleotide_accession(test_accession)}")
    
    print("\n6. Search Query Formatting")
    print("-" * 30)
    
    # Build complex search queries
    author_query = FormatHelpers.format_author_search("Smith J")
    journal_query = FormatHelpers.format_journal_search("Nature")
    mesh_query = FormatHelpers.format_mesh_term("COVID-19")
    
    complex_query = FormatHelpers.build_complex_query([
        author_query, journal_query, mesh_query
    ], "AND")
    
    print(f"Complex query: {complex_query}")
    
    print("\n7. Data Processing Examples")
    print("-" * 30)
    
    # Example data processing
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chunks = DataHelpers.chunk_list(sample_data, 3)
    print(f"Chunked data: {chunks}")
    
    # Remove duplicates
    data_with_dupes = ["A", "B", "A", "C", "B", "D"]
    unique_data = DataHelpers.remove_duplicates(data_with_dupes)
    print(f"Unique data: {unique_data}")
    
    print("\n8. Datasets API Example")
    print("-" * 30)
    
    try:
        # Initialize Datasets API
        datasets = DatasetsAPI(client)
        
        # Search for E. coli genomes
        genome_search = datasets.search_genomes(
            taxon="Escherichia coli",
            filters={"filters.assembly_level": "Complete Genome"},
            page_size=3
        )
        
        print("Found genome assemblies (first few):")
        if 'reports' in genome_search:
            for assembly in genome_search['reports'][:2]:
                print(f"- {assembly.get('accession', 'N/A')}: {assembly.get('organism', {}).get('organism_name', 'N/A')}")
        
    except Exception as e:
        print(f"Datasets API example failed: {e}")
    
    print("\n9. PubChem API Example")
    print("-" * 30)
    
    try:
        # Initialize PubChem API
        pubchem = PubChemAPI(client)
        
        # Search for aspirin
        compound_data = pubchem.get_compound_by_name("aspirin", properties=["MolecularFormula", "MolecularWeight"])
        
        print("Aspirin compound information:")
        if 'PropertyTable' in compound_data:
            props = compound_data['PropertyTable']['Properties'][0]
            print(f"- Molecular Formula: {props.get('MolecularFormula', 'N/A')}")
            print(f"- Molecular Weight: {props.get('MolecularWeight', 'N/A')}")
        
    except Exception as e:
        print(f"PubChem API example failed: {e}")
    
    print("\n10. Caching Example")
    print("-" * 30)
    
    # Initialize cache
    cache = CacheManager(default_ttl=300)  # 5 minutes
    
    # Example cache usage
    cache_key = "test_data"
    test_data = {"message": "This is cached data", "timestamp": "2024-01-01"}
    
    # Store in cache
    cache.set("http://example.com/api", test_data, ttl=600)
    
    # Retrieve from cache
    cached_data = cache.get("http://example.com/api")
    if cached_data:
        print(f"Retrieved from cache: {cached_data}")
    
    # Get cache statistics
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    print("\n=== Example Complete ===")
    print("\nThis example demonstrates the major features of the ncbi-client package.")
    print("For production use, make sure to:")
    print("1. Set your actual email address")
    print("2. Get an API key from NCBI for higher rate limits") 
    print("3. Handle errors appropriately")
    print("4. Use appropriate retry logic for network requests")


if __name__ == "__main__":
    main()
