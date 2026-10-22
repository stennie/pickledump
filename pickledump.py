#!/usr/bin/env python3

import click
import pickle
import pickletools
import sys
import pprint
from pathlib import Path

__version__ = "1.0.0"

@click.command()
@click.version_option(version=__version__, prog_name="pickledump")
@click.argument('pickle_files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    '--mode',
    type=click.Choice(['dump', 'disassemble'], case_sensitive=False),
    default='dump',
    help='Mode: dump (deserialize) or disassemble (safe for untrusted files)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file (default: stdout)'
)
@click.option(
    '--annotate',
    '-a',
    is_flag=True,
    help='Annotate each line with opcode descriptions (disassemble mode only)'
)
@click.option(
    '--indent-level',
    '-l',
    type=int,
    default=4,
    help='Indent level for MARK operations (disassemble mode only)'
)
@click.option(
    '--memo',
    '-m',
    is_flag=True,
    help='Preserve memo between disassemblies (disassemble mode only)'
)
def pickle_cli(pickle_files, mode, output, annotate, indent_level, memo):
    """
    Dump or disassemble Python pickle files.
    
    PICKLE_FILES: One or more pickle files to process
    """
    
    # Determine output destination
    out_file = None
    if output:
        out_file = open(output, 'w')
    else:
        out_file = sys.stdout
    
    try:
        for pickle_file in pickle_files:
            if len(pickle_files) > 1:
                click.echo(f"\n{'='*60}", file=out_file)
                click.echo(f"File: {pickle_file}", file=out_file)
                click.echo(f"{'='*60}\n", file=out_file)
            
            with open(pickle_file, 'rb') as f:
                if mode.lower() == 'dump':
                    try:
                        obj = pickle.load(f)
                        # Use pprint for better formatting
                        pprint.pprint(obj, stream=out_file, width=80)
                    except Exception as e:
                        click.echo(
                            f"Error deserializing {pickle_file}: {e}",
                            err=True
                        )
                else:  # disassemble
                    f.seek(0)
                    try:
                        pickletools.dis(
                            f,
                            out=out_file,
                            indentlevel=indent_level,
                            annotate=annotate,
                            memo={} if memo else None
                        )
                    except Exception as e:
                        click.echo(
                            f"Error disassembling {pickle_file}: {e}",
                            err=True
                        )
    finally:
        if output:
            out_file.close()


if __name__ == '__main__':
    pickle_cli()
