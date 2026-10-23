#!/usr/bin/env python3

import click
import pickle
import pickletools
import sys
import io
import pprint
from pathlib import Path

__version__ = "1.0.1"

def _get_pickle_protocol(ops):
    """
    Determine the Pickle protocol version from a list of (opcode, arg) pairs.

    Protocol 2+ pickles start with a PROTO opcode whose argument is the protocol version.
    Protocol 0 pickles use text-based opcodes only, while protocol 1 adds binary opcodes
    (e.g. BININT1, BINUNICODE) and EMPTY_* operations on top of the protocol 0 ones.
    """
    protocol = 0
    for op, arg in ops:
        if op.name == 'PROTO':
            protocol = arg
            break
        if op.name.startswith('BIN') or op.name.startswith('EMPTY'):
            protocol = 1
            break
    return protocol

class _PickleClassCollector(pickle.Unpickler):
    """
    Unpickler subclass that records the object classes referenced
    by a pickle (via find_class) without discarding them.
    """
    def __init__(self, file):
        super().__init__(file)
        self.classes = []

    def find_class(self, module, name):
        if (module, name) not in self.classes:
            self.classes.append((module, name))
        return super().find_class(module, name)

def _summarise_pickle_file(pickle_file, out_file):
    """
    Print summary information about a single pickle file,
    including its size, Pickle protocol version, and any custom object classes.
    """
    try:
        with open(pickle_file, 'rb') as f:
            data = f.read()
        ops = [(op, arg) for op, arg, _pos in pickletools.genops(data)]
        protocol = _get_pickle_protocol(ops)
    except Exception as e:
        click.echo(f"Error summarising {pickle_file}: {e}", err=True)
        return

    click.echo(f"  Size:              {len(data)} bytes", file=out_file)
    click.echo(f"  Pickle protocol:   {protocol}", file=out_file)
    click.echo(f"  Operations:        {len(ops)}", file=out_file)

    classes = []
    collector = None
    try:
        collector = _PickleClassCollector(io.BytesIO(data))
        collector.load()
        classes = list(collector.classes)
    except Exception as e:
        if collector is not None:
            classes = list(collector.classes)
            if not classes:
                click.echo(f"Error reading classes from {pickle_file}: {e}", err=True)

    custom_classes = []
    seen = set()
    for module, name in classes:
        class_name = f"{module}.{name}"
        if class_name in seen:
            continue
        seen.add(class_name)
        if module.split('.')[0] in ('builtins', '__builtin__') or module in ('copy_reg', '__builtin__'):
            continue
        custom_classes.append(class_name)

    if custom_classes:
        click.echo("\nCustom object classes:", file=out_file)
        for class_name in custom_classes:
            click.echo(f"  - {class_name}", file=out_file)

class PickledumpCommand(click.Command):
    """
    Click command that renders help with grouped option sections.
    """

    def format_options(self, ctx, formatter):
        """
        Write options in grouped sections: Actions, Output options, Disassemble options.
        """
        groups = [
            ('Actions', ('summary', 'disasm', 'dump')),
            ('Output options', ('output',)),
            ('Disassemble options', ('annotate', 'indent_level', 'memo')),
        ]

        written = set()
        for heading, names in groups:
            records = []
            for param in self.get_params(ctx):
                if isinstance(param, click.Option) and param.name in names:
                    record = param.get_help_record(ctx)
                    if record is not None:
                        records.append(record)
            if records:
                with formatter.section(heading):
                    formatter.write_dl(records)
                written.update(names)

        leftovers = [
            param for param in self.get_params(ctx)
            if isinstance(param, click.Option)
            and param.name not in written
            and param.name not in ('help', 'version')
        ]
        records = [param.get_help_record(ctx) for param in leftovers]
        records = [record for record in records if record is not None]
        if records:
            with formatter.section('Options'):
                formatter.write_dl(records)

@click.command(cls=PickledumpCommand)
@click.version_option(message=f'pickledump {__version__} || Python {sys.version}')
@click.argument('pickle_files', nargs=-1, required=True, type=click.Path(exists=True))
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
@click.option(
    '--summary',
    '-s',
    is_flag=True,
    help='Summarise information about the pickle file(s), including the Pickle protocol version and custom object classes'
)
@click.option(
    '--disasm',
    '-x',
    is_flag=True,
    help='Disassemble mode (safe for untrusted files)'
)
@click.option(
    '--dump',
    '-d',
    is_flag=True,
    help='Dump mode (deserialize)'
)
def pickle_cli(pickle_files, output, annotate, indent_level, memo, summary, disasm, dump):
    """
    Dump, disassemble, or summarise Python pickle files.
    
    PICKLE_FILES: One or more pickle files to process
    """
    
    # Determine output destination
    out_file = None
    if output:
        out_file = open(output, 'w')
    else:
        out_file = sys.stdout
    
    # Resolve the action via --summary/--disasm/--dump; default is summary.
    if disasm:
        mode = 'disassemble'
    elif dump:
        mode = 'dump'
    else:
        mode = 'summary'

    try:
        for pickle_file in pickle_files:
            click.echo(f"\n{'='*60}", file=out_file)
            click.echo(f"File: {pickle_file}", file=out_file)
            click.echo(f"{'='*60}\n", file=out_file)
            
            if mode.lower() == 'summary':
                _summarise_pickle_file(pickle_file, out_file)
                continue

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
