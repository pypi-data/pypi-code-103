import sys
import os
_packageName=os.sep+'SampleDistribution'

def importPkgs():
    # Extract SampleDistribution_1 path from SampleDistribution_1\pkg2\main filename and insert into sys.path list
    sys.path.insert(1,__file__[:__file__.rfind(os.sep+'pkg2')])
    # Create SampleDistribution_2 path from SampleDisrtibution\pkg2\main filename and insert into sys.path list.
    sys.path.insert(2,__file__[:__file__.rfind(_packageName+'_1')] + _packageName + '_2' )
    import mod1
    from pkg1 import mod2

if __name__ == '__main__':
    importPkgs()