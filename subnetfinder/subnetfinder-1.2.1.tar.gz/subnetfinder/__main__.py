#######################################################
###  __main__.py
###  This script is called when the module is executed
###  from the command line, via python -m <mod>.
###  Therefore, this will rationalize the options 
###  provided from the CLI and pass them to the module
###  method.
#######################################################

import ipaddress
import argparse
import sys
import subnetfinder.subnetfinder as subnetfinder
from subnetfinder.__init__ import __version__

def main():
    '''
    This method will rationalize the input so that the "ProcessSubnets" method can be called
    as a module from other scripts.
    '''
    
    ###################################
    ###  This code is only used if this
    ###  module is called from the CLI
    ###  directly rather than being 
    ###  called as a module.
    ###################################

    parser=argparse.ArgumentParser(description='Find unused subnets from a provided list of used subnets.',
    prog='subnetfinder',
        epilog='''
        Use this program to find unused blocks of IPs, or
        blocks used a limited number of times, with 
        prefix length pl within the subnet sn, based on 
        the IPs or blocks supplied.''')
    parser.add_argument('-s','--supernet',metavar='sn', type=ipaddress.ip_network, dest='sn',
        help='The Super Net in which to find open IP blocks, such as 10.0.0.0/8.',
        required=True)
    parser.add_argument('-p','--prefix',metavar='pl',type=int,dest='pl',
        help='The maximum prefix length to consider, such as 16.  This must be longer than the supernet prefix length.',
        required=True)
    parser.add_argument('-u','--uniquein',metavar='N',type=int,dest='uniquein',default=0,
        help='Specify the maximum number of groups that can contain a prefix.  Can be used to find\
            prefixes unique to two or more lists.  Groups must have headings of "group: <groupname>".')
    parser.add_argument(nargs='?',type=argparse.FileType('r'),default=sys.stdin,dest='FILE',
        help='If present, the file name of the source list with one prefix per line.  Default is from STDIN.')
    parser.add_argument('--summarize',action='store_true',
        help='Summarize contiguous subnets into supernets if possible.')
    parser.add_argument('--version',action='version',version='%(prog)s version '+ __version__)
    parser.add_argument('-v','--verbose',action='count',default=0,
        help='Be more verbose with output. Verbose levels 1 to 3 are -v to -vvv.')
    parser.add_argument('--debug',action='store_true',
        help='Display additional output for lines.')
    parser.add_argument('--test',action='store_true',
        help='Used only for unit testing')
    parsed=parser.parse_args()

    if (parsed.sn.prefixlen>=parsed.pl):
        parser.error('The prefix length of the Super Net supplied must be shorter than the target prefix length. You gave me a Super Net prefix of ('+
        str(parsed.sn.prefixlen)+') and a target prefix of ('+str(parsed.pl)+').')
    
    file=parsed.FILE
    supernet=parsed.sn
    prefixlen=parsed.pl
    debug=parsed.debug
    summarize=parsed.summarize
    uniquein=parsed.uniquein
    verbose=parsed.verbose
    if debug:
        print("Options Provided:")
        print(" Supernet: %s"%(supernet))
        print(" Prefix Len: %d"%(prefixlen))
        print(" Unique In: %d"%(uniquein))
        print(" Debug? %s"%(debug))
        print(" Summarize? %s"%(summarize))
        print(" Verbose Level: %d"%(verbose))
    usedlist=file.readlines()
    if parsed.test:
        return parsed
    else:
        availablelist=subnetfinder.ProcessSubnets(supernet,usedlist,prefixlen,showdebug=debug,summarize=summarize,screenout=True,uniquein=uniquein)
    
    print("Available Subnets:")
    for x in [str(x) for x in availablelist ]:
        print("%s"%(x))

    if (uniquein > 0) & (verbose>=1):
        print("Subnets which occur in no more than "+ str(uniquein) +" group(s)")
        for x in [str(x) for x in subnetfinder.uniquelist]:
            print("%s"%(x))

    return

if __name__=='__main__':
    main()
