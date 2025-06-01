#!/bin/bash

# Function to install a specific Python version with optimizations on Arch Linux
install_python() {
    VERSION=$1
    PYTHON_BIN="/usr/local/bin/python${VERSION%.*}"

    # Check if the version is already installed
    if [ -x "$PYTHON_BIN" ] && [[ "$($PYTHON_BIN --version 2>&1)" == *"$VERSION"* ]]; then
        echo "Python $VERSION is already installed."
    else
        echo "Installing Python $VERSION with optimizations..."

        # Update package list
        sudo pacman -Syu --noconfirm

        # Install build dependencies (Arch equivalents)
        sudo pacman -S --needed --noconfirm base-devel zlib ncurses gdbm \
            nss openssl readline libffi sqlite wget curl xz tk lzma \
            util-linux bzip2

        # Download and compile Python
        cd /tmp
        curl -O https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tgz
        tar -xvzf Python-$VERSION.tgz
        cd Python-$VERSION

        ./configure --enable-optimizations --with-lto
        make -j "$(nproc)" profile-opt  # Uses PGO
        sudo make altinstall

        # Clean up
        cd ..
        rm -rf Python-$VERSION Python-$VERSION.tgz

        # Ensure pip is installed
        $PYTHON_BIN -m ensurepip

        # Verify installation
        $PYTHON_BIN --version
    fi

    # Install pyperformance if not already installed
    if ! $PYTHON_BIN -m pip show pyperformance &>/dev/null; then
        echo "Installing pyperformance for $PYTHON_BIN..."
        $PYTHON_BIN -m pip install --upgrade pip
        $PYTHON_BIN -m pip install pyperformance
    else
        echo "pyperformance is already installed for $PYTHON_BIN."
    fi
}

# Install Python versions with optimizations
install_python "3.9.22"
install_python "3.10.17"
install_python "3.11.12"
install_python "3.12.10"
install_python "3.13.3"

echo "Installation complete!"
