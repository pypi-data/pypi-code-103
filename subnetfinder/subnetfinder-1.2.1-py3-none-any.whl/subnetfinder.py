#######################################################
###  subnetfinder.py
###  This is the primary module.  This provides the 
###  ProcessSubnets method which really is all that 
###  should be called externally.
#######################################################

import ipaddress
import sys
import math

VERSION='1.2'
MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

uniquelist=[]

def __findsupernets(sourcelist,showdebug):
    '''
    This method takes a list of ipaddress.IPv4Network objects and looks for supernets 
    which are completely contained by objects within the list, by stepping back up the
    CIDR tree one by one.  This module would not normally be called from another script.
    '''

    availablelist=[]
    count=0  # used as a counter for user information in debug
    #while more:
    more=answer=False
    # supernet=None

    sourcelist.sort()

    count+=1
    if len(sourcelist):
        prefix=sourcelist[0].prefixlen
        minprefix=int(prefix-math.log(len(sourcelist),2))
        if showdebug:
            print("Rollup scan pass %d.  Currently %d networks."%(count,len(sourcelist)))
            print("The calculated minimum supernet prefix lenth is %d"%(minprefix))
            print("Current available subnets")
            for x in sourcelist:
                print("%s"%(x))

    ###################################
    ###  This is the main loop which 
    ###  steps through each network
    ###  This selects one subnet and tries to find
    ###  the shortest prefix that can be represent
    ###  completely represented.
    ###################################
    
    for net in sourcelist:
        answer=True
        supernetprefix=prefix
        if showdebug:
            print("Checking %s"%(net))
        while answer & (supernetprefix>minprefix):
            supernetprefix-=1
            supernet=net.supernet(new_prefix=supernetprefix)
            if showdebug:
                print("Will try supernet %s"%(supernet))

            ###################################
            ###  This section could be optimized to make half
            ###  as many passes by recording which supernet's
            ###  subnets have already been checked.  Since this
            ###  entire script runs infrequently, it probably 
            ###  isn't worth the time.
            ###################################

            for x in supernet.subnets(new_prefix=prefix):
                answer &= (x in sourcelist)
                if showdebug & (x in sourcelist): # & (x != net):
                    print("Found subnet %s in available list"%(x))
                if x not in sourcelist:
                    if showdebug:
                        print("Didn't find %s in list"%(x))
                    break
            
            ###################################
            ###  If all subnets from the supernet
            ###  are found within the available list
            ###  then remove all subnets
            ###  and add the supernet.  Also set
            ###  the flag so to rescan the entire 
            ###  available list.
            ###################################

        if showdebug:
            print("Analysis shows supernet prefix %d, minimum prefix %d, answer %d"%(supernetprefix,minprefix,answer))    

        if (supernetprefix==minprefix) & answer:
            if showdebug:
                print("Special case:  Entire supernet is available.")
            return [ net.supernet(new_prefix=minprefix) ]
        elif supernetprefix+1<prefix:
            supernet=net.supernet(new_prefix=supernetprefix+1)
            if showdebug:
                print("Summarizing to /%s"%(supernet))
            for x in supernet.subnets(new_prefix=prefix):
                if showdebug:
                    print("Removing %s"%(x))
                sourcelist.remove(x)
            if supernet not in availablelist:
                if showdebug:
                    print("Adding %s"%(supernet))
                availablelist.append(supernet)
        else:
            if net not in availablelist:
                if showdebug:
                    print("Adding %s"%(supernet))
            availablelist.append(net)

    more |= answer #  set "more" to true if any supernets are found

    ###################################
    ###  If the loop found any supernets
    ###  the "while" loop continues
    ###################################
    
    if showdebug:
        print("Continue flags set to %s"%(more))

    return availablelist

