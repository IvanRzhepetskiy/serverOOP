import sqlite3
import socket
import sys
import traceback
from threading import *
names_adresses = {}    #dict of names and adresses
#states = {}  #dict for states and adresses
clients=[]

connections = list()
import pandas as pd

def addMarkToDB(name_of_lection,connection,conn):

    pass
def sendExactLection(name_of_lection,mark,connection,conn):
    print(name_of_lection)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lections WHERE Name =?",(name_of_lection,))
    rows = cursor.fetchall()
    stringToSend = ''
    if len(rows[0][2])!= 0:
        print(rows[0][1])
        for data in rows[0]:
            stringToSend += str(data) + '!=,/ds'
    connection.sendall(("--lection_ready--" + stringToSend).encode("utf8"))

    pass
def sendLections(connection,conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lections")
    rows = cursor.fetchall()
    stringToSend = ''
    for row in rows:
        stringToSend+=str(row[0])+'!=,/ds'
    connection.sendall(("--lections--"+stringToSend).encode("utf8"))

    pass

def addLection(data_list,conn):
    cursor = conn.cursor()
    print(len(data_list))
    if len(data_list) == 5:
        cursor.execute("INSERT INTO Lections VALUES (?,?,?,?,?,?,?,?,?,?,?)", (data_list[0], data_list[1],data_list[2],data_list[3],None,None,None,None,None,None,None))
        conn.commit()
        print("Added Lection")
    elif len(data_list) == 7:
        cursor.execute("INSERT INTO Lections VALUES (?,?,?,?,?,?,?,?,?,?,?)", (data_list[0], data_list[1],data_list[2],data_list[3],data_list[4],data_list[5],None,None,None,None,None))
        conn.commit()
        print("Added Lection")
    elif len(data_list) == 9:
        cursor.execute("INSERT INTO Lections VALUES (?,?,?,?,?,?,?,?,?,?,?)", (data_list[0], data_list[1],data_list[2],data_list[3],data_list[4],data_list[5],data_list[6],data_list[7],None,None,None))
        conn.commit()
        print("Added Lection")
    elif len(data_list) == 11:
        cursor.execute("INSERT INTO Lections VALUES (?,?,?,?,?,?,?,?,?,?,?)", (data_list[0], data_list[1],data_list[2],data_list[3],data_list[4],data_list[5],data_list[6],data_list[7],data_list[8],data_list[9]))
        conn.commit()
        print("Added Lection")
    pass


def checkLogAndPassword(login, password,connection,conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authData WHERE Login=?", (login,))
    rows = cursor.fetchall()
    print('rows are printed')
    print(rows)
    if not rows:
        print('Неверный логин')
        #TODO Отправить неверный логин и возможность восстановить его
        #connection.sendall("--pass_incorrect--".encode("utf8"))
    else:
        print(rows[0][1])
        if rows[0][1] == password:
            print('Пароль верен')
            if rows[0][2] == 1:
                connection.sendall("--accepted_teacher--".encode("utf8"))
            else:
                connection.sendall("--accepted_student--".encode("utf8"))
        else:
            connection.sendall("--pass_incorrect--".encode("utf8"))

    pass

def registerNewUser(name,login,password,isTeacher,connection,conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authData WHERE Login=?", (login,))
    rows = cursor.fetchall()
    print(rows)
    if not rows:
        cursor.execute("INSERT INTO authData VALUES (?,?,?,?)", (login, password, int(isTeacher),name))
        if isTeacher == str('1'):
            connection.sendall("--accepted_teacher--".encode("utf8"))
        else:
            connection.sendall("--accepted_student--".encode("utf8"))
    else:
        print('Логин существует')
        connection.sendall("--login_exists--".encode('utf-8'))
    conn.commit()



    pass

def main():

    start_server()



def start_server():
    host = "localhost"
    port = 8889     # arbitrary non-privileged port
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(15)       # queue up to 15 requests
    print("Socket now listening")

    # infinite loop- do not reset for every requests
    while True:
        flag = True
        connection, address = soc.accept()

        print("our type")
        print(type(connection))
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)
        clients.append(address)


        try:
            Thread(target=client_thread, args=(connection, ip, port,address)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()

    soc.close()


def client_thread(connection, ip, port,adress , max_buffer_size = 80000):
    is_active = True
    conn = sqlite3.connect("mydatabase.db")
    while is_active:
        client_input = receive_input(connection, max_buffer_size)
        #ci = client_input.decode("utf8")
        QUITstring='--quit--'
        CONNECTstring = '--connect--'
        REGISTERstring = '--register--'
        ADDLECTIONstring = '--add_lection--'
        GETLECTIONstring = '--get_lections--'
        GETEXACTLECTONstring = '--get_exact_lection--'
        ADDMARKstring = '--add_mark--'
        if client_input.find(CONNECTstring) == 0:
            print("--------------NEW TRY--------------")
            print(client_input[11:])
            loginAndPassword = client_input[11:].split() #LoginAndPassword[0] IS LOGIN , [1] IS PASSWORD
            print(loginAndPassword)
            checkLogAndPassword(loginAndPassword[0], loginAndPassword[1],connection,conn)

        elif client_input.find(REGISTERstring)==0:
            nameLoginPassword = client_input[12:].split('!=,/ds')
            print(nameLoginPassword)
            registerNewUser(nameLoginPassword[0],nameLoginPassword[1],nameLoginPassword[2],nameLoginPassword[3], connection,conn)
            print("--------------NEW USER REGISTERED--------------")

        elif client_input.find(QUITstring) == 0:
            print("--------------CONNECTION CLOSED--------------")
            connection.sendall("--changeFlag--".encode("utf8"))
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False

        elif client_input.find(ADDLECTIONstring) == 0:
            print("--------------ADDING NEW LECTION--------------")
            textAndQuestions = client_input[15:].split('!=,/ds')
            print(textAndQuestions)
            addLection(textAndQuestions,conn)

            print(textAndQuestions)
        elif client_input.find(GETLECTIONstring) == 0:
            print("--------------READY TO SEND NEW LECTION--------------")
            sendLections(connection,conn)
        elif client_input.find(GETEXACTLECTONstring) == 0:
            print('---------------FINDING EXACT LECTION-----------------')
            lectionName = client_input[21:]
            sendExactLection(lectionName,connection,conn)
        elif client_input.find(ADDMARKstring) == 0:
            print('---------------ADDING NEW MARK-----------------')
            name_and_mark = client_input[12:].split('!=,/ds')
            addMarkToDB(name_and_mark[0],name_and_mark[1],connection,conn)

        else:
            print("Processed result: {}".format(client_input))
            connection.sendall("r-".encode("utf8"))

def receive_input(connection, max_buffer_size):

    print("RECIEVING")
    client_input = connection.recv(max_buffer_size)

    decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
    result = process_input(decoded_input)

    return result


def process_input(input_str):
    return ''+ str(input_str)


if __name__ == "__main__":
    main()