def extractParams(param_str):
    """
    Extracts parameters into a dict from string.
    Input:
        1. param_str (str) string of parameters in format “k1:10;k2:20” 

    Returns:
        2. mydict (dict) with format {k1: 10, k2:20}
    """
    mydict = {}
    mystr = param_str.split(';')
    for s in mystr:
        k,v = s.split(':')
        mydict[k.strip()] = v.strip()
    return mydict

def formatSpecies(x, find, replace):
    """
    Processes strings to make compliant with Tellurium model. 
    Input:
        1. x (str) string to process
        2. Find (list of str) characters to remove
        3. Replace (list of str) characters to replace characters in “Find” with. Must have same length as Find.

    Returns:
        1. x (str) processed string
    """

    x = x.upper()
    if x[0].isnumeric() and x[1] != ' ':
        x = 'z'+x 
    for f,r in zip(find,replace):
        x = x.replace(f,r)
    x = x.strip()
    return x

FIND = ['-',',','+',' ']
REPLACE = ['_','_','_plus','']
fmt = lambda x: formatSpecies(x, FIND, REPLACE)