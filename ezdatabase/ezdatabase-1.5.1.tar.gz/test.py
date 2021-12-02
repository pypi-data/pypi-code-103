from ezdatabase import db

database = db("MyDatabase.db")

database["ses"] = "sas"
print(database["ses"])