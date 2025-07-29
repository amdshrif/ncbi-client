#!/usr/bin/env python3
"""
Simple command-line interface example without external dependencies.

This demonstrates how to create basic CLI functionality using only
Python standard library, suitable for integration into scripts.
"""

import sys
import json
import argparse
from ncbi_client import NCBIClient


def search_command(args):
    """Execute search command."""
    client = NCBIClient(
        api_key=args.api_key, 
        email=args.email,
        verify_ssl=args.ssl_verify
    )
    
    print(f"Searching {args.database} for: {args.query}")
    
    results = client.esearch.search(
        db=args.database,
        term=args.query,
        retmax=args.retmax,
        retstart=args.retstart
    )
    
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    elif args.format == 'ids':
        for uid in results['id_list']:
            print(uid)
    elif args.format == 'count':
        print(results['count'])
    else:
        print(f"Found {results['count']} results:")
        for uid in results['id_list']:
            print(f"  {uid}")


def fetch_command(args):
    """Execute fetch command."""
    client = NCBIClient(
        api_key=args.api_key, 
        email=args.email,
        verify_ssl=args.ssl_verify
    )
    
    # Parse comma-separated IDs
    id_list = [id.strip() for id in args.ids.split(',')]
    
    print(f"Fetching {len(id_list)} records from {args.database}")
    
    results = client.efetch.fetch(
        db=args.database,
        id_list=id_list,
        rettype=args.rettype,
        retmode=args.retmode
    )
    
    print(results)


def summary_command(args):
    """Execute summary command."""
    client = NCBIClient(
        api_key=args.api_key, 
        email=args.email,
        verify_ssl=args.ssl_verify
    )
    
    # Parse comma-separated IDs
    id_list = [id.strip() for id in args.ids.split(',')]
    
    print(f"Getting summaries for {len(id_list)} records from {args.database}")
    
    results = client.esummary.summary(
        db=args.database,
        id_list=id_list,
        version=args.version
    )
    
    print(json.dumps(results, indent=2))


def info_command(args):
    """Execute info command."""
    client = NCBIClient(
        api_key=args.api_key, 
        email=args.email,
        verify_ssl=args.ssl_verify
    )
    
    if args.list_only:
        databases = client.einfo.get_databases()
        for db in databases:
            print(db)
    elif args.database:
        db_info = client.einfo.get_database_info(args.database)
        print(json.dumps(db_info, indent=2))
    else:
        print("Available databases:")
        databases = client.einfo.get_databases()
        for db in databases:
            print(f"  {db}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Simple NCBI Client CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python simple_cli.py search pubmed "COVID-19"
  python simple_cli.py fetch pubmed "33946458,33940777" --rettype abstract
  python simple_cli.py summary protein "1579325,1579326" --version 2.0
  python simple_cli.py info --list-only
        '''
    )
    
    # Global options
    parser.add_argument('--api-key', help='NCBI API key')
    parser.add_argument('--email', help='Email address for identification')
    parser.add_argument('--no-ssl-verify', action='store_true', 
                       help='Disable SSL certificate verification')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search NCBI database')
    search_parser.add_argument('database', help='Database name (e.g., pubmed, protein)')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--retmax', type=int, default=20, help='Max results (default: 20)')
    search_parser.add_argument('--retstart', type=int, default=0, help='Starting index (default: 0)')
    search_parser.add_argument('--format', choices=['json', 'ids', 'count', 'summary'], 
                             default='summary', help='Output format (default: summary)')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch records by ID')
    fetch_parser.add_argument('database', help='Database name')
    fetch_parser.add_argument('ids', help='Comma-separated list of IDs')
    fetch_parser.add_argument('--rettype', default='docsum', help='Retrieval type (default: docsum)')
    fetch_parser.add_argument('--retmode', default='xml', help='Retrieval mode (default: xml)')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Get document summaries')
    summary_parser.add_argument('database', help='Database name')
    summary_parser.add_argument('ids', help='Comma-separated list of IDs')
    summary_parser.add_argument('--version', choices=['1.0', '2.0'], default='1.0',
                               help='ESummary version (default: 1.0)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get database information')
    info_parser.add_argument('database', nargs='?', help='Database name (optional)')
    info_parser.add_argument('--list-only', action='store_true', help='List databases only')
    
    args = parser.parse_args()
    
    # Convert no-ssl-verify flag to ssl_verify boolean
    args.ssl_verify = not args.no_ssl_verify
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'search':
            search_command(args)
        elif args.command == 'fetch':
            fetch_command(args)
        elif args.command == 'summary':
            summary_command(args)
        elif args.command == 'info':
            info_command(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
