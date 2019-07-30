import sys
from SocketListen import *

print("==================================")
print("==  Welcome to fake app server  ==")
print("==================================")

port = input("input port number: ")
users = input("input max number of simultaneous connections: ")
dbhost = input("input ip address of database server: ")
dbuser = input("input username of database server: ")
dbpass = input("input password of database server: ")
dbname = input("input dbname of database: ")

opensocket = socketlistener("127.0.0.1", int(port), int(users), dbhost, dbuser, dbpass, dbname)

print("\n===== App server is up and running! =====")

opensocket.openport()

