import sqlite3
import socket
import sys
import traceback
from threading import *
names_adresses = {}    #dict of names and adresses
#states = {}  #dict for states and adresses
clients=[]
data=[]
connections = list()
import pandas as pd



def addLection(nameOfLection,textOfLection, question1,question2,question3,question4):
    

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
        if rows[1] == password:
            print('Пароль верен')
            if rows[2] == 1:
                connection.sendall("--accepted_teacher--".encode("utf8"))
            else:
                connection.sendall("--accepted_student--".encode("utf8"))
        else:
            connection.sendall("--pass_incorrect--".encode("utf8"))
    """
    print(data)
    # Сначала ищем логин в списке
    for dat in data:
        if dat[0] == login:
            if dat[1]==password:
                print("Все ок, пусть заходит")
                if dat[2]==str('1'):
                    connection.sendall("--accepted_teacher--".encode("utf8"))
                else:
                    connection.sendall("--accepted_student--".encode("utf8"))
                break
            else:
                print("Взлом не пройдет")
                connection.sendall("--pass_incorrect--".encode("utf8"))

                break
        print("Взлом не пройдет")
        """
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
    """

    isIn = False
    for dat in data:
        if dat[0] == login:
            isIn = True
    if isIn:
        print("Логин уже существует")
        connection.sendall("--login_exists--".encode('utf-8'))
    else:
        data.append([login,password])
        f = open("data.txt", "a+")
        f.write("%s %s %s\n" % (login,password,isTeacher))
        f.close()
        print(data)

        if isTeacher == str('1'):
            connection.sendall("--accepted_teacher--".encode("utf8"))
        else:
            connection.sendall("--accepted_student--".encode("utf8"))
    """
    pass

def main():

    start_server()



def start_server():
    host = "192.168.1.101"
    port = 8889     # arbitrary non-privileged port

    global data
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(15)       # queue up to 5 requests
    print("Socket now listening")
    # При перезапуске сервера мы считываем данные из нашего файла
    with open(r"C:\Users\Ivan\PycharmProjects\serverOOP\data.txt") as f:
        data = f.read().splitlines()
    i = 0
    for line in data:
        data[i] = line.split(" ")
        i = i + 1
    f.close()

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

            addLection(textAndQuestions[0],textAndQuestions[1],textAndQuestions[2],textAndQuestions[3],textAndQuestions[4],textAndQuestions[5])

            print(textAndQuestions)
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