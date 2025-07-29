# Literature Search Tutorial

Learn how to search and retrieve literature from PubMed and PMC using NCBI Client.

## Overview

This tutorial covers:
- Basic literature searches
- Advanced search techniques
- Retrieving full abstracts and metadata
- Finding related articles
- Exporting citations
- Analyzing publication trends

## Basic Literature Search

### Simple Search

```python
from ncbi_client import NCBIClient

# Initialize client
client = NCBIClient(email="your.email@example.com")

# Search for COVID-19 vaccine papers
results = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine",
    retmax=50
)

print(f"Found {results['count']} articles")
print(f"Retrieved {len(results['id_list'])} PMIDs")
```

### Search with Date Range

```python
# Search for recent papers (last 2 years)
recent_papers = client.esearch.search(
    db="pubmed",
    term="machine learning AND genomics",
    retmax=100,
    datetype="pdat",  # Publication date
    reldate=730       # Last 730 days (2 years)
)

# Or specify exact date range
date_range_papers = client.esearch.search(
    db="pubmed", 
    term="CRISPR gene editing",
    retmax=100,
    datetype="pdat",
    mindate="2023/01/01",
    maxdate="2023/12/31"
)
```

### Sort Results

```python
# Sort by publication date (newest first)
sorted_results = client.esearch.search(
    db="pubmed",
    term="artificial intelligence healthcare",
    retmax=50,
    sort="pub_date"
)

# Sort by first author
author_sorted = client.esearch.search(
    db="pubmed",
    term="cancer immunotherapy", 
    retmax=50,
    sort="first_author"
)

# Sort by journal name
journal_sorted = client.esearch.search(
    db="pubmed",
    term="climate change health",
    retmax=50,
    sort="journal"
)
```

## Advanced Search Techniques

### Boolean Operators

```python
# AND operator (default)
results = client.esearch.search(
    db="pubmed",
    term="diabetes AND insulin AND therapy"
)

# OR operator
results = client.esearch.search(
    db="pubmed", 
    term="(cancer OR tumor OR neoplasm) AND treatment"
)

# NOT operator
results = client.esearch.search(
    db="pubmed",
    term="heart disease NOT congenital"
)

# Complex boolean logic
results = client.esearch.search(
    db="pubmed",
    term="(COVID-19 OR SARS-CoV-2) AND (vaccine OR vaccination) NOT review[ptyp]"
)
```

### Field-Specific Searches

```python
# Search in title only
title_search = client.esearch.search(
    db="pubmed",
    term="machine learning[Title]"
)

# Search by author
author_search = client.esearch.search(
    db="pubmed",
    term="Smith J[Author]"
)

# Search by journal
journal_search = client.esearch.search(
    db="pubmed", 
    term="Nature[Journal]"
)

# Search by publication type
review_search = client.esearch.search(
    db="pubmed",
    term="cancer therapy AND review[ptyp]"
)

# Search by MeSH terms
mesh_search = client.esearch.search(
    db="pubmed",
    term="Diabetes Mellitus[MeSH Terms]"
)
```

### Combining Fields

```python
# Multiple field search
complex_search = client.esearch.search(
    db="pubmed",
    term='("machine learning"[Title/Abstract]) AND (genomics[MeSH Terms]) AND (2023[PDAT])'
)

# Search with multiple authors
multi_author = client.esearch.search(
    db="pubmed",
    term="(Smith J[Author]) OR (Johnson M[Author])"
)
```

## Retrieving Article Details

### Get Abstracts

```python
# Get detailed abstracts
abstracts = client.efetch.fetch(
    db="pubmed",
    id_list=results['id_list'][:10],
    rettype="abstract",
    retmode="xml"
)

# Parse abstracts (basic example)
print("Abstract data retrieved:")
print(abstracts[:1000] + "...")  # First 1000 characters
```

### Get Article Summaries

```python
# Get structured summaries
summaries = client.esummary.summary(
    db="pubmed",
    id_list=results['id_list'][:10],
    version="2.0"
)

# Extract key information
for summary in summaries['docsums']:
    print(f"PMID: {summary['uid']}")
    print(f"Title: {summary['title']}")
    print(f"Authors: {', '.join(summary.get('authors', []))}")
    print(f"Journal: {summary.get('source', 'Unknown')}")
    print(f"Date: {summary.get('pubdate', 'Unknown')}")
    print(f"DOI: {summary.get('doi', 'Not available')}")
    print("---")
```

### Get Citation Format

```python
# Get MEDLINE format for citations
citations = client.efetch.fetch(
    db="pubmed",
    id_list=results['id_list'][:5],
    rettype="medline",
    retmode="text"
)

print("MEDLINE format citations:")
print(citations)
```

## Finding Related Articles

### Related by Content

```python
# Find articles similar to a specific paper
related_articles = client.elink.link(
    dbfrom="pubmed",
    db="pubmed",
    id_list=["12345678"],  # Replace with actual PMID
    cmd="neighbor"
)

print(f"Found {len(related_articles['linked_ids'])} related articles")

# Get summaries of related articles
if related_articles['linked_ids']:
    related_summaries = client.esummary.summary(
        db="pubmed",
        id_list=related_articles['linked_ids'][:5]
    )
```

