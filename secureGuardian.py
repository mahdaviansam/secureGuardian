#!/usr/bin/python3

import sys
import time
import requests
import subprocess
from scapy.all import *
import threading


restart_time = 300
threshold = 5
server_name = ""
traffic_counts = {}
white_list = [
    "1.1.1.1",
    "8.8.8.8",
    "17.253.20.253",
    "17.253.20.125",
    "31.13.88.62",
    "157.240.241.62",
    "157.240.11.51",
    "216.239.35.8",
]


if len(sys.argv) == 2:
    server_name = sys.argv[1]
    print(f"{server_name} name server")
elif len(sys.argv) > 2:
    print("Usage: python SecureGuardian.py <server_name>")
    sys.exit(1)
else:
    server_name = input("Enter server name: ")


def send_telegram_message(message):
    bot_token = "7077359585:AAGmG8h0U9b4K22yEz6UVxPQzv1sLD4dSto"
    usernames = ["98801449", "98801449"]
    for username in usernames:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": username, "text": message}
        response = requests.post(url, data=data)
        if response.ok:
            print("Message sent successfully!")
        else:
            print("Failed to send message!", response)


def get_local_ip():
    # local ip man ro migire
    result = subprocess.run(["ip", "route", "get", "1"], capture_output=True, text=True)
    output = result.stdout.strip().split()
    return output[output.index("src") + 1]


my_ip = get_local_ip()


def process_packet(packet):
    if UDP in packet and IP in packet:
        source_ip = packet[IP].src
        dest_ip = packet[IP].dst
        if my_ip in source_ip:
            if dest_ip not in traffic_counts:
                traffic_counts[dest_ip] = 1
            else:
                traffic_counts[dest_ip] += 1


def sniff_traffic(white_list):
    white_list_filter = (
        " and not (host " + " or host ".join(white_list) + ")" if white_list else " "
    )
    print(f"white_list_filter: {white_list_filter}")
    time.sleep(0.01)
    sniff(
        filter=f"udp and not (port 53 or port 443) {white_list_filter}",
        prn=process_packet,
        count=1,
    )


def find_ip_ranges(data, prefix_length):
    # ye ip migire 3 bakhshe aval ro negah midare
    ranges = {}
    for ip in data:
        prefix = ".".join(ip.split(".")[:prefix_length])
        if prefix not in ranges:
            ranges[prefix] = []
        ranges[prefix].append(ip)
    return ranges


def get_ip_ownership(ip, white_list):
    ip_prefix = ".".join(ip.split(".")[:3])
    if not any(white_ip.startswith(ip_prefix) for white_ip in white_list):
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        data = response.json()
        message = data
        send_telegram_message(message)
        if "org" in data:
            white_list.append(ip)
            return data["org"]
        else:
            command = f"iptables -A OUTPUT -d {ip_prefix}.0/24 -p udp -j DROP"
            subprocess.run(command, shell=True)
            messagez = f"bayad block she : {ip_prefix}.0/24"
            send_telegram_message(messagez)
            return "Unknown"


def print_ip_ownership(ip_ranges):
    # in faghat get_ip_ownership ro seda mikone
    for prefix, ips in ip_ranges.items():
        if len(ips) > threshold:
            get_ip_ownership(ips[0], white_list)


def run_sniffer():
    start_time = time.time()
    while True:
        current_time = time.time()
        ip_ranges = find_ip_ranges(traffic_counts, 3)
        print_ip_ownership(ip_ranges)
        if current_time - start_time >= restart_time:
            traffic_counts = {}
            start_time = current_time
        sniff_traffic(white_list)


sniffer_thread = threading.Thread(target=run_sniffer)
sniffer_thread.daemon = True
sniffer_thread.start()
