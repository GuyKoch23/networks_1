import socket
import sys
from util import *
# Utility functions (sendall, send_message, recvall, recv_message are defined above)

def login(client_socket):
        while True:
            input_text = handle_input(client_socket)
            if input_text == "QUT":
                return "QUT"

            user = input_text.strip()
            while not user:
                input_text = handle_input(client_socket)
                if input_text == "QUT":
                    return "QUT"

            input_text = handle_input(client_socket)
            if input_text == "QUT":
                return "QUT"

            password = input_text.strip()
            while not password:
                input_text = handle_input(client_socket)
                if input_text == "QUT":
                    return "QUT"

                password = input_text.strip()
            
            command = ",".join(["AUTH", user, password])
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
    try:
        client_socket.connect((hostname, port))
    except Exception as e:
        print(f"Could not connect to the server due to error: {e}")
        return

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

            if(command.startswith("calculate: ")):
                command = f"CLC"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                elif response.startswith("ERR"):
                    print(response[4:])
                else:
                    print("response: " + response[4:] + ".")


            elif(command.startswith("max: ")):
                command = f"MAX"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                print(response[4:].strip())


            elif(command.startswith("factors: ")):
                command = f"FAC"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                elif response.startswith("ERR"):
                    print(response[4:])
                else:
                    print(response[4:].strip())


            else: # unknown command or (command.startswith("quit")):
                send_message(client_socket, "QUT")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_program()
