class ElementTagValue():
    def __init__(self, parent, name:str):
        self.parent = parent
        self.name = name
        self.__items_cache = None

    def __get__(self, instance, owner):
        return self.parent.subelements.findall(self.name)

    def __getitem__(self, item):
        if self.__items_cache == None:
            self.__items_cache = self.parent.findall(self.name)
            
        return self.__items_cache[item]

    def __len__(self):
        if self.__items_cache == None:
            self.__items_cache = self.parent.findall(self.name)
            
        return len(self.__items_cache)