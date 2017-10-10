import argparse
import socket
import json
import sys
from select import select

"""The client program, on startup, registers a user with the server and then permits the user
 to send commands to the server and send messages to other clients"""

class ChatClient:
    __BUFFER_LENGTH = 65507
    __permitted_size = __BUFFER_LENGTH - 32
    __params = {"command": "signin"}
    __UDP_IP = "127.0.0.1"
    __messages = {"signin failed": "signin fail", "success": "Successfully signed in"}
    __response_message = {"signin failed": "User sign in failed, Please try other username",
                          "running": "client running on port", "running": ""}

    def __init__(self, args):
        self.username = args.username
        self.sIP = args.sIP
        self.UDP_PORT = int(args.sp)
        self.__params["username"] = self.username
        self.initialize_connect_socket(self.__params)
        # map that contains the functions which gets called with each input
        self.user_input = {"send": self.send_user_message,
                           "list": self.print_user_list}
        self.send_signin()

    def send_signin(self):
        self.sock.sendto(json.dumps(self.__params), (self.sIP, self.UDP_PORT))
        data, address = self.sock.recvfrom(self.__BUFFER_LENGTH)
        if "fail" in self.__messages[data]:
            print(self.__response_message[data])
            exit()
        else:
            print(self.__response_message["running"] + str(self.UDP_PORT))
            self.run_client_server()

    # initialize the socket connection
    def initialize_connect_socket(self, params):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.__UDP_IP, 0))

    # utility to print the received messages
    def print_received_message(self):
        data, address = self.sock.recvfrom(self.__BUFFER_LENGTH)
        message = json.loads(data)["message"]
        print("<- <From {0}:{1}:{2}>  " + message).format(address[0], address[1], json.loads(data)["user"])

    # a send and receive utility that sends message and receives a response
    def send_and_receive(self, message, ip, port):
        try:
            self.sock.sendto(message, (ip, port))
            return self.sock.recvfrom(self.__BUFFER_LENGTH)
        except Exception as e:
            print(e)

    # send the user a message based on the command on the command line.
    def send_user_message(self, input_array):
        u_input = input_array[0]
        if len(input_array) < 3:
            print("Invalid Input. Usage: " + u_input + " <username> <message>")
        else:
            data, address = self.send_and_receive(json.dumps({"command": "send", "user": input_array[1]}),
                                                  self.sIP,
                                                  self.UDP_PORT)
            if data == "null":
                print("The specified user is not logged in. please try again later.")
            else:
                temp = json.loads(data)
                message = ' '.join(input_array[2:])
                if len(message.encode('utf-8')) > self.__permitted_size:
                    while len(message.encode('utf-8')) > self.__permitted_size:
                        toSend = message[0:self.__permitted_size]
                        self.sock.sendto(json.dumps({"user": self.username,
                                                     "message": toSend}),
                                                    (temp[0], int(temp[1])))
                        message = message[self.__permitted_size:]
                    self.sock.sendto(json.dumps({"user": self.username,
                                                 "message": message}),
                                                 (temp[0], int(temp[1])))
                else:
                    self.sock.sendto(json.dumps({
                        "user": self.username, "message": ' '.join(input_array[2:])}),
                        (temp[0], int(temp[1])))

    # prints the list of users maintained in the server
    def print_user_list(self, input_array):
        if len(input_array) > 1:
            print("Invalid Input. Usage: list")
        else:
            data, address = self.send_and_receive(json.dumps({"command": "list"}), self.sIP, self.UDP_PORT)
            user = []
            parsed_user = json.loads(data)
            del parsed_user[args.username]
            if not parsed_user:
                print("<- No users signed in")
            else:
                for x in parsed_user:
                    user.append(x)
                print "<- Signed In Users: {0}".format(','.join(user))

    # runs the client program in a while loop and keeps fetching the user command baed on console input
    def run_client_server(self):
        try:
            inp = [sys.stdin, self.sock]
            # keep listening to the program console for the readiness. If stdin or socket is ready
            while True:
                print('+> ')
                input_list, output_list, exception_list = select(inp, [], [])
                for s in input_list:
                    if s == self.sock:
                        self.print_received_message()
                    elif s == sys.stdin:
                        input = raw_input()
                        input_array = input.split(" ")
                        u_input = input_array[0]
                        if u_input in self.user_input.keys():
                            self.user_input[u_input](input_array)
                        else:
                            print("Invalid Input. Command not supported")

        # handle keyboard interrupts, should terminate the user session if interrupt happens
        except KeyboardInterrupt:
            self.sock.sendto(json.dumps({"command": "terminate", "username": self.username}), (self.sIP, self.UDP_PORT))
            self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username for the chat client")
    parser.add_argument("-sip", "--sIP", help="The server IP to connect from the client")
    parser.add_argument("-sp", "--sp", help="The server port to connect to from the client")
    args = parser.parse_args()
    cs = ChatClient(args)
    print "Running chat server on port " + str(cs.portNumber)