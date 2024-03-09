#!/bin/bash

# Download the script
curl -o SecureGuardian.py https://raw.githubusercontent.com/mahdaviansam/secureGuardian/main/SecureGuardian.py

# Make it executable
chmod +x SecureGuardian.py

# Move it to /usr/local/bin
sudo mv SecureGuardian.py /usr/local/bin/secureGuardian

# Set ownership
sudo chown root:root /usr/local/bin/secureGuardian

# Install dependencies
pip install scapy requests

# Set up systemd service
sudo tee /etc/systemd/system/secureGuardian.service >/dev/null <<EOF
[Unit]
Description=Secure Guardian Service
After=network.target

[Service]
ExecStart=/usr/local/bin/secureGuardian
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable secureGuardian
sudo systemctl start secureGuardian

echo "SecureGuardian installed successfully!"
