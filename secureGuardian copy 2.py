#!/usr/bin/python3


import time
import requests
import threading
import subprocess
from scapy.all import *


result = subprocess.run("hostname", shell=True, capture_output=True, text=True)
restart_time = 300
threshold = 5
server_name = result.stdout.strip()
alaki = 0
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
    "138.2.159.70",
    "130.162.37.51",
    "157.240.252.62",
]


def send_telegram_message(message):
    bot_token = "7077359585:AAGmG8h0U9b4K22yEz6UVxPQzv1sLD4dSto"
    usernames = ["98801449", "515682711"]
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
    time.sleep(0.01)
    sniff(
        filter=f"udp and not (port 53 or port 443) {white_list_filter}",
        prn=process_packet,
        count=1,
    )


def find_ip_ranges(data, prefix_length):
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
        message = f"INFO : {data} roye server {server_name}"
        send_telegram_message(message)
        if "org" in data:
            url = "http://65.109.214.187:9000/whitelist/add"
            data = {"ip": ip}
            response = requests.post(url, data=data)
            white_list.append(ip)
            return data["org"]
        else:
            # command = f"iptables -A OUTPUT -d {ip_prefix}.0/24 -p udp -j DROP"
            # subprocess.run(command, shell=True)
            command_check = f"iptables -C OUTPUT -d {ip_prefix}.0/24 -p udp -j DROP"
            result = subprocess.run(command_check, shell=True)
            if result.returncode != 0:
                command_add = f"iptables -A OUTPUT -d {ip_prefix}.0/24 -p udp -j DROP"
                subprocess.run(command_add, shell=True)
                print(f"Rule added for {ip_prefix}.0/24 successfully!")
                message = f"BLOCK : {ip_prefix}.0/24 roye server {server_name}"
                send_telegram_message(message)
            else:
                print(f"Rule already exists for {ip_prefix}.0/24, skipping...")
            return "Unknown"


def print_ip_ownership(ip_ranges):
    # in faghat get_ip_ownership ro seda mikone
    for prefix, ips in ip_ranges.items():
        if len(ips) > threshold:
            get_ip_ownership(ips[0], white_list)


start_time = time.time()
while True:
    current_time = time.time()
    ip_ranges = find_ip_ranges(traffic_counts, 3)
    print_ip_ownership(ip_ranges)
    if current_time - start_time >= restart_time:
        # message = f"CHECK HEALTH : {server_name} traffic_counts: {traffic_counts}"
        # send_telegram_message(message)
        traffic_counts = {}
        start_time = current_time
    if alaki < 1:
        messagezx = f"START SERVER : {server_name}"
        send_telegram_message(messagezx)
        alaki = alaki + 1
        time.sleep(4)
    sniff_traffic(white_list)
