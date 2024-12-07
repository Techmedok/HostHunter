import dns.resolver
import socket
import json
from typing import Dict, List, Optional, Union, Any

def GetDNSRecords(domain: str) -> Dict[str, Optional[List[Dict[str, Union[str, int]]]]]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3  
    resolver.lifetime = 5 
    
    record_types = {
        'A': 'resolve_standard',
        'AAAA': 'resolve_standard', 
        'CNAME': 'resolve_standard',
        'MX': 'resolve_mx',
        'NS': 'resolve_standard', 
        'TXT': 'resolve_standard',
        'CAA': 'resolve_standard',
        'SOA': 'resolve_soa'
    }
    
    results: Dict[str, Optional[List[Dict[str, Union[str, int]]]]] = {}
    
    def resolve_standard(record_type: str) -> Optional[List[Dict[str, Union[str, int]]]]:
        try:
            answers = resolver.resolve(domain, record_type)
            return [
                {
                    "Content": str(rdata),
                    "TTL": answers.response.answer[0].ttl if answers.response.answer else None,
                    "Type": record_type
                } 
                for rdata in answers
            ]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
                dns.resolver.NoNameservers, dns.exception.Timeout):
            return None
    
    def resolve_mx(record_type: str) -> Optional[List[Dict[str, Union[str, int]]]]:
        try:
            answers = resolver.resolve(domain, record_type)
            return [
                {
                    "Content": f"{rdata.preference} {rdata.exchange}",
                    "Preference": rdata.preference,
                    "Exchange": str(rdata.exchange),
                    "TTL": answers.response.answer[0].ttl if answers.response.answer else None,
                    "Type": record_type
                } 
                for rdata in answers
            ]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
                dns.resolver.NoNameservers, dns.exception.Timeout):
            return None
    
    def resolve_soa(record_type: str) -> Optional[List[Dict[str, Union[str, int]]]]:
        try:
            answers = resolver.resolve(domain, record_type)
            soa_record = answers[0]
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
                    "TTL": answers.response.answer[0].ttl if answers.response.answer else None,
                    "Type": record_type
                }
            ]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return None
    
    def get_ptr_record() -> Optional[List[Dict[str, str]]]:
        try:
            ip_address = socket.gethostbyname(domain)
            ptr = socket.gethostbyaddr(ip_address)[0]
            return [{"Content": ptr, "Type": "PTR"}]
        except (socket.herror, socket.gaierror):
            return None
    
    for record_type, resolver_method in record_types.items():
        results[record_type] = locals()[resolver_method](record_type)
    
    results['PTR'] = get_ptr_record()
    
    return results

# domain = "techmedok.com"  
# dns_records = GetDNSRecords(domain)
# print(json.dumps(dns_records, indent=2))