Simple python program to implement chat application in the form of a client and server program using UDP protocol
1) server.py - Implements simple chat application using sockets in python. The server listens to incoming requests
   from clients, and performs actions based on the command that it receives from the client.

2. client.py - The client side of the chat application. It registers a user with the server on startup and permits the
    user to send commands to the server and send messages to other clients

Following are the
commands to compile and run the code
Server side
    python server.py -sp 9001 (python server.py -sp <port>)

Client side
    python client.py -u rohit -sip 127.0.0.1 -sp 9001 (python client.py <IP Address> <Port Number>)

Requirements:
Python 3.5.1
Dependencies
1. argparse
2. socket
3. select
4. json
5. sys
