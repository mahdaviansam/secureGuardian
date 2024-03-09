# Stop and disable the old service if it exists
sudo systemctl stop secureGuardian
sudo systemctl disable secureGuardian

# Remove the old service file
sudo rm -rf /etc/systemd/system/secureGuardian.service

# Remove the old script if it exists
sudo rm -rf /usr/local/bin/secureGuardian

# Remove any old dependencies
# pip uninstall -y scapy requests

# Download the new script
curl -o secureGuardian.py https://raw.githubusercontent.com/mahdaviansam/secureGuardian/main/secureGuardian.py

# Make it executable
chmod +x secureGuardian.py

# Move it to /usr/local/bin
sudo mv secureGuardian.py /usr/local/bin/secureGuardian

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
