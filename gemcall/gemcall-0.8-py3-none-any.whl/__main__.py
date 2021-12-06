#!/usr/bin/env python3
# vim: tabstop=4 shiftwidth=4 expandtab

import argparse
import sys
import gemcall

def main():
    parser = argparse.ArgumentParser(prog="gemcall",description="Python module/CLI program for making network requests with the gemini protocol.")
    parser.add_argument("-c","--clientcert",help="Path to client certificate. This is optional, but must be used when -k/--clientkey is used.")
    parser.add_argument("-k","--clientkey",help="Path to the private key file for a client certificate. This is optional, but must be used when -c/--clientcert is used.")
    parser.add_argument("-u","--url",help="Fully qualified URL to fetch.")
    parser.add_argument("-o","--outputfile",help="File to output response body to.")
    parser.add_argument("-t","--timeout",help="Timeout of connection attempt, in seconds. Default is 3.",default=3,type=int)
    parser.add_argument("-q","--quiet",help="Don't print response header.",action="store_true")
    parser.add_argument("-n","--nobody",help="Only print response header.",action="store_true")
    parser.add_argument("-s","--stdoutonly",help="Print everything to stdout",action="store_true")
    args = parser.parse_args()

    if not args.url:
        parser.print_help()
    else:
        responseobj = gemcall.request(url = args.url, clientcert = args.clientcert, clientkey = args.clientkey, timeout = args.timeout)

        if not args.quiet:
            header = str.encode("%s %s\n" % (responseobj.responsecode, responseobj.meta))
            if args.stdoutonly:
                sys.stdout.buffer.write(header)
            else:
                sys.stderr.buffer.write(header)
        outputfile = open(args.outputfile, "wb") if args.outputfile else None
        while not args.nobody:
            buf = responseobj.read()
            if len(buf) == 0:
                break
            elif outputfile:
                outputfile.write(buf)
                outputfile.close()
            else:
                sys.stdout.buffer.write(buf) 

        responseobj.discard()

if __name__ == "__main__":

    main()

