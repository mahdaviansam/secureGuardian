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
files=(
    "secureGuardian.py"
)

link="https://raw.githubusercontent.com/mahdaviansam/secureGuardian/main/src/"

mkdir -p /tmp/secureGuardian

for file in "${files[@]}"; do
    echo "Downloading $file..."
    wget -q "${link}$file" -P "/tmp/secureGuardian"
    echo "Downloaded $file"
done

# Move files to appropriate directory
echo "Moving files to appropriate directory..."
mkdir -p /usr/local/bin/secureGuardian
mv /tmp/secureGuardian/* /usr/local/bin/secureGuardian/

# Add execute permissions to files
echo "Adding execute permissions to files..."
chmod +x /usr/local/bin/secureGuardian/*.py

echo "secureGuardian package installed successfully."

# Install Python dependencies
pip install requests scapy

#! Install required Python packages
