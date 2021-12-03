from ..data import DataObject as DATA

def raise_dataobject(dataobject):
    if not isinstance(dataobject, DATA):
        raise Exception(f"not an {DATA}")
    dataobject.check()
    return dataobject