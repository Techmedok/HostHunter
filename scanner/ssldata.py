import ssl
import socket
import traceback
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import json

def decode_bytes(obj):
    """
    Recursively decode byte strings to regular strings
    """
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, dict):
        return {decode_bytes(key): decode_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decode_bytes(item) for item in obj]
    return obj

def get_ssl_details(hostname, port=443):
    """
    Retrieve SSL/TLS certificate details using multiple methods.
    :param hostname: Website domain name
    :param port: SSL port (default 443)
    :return: Dictionary containing comprehensive SSL details
    """
    ssl_details = {}
    try:
        # Using socket and ssl modules
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                # Basic socket-level SSL details
                ssl_details['socket_ssl_version'] = secure_sock.version()
                ssl_details['cipher'] = list(secure_sock.cipher())
                # Peer certificate
                cert = secure_sock.getpeercert(binary_form=True)
                x509_cert = x509.load_der_x509_certificate(cert, default_backend())
                # Certificate details
                ssl_details.update({
                    'subject': {attr.oid._name: str(attr.value) for attr in x509_cert.subject},
                    'issuer': {attr.oid._name: str(attr.value) for attr in x509_cert.issuer},
                    'serial_number': str(x509_cert.serial_number),
                    'not_valid_before': x509_cert.not_valid_before_utc.isoformat(),
                    'not_valid_after': x509_cert.not_valid_after_utc.isoformat(),
                    'signature_algorithm': x509_cert.signature_algorithm_oid._name,
                    'version': str(x509_cert.version)  # Convert the Version to a string
                })
                
                # Extract the public key and convert to PEM format
                public_key = x509_cert.public_key()
                pem_public_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')

                # Optionally, you can strip the "-----BEGIN PUBLIC KEY-----" and "-----END PUBLIC KEY-----" to get the raw key part
                raw_public_key_str = pem_public_key.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").strip()

                ssl_details['public_key'] = str(x509_cert.public_key().public_numbers())
                ssl_details['public_key_str'] = raw_public_key_str

    except ssl.SSLError as ssl_err:
        ssl_details['ssl_error'] = str(ssl_err)
    except Exception as e:
        ssl_details['socket_error'] = {
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }

    try:
        # Using requests module for additional information
        with requests.Session() as session:
            session.verify = False  # Disable verification for testing purposes
            disable_warnings(InsecureRequestWarning)  # Suppress warning
            response = session.get(f'https://{hostname}', timeout=10)
            ssl_details['requests_status_code'] = response.status_code
            # Connection details if available
            if hasattr(response, 'raw') and hasattr(response.raw, 'connection'):
                connection = response.raw.connection
                if hasattr(connection, 'sock') and connection.sock:
                    sock = connection.sock
                    ssl_details['ssl_connection_details'] = {
                        'protocol': sock.version() if hasattr(sock, 'version') else 'Unknown',
                        'peercert': sock.getpeercert() if hasattr(sock, 'getpeercert') else 'Unavailable'
                    }
    except requests.RequestException as req_err:
        ssl_details['requests_error'] = str(req_err)

    return decode_bytes(ssl_details)

# website = 'techmedok.com'
# details = get_ssl_details(website)
# print(json.dumps(details, indent=2))
