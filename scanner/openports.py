import socket
import concurrent.futures

# List of ports to scan
ports = [
    21, 22, 23, 25, 53, 80, 110, 139, 143, 161, 389, 443, 3306, 3389, 5432, 5900,
    8080, 6379, 6660, 6661, 6662, 6663, 6664, 6665, 6666, 6667, 6668, 6669, 9200,
    7, 9, 161, 162, 514, 3127, 6000, 9000, 10000, 11211, 1433, 1434, 27017, 31337
]

# Function to scan a single port
def scan_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set a timeout for the connection attempt (1 second)
    
    try:
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            return port  # Return the port if it's open
        else:
            return None  # Return None if the port is closed
    except socket.error:
        return None  # Return None if an error occurs (e.g., timeout or unreachable)
    finally:
        sock.close()

# Function to scan multiple ports and return a list of open ports
def scan_ports(target_ip, ports):
    open_ports = []  # List to store open ports
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(lambda port: scan_port(target_ip, port), ports)
        
    # Collect only the open ports
    for result in results:
        if result is not None:
            open_ports.append(result)
    
    return open_ports

# target_ip = "161.97.70.226"
# open_ports = scan_ports(target_ip, ports)
# print(open_ports)
