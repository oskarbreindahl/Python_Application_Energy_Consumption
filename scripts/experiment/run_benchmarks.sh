#!/bin/bash
# Run this script with desired Python version as argument.

# Function to run benchmarks on a specific Python version
run_benchmarks() {
    PYTHON_BIN=$1
    PYTHON_PATH=$2 
    $PYTHON_BIN -m pyperformance run --benchmarks=2to3,chameleon,tornado_http --python=$PYTHON_PATH -o $PYTHON_BIN.json
}

# Script finds path to desired Python version
if command -v $1 &>/dev/null; then
    PYTHON_PATH=$($1 -c "import sys; print(sys.executable)")
    echo "Running benchmarks for $1 at $PYTHON_PATH..."
    run_benchmarks $1 $PYTHON_PATH
else
    echo "$1 is not installed. Exiting."
fi

echo "Benchmarking complete for all versions."
