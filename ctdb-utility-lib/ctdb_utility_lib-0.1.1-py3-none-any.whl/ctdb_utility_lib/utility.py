import psycopg2
import re
from datetime import datetime
import sys

# check email format
def validate_email_format(email: str):
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    return re.search(regex, email) != None


# add a scan to the scans table in db
# returns -1 in case of an invalid email format
# throws exception in case of error accessing db
def add_scan(email: str, room_id: str):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # Cursor
    cur = conn.cursor()

    # Invalid email format
    if not validate_email_format(email):
        cur.close()
        conn.close()
        return -1

    # create current datetime obj
    current_date_time = datetime.now()

    # add scan info to scans table
    cur.execute(
        f"INSERT INTO scans (scan_id, person_email,scan_time,room_id) \
            VALUES (DEFAULT,'{email}',TIMESTAMP '{current_date_time}','{room_id}')"
    )

    # commit changes to db
    conn.commit()
    cur.close()
    conn.close()

    # success
    return 0


# retrieves scan info
# returns -1 if no match found
def get_scan(scan_id: int):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM scans WHERE scan_id = '{scan_id}'")

    # scan row
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# Checks if a person with the specified email exists in the people table
def exists_in_people(email: str, cur):

    cur.execute(f"SELECT COUNT(*) FROM PEOPLE WHERE email = '{email}'")

    result = cur.fetchone()

    # person exists in people table
    if result[0] != 0:
        return True
    # person doesn't exist in people table
    else:
        return False


# add person to people table
def add_person(first: str, last: str, id: int):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    # generate email
    email = first + last + str(datetime.now().timestamp()) + "@fake.com"

    # person exists in the people table
    if exists_in_people(email, cur):
        return None

    name = first + " " + last

    # add person info to people table
    cur.execute(
        f"INSERT INTO PEOPLE (email,name,student_id) \
        VALUES ('{email}','{name}',{id})"
    )

    # commit changes to db
    conn.commit()
    cur.close()
    conn.close()

    return email


# retrieves info for person with email from db
# returns -1 if no match found
def get_person(email: str):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM PEOPLE WHERE email = '{email}'")

    # person row
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# Checks if room with room_id already exists
def exists_in_rooms(room_id: str, cur):

    cur.execute(f"SELECT COUNT(*) FROM ROOMS WHERE room_id = '{room_id}'")

    result = cur.fetchone()

    # room exists in rooms table
    if result[0] != 0:
        return True
    # rooms doesn't exist in rooms table
    else:
        return False


# add room entry to room table
def add_room(room_id: str, capacity: int, building_name: str):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    if not (room_id and building_name):
        cur.close()
        conn.close()
        return -1

    # person exists in the people table
    if exists_in_rooms(room_id, cur):
        cur.close()
        conn.close()
        return -1

    # add room to rooms table
    cur.execute(
        f"INSERT INTO ROOMS (room_id,capacity,building_name) \
        VALUES ('{room_id}','{capacity}','{building_name}')"
    )

    # commit changes to db
    conn.commit()
    cur.close()
    conn.close()

    return 0


# retrieves room info
# returns -1 if no match found
def get_room(room_id: str):

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM ROOMS WHERE room_id = '{room_id}'")

    # room row
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# retrieves all users from people table
def get_all_users():

    # Conect to DB
    conn = psycopg2.connect(
        database="ctdb",
        user="postgres",
        password="capstone rocks",
        host="127.0.0.1",
        port="5432",
    )

    # cursor
    cur = conn.cursor()

    # execute query
    cur.execute(f"SELECT * FROM PEOPLE")

    # rows
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result
