import sqlite3


class Database:
    def __init__(self, location):
        self.location = location
        self.connection = sqlite3.connect(self.location, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.executescript(
            """
                CREATE TABLE "status_codes" (
                    "code"	INTEGER NOT NULL,
                    "message"	TEXT NOT NULL DEFAULT 'Unknown',
                    PRIMARY KEY("code")
                );
                CREATE TABLE "hostnames" (
                    "name"	TEXT NOT NULL,
                    "id"	INTEGER NOT NULL,
                    PRIMARY KEY("id")
                );
                CREATE TABLE "requests" (
                    "id"	INTEGER NOT NULL,
                    "endpoint"	TEXT NOT NULL,
                    "request_datetime"	TEXT NOT NULL,
                    "response_time"	INTEGER NOT NULL,
                    "response_success"	INTEGER NOT NULL,
                    "test_id"	INTEGER NOT NULL,
                    "status_code_id"	INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );
                CREATE TABLE "tests" (
                    "code"	TEXT NOT NULL,
                    "user_count"	INTEGER NOT NULL,
                    "id"	INTEGER NOT NULL,
                    "start_datetime"	BLOB NOT NULL,
                    "end_datetime"	TEXT NOT NULL,
                    "cpu_usage"	INTEGER NOT NULL,
                    "ram_usage"	INTEGER NOT NULL,
                    "hostname_id"	INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT),
                    FOREIGN KEY("hostname_id") REFERENCES "hostnames"("id")
                );
            """
        )
        self.connection.commit()

    def store_test(self, code, user_count, start_datetime, end_datetime, cpu_usage, ram_usage, hostname_id):
        test_id = self.cursor.execute(
            """
                INSERT INTO
                tests(code, user_count, start_datetime, end_datetime, cpu_usage, ram_usage, hostname_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            , (code, user_count, start_datetime, end_datetime, cpu_usage, ram_usage, hostname_id)).lastrowid
        self.connection.commit()
        return test_id

    def store_request(self, endpoint, request_datetime, response_time, response_success, status_code, test_id):
        request_id = self.cursor.execute(
            """
                INSERT INTO
                requests(endpoint, request_datetime, response_time, response_success, status_code_id, test_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            , (endpoint, request_datetime, response_time, response_success, status_code, test_id)).lastrowid
        self.connection.commit()
        return request_id

    def store_hostname(self, name):
        hostname_id = self.cursor.execute(
            """
                INSERT INTO
                hostnames(name)
                VALUES (?)
            """
            , [name]).lastrowid
        self.connection.commit()
        return hostname_id

    def get_all_tests(self):
        return self.cursor.execute(
            """SELECT * FROM tests"""
        ).fetchall()

    def get_all_requests(self):
        return self.cursor.execute(
            """SELECT * FROM requests"""
        ).fetchall()

    def get_all_hostnames(self):
        return self.cursor.execute(
            """SELECT * FROM hostnames"""
        ).fetchall()

    def get_all_status_codes(self):
        return self.cursor.execute(
            """SELECT * FROM status_codes"""
        ).fetchall()
