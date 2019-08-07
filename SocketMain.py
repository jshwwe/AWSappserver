import sys
from SocketListen import *

print("==================================")
print("==  Welcome to fake app server  ==")
print("==================================")

# port = input("input port number: ")
# users = input("input max number of simultaneous connections: ")
# dbhost = input("input ip address of database server: ")
# dbuser = input("input username of database server: ")
# dbpass = input("input password of database server: ")
# dbname = input("input dbname of database: ")

# opensocket = socketlistener("", int(port), int(users), dbhost, dbuser, dbpass, dbname)

config = extractconfig("/var/AWSappserver/config.txt")
opensocket = socketlistener("", int(config[0]), int(config[1]), config[2], config[3], config[4], config[5])

print("\n* App server is up and running! *")

opensocket.openport()

