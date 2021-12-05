##
# File: CifToNmrStar.py
# Date: 19-Jul-2021
#
# Updates:
# 13-Oct-2021  M. Yokochi - code revision according to PEP8 using Pylint (DAOTHER-7389, issue #5)
##
""" Wrapper class for CIF to NMR-STAR converter.
    @author: Masashi Yokochi
"""
import sys
import os
import os.path
import pynmrstar

from wwpdb.utils.nmr.io.mmCIFUtil import mmCIFUtil


class CifToNmrStar:
    """ Simple CIF to NMR-STAR converter.
    """

    def __init__(self, log=sys.stderr):
        self.__lfh = log

    def convert(self, cifPath=None, strPath=None):
        """ Convert CIF to NMR-STAR for re-upload without CS data
        """

        if cifPath is None or strPath is None:
            return False

        try:

            cifObj = mmCIFUtil(filePath=cifPath)

            block_name_list = cifObj.GetBlockIDList()

            strObj = pynmrstar.Entry.from_scratch(os.path.basename(cifPath))

            for block_name in block_name_list:
                sf = pynmrstar.Saveframe.from_scratch(block_name)

                dict_list = cifObj.GetDataBlock(block_name)

                has_sf_category = False

                for category, itVals in dict_list.items():

                    if not has_sf_category:

                        sf.set_tag_prefix(category)

                        for item, value in zip(itVals['Items'], itVals['Values'][0]):
                            sf.add_tag(item, block_name if item == 'Sf_framecode' else value)

                        has_sf_category = True

                    else:

                        lp = pynmrstar.Loop.from_scratch(category)

                        for item in itVals['Items']:
                            lp.add_tag(item)

                        for row in itVals['Values']:
                            lp.add_data(row)

                        sf.add_loop(lp)

                strObj.add_saveframe(sf)

            strObj.write_to_file(strPath, skip_empty_tags=False)

        except Exception as e:
            self.__lfh.write('+ERROR- CifToNmrStar.convert() %s\n' % e)

        return False
