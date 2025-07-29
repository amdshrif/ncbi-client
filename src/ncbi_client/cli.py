"""
Command-line interface for NCBI Client.

Provides basic CLI functionality for common E-utilities operations.
"""

import os
import json
import sys
from typing import Optional

import click

from ncbi_client import NCBIClient
from ncbi_client.core.exceptions import NCBIError


@click.group()
@click.option('--api-key', envvar='NCBI_API_KEY', help='NCBI API key')
@click.option('--email', envvar='NCBI_EMAIL', help='Email address for identification')
@click.option('--tool', default='ncbi-client-cli', help='Tool name for identification')
@click.option('--no-ssl-verify', is_flag=True, help='Disable SSL certificate verification')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, api_key: Optional[str], email: Optional[str], tool: str, no_ssl_verify: bool, verbose: bool):
    """NCBI Client command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = NCBIClient(
        api_key=api_key, 
        email=email, 
        tool=tool,
        verify_ssl=not no_ssl_verify
    )
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('database')
@click.argument('query')
@click.option('--retmax', default=20, help='Maximum number of results')
@click.option('--retstart', default=0, help='Starting index')
@click.option('--sort', help='Sort order')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'ids', 'count']),
              help='Output format')
@click.pass_context
def search(ctx, database: str, query: str, retmax: int, retstart: int, 
           sort: Optional[str], output: Optional[str], output_format: str):
    """Search an NCBI database."""
    try:
        client = ctx.obj['client']
        
        if ctx.obj['verbose']:
            click.echo(f"Searching {database} for: {query}")
        
        results = client.esearch.search(
            db=database,
            term=query,
            retmax=retmax,
            retstart=retstart,
            sort=sort
        )
        
        # Format output
        if output_format == 'json':
            output_text = json.dumps(results, indent=2)
        elif output_format == 'ids':
            output_text = '\n'.join(results['id_list'])
        elif output_format == 'count':
            output_text = str(results['count'])
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            if ctx.obj['verbose']:
                click.echo(f"Results written to {output}")
        else:
            click.echo(output_text)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('database')
@click.argument('ids')
@click.option('--rettype', default='docsum', help='Retrieval type')
@click.option('--retmode', default='xml', help='Retrieval mode')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.pass_context
def fetch(ctx, database: str, ids: str, rettype: str, retmode: str, 
          output: Optional[str]):
    """Fetch records from an NCBI database."""
    try:
        client = ctx.obj['client']
        
        # Parse IDs
        id_list = [id.strip() for id in ids.split(',')]
        
        if ctx.obj['verbose']:
            click.echo(f"Fetching {len(id_list)} records from {database}")
        
        results = client.efetch.fetch(
            db=database,
            id_list=id_list,
            rettype=rettype,
            retmode=retmode
        )
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(results)
            if ctx.obj['verbose']:
                click.echo(f"Results written to {output}")
        else:
            click.echo(results)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('database')
@click.argument('ids')
@click.option('--version', default='1.0', type=click.Choice(['1.0', '2.0']),
              help='ESummary version')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.pass_context
def summary(ctx, database: str, ids: str, version: str, output: Optional[str]):
    """Get document summaries from an NCBI database."""
    try:
        client = ctx.obj['client']
        
        # Parse IDs
        id_list = [id.strip() for id in ids.split(',')]
        
        if ctx.obj['verbose']:
            click.echo(f"Getting summaries for {len(id_list)} records from {database}")
        
        results = client.esummary.summary(
            db=database,
            id_list=id_list,
            version=version
        )
        
        output_text = json.dumps(results, indent=2)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            if ctx.obj['verbose']:
                click.echo(f"Results written to {output}")
        else:
            click.echo(output_text)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('dbfrom')
@click.argument('dbto')
@click.argument('ids')
@click.option('--cmd', default='neighbor', help='Link command')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.pass_context
def link(ctx, dbfrom: str, dbto: str, ids: str, cmd: str, output: Optional[str]):
    """Find links between NCBI databases."""
    try:
        client = ctx.obj['client']
        
        # Parse IDs
        id_list = [id.strip() for id in ids.split(',')]
        
        if ctx.obj['verbose']:
            click.echo(f"Finding links from {dbfrom} to {dbto}")
        
        results = client.elink.link(
            dbfrom=dbfrom,
            db=dbto,
            id_list=id_list,
            cmd=cmd
        )
        
        output_text = json.dumps(results, indent=2)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            if ctx.obj['verbose']:
                click.echo(f"Results written to {output}")
        else:
            click.echo(output_text)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('database', required=False)
@click.option('--list-only', is_flag=True, help='List databases only')
@click.pass_context
def info(ctx, database: Optional[str], list_only: bool):
    """Get database information."""
    try:
        client = ctx.obj['client']
        
        if list_only or not database:
            databases = client.einfo.get_databases()
            for db in databases:
                click.echo(db)
        else:
            db_info = client.einfo.get_database_info(database)
            output_text = json.dumps(db_info, indent=2)
            click.echo(output_text)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.pass_context
def global_search(ctx, query: str, output: Optional[str]):
    """Perform global search across all NCBI databases."""
    try:
        client = ctx.obj['client']
        
        if ctx.obj['verbose']:
            click.echo(f"Global search for: {query}")
        
        results = client.egquery.global_search(query)
        output_text = json.dumps(results, indent=2)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            if ctx.obj['verbose']:
                click.echo(f"Results written to {output}")
        else:
            click.echo(output_text)
            
    except NCBIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    cli()


if __name__ == '__main__':
    main()
