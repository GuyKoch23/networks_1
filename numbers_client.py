import socket
import sys
from util import *
# Utility functions (sendall, send_message, recvall, recv_message are defined above)

def login(client_socket):
        while True:
            user = input("").strip()[6:]
            while not user:
                user = input("").strip()[6:]
            
            password = input("").strip()[10:]
            while not password:
                password = input("").strip()[10:]

            command = " ".join(["AUTH", user, password])
            send_message(client_socket, command)
            response = recv_message(client_socket).strip()
            if response.startswith("SUC"):
                print(response[4:])
                return "SUC"
            if response.startswith("QUT"):
                return "QUT"
            print(response[4:])

def client_program():
    hostname = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((hostname, port))

    try:
        # Receive and display the welcome message
        welcome_message = recv_message(client_socket)
        print(welcome_message)

        login_res = login(client_socket)
        if login_res == "QUT":
            return

        # Start interacting with the server
        while True:
            command = input("").strip()
            if not command:
                continue

            if(command.startswith("calculate")):
                command = f"CLC"+command[10:]
                send_message(client_socket, command)
                response = recv_message(client_socket)
                print("response:" + response[4:] + ".")
                if(response.startswith("QUT")):
                    break

            elif(command.startswith("max")):
                command = f"MAX"+command[4:]
                send_message(client_socket, command)
                response = recv_message(client_socket)
                print(response[4:].strip())
                if(response.startswith("QUT")):
                    break

            elif(command.startswith("factors")):
                command = f"FAC"+command[8:]
                send_message(client_socket, command)
                response = recv_message(client_socket)
                print(response[4:].strip())
                if(response.startswith("QUT")):
                    break

            else: # unknown command or (command.startswith("quit")):
                send_message(client_socket, "QUT")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_program()
