# Default task: list available tasks
default:
    @just --list

# Install the package
install:
    pip install -e .

# Run the CLI (arguments are passed through, e.g. `just run -- file.pkl`)
run *ARGS:
    python pickledump.py {{ARGS}}

# Build source and wheel distributions
build:
    python -m build

# Clean build artifacts
clean:
    rm -rf build dist *.egg-info __pycache__