### Reviews and Meta-Analyses

```python
# Find reviews related to your topic
review_search = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine AND (review[ptyp] OR meta-analysis[ptyp])",
    retmax=20
)

# Find systematic reviews specifically
systematic_reviews = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine AND systematic review[ti]",
    retmax=10
)
```

### Clinical Trials

```python
# Find clinical trials
clinical_trials = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine AND clinical trial[ptyp]",
    retmax=30
)

# Find randomized controlled trials
rct_search = client.esearch.search(
    db="pubmed",
    term="diabetes treatment AND randomized controlled trial[ptyp]",
    retmax=25
)
```

## Working with Large Result Sets

### Using History Server

```python
# For large searches, use history server
large_search = client.esearch.search_with_history(
    db="pubmed",
    term="cancer",
    retmax=0  # Just get count and history
)

print(f"Total results: {large_search['count']}")

# Fetch results in batches
batch_size = 500
total_batches = min(large_search['count'], 10000) // batch_size

for batch in range(total_batches):
    start = batch * batch_size
    
    batch_summaries = client.esummary.summary_from_history(
        db="pubmed",
        webenv=large_search['webenv'],
        query_key=large_search['query_key'],
        retstart=start,
        retmax=batch_size
    )
    
    print(f"Processed batch {batch + 1}/{total_batches}")
    # Process your batch here
```

### Pagination

```python
# Manual pagination for smaller sets
def paginate_search(client, term, total_results=1000, page_size=100):
    all_ids = []
    
    for start in range(0, total_results, page_size):
        page_results = client.esearch.search(
            db="pubmed",
            term=term,
            retmax=page_size,
            retstart=start
        )
        
        all_ids.extend(page_results['id_list'])
        
        if len(page_results['id_list']) < page_size:
            break  # No more results
    
    return all_ids

# Use pagination
all_pmids = paginate_search(client, "machine learning healthcare", 500, 50)
print(f"Retrieved {len(all_pmids)} PMIDs total")
```

## Data Export and Analysis

### Export to Different Formats

```python
import json
import csv

def export_summaries_csv(summaries, filename):
    """Export summaries to CSV format."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['PMID', 'Title', 'Authors', 'Journal', 'Date', 'DOI']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for summary in summaries['docsums']:
            writer.writerow({
                'PMID': summary['uid'],
                'Title': summary.get('title', ''),
                'Authors': '; '.join(summary.get('authors', [])),
                'Journal': summary.get('source', ''),
                'Date': summary.get('pubdate', ''),
                'DOI': summary.get('doi', '')
            })

def export_summaries_json(summaries, filename):
    """Export summaries to JSON format."""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(summaries, jsonfile, indent=2, ensure_ascii=False)

# Usage
search_results = client.esearch.search(
    db="pubmed",
    term="artificial intelligence radiology",
    retmax=100
)

summaries = client.esummary.summary(
    db="pubmed",
    id_list=search_results['id_list'],
    version="2.0"
)

# Export data
export_summaries_csv(summaries, "ai_radiology_papers.csv")
export_summaries_json(summaries, "ai_radiology_papers.json")
```

### Generate Bibliography

```python
def generate_bibliography(summaries):
    """Generate formatted bibliography."""
    bibliography = []
    
    for summary in summaries['docsums']:
        # Format: Authors. Title. Journal. Year;Volume(Issue):Pages. DOI
        authors = summary.get('authors', [])
        title = summary.get('title', 'No title')
        journal = summary.get('source', 'Unknown journal')
        year = summary.get('pubdate', '').split()[0] if summary.get('pubdate') else 'Unknown'
        doi = summary.get('doi', '')
        
        # Format authors (first 3, then et al.)
        if len(authors) > 3:
            author_str = ', '.join(authors[:3]) + ', et al.'
        else:
            author_str = ', '.join(authors)
        
        # Create citation
        citation = f"{author_str}. {title}. {journal}. {year}."
        if doi:
            citation += f" doi:{doi}"
        
        bibliography.append(citation)
    
    return bibliography

# Generate bibliography
bibliography = generate_bibliography(summaries)

# Save to file
with open("bibliography.txt", "w", encoding="utf-8") as f:
    for i, citation in enumerate(bibliography, 1):
        f.write(f"{i}. {citation}\n\n")
```

## Publication Trend Analysis

### Analyze by Year

```python
def analyze_publication_trends(term, years=10):
    """Analyze publication trends over time."""
    import matplotlib.pyplot as plt
    from datetime import datetime
    
    current_year = datetime.now().year
    yearly_counts = {}
    
    for year in range(current_year - years, current_year + 1):
        year_query = f"{term} AND {year}[PDAT]"
        
        results = client.esearch.search(
            db="pubmed",
            term=year_query,
            retmax=0  # Just get count
        )
        
        yearly_counts[year] = results['count']
    
    # Plot results
    years = list(yearly_counts.keys())
    counts = list(yearly_counts.values())
    
    plt.figure(figsize=(12, 6))
    plt.plot(years, counts, marker='o', linewidth=2, markersize=8)
    plt.title(f'Publication Trends: {term}')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return yearly_counts

# Analyze trends
trends = analyze_publication_trends("machine learning healthcare", years=15)
print("Publications by year:", trends)
```

