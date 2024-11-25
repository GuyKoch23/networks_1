#!/usr/bin/python3
import socket
import sys
from util import * # sendall, send_message, recvall, recv_message

def login(client_socket):
        while True:
            input_text = handle_input(client_socket)
            if input_text == "QUT": # clients quits the session, sent to server in handle_input
                return "QUT"

            user = input_text.strip()
            while not user: # empty input
                input_text = handle_input(client_socket)
                if input_text == "QUT":
                    return "QUT"

                user = input_text.strip()

            input_text = handle_input(client_socket)
            if input_text == "QUT": # not empty, checking last time not quiting, end-case covered
                return "QUT"

            password = input_text.strip()
            while not password:
                input_text = handle_input(client_socket)
                if input_text == "QUT": # client can quit on login process
                    return "QUT"

                password = input_text.strip()
            
            command = ",".join(["AUTH", user, password]) # auth header indication for server
            send_message(client_socket, command)
            response = recv_message(client_socket).strip()
            if response.startswith("SUC"): # login successful
                print(response[4:])
                return "SUC"
            if response.startswith("ERR"): # fatal error in login, cannot continue, printing to user
                print("An error occurred, connection closed...")
                return "QUT"
            if response.startswith("QUT"): # server quits, quiting
                return "QUT"
            print(response[4:]) # other message, trying login again

def client_program():
    hostname = sys.argv[1] if len(sys.argv) > 1 else "localhost" # optional field
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337       # optional field

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((hostname, port))
    except Exception as e:
        print(f"Could not connect to the server due to error: {e}")
        return

    try:
        welcome_message = recv_message(client_socket) # receive and print welcome
        print(welcome_message)

        login_res = login(client_socket)
        if login_res == "QUT" or login_res == "ERR":
            return # already printed to user and sent to server

        # Start interacting with the server, all good
        while True:
            command = input("").strip()
            if not command: # empty command
                continue

            # calculation command
            if(command.startswith("calculate")):
                command = f"CLC"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                elif response.startswith("CER"): # handled-calculation error
                    print(response[4:])
                elif response.startswith("ERR"): # unhandled-claulation error
                    print("An error occurred, connection closed...")
                    break
                else:
                    print("response: " + response[4:] + ".") # success calculation

            # maximization command
            elif(command.startswith("max")):
                command = f"MAX"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                if response.startswith("MER"):
                    print("An error occurred, connection closed...")
                    break
                elif response.startswith("ERR"): # unhandled-claulation error
                    print("An error occurred, connection closed...")
                    break
                print(response[4:].strip()) # success maximization

            # factorization command
            elif(command.startswith("factors")):
                command = f"FAC"+command
                send_message(client_socket, command)
                response = recv_message(client_socket)
                if(response.startswith("QUT")):
                    break
                elif response.startswith("FER"): # handled-factorization error
                    print(response[4:].strip())
                elif response.startswith("ERR"): # unhandled-factorization error
                    print("An error occurred, connection closed...")
                    break
                else:
                    print(response[4:].strip()) # success factorization
            
            # quiting command
            elif(command == "quit"):
                send_message(client_socket, "QUT")
                break

            else: # unknown command or (command.startswith("quit")):
                send_message(client_socket, "QUT")
                print("An error occurred, connection closed...")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_program()
