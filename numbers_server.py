#!/usr/bin/python3
import socket
import select
import struct
from util import * # sendall, send_message, recvall, recv_message
import sys


def load_users(filename):
    '''loading users from file'''
    users = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                username, password = line.strip().split("\t")
                users[username] = password
        return users
    except Exception as e:
        print(f"Error: {e}") # problem with users file
        return


def handle_max(numbers):
    '''calculate max(numbers)'''
    try:
        nums = list(map(int, numbers.split(" ")))
        if len(nums) > 2**31 - 1:
            return "QUT"
        return f"the maximum is {max(nums)}"
    except:
        return "MER"


def handle_factors(number):
    '''calcuate the factors of input number'''
    try:
        x = int(number)
        if x < 0:
            return "FER Can't calculate factors of a negative number"
        if x == 0:
            return "FER Can't calculate factors of 0"
        if x == 1:
            return "FER Can't calculate factors of 1"
        factors = []
        divisor = 2
        while x > 1:
            while x % divisor == 0:
                if divisor not in factors:
                    factors.append(divisor)
                x //= divisor
            divisor += 1
        return f"the prime factors of {number} are: {', '.join(map(str, factors))}"
    except:
        return "ERR"


def send_welcome_message(client_socket):
    '''Sending welcome message to client'''
    welcome_message = "Welcome! Please log in."
    send_message(client_socket, welcome_message)


def handle_client_message(client_socket, message, authenticated_clients, users):
    '''client message handling'''
    if client_socket not in authenticated_clients:
        if message.startswith("AUTH"): # authentication message
            parts = message.split(',')
            if len(parts) == 3:
                username, password = parts[1], parts[2]
                if not username.startswith("User: ") or not password.startswith("Password: "):
                    print("Invalid login format, disconnecting from socket")
                    return "ERR"

                username = username[6:]
                password = password[10:]
                if username in users and users[username] == password:
                    authenticated_clients[client_socket] = username
                    return f"SUC Hi {username}, good to see you."
                else:
                    return "FLR Failed to login."
            else:
                return "ERR"
        else:
            return "ERR"
    else:
        if message.startswith("CLCcalculate: "): # calculation message
            parts = message.split()
            if len(parts) == 4:
                op1, operation, op2 = int(parts[1]), parts[2], int(parts[3])
                try:
                    if operation == "+":
                        result = op1 + op2
                    elif operation == "-":
                        result = op1 - op2
                    elif operation == "*":
                        result = op1 * op2
                    elif operation == "/":
                        result = round(op1 / op2, 2)
                    elif operation == "^":
                        result = op1**op2
                    else:
                        print("Invalid operation, disconnecting from socket")
                        del authenticated_clients[client_socket]
                        return "QUT"
                    
                    if result > 2**31 - 1 or result < -2**31:
                        return "CER error: result is too big"
                    return f"RES {result}"
                except Exception as e:
                    return f"ERR {str(e)}"
            else:
                return "ERR"

        elif message.startswith("MAXmax: "): # maximization message
            res = handle_max(message[9:-1])
            if res == "QUT" or res == "MER":
                del authenticated_clients[client_socket]
                return res
            return f"MRS {res}"

        elif message.startswith("FACfactors: "): # factorization message
            res = handle_factors(
                message[12:]
            )
            if res.startswith("FER"):
                return res
            if res == "QUT" or res.startswith("ERR"):
                del authenticated_clients[client_socket]
                return res
            return f"FRS {res}"

        elif message == "QUT":
            del authenticated_clients[client_socket]
            return "QUT"
        else:
            del authenticated_clients[client_socket]
            return "ERR" # invalid command


def start_server(users, port, authenticated_clients):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()
    inputs = [server_socket]
    run = True

    print(f"Server listening on port {port}")

    clients = {}

    while run:
        readable, _, _ = select.select(inputs, [], [])

        for sock in readable:
            try:
                if sock == server_socket:
                    client_socket, client_address = server_socket.accept()
                    print(f"New connection from {client_address}")
                    client_socket.setblocking(0)
                    inputs.append(client_socket)
                    clients[client_socket] = b""
                    send_welcome_message(client_socket)  # Send welcome message
                else:
                    try:
                        message = recv_message(sock)
                        response = handle_client_message(
                            sock, message.strip(), authenticated_clients, users
                        )
                        if response == "QUT" or response == "ERR":
                            send_message(sock, response)
                            inputs.remove(sock)
                            if sock in authenticated_clients:
                                del authenticated_clients[sock]
                            if sock in clients:
                                del clients[sock]
                            sock.close()
                        else:
                            send_message(sock, response)
                    except Exception as e:
                        print(f"Client error: {e}")
                        inputs.remove(sock)
                        if sock in authenticated_clients:
                            del authenticated_clients[sock]
                        if sock in clients:
                            del clients[sock]
                        sock.close()
            except (ConnectionResetError, BrokenPipeError):
                print("Client abruptly closed the connection.")
                inputs.remove(sock)
                sock.close()
                if sock in authenticated_clients:
                    del authenticated_clients[sock]
            except:
                print("Error has occured. Exiting...")
                run = False
                break

    for sock in inputs:  # Close all sockets
        sock.close()
        if sock in authenticated_clients:
            del authenticated_clients[sock]


def main():
    if len(sys.argv) < 2:
        print("Incorrect usage of program...")
        return
    users_file = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 1337
    users = load_users(users_file)
    if not users:
        print("Error with users file...")
        return
    authenticated_clients = {}
    start_server(users, port, authenticated_clients)


if __name__ == "__main__":
    main()
