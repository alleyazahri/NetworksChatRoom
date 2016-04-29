# Created by: Joshua Schooley & Megan Francis
# This program is a multi-threaded chat room application. It takes the IP address
# of a chat server as an argument. When the GUI is loaded it accepts a username
# (within certain parameters) and populates the chatroom GUI with the current users
# in the chatroom and a welcome message sent from the server.

from Tkinter import *

import Tkinter
import socket
import sys
import thread
import tkMessageBox
import datetime
import time

# Design Variables
CHAT_FONT = ("Verdana", 10)
TIME_STAMP_FONT = ("Verdana", 8)

DEFAULT_PORT = 1337


class ChatClient:

    # This function initializes a login window and attempts to connect to a chat server
    def __init__(self, serverIP, login, chatroom):
        # The next y-position in the canvas window to place text
        global yPosition
        yPosition = 10

        # Variables managing users & where messages should be sent
        self.userSelect = "All Users"
        self.userArray = []

        self.serverIP = serverIP

        # Tkinter window variables & their configurations
        self.login = login
        self.login.title("Login")
        self.chatroom = chatroom
        self.chatroom.title("Chat Room")
        self.chatroom.protocol('WM_DELETE_WINDOW',self.closeChat)

        # Login Instructions
        Label(self.login, text="Please Choose a Username, see help").grid(row=0, column=0, columnspan=2, padx=5, pady=(5,0), sticky="EW")
        Label(self.login, text="for correct character usage.").grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="EW")

        # Login Variables
        self.username = Entry(self.login)
        tryLogin = Button(self.login, text = "Login", command = self.loginWin)
        self.username.grid(row = 2, column = 0, columnspan = 2, padx = 15, pady = 5, sticky="EW")
        tryLogin.grid(row = 3, column = 0, padx = 5, pady = 5)
        self.login.bind("<Return>", self.loginWin)

        # Help Button for Login Window
        help = Button(self.login, text="Help", command = self.loginHelp)
        help.grid(row = 3, column = 1, padx = 5, pady = 5)

    # Function for logging into the chat room
    def loginWin(self, enter=None):
        # Global positioning variables
        global yPosition
        global userIndex

        # Establish socket
        self.s = socket.socket()
        self.s.connect((self.serverIP, DEFAULT_PORT))

        # Save & Send username to server
        self.curUser = self.username.get()
        self.s.send("0 "+ self.curUser+ "\r\n")

        # Wait for server reply
        reply = self.s.recv(1024)

        # Server accepted username
        if reply[0] == "1":
            # Parse reply into a list of users and a welcome message
            reply = reply[2:]
            self.userArray = reply[:reply.index(" ")]
            self.userArray = self.userArray.split(",")
            reply = reply[reply.index(" ")+1:]

            # Get rid of the Login Window
            self.login.destroy()

            # Set up the Chat Room Canvas & Scroll Bar
            self.yScroll = Scrollbar(self.chatroom)
            self.chatWindow = Canvas(self.chatroom,yscrollcommand = self.yScroll.set, bg = "#284942", height = 400, width = 550, relief=SUNKEN, scrollregion = (0, 0, 550, 400))
            self.yScroll.config(command=self.chatWindow.yview)
            self.yScroll.grid(row=0, column=1, sticky="NSW", rowspan = 3, pady=5)
            self.chatWindow.grid(row = 0, column = 0, rowspan = 3, padx = (5,0), pady=5)

            # Send Server Welcome Message to Canvas
            self.chatWindow.create_text(10, yPosition, anchor ="nw", text = reply, fill="#00FF00", font=CHAT_FONT)
            yPosition += 20

            # Information about using the user list box
            Label(self.chatroom,text = "To send private message, click").grid(row=0 ,column=4, padx=(0,10), pady=(10,0), sticky="S")
            Label(self.chatroom,text = "the user you wish to send to.").grid(row=1, column=4, padx=(0,10), pady=(0,10), sticky="N")

            # Set Up a User List
            self.userList = Listbox(self.chatroom)
            self.userList.insert(1,"All Users")
            userIndex = 2
            for i in self.userArray:
                self.userList.insert(userIndex,i)
                userIndex += 1
            self.userList.grid(row=2, column=4, padx = (0,10), pady = 5, sticky = "NS")
            self.userList.bind("<<ListboxSelect>>", self.privChat)

            # Set up the Message Box for user entry
            self.textBox = Entry(self.chatroom, width=92)
            self.textBox.grid(row = 3, column = 0, padx = (5,0), pady = (0,5), sticky = "W")

            # Send button
            self.sendText = Button(self.chatroom, text = "Send", command = self.toServer)
            self.sendText.grid(row = 3, column = 1, pady = (0,5), columnspan = 2, sticky = "W")

            # Let 'Enter' work as 'Send' Does
            self.chatroom.bind("<Return>", self.toServer)

            # Start a new thread to receive messages from server
            thread.start_new_thread(self.fromServer, ())
        # Server declined username
        else:
            # Let client know the username is bad
            fail = Label(self.login, text = "Bad Username, see Help for more information.")
            fail.grid(row = 4, column = 0, columnspan = 2)

            # Close the socket connection with the server
            self.s.close()

    # This function will close the socket and destroy the chatroom window
    def closeChat(self):
        try:
            self.s.close()
        except:
            pass
        self.chatroom.destroy()

    # Changes the userSelect variable to let the program know
    # which users to send messages to.
    def privChat(self, userlistbox):

        # Get the value selected in the user list box
        temp = userlistbox.widget
        index = int(temp.curselection()[0])
        value = temp.get(index)

        # Set the variable
        self.userSelect = value

    # Displays a help message from the Login Window
    def loginHelp(self):
        tkMessageBox.showinfo("Help", "Things that are allowed: \r\n -Numbers 0-9 \r\n "
                                      "-Special Character Allowed: _ \r\n -English letters both upper and lower case\r"
                                      "\n -Max Length: 16 Characters")

    # Receives Messages from the server
    def fromServer(self):
        # Global Position Variables
        global yPosition
        global userIndex

        # Wait for a message until program closes
        while True:
            # Receive message from server
            received = self.s.recv(1024)

            # Remove the \r\n at end of messagee
            received = received[:len(received)-2]

            # Message to be sent to chat window
            message = ""

            # Received a general message
            if received[0] == "5":
                # Parse
                received = received[2:]
                fromUser = received[:received.index(" ")]

                # Change color for font to a green!
                if fromUser == self.curUser:
                    color = "#00FFCC"
                else:
                    color = "#B7C8B6"

                # Compile message to send to chat window
                message = fromUser + ":  " + received[len(fromUser)+21:]

            # Received a private message
            elif received[0] == "6":
                # Parse message for from user and message
                received = received[2:]
                fromUser = received[:received.index(" ")]
                received = received[received.index(" ")+1:]
                received = received[received.index(" ")+21:]

                # Compile message to send to chat window
                message = fromUser + ":  " + received

                # Change color for font to another green!
                color = "#BCED91"

            # Received disconnect message from server
            elif received[0] == "9":
                # Parse message for the user who has left
                fromUser = received[2:]

                # Compile message to send to chat room
                message = fromUser + " has left."

                # Update user list in chat window
                self.userList.delete(0,END)
                if fromUser in self.userArray:
                    self.userArray.remove(fromUser)
                userIndex = 2
                self.userList.insert(1,"All Users")
                for i in self.userArray:
                    self.userList.insert(userIndex,i)
                    userIndex += 1

                # Change color for font to a server green (A.K.A. very bright)
                color = "#00FF00"

            # Received a connect message from server
            elif received[0] == "1" and received[1] == "0":
                # Parse message for user connected
                fromUser = received[3:]

                # Compile message to send to chat room
                message = fromUser + " has joined."

                # Update user list in chat window
                if fromUser != self.curUser:
                    self.userList.insert(userIndex, fromUser)
                    self.userArray.append(fromUser)
                    userIndex += 1
                # Change color for font to a server green (A.K.A. very bright)
                color = "#00FF00"

            # Send message to chat window
            self.chatWindow.create_text(10, yPosition, anchor="nw", text=message, fill=color, font=CHAT_FONT, width=480)

            # Create a time stamp & send to chat window
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M')
            self.chatWindow.create_text(500, yPosition, anchor="nw", text=timestamp, fill=color, font=TIME_STAMP_FONT)

            # Increment location for next line of text
            yPosition += 20
            if len(message) > 74:
                yPosition += (20 * (len(message) / 74))

            # Increase scrollbar area and move it to the botton
            if yPosition > 400:
                self.chatWindow.config(scrollregion = (0, 0, 550, yPosition + 5))
                self.chatWindow.yview_moveto(yPosition)

    # Sends messages to the server
    def toServer(self, enter=None):
        # Grab message from the entry box
        toSend = self.textBox.get()

        # Decide if it is private or public based on what is selected
        if self.userSelect == "All Users":
            self.s.send("3 "+toSend+"\r\n")
        else:
            self.s.send("4 " + self.curUser + " " + self.userSelect + " " + toSend + "\r\n")

        # Clear the entry in the text box
        self.textBox.delete(0, "end")

# Accepts IP address command line
if __name__=="__main__" :
    # Create the login and chat room Tkinter windows
    login = Tkinter.Tk()
    chatroom = Tkinter.Tk()

    # Create a ChatClient object
    thing = ChatClient(sys.argv[1], login, chatroom)

    # Let the windows loop!
    login.mainloop()
    chatroom.mainloop()