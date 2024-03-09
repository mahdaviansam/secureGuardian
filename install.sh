#!/bin/bash

# Install required packages
apt update
apt install -y python3-pip

# Remove existing files and directories before installation
echo "Removing existing files and directories..."
rm -rf /usr/local/bin/secureGuardian
rm -rf /tmp/secureGuardian

# Download the package files
echo "Downloading package files..."
link="https://raw.githubusercontent.com/mahdaviansam/secureGuardian/main/"
file="secureGuardian.py"

mkdir -p /tmp/secureGuardian
echo "Downloading $file..."
wget -q "${link}$file" -P "/tmp/secureGuardian"
echo "Downloaded $file"

# Move file to appropriate directory
echo "Moving files to appropriate directory..."
mkdir -p /usr/local/bin/secureGuardian
mv "/tmp/secureGuardian/$file" "/usr/local/bin/secureGuardian/"

# Add execute permissions to file
echo "Adding execute permissions to file..."
chmod +x "/usr/local/bin/secureGuardian/$file"

# Update PATH variable if not already done
if ! grep -q "/usr/local/bin/secureGuardian" ~/.bashrc; then
    echo 'export PATH="$PATH:/usr/local/bin/secureGuardian"' >>~/.bashrc
fi

# Source the updated .bashrc to apply changes
source ~/.bashrc

echo "secureGuardian package installed successfully."

# Install Python dependencies
pip install requests scapy
