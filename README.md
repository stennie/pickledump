# pickledump

A command-line tool to dump or disassemble Python pickle files.

## Installation

```bash
pip install .
```

## Usage

```bash
pickledump <pickle_files> [OPTIONS]
```

### Arguments

- `pickle_files`: One or more pickle files to process

### Options

- `--disasm, -x`: Disassemble mode (safe for untrusted files)
- `--dump, -d`: Dump mode (deserialize)
- `--output, -o`: Output file (default: stdout)
- `--annotate, -a`: Annotate each line with opcode descriptions (disassemble mode only)
- `--indent-level, -l`: Indent level for MARK operations (disassemble mode only). Defaults to 4.
- `--memo, -m`: Preserve memo between disassemblies (disassemble mode only)
- `--summary, -s`: Summarise information about the pickle file(s), including the Pickle protocol version and any custom object classes found in the file. This is the default action.

### Examples

Dump a pickle file:

```bash
pickledump --dump data.pkl
```

Disassemble a pickle file safely:

```bash
pickledump --disasm untrusted.pkl
```

Summarise information about a pickle file (size, Pickle protocol version and custom object classes):

```bash
pickledump --summary data.pkl
```

Summarise multiple pickle files:

```bash
pickledump --summary data1.pkl data2.pkl
```

## Testing

Run the test suite with pytest:

```bash
python -m pytest
```

Or via the Just task runner:

```bash
just test
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

## Feedback or Suggestions?

Bug reports, feature requests, and questions can be posted in the [Issues](https://github.com/stennie/pickledump/issues) section on GitHub.