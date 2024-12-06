import dns.resolver
import socket

def get_dns_records(domain):
    """
    Retrieve various DNS record types for a given domain.
    
    Args:
        domain (str): The domain name to query
    """
    record_types = {
        'A': dns.resolver.resolve,
        'AAAA': dns.resolver.resolve,
        'CNAME': dns.resolver.resolve,
        'MX': dns.resolver.resolve,
        'NS': dns.resolver.resolve,
        'TXT': dns.resolver.resolve,
        'SRV': dns.resolver.resolve,
        'CAA': dns.resolver.resolve
    }
    
    # PTR record requires a reverse IP lookup
    def get_ptr_record(domain):
        try:
            return socket.gethostbyaddr(socket.gethostbyname(domain))[0]
        except (socket.herror, socket.gaierror):
            return "PTR record not found"
    
    # SOA record has a slightly different resolution method
    def get_soa_record(domain):
        try:
            soa = dns.resolver.resolve(domain, 'SOA')
            return str(soa[0])
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return "SOA record not found"
    
    print(f"DNS Records for {domain}:")
    print("-" * 40)
    
    # Lookup A Record
    try:
        a_records = record_types['A'](domain, 'A')
        print("A Records:")
        for rdata in a_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"A Record Error: {e}")
    
    # Lookup AAAA Record
    try:
        aaaa_records = record_types['AAAA'](domain, 'AAAA')
        print("\nAAAA Records:")
        for rdata in aaaa_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"AAAA Record Error: {e}")
    
    # Lookup CNAME Record
    try:
        cname_records = record_types['CNAME'](domain, 'CNAME')
        print("\nCNAME Records:")
        for rdata in cname_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"CNAME Record Error: {e}")
    
    # Lookup MX Record
    try:
        mx_records = record_types['MX'](domain, 'MX')
        print("\nMX Records:")
        for rdata in mx_records:
            print(f"  Priority: {rdata.preference}, Mail Server: {rdata.exchange}")
    except Exception as e:
        print(f"MX Record Error: {e}")
    
    # Lookup NS Record
    try:
        ns_records = record_types['NS'](domain, 'NS')
        print("\nNS Records:")
        for rdata in ns_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"NS Record Error: {e}")
    
    # PTR Record (Reverse DNS)
    print("\nPTR Record:")
    print(f"  {get_ptr_record(domain)}")
    
    # Lookup SOA Record
    print("\nSOA Record:")
    print(f"  {get_soa_record(domain)}")
    
    # Lookup TXT Record
    try:
        txt_records = record_types['TXT'](domain, 'TXT')
        print("\nTXT Records:")
        for rdata in txt_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"TXT Record Error: {e}")
    
    # Lookup SRV Record (example service)
    try:
        srv_records = record_types['SRV'](f"_sip._tcp.{domain}", 'SRV')
        print("\nSRV Records:")
        for rdata in srv_records:
            print(f"  Priority: {rdata.priority}, Weight: {rdata.weight}, "
                  f"Port: {rdata.port}, Target: {rdata.target}")
    except Exception as e:
        print(f"SRV Record Error: {e}")
    
    # Lookup CAA Record
    try:
        caa_records = record_types['CAA'](domain, 'CAA')
        print("\nCAA Records:")
        for rdata in caa_records:
            print(f"  {rdata}")
    except Exception as e:
        print(f"CAA Record Error: {e}")

# Example usage
if __name__ == "__main__":
    domain = "techmedok.com"  # Replace with the domain you want to query
    get_dns_records(domain)