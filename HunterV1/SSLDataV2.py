import ssl
import socket
import traceback
import json
import datetime
import requests
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

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

def extract_subject_alt_names(cert):
    """
    Extract Subject Alternative Names from the certificate
    """
    try:
        san_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        return [str(name) for name in san_ext.value]
    except Exception:
        return []

def check_certificate_validity(cert):
    """
    Check certificate validity and remaining days
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    not_before = cert.not_valid_before_utc
    not_after = cert.not_valid_after_utc
    
    is_valid = now >= not_before and now <= not_after
    days_remaining = (not_after - now).days
    
    return {
        'is_valid': is_valid,
        'days_remaining': days_remaining
    }

def get_extended_key_usage(cert):
    """
    Extract Extended Key Usage from the certificate
    """
    try:
        eku_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.EXTENDED_KEY_USAGE)
        return [str(usage) for usage in eku_ext.value]
    except Exception:
        return []

def GetSSLData(hostname, port=443, timeout=10):
    """
    Comprehensive SSL/TLS certificate details retrieval
    :param hostname: Website domain name
    :param port: SSL port (default 443)
    :param timeout: Connection timeout
    :return: Dictionary containing detailed SSL information
    """
    ssl_details = {
        'hostname': hostname,
        'port': port,
        'has_ssl': False
    }

    try:
        # SSL Socket Connection Method
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                # Basic SSL Connection Details
                ssl_details.update({
                    'has_ssl': True,
                    'ssl_version': secure_sock.version(),
                    'cipher': list(secure_sock.cipher())
                })

                # Certificate Parsing
                cert_der = secure_sock.getpeercert(binary_form=True)
                x509_cert = x509.load_der_x509_certificate(cert_der, default_backend())
                
                # Detailed Certificate Information
                ssl_details.update({
                    'subject': {attr.oid._name: str(attr.value) for attr in x509_cert.subject},
                    'issuer': {attr.oid._name: str(attr.value) for attr in x509_cert.issuer},
                    'serial_number': str(x509_cert.serial_number),
                    'not_valid_before': x509_cert.not_valid_before_utc.isoformat(),
                    'not_valid_after': x509_cert.not_valid_after_utc.isoformat(),
                    'signature_algorithm': x509_cert.signature_algorithm_oid._name,
                    'version': str(x509_cert.version),
                    'subject_alt_names': extract_subject_alt_names(x509_cert),
                    'extended_key_usage': get_extended_key_usage(x509_cert)
                })

                # Certificate Validity Check
                validity = check_certificate_validity(x509_cert)
                ssl_details.update(validity)

                # Public Key Information
                public_key = x509_cert.public_key()
                pem_public_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')

                ssl_details.update({
                    'public_key_type': type(public_key).__name__,
                    'public_key_bits': public_key.key_size if hasattr(public_key, 'key_size') else 'Unknown',
                    'public_key_pem': pem_public_key
                })

    except ssl.SSLError as ssl_err:
        ssl_details['ssl_error'] = str(ssl_err)
    except socket.gaierror:
        ssl_details['connection_error'] = f"Could not resolve hostname: {hostname}"
    except ConnectionRefusedError:
        ssl_details['connection_error'] = f"Connection refused to {hostname}:{port}"
    except Exception as e:
        ssl_details['unexpected_error'] = {
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }

    # Additional Request-based SSL Information (optional)
    try:
        with requests.Session() as session:
            session.verify = False 
            disable_warnings(InsecureRequestWarning) 
            response = session.get(f'https://{hostname}', timeout=timeout)
            ssl_details['http_status_code'] = response.status_code
    except requests.RequestException as req_err:
        ssl_details['requests_error'] = str(req_err)

    return decode_bytes(ssl_details)

def GetSSLDataV2(website):
    details = GetSSLData(website)
    if details.get('has_ssl'):
        return json.dumps(details)
    else:
        return None

# print(GetSSLDataV2("techmedok.com"))