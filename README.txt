Computer Networks
Spring 2016

Chat room Server and Client README

This is a chat room server and client that use the same protocol so they can run smoothly together.

The server needs to be set to the IP address of the machine that will be running it. Also, if you would like to run it on a specific port, you can change this as well. Both of these variables are near the top of program for ease of access. Once set, you can run the server and it will listen at that port and take any incoming clients and service them on a seperate thread.

The client needs one parameter which is the IP of the host machine running the server. If you changed the port on the server then you must match the port that was changed. This is in the variable "PORT" near the top of the program. Once running, it will ask you for a login user name. There is a help button if you need to know what is allowed in a user name. You may hit the "Login" button or hit the "Enter" key to check if your user name was accepted. When your user name is accepted, the chat room will populate with the main window where text will appear, a list of users on the right side with instructions on how to send a private message to someone, an input bar at the bottom for typing and a send button to send your message. You may also hit the "Enter" key to send a message.

Every message received is a different shade of green, with the server announcements being neon green, a message from you to all being a teal, private messages are in a dull green and messages from other users to all users is in an almost gray green.

To leave the server, simply hit the "X" at the top and close the chat window. This will close the sockets on both the client and the server side. 

Welcome to our Chat Room and have fun! =D