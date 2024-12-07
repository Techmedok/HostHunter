import dns.resolver
import socket
import logging
import concurrent.futures
from typing import Dict, List, Optional, Union
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global resolver configuration
resolver = dns.resolver.Resolver()
resolver.timeout = 3
resolver.lifetime = 5
resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']

def _format_record_result(record_type: str, answers: dns.resolver.Answer) -> List[Dict[str, Union[str, int]]]:
    """
    Format DNS query results into a consistent dictionary format.
    
    :param record_type: Type of DNS record
    :param answers: DNS resolver answers
    :return: Formatted list of record dictionaries
    """
    try:
        ttl = answers.response.answer[0].ttl if answers.response.answer else None
        return [
            {
                "Content": str(rdata),
                "TTL": ttl,
                "Type": record_type
            }
            for rdata in answers
        ]
    except Exception as e:
        logger.warning(f"Error formatting {record_type} record: {e}")
        return []

def _resolve_standard(domain: str, record_type: str, resolver: dns.resolver.Resolver) -> Optional[List[Dict[str, Union[str, int]]]]:
    """
    Resolve standard DNS record types.
    
    :param domain: Domain to resolve
    :param record_type: Type of DNS record to resolve
    :param resolver: DNS resolver instance
    :return: List of resolved records or None
    """
    try:
        answers = resolver.resolve(domain, record_type)
        return _format_record_result(record_type, answers)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return None
    except Exception as e:
        logger.error(f"Unexpected error resolving {record_type} record for {domain}: {e}")
        return None

def _resolve_mx(domain: str, record_type: str, resolver: dns.resolver.Resolver) -> Optional[List[Dict[str, Union[str, int]]]]:
    """
    Resolve MX (Mail Exchanger) DNS records.
    
    :param domain: Domain to resolve
    :param record_type: Record type (MX)
    :param resolver: DNS resolver instance
    :return: List of MX records or None
    """
    try:
        answers = resolver.resolve(domain, record_type)
        ttl = answers.response.answer[0].ttl if answers.response.answer else None
        return [
            {
                "Content": f"{rdata.preference} {rdata.exchange}",
                "Preference": rdata.preference,
                "Exchange": str(rdata.exchange),
                "TTL": ttl,
                "Type": record_type
            }
            for rdata in answers
        ]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return None
    except Exception as e:
        logger.error(f"Unexpected error resolving MX record for {domain}: {e}")
        return None

def _resolve_soa(domain: str, record_type: str, resolver: dns.resolver.Resolver) -> Optional[List[Dict[str, Union[str, int]]]]:
    """
    Resolve SOA (Start of Authority) DNS records.
    
    :param domain: Domain to resolve
    :param record_type: Record type (SOA)
    :param resolver: DNS resolver instance
    :return: List of SOA records or None
    """
    try:
        answers = resolver.resolve(domain, record_type)
        soa_record = answers[0]
        ttl = answers.response.answer[0].ttl if answers.response.answer else None
        return [
            {
                "Content": str(soa_record),
                "Mname": str(soa_record.mname),
                "Rname": str(soa_record.rname),
                "Serial": soa_record.serial,
                "Refresh": soa_record.refresh,
                "Retry": soa_record.retry,
                "Expire": soa_record.expire,
                "Minimum": soa_record.minimum,
                "TTL": ttl,
                "Type": record_type
            }
        ]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return None
    except Exception as e:
        logger.error(f"Unexpected error resolving SOA record for {domain}: {e}")
        return None

@lru_cache(maxsize=128)
def _get_ptr_record(domain: str) -> Optional[List[Dict[str, str]]]:
    """
    Retrieve PTR (Reverse DNS) record for a domain.
    
    :param domain: Domain to resolve
    :return: List containing PTR record or None
    """
    try:
        ip_address = socket.gethostbyname(domain)
        ptr = socket.gethostbyaddr(ip_address)[0]
        return [{"Content": ptr, "Type": "PTR"}]
    except (socket.herror, socket.gaierror):
        return None

def GetDNSRecords(domain: str) -> Dict[str, Optional[List[Dict[str, Union[str, int]]]]]:
    """
    Retrieve all configured DNS record types for a given domain.
    
    :param domain: Domain to retrieve DNS records for
    :return: Dictionary of DNS records by record type
    """
    # Record types to resolve
    record_types = {
        'A': _resolve_standard,
        'AAAA': _resolve_standard,
        'CNAME': _resolve_standard,
        'MX': _resolve_mx,
        'NS': _resolve_standard,
        'TXT': _resolve_standard,
        'CAA': _resolve_standard,
        'SOA': _resolve_soa
    }
    
    # Use concurrent execution to speed up record retrieval
    results: Dict[str, Optional[List[Dict[str, Union[str, int]]]]] = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(record_types)) as executor:
        # Create a dictionary to map futures to record types
        future_to_record_type = {
            executor.submit(resolver_func, domain, record_type, resolver): record_type
            for record_type, resolver_func in record_types.items()
        }
        
        for future in concurrent.futures.as_completed(future_to_record_type):
            record_type = future_to_record_type[future]
            try:
                results[record_type] = future.result()
            except Exception as e:
                logger.error(f"Error processing {record_type} records: {e}")
                results[record_type] = None
    
    # Add PTR record separately as it uses a different resolution method
    results['PTR'] = _get_ptr_record(domain)
    
    return results