### Compare Multiple Topics

```python
def compare_topics(topics, years=10):
    """Compare publication trends for multiple topics."""
    import matplotlib.pyplot as plt
    from datetime import datetime
    
    current_year = datetime.now().year
    all_data = {}
    
    for topic in topics:
        yearly_counts = {}
        
        for year in range(current_year - years, current_year + 1):
            year_query = f"{topic} AND {year}[PDAT]"
            
            results = client.esearch.search(
                db="pubmed",
                term=year_query,
                retmax=0
            )
            
            yearly_counts[year] = results['count']
        
        all_data[topic] = yearly_counts
    
    # Plot comparison
    plt.figure(figsize=(14, 8))
    
    for topic, data in all_data.items():
        years = list(data.keys())
        counts = list(data.values())
        plt.plot(years, counts, marker='o', linewidth=2, label=topic)
    
    plt.title('Publication Trends Comparison')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return all_data

# Compare topics
topics = ["machine learning", "artificial intelligence", "deep learning"]
comparison = compare_topics(topics, years=10)
```

## Complete Literature Review Workflow

```python
def comprehensive_literature_review(topic, max_papers=200):
    """Complete workflow for literature review."""
    
    print(f"Starting literature review for: {topic}")
    
    # 1. Initial search
    print("1. Performing initial search...")
    initial_search = client.esearch.search(
        db="pubmed",
        term=topic,
        retmax=max_papers,
        sort="pub_date"
    )
    
    print(f"   Found {initial_search['count']} total papers")
    print(f"   Retrieved {len(initial_search['id_list'])} PMIDs")
    
    # 2. Get summaries
    print("2. Retrieving article summaries...")
    summaries = client.esummary.summary(
        db="pubmed",
        id_list=initial_search['id_list'],
        version="2.0"
    )
    
    # 3. Find review articles
    print("3. Finding review articles...")
    review_search = client.esearch.search(
        db="pubmed",
        term=f"{topic} AND review[ptyp]",
        retmax=50
    )
    
    review_summaries = client.esummary.summary(
        db="pubmed",
        id_list=review_search['id_list'],
        version="2.0"
    ) if review_search['id_list'] else {'docsums': []}
    
    # 4. Export data
    print("4. Exporting data...")
    export_summaries_csv(summaries, f"{topic.replace(' ', '_')}_papers.csv")
    export_summaries_csv(review_summaries, f"{topic.replace(' ', '_')}_reviews.csv")
    
    # 5. Generate bibliography
    print("5. Generating bibliography...")
    bibliography = generate_bibliography(summaries)
    
    with open(f"{topic.replace(' ', '_')}_bibliography.txt", "w", encoding="utf-8") as f:
        for i, citation in enumerate(bibliography, 1):
            f.write(f"{i}. {citation}\n\n")
    
    # 6. Summary report
    print("6. Generating summary report...")
    report = f"""
Literature Review Summary: {topic}
{'=' * 50}

Total papers found: {initial_search['count']}
Papers analyzed: {len(initial_search['id_list'])}
Review articles found: {len(review_search['id_list'])}

Date range: {min([s.get('pubdate', '').split()[0] for s in summaries['docsums'] if s.get('pubdate')])} - {max([s.get('pubdate', '').split()[0] for s in summaries['docsums'] if s.get('pubdate')])}

Top journals:
"""
    
    # Count journals
    journal_counts = {}
    for summary in summaries['docsums']:
        journal = summary.get('source', 'Unknown')
        journal_counts[journal] = journal_counts.get(journal, 0) + 1
    
    top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for journal, count in top_journals:
        report += f"  {journal}: {count} papers\n"
    
    with open(f"{topic.replace(' ', '_')}_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Literature review complete!")
    print(f"Files generated:")
    print(f"  - {topic.replace(' ', '_')}_papers.csv")
    print(f"  - {topic.replace(' ', '_')}_reviews.csv") 
    print(f"  - {topic.replace(' ', '_')}_bibliography.txt")
    print(f"  - {topic.replace(' ', '_')}_report.txt")
    
    return {
        'summaries': summaries,
        'reviews': review_summaries,
        'bibliography': bibliography,
        'journal_counts': journal_counts
    }

# Run comprehensive review
results = comprehensive_literature_review("machine learning healthcare")
```

## Next Steps

- **Explore [Sequence Analysis Tutorial](sequence-analysis.md)** for working with biological data
- **Check [Batch Processing Tutorial](batch-processing.md)** for handling large datasets
- **Learn about [Data Analysis Examples](../examples/data-analysis.md)** for advanced analytics

---

**Tips:**
- Always use specific search terms for better results
- Consider using MeSH terms for medical searches
- Use date filters to find recent research
- Export data for further analysis in tools like Excel or R
