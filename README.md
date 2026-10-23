# pickledump

A command-line tool to dump, disassemble, or summarise Python pickle files.

## Installation

```bash
pip install .
```

## Usage

```
Usage: pickledump [OPTIONS] PICKLE_FILES...

  Dump, disassemble, or summarise Python pickle files.

  PICKLE_FILES: One or more pickle files to process

Actions:
  -s, --summary  Summarise information about the pickle file(s), including the
                 Pickle protocol version and custom object classes
  -x, --disasm   Disassemble mode (safe for untrusted files)
  -d, --dump     Dump mode (deserialize)

Output options:
  -o, --output PATH  Output file (default: stdout)

Disassemble options:
  -a, --annotate              Annotate each line with opcode descriptions
                              (disassemble mode only)
  -l, --indent-level INTEGER  Indent level for MARK operations (disassemble
                              mode only)
  -m, --memo                  Preserve memo between disassemblies (disassemble
                              mode only)
```

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