def DevpostAuth(flask_app, socketio_app):
  from flask_socketio import emit
  from flask import request
  import sqlite3 as sl
  import requests
  import json
  import uuid

  try:
    con = sl.connect('uuids.db', check_same_thread=False)
    con.execute("""
      CREATE TABLE INFO (
        uuid TEXT,
        user TEXT
      );
    """)
    con.commit()
    con.close()
  except:
    pass

  @socketio_app.on("__req_uuid")
  def uuidhandle(msg):
    specuuid = str(uuid.uuid4())
    emit("__get_uuid", specuuid)

  @socketio_app.on("__req_user")
  def userhandle(msg):
    con = sl.connect('uuids.db', check_same_thread=False)
    try:
      if len(list(con.execute("SELECT * FROM INFO WHERE uuid == '" + msg + "'"))[0][1]) != 0:
        emit("__rec_user", list(con.execute("SELECT * FROM INFO WHERE uuid == '" + msg + "'"))[0][1])
    except IndexError:
      pass
    except:
      print("error")
    finally:
      con.close()

  @flask_app.route('/__log/<dauuid>')
  def logreq(dauuid):
    if requests.get("https://devpost.com/" + request.args.get('user')).status_code != 404:
      sql = 'INSERT INTO INFO (uuid, user) values(?, ?)'
      userinfostuff = str(json.dumps(json.loads(json.dumps(json.loads(requests.get("https://devpost-user-information-api.epiccodewizard2.repl.co/user/" + request.args.get('user')).text)))))
      data = [(dauuid, userinfostuff)]
      con = sl.connect('uuids.db', check_same_thread=False)
      cur = con.cursor()
      cur.execute(sql, *data)
      con.commit()
      con.close()
      return dauuid