import socket

def DomainCheck(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None
    
# ip = DomainCheck("authfi.one")
# print(f"{ip}")
