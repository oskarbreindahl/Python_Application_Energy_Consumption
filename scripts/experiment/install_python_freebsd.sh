#!/bin/sh

# Function to install a specific Python version with optimizations on FreeBSD
install_python() {
    VERSION=$1
    MAJOR_MINOR=$(echo "$VERSION" | cut -d. -f1,2)
    PYTHON_BIN="/usr/local/bin/python${MAJOR_MINOR}"

    # Check if Python version is already installed
    if [ -x "$PYTHON_BIN" ] && [ "$($PYTHON_BIN --version 2>&1)" = "Python $VERSION" ]; then
        echo "Python $VERSION is already installed."
        return
    fi

    echo "Installing Python $VERSION with optimizations..."

    # Install build dependencies
    sudo pkg install -y git bash wget curl gmake pkgconf \
        libffi readline sqlite3 openssl zlib xz tk \
        bzip2 lzma

    # Fetch and compile Python from source
    cd /tmp || exit 1
    fetch https://www.python.org/ftp/python/${VERSION}/Python-${VERSION}.tgz
    tar -xvzf Python-${VERSION}.tgz
    cd Python-${VERSION} || exit 1

    ./configure --enable-optimizations --with-lto
    CPU_COUNT=$(sysctl -n hw.ncpu)
    gmake -j "$CPU_COUNT" profile-opt
    sudo gmake altinstall

    cd ..
    rm -rf Python-${VERSION} Python-${VERSION}.tgz

    # Ensure pip is installed
    "$PYTHON_BIN" -m ensurepip

    # Verify installation
    "$PYTHON_BIN" --version

    # Install pyperformance if not already present
    if ! "$PYTHON_BIN" -m pip show pyperformance >/dev/null 2>&1; then
        echo "Installing pyperformance for $PYTHON_BIN..."
        "$PYTHON_BIN" -m pip install --upgrade pip
        "$PYTHON_BIN" -m pip install pyperformance
    else
        echo "pyperformance is already installed for $PYTHON_BIN."
    fi
}

# Install desired Python versions
install_python "3.9.22"
install_python "3.10.17"
install_python "3.11.12"
install_python "3.12.10"
install_python "3.13.3"

echo "Installation complete!"
