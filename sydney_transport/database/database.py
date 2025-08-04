import mysql.connector

def connect(username, password):
    sydtp_db = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database="SydneyTransport"
    )

    return sydtp_db

def query(sql, params, db_connection) -> list[tuple]:
    with db_connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()