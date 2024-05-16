#!/usr/bin/python3


import time
import requests
import threading
import subprocess
from scapy.all import *


result = subprocess.run("hostname", shell=True, capture_output=True, text=True)
restart_time = 300
threshold = 2
server_name = result.stdout.strip()
alaki = 0
traffic_counts = {}

white_list = []


def add_to_whitelist(ip):
    url = "http://65.109.214.187:9000/whitelist/add"
    payload = {"ip": ip}
    response = requests.post(url, json=payload)
    if response.ok:
        print(f"IP {ip} successfully added to the whitelist.")
        return True
    else:
        print(f"Failed to add IP {ip} to the whitelist.")
        return False


def get_whitelist():
    url = "http://65.109.214.187:9000/whitelist/all"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        whitelist = data.get("data", [])
        return whitelist
    else:
        print("Failed to fetch whitelist.")
        return []


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
white_list = get_whitelist()


# functioni ke sniff azash estefade mikone
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
    time.sleep(0.02)
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
    print('SEDA SHOD')
    ip_prefix = ".".join(ip.split(".")[:3])
    if not any(white_ip.startswith(ip_prefix) for white_ip in white_list):
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        data = response.json()
        message = f"INFO : {data} roye server {server_name}"
        send_telegram_message(message)
        if "org" in data:
            # inja
            add_to_whitelist(ip)
            white_list.append(ip)
            white_list = get_whitelist()
            print(f"data ====> {data}")
            return data["org"]
        else:
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
        # message = f"whitelist : {white_list}"
        # send_telegram_message(message)
        traffic_counts = {}
        print(f"traffic_counts {traffic_counts}")
        print(f"white_list {white_list}")
        start_time = current_time
    if alaki < 1:
        print("AZ AVAL")
        messagezx = f"START z SERVER : {server_name}"
        send_telegram_message(messagezx)

        message2 = f"whitelist : {white_list}"
        send_telegram_message(message2)
        alaki = alaki + 1
        time.sleep(4)
    sniff_traffic(white_list)
