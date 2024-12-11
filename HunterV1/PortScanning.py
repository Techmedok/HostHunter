import socket
import concurrent.futures
import ipaddress
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 161, 389, 443, 3306, 3389, 5432, 5900, 8080, 6379, 6660, 6667, 9200]

def validate_ip_address(ip: str) -> bool:
    """
    Validate the input IP address.
    
    Args:
        ip (str): IP address to validate
    
    Returns:
        bool: True if valid IP, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        logger.error(f"Invalid IP address: {ip}")
        return False

def scan_port(target_ip: str, port: int, timeout: float = 1.0) -> Optional[int]:
    """
    Scan a single port on the target IP.
    
    Args:
        target_ip (str): Target IP address
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds
    
    Returns:
        Optional[int]: Port number if open, None otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            result = sock.connect_ex((target_ip, port))
            
            if result == 0:
                return port
            
            return None
    
    except socket.timeout:
        logger.debug(f"Timeout on port {port}")
        return None
    except socket.error as e:
        logger.error(f"Socket error on port {port}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scanning port {port}: {e}")
        return None

def GetOpenPorts(
    target_ip: str, 
    ports: List[int] = DEFAULT_PORTS, 
    max_workers: int = 20
) -> List[int]:
    """
    Scan multiple ports concurrently.
    
    Args:
        target_ip (str): Target IP address
        ports (List[int]): List of ports to scan
        max_workers (int): Maximum number of concurrent threads
    
    Returns:
        List[int]: List of open ports
    """
    if not validate_ip_address(target_ip):
        logger.error("Cannot proceed with port scanning")
        return []
    
    open_ports = []
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(lambda port: scan_port(target_ip, port), ports))
            open_ports = [port for port in results if port is not None]
    
    except concurrent.futures.TimeoutError:
        logger.error("Port scanning timed out")
    except Exception as e:
        logger.error(f"Error during port scanning: {e}")
    
    return sorted(open_ports)


# target_ip = "161.97.70.226" 
# open_ports = GetOpenPorts(target_ip)

# if open_ports:
#     print("\nOpen Ports:")
#     for port in open_ports:
#         print(f"Port {port} is open")
# else:
#     print("No open ports found.")