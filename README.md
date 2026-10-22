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

- `--mode [dump|disassemble]`: Mode: dump (deserialize) or disassemble (safe for untrusted files). Defaults to `dump`.
- `--output, -o`: Output file (default: stdout)
- `--annotate, -a`: Annotate each line with opcode descriptions (disassemble mode only)
- `--indent-level, -l`: Indent level for MARK operations (disassemble mode only). Defaults to 4.
- `--memo, -m`: Preserve memo between disassemblies (disassemble mode only)

### Examples

Dump a pickle file:

```bash
pickledump data.pkl
```

Disassemble a pickle file safely:

```bash
pickledump --mode disassemble untrusted.pkl
```


## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

## Feedback or Suggestions?

Bug reports, feature requests, and questions can be posted in the [Issues](https://github.com/stennie/pickledump/issues) section on GitHub.