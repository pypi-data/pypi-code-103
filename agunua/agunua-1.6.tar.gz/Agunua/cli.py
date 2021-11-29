#!/usr/bin/env python3

# https://framagit.org/bortzmeyer/agunua
import Agunua
import Agunua.status

import sys
import getopt
import signal
import urllib.parse
import re

def usage(msg=None):
    print("Usage: %s url ..." % sys.argv[0], file=sys.stderr)
    if msg is not None:
        print(msg, file=sys.stderr)

def main():
    # Defaults
    debug = False
    verbose = False
    insecure = True
    follow_redirect = True
    tofu = Agunua.TOFU
    send_sni = Agunua.SEND_SNI
    maximum_time = 30 # Seconds
    force_ipv4 = False
    force_ipv6 = False
    display_links = False
    parse_content = False
    connect_to = None
    socks = None
    accept_expired_cert = False
    binary = False
    maxlines = Agunua.MAXLINES
    maxsize = Agunua.MAXSIZE
    certificate = None
    privatekey = None
    try:
        optlist, args = getopt.getopt (sys.argv[1:], "bc:dfhik:msv:46",
                                       ["help", "version", "verbose", "debug",
                                        "insecure", "secure", "no-tofu",
                                        "not-follow-redirect", "maximum-time=",
                                        "force-ipv4", "force-ipv6",
                                        "display-links", "connect-to=",
                                        "no-sni", "socks=",
                                        "accept-expired-certificate",
                                        "certificate=", "key=", "binary",
                                        "maximum-lines=", "maximum-size="])
        for option, value in optlist:
            if option == "--help" or option == "-h":
                usage()
                sys.exit(0)
            elif option == "--version":
                print(Agunua.VERSION)
                sys.exit(0)
            elif option == "--debug" or option == "-d":
                verbose = True
                debug = True
            elif option == "--verbose" or option == "-v":
                verbose = True
            elif option == "--binary" or option == "-b":
                binary = True
            elif option == "--insecure" or option == "-i":
                # Now a no-op, we are insecure by default
                pass
            elif option == "--secure" or option == "-s":
                insecure = False
            elif option == "--display-links":
                display_links = True
                parse_content = True
            elif option == "--connect-to":
                connect_to = value
            elif option == "--no-sni":
                send_sni = False
            elif option == "--socks":
                match = re.search("^\[?(([\w\.]+)|(([a-fA-F0-9:]+))|([0-9\.]+))\]?:([0-9]+)$", value)
                if not match:
                    usage("Socks must be host:port")
                    sys.exit(1)
                socks = (match.group(1), int(match.group(6)))
            elif option == "--no-tofu":
                tofu = ""
            elif option == "--accept-expired-certificate":
                accept_expired_cert = True
            elif option == "--certificate" or option == "-c":
                certificate = str(value)
            elif option == "--key" or option == "-k":
                privatekey = str(value)
            elif option == "--not-follow-redirect" or option == "-f":
                follow_redirect = False
            elif option == "--maximum-time" or option == "-m":
                maximum_time = int(value)
            elif option == "--maximum-lines":
                maxlines = int(value)
            elif option == "--maximum-size":
                maxsize = int(value)
            elif option == "--force-ipv4" or option == "-4":
                force_ipv4 = True
            elif option == "--force-ipv6" or option == "-6":
                force_ipv6 = True
            else:
                # Should never occur, it is trapped by getopt
                usage("Unknown option %s" % option)
    except getopt.error as reason:
        usage(reason)
        sys.exit(1)
    if len(args) == 0:
        usage()
        sys.exit(1)
    if binary and display_links:
        usage("Binary mode not compatible with link display")
        sys.exit(1)
    if (certificate is not None and privatekey is None) or (certificate is None and privatekey is not None):
        usage("You must indicate both the certificate and the private key")
        sys.exit(1)

    error = False
    def alarm(*_):                                                                                                 
        print("Maximum time (%i seconds) elapsed, stopping" % maximum_time, file=sys.stderr)
        sys.exit(1)
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(maximum_time)
    for url in args:
        if verbose:
            print("Trying to get %s ..." % url)
        try:
            u = Agunua.GeminiUri(url, get_content=True,
                                 parse_content=parse_content,
                                 follow_redirect=follow_redirect,
                                 insecure=insecure, tofu=tofu,
                                 send_sni=send_sni, connect_to=connect_to,
                                 use_socks=socks, debug=debug,
                                 binary=binary, maxlines=maxlines,
                                 maxsize=maxsize, force_ipv4=force_ipv4,
                                 accept_expired=accept_expired_cert,
                                 clientcert=certificate, clientkey=privatekey,
                                 force_ipv6=force_ipv6)
        except Agunua.NonGeminiUri as e:
            components = urllib.parse.urlparse(url)
            if components.scheme == "": # See #30
                scheme = "gemini"
                if components.netloc == "":
                    try:
                        (netloc, path) = components.path.split("/", maxsplit=1)
                    except ValueError:
                        netloc = components.path
                        path = ""
                else:
                    netloc = components.netloc
                    path = components.path
                url = urllib.parse.urlunsplit((scheme, netloc, path,
                                               components.query, components.fragment))
                u = Agunua.GeminiUri(url, get_content=True,
                                     parse_content=parse_content,
                                     follow_redirect=follow_redirect,
                                     insecure=insecure, tofu=tofu,
                                     send_sni=send_sni,
                                     connect_to=connect_to,
                                     use_socks=socks, debug=debug,
                                     binary=binary, maxlines=maxlines,
                                     maxsize=maxsize,
                                     force_ipv4=force_ipv4,
                                     accept_expired=accept_expired_cert,
                                     clientcert=certificate, clientkey=privatekey,
                                     force_ipv6=force_ipv6)
            else:
                print("Non-Gemini URI (scheme is \"%s\") \"%s\"" % (e, url), file=sys.stderr)
                error = True
                continue
        except Agunua.InvalidUri:
            print("Invalid URI \"%s\"" % url , file=sys.stderr)
            error = True
            continue
        if debug and "header" in u.__dict__:
            print("Header line: \"%s\"" % u.header)
        if u.network_success:
            if verbose:
                print("Network success with %s." % u.ip_address)
            #if u.no_shutdown:
            #    print("Warning, no TLS shutdown received from the server", file=sys.stderr)
            if tofu != "" and debug:
                print("Public key is %s." % u.keystring)
            if debug:
                print("Certificate issued by \"%s\" for \"%s\". Algorithm is %s, public key is of type %s (%i bits)." % \
                      (u.issuer, u.subject, u.cert_algo, u.cert_key_type, u.cert_key_size))
            if u.status_code == "20":
                if verbose:
                    print("Media type is %s" % u.meta)
                if not binary and u.binary: # Decoding failed
                    print("Decoding failed: %s" % u.error, file=sys.stderr)
                    error = True
                elif not display_links:
                    if not binary and u.mediatype.startswith("text/"):
                        print(u.payload, end="")
                    else:
                        if not sys.stdout.isatty():
                            sys.stdout.buffer.write(u.payload)
                        else:
                            print("Cannot display binary content to a terminal", file=sys.stderr)
                            error = True
                else:
                    print(u.links)
            elif u.status_code == "10" or u.status_code == "11":
                print("Input requested (\"%s\") send it with a query (?search-term at the end of the URL)" % \
                      u.meta)
            else:
                if u.status_code in Agunua.status.codes:
                    status = Agunua.status.codes[u.status_code]
                elif u.status_code[0] in Agunua.status.categories:
                    status = "illegal status code, category \"%s\"" % Agunua.status.categories[u.status_code[0]]
                else:
                    status = "completely illegal status code \"%s\"" % u.status_code
                print("Problem, %s (extra message: \"%s\")." % (status, u.meta), file=sys.stderr)
                error = True
        else:
            print("Network problem, %s." % u.error, file=sys.stderr)
            error = True
    if error:
        sys.exit(1)
    else:
        sys.exit(0)

