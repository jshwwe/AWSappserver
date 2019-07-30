import socket
import sys
import threading
import pymysql
import pymysql.cursors

class socketlistener:
    def __init__(self, host, port, users, dbhost, dbuser, dbpass, dbname):

        self.host = host
        self.port = port
        self.users = users
        self.counter = 0

        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.host, self.port))

        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        self.socket.listen(self.users)

    def openport(self):
        while True:
            self.socket.listen(self.users)
            conn, addr = self.socket.accept()
            t = threading.Thread(target=self.acceptconn(conn, addr))
            t.run()


    def acceptconn(self, conn, addr):
        self.counter += 1
        print('\n\nConnected with ' + addr[0] + ' on port ' + str(addr[1]) + ' current connections: ' + str(self.counter) + "\n")

        request = ''

        while True:
            data = conn.recv(16).decode("utf-8")
            if data[-1] == ";":
                request = request + data[:-1]
                break
            request = request + data

        data_array = request.split("|")

        data_array = [str(item) for item in data_array]

        #Different types of queries
        if data_array[0] == 'register':
            sqlresult = self.registerquery(data_array[1], data_array[2], data_array[3], data_array[4])
            conn.sendall(str(sqlresult).encode('utf-8'))

        elif data_array[0] == 'login':
            sqlresult = self.loginquery(data_array[1], data_array[2])
            conn.sendall(str(sqlresult).encode('utf-8'))

        elif data_array[0] == 'book':
            sqlresult = self.bookquery(data_array[1], data_array[2], data_array[3], data_array[4], data_array[5])
            conn.sendall(str(sqlresult).encode('utf-8'))

        elif data_array[0] == 'mybookings':
            sqlresult = self.checkquery(data_array[1])
            conn.sendall(str(sqlresult[0]).encode('utf-8') + "|".encode('utf-8') + str(sqlresult[1])[:-1].encode('utf-8'))

        elif data_array[0] == 'cancel':
            sqlresult = self.cancelquery(data_array[1])
            conn.sendall(str(sqlresult).encode('utf-8'))
        else:
            pass

        conn.close()
        self.counter -= 1
        print('\nFinished connection with ' + addr[0] + ' on port ' + str(addr[1]) + ' current connections: ' + str(self.counter))


#Different query types methods

    def registerquery(self, username, password, password2, fullname):
        if password != password2:
            return 1

        try:
            print("== Initialising (register) DB connection ==")
            sqlconn = pymysql.connect(self.host, user=self.dbuser, password=self.dbpass, db=self.dbname,
                                  cursorclass=pymysql.cursors.DictCursor)

            with sqlconn.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `users` (`username`, `password`, `fullname`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, password, fullname))
            print("Created new user: (" + username + ")")
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            sqlconn.commit()
            sqlconn.close()
            print("== DB query successful ==")
            return 0

        except Exception as e:
            print("Error in DB connection or query " + str(e))
            print("== DB query unsuccessful ==")
            return 2

    def loginquery(self, username, password):
        try:
            print("== Initialising (login) DB connection ==")
            sqlconn = pymysql.connect(self.host, user=self.dbuser, password=self.dbpass, db=self.dbname,
                                      cursorclass=pymysql.cursors.DictCursor)

            with sqlconn.cursor() as cursor:
                # Authenticate user
                sql = "SELECT * FROM users WHERE username=%s and password =%s"
                cursor.execute(sql, (username, password))
            print("authenticated user: (" + username + ") with password: (" + password + ")")

            if cursor.rowcount <= 0:
                sqlconn.close()
                print("== DB query unsuccessful (incorrect user or pass) ==")
                return 1

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            else:
                sqlconn.commit()
                sqlconn.close()
                print("== DB query successful ==")
                return 0

        except Exception as e:
            print("Error in DB connection or query " + str(e))
            print("== DB query unsuccessful ==")
            return 2

    def bookquery(self, username, venue, activity, date, time):
        try:
            print("== Initialising (book) DB connection ==")
            sqlconn = pymysql.connect(self.host, user=self.dbuser, password=self.dbpass, db=self.dbname,
                                      cursorclass=pymysql.cursors.DictCursor)

            with sqlconn.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO bookings (activity, venue, time, date, user) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql, (activity, venue, date, time, username))
            print("Created booking for user: " + username + " || details: " + venue + " " + activity + " " + time + " " + date)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            sqlconn.commit()
            sqlconn.close()
            print("== DB query successful ==")
            return 0

        except Exception as e:
            print("Error in DB connection or query " + str(e))
            print("== DB query unsuccessful ==")
            return 2

    def checkquery(self, username):
        try:
            print("== Initialising (check) DB connection ==")
            sqlconn = pymysql.connect(self.host, user=self.dbuser, password=self.dbpass, db=self.dbname,
                                      cursorclass=pymysql.cursors.DictCursor)

            with sqlconn.cursor() as cursor:
                # Select record
                sql = "SELECT * FROM bookings WHERE user=%s"
                cursor.execute(sql, (username))
            print("Checking booking for user: " + username)

            fullquery = ''
            for row in cursor:
                fullquery += (str(row['activity']) + "!")
                fullquery += (str(row['venue']) + "!")
                fullquery += (str(row['time']) + "!")
                fullquery += (str(row['date']) + "!")
                fullquery += (str(row['bookingid']) + "|")

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            sqlconn.commit()
            sqlconn.close()
            print("== DB query successful ==")
            return 0, fullquery

        except Exception as e:
            print("Error in DB connection or query " + str(e))
            print("== DB query unsuccessful ==")
            return 2

    def cancelquery(self, bookid):
        try:
            print("== Initialising (cancel) DB connection ==")
            sqlconn = pymysql.connect(self.host, user=self.dbuser, password=self.dbpass, db=self.dbname,
                                      cursorclass=pymysql.cursors.DictCursor)

            with sqlconn.cursor() as cursor:
                # Create a new record
                sql = "DELETE FROM bookings WHERE bookingid=%s"
                cursor.execute(sql, (bookid))
            print("Canceling booking with id: " + bookid)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            sqlconn.commit()
            sqlconn.close()
            print("== DB query successful ==")
            return 0

        except Exception as e:
            print("Error in DB connection or query " + str(e))
            print("== DB query unsuccessful ==")
            return 2
