import argparse
import socket
import json
"""Chat server which uses UDP protocol to send and receive message to preconfigured client. 
It is connection less protocol
"""

class ChatServer:
    # max size of the UDP buffer in bytes
    __BUFFER_LENGTH = 65507

    def __init__(self, PORT):
        self.PORT = int(PORT)
        # making the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.PORT))
        self.users = {}
        # list of functions in a map that gets called for each input type
        self.command_map = {"list": self.list_users,
                            "signin": self.sign_in,
                            "send": self.send_user_data,
                            "terminate": self.delete_user}
        self.receive_messages()

    # sign in function, gets called when the users first starts the client program
    def sign_in(self, parsed_data, address):
        user_name = parsed_data["username"]
        if self.users.get(parsed_data["username"]):
            self.send_messages("signin failed", address)
        else:
            print "signinig in " + user_name
            self.users[user_name] = address
            self.send_messages("success", address)

    # list utility that allows users to gets a list of all signed users
    def list_users(self, parsed_data, address):
        self.send_messages(json.dumps(self.users), address)

    def send_user_data(self, parsed_data, address):
        self.send_messages(json.dumps(self.users.get(parsed_data["user"])), address)

    def delete_user(self,  parsed_data, address):
        if self.users.get(parsed_data["username"]):
            del self.users[parsed_data["username"]]

    def receive_messages(self):
        while True:
            data, address = self.sock.recvfrom(self.__BUFFER_LENGTH)
            parsed_data = json.loads(data)
            self.command_map[parsed_data["command"]](parsed_data, address)

    # A commong send messaeg function
    def send_messages(self, message, ip):
        self.sock.sendto(message, ip)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--sp", help="Port to run the server on")
    args = parser.parse_args()
    print("Server Initialized ...")
    cs = ChatServer(args.sp)
