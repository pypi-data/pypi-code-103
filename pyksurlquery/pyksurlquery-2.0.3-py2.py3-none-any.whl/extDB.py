from pymongo import MongoClient


def extDBGetCollection():
    return MongoClient('localhost', 27017)['extDB']['murl']


def extDBTranscodeType(mtype):
    d = {1: 31, 2: 4, 3: 75, 4: 29, 5: 39, 6: 25, 7: 10, 8: 8193, 9: 2, 10: 42, 11: 27}
    try:
        etype = d[mtype]
    except KeyError:
        etype = -1
    return etype


def extDBWrite(mtype, line, db):
    et = extDBTranscodeType(mtype)
    try:
        db.insert({"url": line, "etype": et})
    except Exception as e:
        pass


def extDBInit():
    collection = extDBGetCollection()
    for mtype in range(1, 12):
        fname = 'data/c'+str(mtype)+'.dat'
        with open(fname, 'r') as fp:
            for line in fp:
                url = line.strip()
                extDBWrite(mtype, url, collection)


def extDBClear():
    collection = extDBGetCollection()
    collection.remove()


def extDBQuery(url):
    et = -1
    try:
        collection = extDBGetCollection()
        item = collection.find_one({"url": url})
        et = item['etype']
    except:
        pass
    return et


if __name__ == '__main__':
    extDBClear()
    extDBInit()

