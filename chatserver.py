# Created by: Megan Francis and Josh Schooley
# A multi threaded chat room server that accepts a User Name (within certain parameters), creates a thread for each user
# and allows users connected to communicate to each other through messaging everyone or a single person
# in the chat room. This chat room server also sends connection and disconnection messages with who
# connected/disconnected. Upon entering the chat room, you receive a list of users who are in the chat
# room with a private greeting message.

import thread
import socket
import datetime
import time

# Set the Port number and the IP of the host of the server
DEFAULT_PORT = 1337
HOST_IP = "192.168.1.37"

# Dictionary of Users in the chat room. example: {Username:SocketObject}
usernames = {}

usernamesLock = None

# Function to Login a user
def login(csocket, addr):
    try:
        # Gets the User Name entered and makes sure it's a valid User Name according to the protocol
        cusername = csocket.recv(1024)
        cusername = cusername[2:len(cusername)-2]
        if cusername == "" or len(cusername) > 16:
            csocket.send("2\r\n")
            csocket.close()
            exit(0)

        usernamesLock.acquire()
        if cusername in usernames:
            csocket.send("2\r\n")
            csocket.close()
            usernamesLock.release()
            exit(0)

        x = 0
        for i in cusername:
            x += 1
            if 47 < ord(i) < 58 or 64 < ord(i) < 91 or ord(i) == 95 or 96 < ord(i) < 123:
                if x == len(cusername):
                    usernames[cusername]= csocket  #addr
                    users = usernames.keys()
                    sendStr = "1 "
                    for j in users:
                        sendStr += j + ","
                    sendStr = sendStr[:len(sendStr)-1]
                    csocket.send(sendStr + " Welcome to the chatroom!\r\n")
                    usernamesLock.release()
                    thread.start_new_thread(parseNsend,(cusername,"10 "+cusername))
                    chatroom(cusername)

            else:
                csocket.send("2\r\n")
                csocket.close()
                usernamesLock.release()
                exit(0)
    except socket.error:
        csocket.close()

# Function that accepts messages from users and sends them to the correct places
def chatroom(cuser):
    csocket = usernames[cuser]
    # Intentional Disconnect variable
    intDisc = False
    try:
        # Waits to receive a message from user and creates a thread if the user isn't disconnecting.
        #  If User accidentally disconnects, it breaks from the while loop
        message = csocket.recv(1024)
        while message:
            if message[0] == "7":
                intDisc = True
                break
            thread.start_new_thread(parseNsend,(cuser,message))
            message = csocket.recv(1024)
    except socket.error:
        pass
    # Users who disconnect get sent a disconnect acknowledgement and the socket is closed
    usernamesLock.acquire()
    del usernames[cuser]
    usernamesLock.release()
    if intDisc:
        csocket.send("8\r\n")
    parseNsend(cuser,"7")
    csocket.close()
    exit(0)

# Function to parse what is sent to the server and respond accordingly
def parseNsend(cuser, message):
    curTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y:%m:%d:%H:%M:%S')
    # Response if the user sent a message to everyone in the chat room
    if message[0] == "3":
        if len(message)<515:
            message = message[1:]
            message = "5 " + cuser + " " + curTime + message + "\r\n"
            usernamesLock.acquire()
            for user in usernames:
                usernames[user].send(message)
            usernamesLock.release()
    # Response if the user sent a message to a single user
    elif message[0] == "4":
        message = message[2:]
        message = message[message.index(' ')+1:]
        sendTo = message[:message.index(' ')]
        message = message[message.index(' ') + 1:]
        if len(message)<513:
            message = "6 "+cuser + " " + sendTo + " " + curTime + " " + message + "\r\n"
            usernamesLock.acquire()
            usernames[cuser].send(message)
            if sendTo in usernames:
                usernames[sendTo].send(message)
            usernamesLock.release()
    # Response if the user sent a disconnect message. Tells the rest of the chat room that the user has left
    elif message[0] == "7":
        #Acquire Lock
        usernamesLock.acquire()
        for user in usernames:
            usernames[user].send("9 "+cuser + "\r\n")
        usernamesLock.release()
    # Response if the user connected. Tells the rest of the chat room that the user has joined
    elif message[0] == "1" and message[1] == "0":
        usernamesLock.acquire()
        for user in usernames:
            usernames[user].send(message + "\r\n")
        usernamesLock.release()
    exit(0)

# Main function to start the server socket and wait for connections. Creates a new thread for each connection
if __name__ == "__main__":
    serverSocket = socket.socket()
    serverSocket.bind((HOST_IP, DEFAULT_PORT))
    serverSocket.listen(5)
    usernamesLock = thread.allocate_lock()

    while True:
        try:
            c, addr = serverSocket.accept()
            thread.start_new_thread(login,(c,addr))
        except:
            print "Error: unable to start thread"