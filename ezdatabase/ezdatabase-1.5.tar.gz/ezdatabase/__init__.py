import json
from base64 import b64encode, b64decode

class db(list):
    def __init__(self, database_name):
        """Initializes the Database

        Args:
            database_name (str): The Name of the Database with ending

        Returns:
            None: __init__ function has to return None
        """
        self.database_name = database_name
        try:
            with open(database_name, "r") as f:
                json.load(f)
        except:
            with open(database_name, "w") as s:
                s.write("[]")
                s.close()
        return None

    def __getitem__(self, key):
        """Read Key from the Database

        Args:
            key (str, int, float): The Key to get read

        Returns:
            str, int, float, bytes: The Value of the Key
        """
        try:
            with open(self.database_name, "r") as f:
                js = json.load(f)
            for x in js:
                if x["key"] == key:
                    type_ = x["type"]
                    if type_ == "<class 'bytes'>":
                        return b64decode(str(x["value"]).encode('ascii')).decode('ascii')
                    return x["value"]
            return None
        except Exception as e:
            print(e)
            return False
    
    def __setitem__(self, key, value):
        """Writes / Updates a key to the Database

        Args:
            key (str, int, float): The Key to get written to
            value (str, int, float, bytes): The Value to get written
        
        Returns:
            Bool: True if the key was written / updated
        """
        type_ = type(value)
        if type_ == bytes:
            value = b64encode(value).decode('ascii')
        try:
            with open(self.database_name, "r") as f:
                js = json.load(f)
            for x in js:
                if x["key"] == key:
                    x["value"] = value
                    x["type"] = str(type_)
                    with open(self.database_name, "w") as f:
                        json.dump(js, f)
                    return True
            js.append({"key": key, "value": value, "type": str(type_)})
            with open(self.database_name, "w") as f:
                json.dump(js, f)
            return True
        except Exception as e:
            print(e)
            return False

    def __delitem__(self, key):
        """Deletes a key from the Database

        Args:
            key (str, int, float): The Key to get Deleted

        Returns:
            Bool: True if the key was deleted
        """
        try:
            deleted = False
            with open(self.database_name, "r") as f:
                js = json.load(f)
            for x in js:
                if x["key"] == key:
                    js.remove(x)
                    deleted = True
            with open(self.database_name, "w") as f:
                json.dump(js, f)
            return deleted
        except Exception as e:
            print(e)
            return False