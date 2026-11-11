import socket
import random
import mysql.connector # Library for connecting to a mysql service on this computer, sqlite3 is for local file databases
import ssl
import os
from pathlib import Path

def generate_key():
    chaset = "abcdefghijklmnopqrstuvwxyz123456789!@#$%^&*"
    k = ""
    for i in range(32):
        k += random.choice(chaset)
    return k

def create_database(cur):
    cur.execute("CREATE DATABASE mydatabase")

def show_databases(cur):
    cur.execute("SHOW DATABASES")
    for x in mycursor:
        print(x)

def create_table(cur):
    cur.execute("CREATE TABLE table_keys (id INT AUTO_INCREMENT PRIMARY KEY, col_key VARCHAR(255))")

def show_tables(cur):
    mycursor.execute("SHOW TABLES")
    for x in mycursor:
        print(x)

def insert_key(cur, ke):
    sql = "INSERT INTO table_keys (col_key) VALUES (%s)"
    val = (ke, )
    cur.execute(sql, val)

def send_key_to_client(cur, server_host, server_port):
    k = generate_key()
    insert_key(cur, k)
    print(f"Testing, key: {k}")

    s = socket.socket()
    s.bind((server_host, server_port))
    s.listen(1)

    print(f"Server is listening on {server_host}:{server_port}...")

    client , addr = s.accept()
    ssl_connection = ssl.wrap_socket(client, server_side=True, certfile="server.crt", keyfile="server.key")

    print(f"Connection established with {addr}")

    ssl_connection.sendall(k.encode("utf-8"))

    print("Key sent. Closing connection.")
    
    s.close()

def get_key_from_db(cur):
    cur.execute("SELECT col_key FROM table_keys")
    res = cur.fetchone()
    if res:
        return res[0]

def get_and_del_key(cur):
    k = get_key_from_db(cur)
    com = "DELETE FROM table_keys WHERE col_key = %s"
    cur.execute(com, (k, ))
    return k

dataBase = mysql.connector.connect(
  host ="localhost",                # Localhost for local connection
  user ="root",
  passwd ="n,GDgw+T/?:4dh#",
  database = "mydatabase" # Connect to the database mydatabase, it already
)

if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent) # Change directory to this script's directory

    mycursor = dataBase.cursor()
    # send_key_to_client(mycursor, "127.0.0.1", 8080) # generating and sending key to client through ssl
    # print(get_key_from_db(mycursor)) # print key without deleting
    # print(get_and_del_key(mycursor)) # print and delete key

    dataBase.commit()
    dataBase.close()