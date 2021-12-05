import dns.resolver

def locate_service(domain, service, proto='tcp'):
    service = '_' + service
    proto = '_' + proto
    query = '.'.join((service, proto, domain))

    # This can raise dns.resolver.NoAnswer
    records = dns.resolver.query(query, 'SRV')

    # TODO: Sort records by priority (lowest first), then by weight (highest first)

    for r in records:
        yield (r.target.to_text(True), r.port)


def locate_ldap_server(domain):
    return locate_service(domain, 'ldap', 'tcp')


def get_domain_ldap_servers(domain, proto=None):
    """Returns a list of ldap URIs for the given domain"""
    if proto is None:
        proto = 'ldap'

    for host, port in locate_ldap_server(domain):
        yield '{}://{}:{}'.format(proto, host, port)
