'''Module containing the list of top names.'''
import logging
from time import sleep, time
from typing import List
from top_names.name_scraper import NameScraper

class NameList:
    '''Wrapper class for the list of top names. Lazily loads names.
    :py:property real_size: The "real size" of the container, i.e. size of elements\
         that are not None.
    :type real_size: int'''

    __NAMES_PER_LIST: int = 400
    SECONDS_BETWEEN_QUERY: float = 0.2

    # Site URLs follow a pattern, https://www.ssa.gov/oact/babynames/decades/names[decade].html
    # Since each decade starts at 2010 and decreases by 10 until 1880,
    # we can use list comprehension here.
    SITES: List[str] = [f"https://www.ssa.gov/oact/babynames/decades/names{x}s.html"\
        for x in range(2010, 1880, -10)]

    SIZE: int = len(SITES) * __NAMES_PER_LIST
    __GLOBAL_CONTAINER: List[str] = [None for _ in range(SIZE)]

    def __init__(self):
        self.__container: List[str] = NameList.__GLOBAL_CONTAINER
        self.__last_query: float = 0


    def __populate_segment(self, containing: int):
        '''Populate the list.
        :param containing: '''
        # If it's been too soon since the last site scrape, we
        # need to wait.

        segment: int = containing // NameList.__NAMES_PER_LIST
        index: int = segment * NameList.__NAMES_PER_LIST

        logging.debug("Begin population of list segment %i-%i",\
            index, index + (NameList.__NAMES_PER_LIST - 1))
        while (time() - self.__last_query) < NameList.SECONDS_BETWEEN_QUERY:
            sleep(0.01)

        site: str = NameList.SITES[segment]
        logging.debug("Scraping from site \"%s\"", site)
        scalper = NameScraper(site)
        for name in scalper:
            logging.debug("Setting index %i to \"%s\".", index, name)
            self.__container[index] = name
            index += 1
        logging.debug("Finished populating segment.")
        self.__last_query = time()

    def get(self, index:int) -> str:
        '''Get a name from the list.

        :param index: Index at which the name resides.
        :type index: int:
        :returns: A name residing at the index.
        :rtype: str'''
        if self.__container[index] is None:
            self.__populate_segment(index)
        return self.__container[index]


    def __getitem__(self, index: int):
        return self.get(index)

    def __len__(self):
        return NameList.SIZE

    @property
    def real_size(self) -> int:
        '''The "real size" of the list, i.e. the length non-None elements.'''
        size: int = 0
        for name in self.__container:
            if not name is None:
                size += 1
        return size
