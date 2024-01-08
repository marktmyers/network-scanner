import socket
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

# Global constants
NUM_THREADS = 100  # Define the number of threads for scanning

# Global variables
queue = Queue()  # Queue for managing threads
open_ports = []  # List to store open ports

def portscan(ip, port, update_callback=None):
    """
    Scans a single port on the given IP address.
    
    Args:
    ip (str): The IP address to scan.
    port (int): The port number to scan.
    update_callback (function): Optional callback function for real-time updates.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_port_info = f"Port {port} is open on {ip}"
            open_ports.append((ip, port))
            if update_callback:
                update_callback(open_port_info)
        sock.close()
    except socket.error:
        pass

def threader():
    """
    Worker function for threading. Retrieves tasks from the queue and processes them.
    """
    while True:
        port, target_ip, callback = queue.get()
        portscan(target_ip, port, callback)
        queue.task_done()

def scan_ports(target_ip, start_port, end_port, update_callback=None):
    """
    Scans a range of ports on a given IP address.

    Args:
    target_ip (str): The IP address to scan.
    start_port (int): The starting port number.
    end_port (int): The ending port number.
    update_callback (function): Optional callback function for real-time updates.
    """
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        future_to_port = {executor.submit(portscan, target_ip, port, update_callback): port for port in range(start_port, end_port + 1)}
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'Port {port} generated an exception: {exc}')

def start_network_scan(ip_range, start_port, end_port, update_callback=None):
    """
    Initiates a network scan over a range of IP addresses.

    Args:
    ip_range (str): The range of IP addresses to scan, in CIDR format.
    start_port (int): The starting port number.
    end_port (int): The ending port number.
    update_callback (function): Optional callback function for real-time updates.
    """
    for ip in ipaddress.IPv4Network(ip_range):
        target_ip = str(ip)
        if update_callback:
            update_callback(f"Scanning {target_ip}")
        scan_ports(target_ip, start_port, end_port, update_callback)
