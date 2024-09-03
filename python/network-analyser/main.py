import os
import platform
import socket
import struct
import time
import json
from datetime import datetime
from threading import Thread
import re
import subprocess

# Setting up a simple logging mechanism to keep track of what happens in our script
log_file = 'network_security_log.txt'
known_devices_file = 'known_devices.json'

def log_event(event):
    # Log an event with a timestamp to both the log file and the console
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - {event}\n")
    print(f"{timestamp} - {event}")

# Detecting which operating system we're running on
OS_TYPE = platform.system()

# Global variable to hold the sniffer socket
sniffer = None

# Load the list of known devices from a file (if it exists)
def load_known_devices():
    try:
        with open(known_devices_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save the updated list of known devices to a file
def save_known_devices(devices):
    with open(known_devices_file, 'w') as f:
        json.dump(devices, f, indent=4)

# Helper function to ping the router, which helps to update the ARP table
def ping_router(gateway_ip):
    log_event(f"Pinging gateway {gateway_ip} to populate ARP table.")
    try:
        if OS_TYPE == 'Windows':
            subprocess.run(["ping", "-n", "1", gateway_ip], stdout=subprocess.DEVNULL)
        else:
            subprocess.run(["ping", "-c", "1", gateway_ip], stdout=subprocess.DEVNULL)
    except Exception as e:
        log_event(f"Failed to ping gateway: {e}")

# Automatically detect the router's MAC address by checking the ARP table
def get_router_mac():
    router_mac = None
    arp_result = None

    try:
        if OS_TYPE == 'Linux':
            # Linux command to find the gateway IP
            route_cmd = "ip route show default"
            result = os.popen(route_cmd).read()
            match = re.search(r'default via (\S+)', result)
            if not match:
                log_event("Could not detect gateway IP.")
                return None
            gateway_ip = match.group(1)
            arp_cmd = f"ip neigh show {gateway_ip}"
        elif OS_TYPE == 'Windows':
            # Windows command to find the gateway IP
            route_cmd = "route print"
            result = os.popen(route_cmd).read()
            match = re.search(r'0\.0\.0\.0\s+(\S+)', result)
            if not match:
                log_event("Could not detect gateway IP.")
                return None
            gateway_ip = match.group(1)
            arp_cmd = f"arp -a {gateway_ip}"

        # Execute the ARP command to fetch MAC addresses
        arp_result = os.popen(arp_cmd).read()

        # If no ARP entries are found, try pinging the router to refresh the table
        if "No ARP Entries Found" in arp_result or not arp_result:
            ping_router(gateway_ip)
            time.sleep(2)  # Give some time for the ARP table to update
            arp_result = os.popen(arp_cmd).read()

        # Extract the router's MAC address from the ARP results
        if OS_TYPE == 'Linux':
            router_mac = re.search(r'(\S+:\S+:\S+:\S+:\S+:\S+)', arp_result).group(1)
        elif OS_TYPE == 'Windows':
            router_mac = re.search(r'(\S+)\s+dynamic', arp_result).group(1)

        if router_mac:
            log_event(f"Router detected: {gateway_ip} - MAC: {router_mac}")
        else:
            log_event(f"Could not detect router MAC address. ARP result: {arp_result}")

    except AttributeError as e:
        log_event(f"Error detecting router MAC address: {e}. ARP result: {arp_result}")

    return router_mac

# Filter out broadcast/multicast addresses and ensure we only deal with valid devices
def is_valid_device(mac, ip):
    # Ignore common multicast and broadcast MAC addresses
    if mac.startswith("01:00:5e") or mac.startswith("ff:ff:ff") or mac.startswith("33:33") or mac == "ff-ff-ff-ff-ff-ff":
        return False
    # Ignore broadcast IP addresses
    if ip.endswith(".255") or ip.startswith("224.") or ip.startswith("239.") or ip == "255.255.255.255":
        return False
    return True

# Scanning the network for connected devices using ARP
def scan_network():
    known_devices = load_known_devices()
    new_devices_detected = False

    # ARP command varies depending on the operating system
    if OS_TYPE == 'Linux':
        arp_cmd = "ip neigh"
    elif OS_TYPE == 'Windows':
        arp_cmd = "arp -a"

    result = os.popen(arp_cmd).read()

    for line in result.splitlines():
        if 'incomplete' in line or 'failed' in line:
            continue
        try:
            parts = line.split()
            ip = parts[0]
            mac = parts[3] if OS_TYPE == 'Linux' else parts[1]
            
            if is_valid_device(mac, ip):
                if mac in known_devices:
                    log_event(f"Known Device Detected: {mac} ({known_devices[mac]}) @ {ip}")
                else:
                    # Attempt to resolve the device name (this can be slow and is optional)
                    try:
                        device_name = socket.gethostbyaddr(ip)[0]
                    except (socket.herror, socket.gaierror):
                        device_name = "Unknown Device"

                    log_event(f"Unknown Device Detected: {mac} @ {ip} ({device_name})")
                    known_devices[mac] = device_name
                    new_devices_detected = True
        except IndexError:
            pass

    # Save the updated known devices list if new devices were detected
    if new_devices_detected:
        save_known_devices(known_devices)

    return known_devices

# Analyze individual packets to detect specific types of traffic or suspicious behavior
def analyze_packet(packet):
    eth_header = packet[:14]
    eth = struct.unpack('!6s6sH', eth_header)
    eth_protocol = socket.ntohs(eth[2])

    # Check if the packet is an IP packet
    if eth_protocol == 8:
        ip_header = packet[14:34]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

        src_ip = socket.inet_ntoa(iph[8])
        dest_ip = socket.inet_ntoa(iph[9])
        protocol = iph[6]

        # Handle TCP packets (common for web traffic)
        if protocol == 6:
            tcp_header = packet[34:54]
            tcph = struct.unpack('!HHLLBBHHH', tcp_header)
            src_port = tcph[0]
            dest_port = tcph[1]

            if dest_port == 80 or dest_port == 443:  # HTTP/HTTPS traffic
                log_event(f"HTTP Traffic Detected: {src_ip}:{src_port} -> {dest_ip}:{dest_port}")

        # Handle UDP packets (common for DNS queries)
        elif protocol == 17:
            udp_header = packet[34:42]
            udph = struct.unpack('!HHHH', udp_header)
            src_port = udph[0]
            dest_port = udph[1]

            if dest_port == 53:  # DNS traffic
                log_event(f"DNS Query Detected: {src_ip} -> {dest_ip}")

        # Log large data transfers for further analysis
        data_size = len(packet)
        if data_size > 1024:  # Log packets larger than 1KB
            log_event(f"High Traffic Detected: {src_ip} -> {dest_ip}, Size: {data_size} Bytes")

# Sniff network traffic and analyze each packet in real-time
def monitor_traffic():
    global sniffer
    try:
        # Create a raw socket to capture all network traffic
        if OS_TYPE == 'Linux':
            sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        elif OS_TYPE == 'Windows':
            sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            sniffer.bind((socket.gethostbyname(socket.gethostname()), 0))
            sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    except socket.error as err:
        log_event(f"Error creating socket: {err}")
        return

    log_event("Traffic Monitoring Started...")

    # Continuously capture and analyze packets
    while True:
        packet = sniffer.recvfrom(65565)[0]
        analyze_packet(packet)

# Periodically scan the network every 30 minutes for connected devices
def periodic_network_scan():
    while True:
        scan_network()
        time.sleep(1800)  # Wait 30 minutes between scans

# Start the network security monitor, running both the scanner and traffic monitor
def start_security_monitor():
    log_event("Starting Network Security Monitor...")

    # Start the network scanning thread
    network_scan_thread = Thread(target=periodic_network_scan)
    network_scan_thread.daemon = True
    network_scan_thread.start()

    # Start the traffic monitoring thread
    traffic_monitor_thread = Thread(target=monitor_traffic)
    traffic_monitor_thread.daemon = True
    traffic_monitor_thread.start()

    # Keep the main program running indefinitely
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_event("Stopping Network Security Monitor...")
        if OS_TYPE == 'Windows' and sniffer:
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)  # Stop sniffing on Windows
        exit()

# Main entry point to start the monitor
if __name__ == "__main__":
    start_security_monitor()
