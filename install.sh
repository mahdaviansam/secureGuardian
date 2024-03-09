# Stop and disable the old service if it exists
systemctl stop secureGuardian
systemctl disable secureGuardian

# Install required packages
echo "Installing required packages..."
apt update
apt install -y python3-pip

# Remove the old service file
rm -rf /etc/systemd/system/secureGuardian.service

# Remove the old script if it exists
rm -rf /usr/local/bin/secureGuardian

# Remove any old dependencies
# pip uninstall -y scapy requests

# Download the new script
curl -o secureGuardian.py https://raw.githubusercontent.com/mahdaviansam/secureGuardian/main/secureGuardian.py

# Make it executable
chmod +x secureGuardian.py

# Move it to /usr/local/bin
mv secureGuardian.py /usr/local/bin/secureGuardian

# Set ownership
chown root:root /usr/local/bin/secureGuardian

# Install dependencies
# Install dependencies
pip install scapy requests

# Set up systemd service
tee /etc/systemd/system/secureGuardian.service >/dev/null <<EOF
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
systemctl daemon-reload

# Enable and start the service
systemctl enable secureGuardian
systemctl start secureGuardian
systemctl restart secureGuardian

echo "SecureGuardian installed successfully!"

# Restart=on-failure
# Restart=always
