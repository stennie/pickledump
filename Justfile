# Default task: list available tasks
[private]
default:
    @just --list

# Build source and wheel distributions
build:
    python -m build

# Clean build artifacts
clean:
    rm -rf build dist *.egg-info __pycache__

# Install the package
install:
    pip install -e .

# Run the CLI (arguments are passed through, e.g. `just run -- file.pkl`)
run *ARGS:
    python pickledump.py {{ARGS}}

# Run the test suite
test *ARGS:
    python -m pytest {{ARGS}}
