import cx_Oracle

# Hold all Oracle connections to prevent unnecessary duplicate connections
connections = {}

# If repeatedly querying for DB objects, the results (over 17,000 of them) can be cached
cached_objects = None


# Close all saved connections and other cached data
def closeout():
    """Close all open Oracle connections"""
    for key in list(connections.keys()):
        try:
            connections[key].close()
        except cx_Oracle.DatabaseError:
            pass
        del connections[key]

    # Remove any cached objects
    cached_objects = None