def ProcessSubnets(supernet,usedlist,targetprefixlen,showdebug=False,screenout=False,summarize=False,uniquein=0):
    '''
    This will build a list of "seen" (used) subnets from the source provided, and then
    return a list of unseen subnets with length "prefixlen" from the same supernet.  
    It will ignore all provided subnets which are outside of the supernet range.  
    It will error and ignore if the line isn't a valid CIDR subnet (10.0.0.0/8) notation.  

    NOTE: The default CIDR length is omitted, a /32 is assumed.

    [Arguments]
    supernet:   The ipaddress.ip_network object for the supernet
    usedlist:   A iterable list of string objects.  Each string object must contain either a used 
                subnet in CIDR format, or a group header.  If a group header is supplied, subsequent 
                CIDR networks will be placed in that group.
                Example CIDR notation:  10.0.0.0/8
                Example group header:  Group: New Group
    targetprefixlen:  
                An int representing the target prefix length
    uniquein:   Can be used to find a subnet which exist only in N or less groups.
    showdebug:  Will print additional debugging information to STDOUT.
                Default is False.
    screenout:  Directs the output to STDOUT and exits rather than returning a list
                Default is False.
    supernets:  Combine contiguous blocks into summary supernets with shorter prefix length pl if possible.
                This may take more time if the list of available subnets is long.
    
    [Returns]
    This method returns a list of ipaddress.IPv4Network objects representing the unused subnets
    matching the characteristics provided.
    '''
    global uniquelist
    usedsubnets={}
    count=0
    if screenout:
        print("Beginning Read")

    ###################################
    ###  This is the main loop
    ###################################

    group='global'
    usedsubnets.update({group:{}})
    for line in usedlist:
        line=line.strip()
        count+=1
        if showdebug:
            print("Line %d:  Read '%s'"%(count,line))
        if line.lower().startswith('group:'):
            group=line[6:].strip()
            if group not in usedsubnets:
                usedsubnets.update({group:{}})
            if showdebug:
                print("line %d:  Changing to group '%s'"%(count,group))
            continue
        try:
            lineip=ipaddress.ip_network(line)
        except:
            if showdebug:
                print("line %d:  An error occured trying to convert '%s' into an IP subnet format"%(count,line))
            continue
        if showdebug:
            print("Line %d:  Converted '%s' to an IP object"%(count,str(lineip)))

        ###################################
        ###  Now, compare whether the used
        ###  subnet's prefix is longer,
        ###  shorter, or the same as the
        ###  target subnet.
        ###################################

        if (lineip.subnet_of(supernet)):
            if(lineip.prefixlen>targetprefixlen):  

                ## used prefix is longer, so add the target prefix length
                
                addsubnets={str(lineip.supernet(new_prefix=targetprefixlen)):1}
                usedsubnets[group].update(addsubnets)
                if showdebug:
                    print("Line %d:  Added %s which covers %s"%(count,list(addsubnets.keys()),str(lineip)))

            elif(lineip.prefixlen,targetprefixlen):

                ## used prefix is shorter, so add all the included target prefix lengths

                addsubnets={str(x):1 for x in lineip.subnets(new_prefix=targetprefixlen)}
                usedsubnets[group].update(addsubnets)
                if showdebug:
                    print("Line %d:  Added %s to include all of %s"%(count,list(addsubnets.keys()),lineip))

            else:

                ## used prefix is the same, so add just the used subnet

                usedsubnets[group].update({str(lineip):1})
                if showdebug:
                    print("Line %d:  Added %s"%(lineip))

        else:

            ### This line is only reached if the used subnet isn't within the supernet

            if showdebug:
                print("Line %d:  Ignoring '%s'.  Not within the supernet '%s'."%(count,line,str(supernet)))

    if screenout:
        print("Done Reading.  Read %d lines"%(count))

    ###################################
    ###  This generator object produces a complete list
    ###  of available subnets based on the supernet,
    ###  the target subnet length, the "unique in" value,
    ###  and the used subnets.
    ###################################    

    if showdebug:
        print("Full list of used subnets are as follows:")
        for x in usedsubnets.keys():
            print('Group: %s'%(x))
            for y in usedsubnets[x].keys():
                print(y)

    availablelist= [ x for x in supernet.subnets(new_prefix=targetprefixlen) 
        if str(x) not in [ z for y in usedsubnets.keys() 
        for z in usedsubnets[y].keys()] ]
    
    uniquelist= [ x for x in supernet.subnets(new_prefix=targetprefixlen) 
        if 0 <  [ z for y in usedsubnets.keys() 
        for z in usedsubnets[y].keys()].count(str(x)) <= uniquein ]

    if showdebug:
        print("Available Subnets")
        print(availablelist)
        for x in availablelist:
            print(x)
        print("Subnets matching uniqueness value")
        print(uniquelist)
        for x in uniquelist:
            print(x)

    availabledict={ x:1 for x in availablelist+uniquelist }
    availablelist=[x for x in availabledict.keys() ]
    availablelist.sort()

    if showdebug:
        print(availabledict)
        print("Combined Lists")
        for x in availablelist:
            print(x)

    if summarize:
        if screenout:
            print("Starting Rollup")
        availablelist=__findsupernets(availablelist,showdebug)

    return availablelist


