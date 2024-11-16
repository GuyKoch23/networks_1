#!/usr/bin/python3
import socket
import select
import sys


def load_users(filename):
    users = {}
    with open(filename, "r") as f:
        for line in f:
            username, password = line.strip().split("\t")
            users[username] = password
    return users


def handle_login(data, client_info, users):
    if client_info["state"] == "waiting_username":
        if data.startswith("User: "):
            client_info["username"] = data[6:].strip()
            client_info["state"] = "waiting_password"
            return "Enter your password\n"
        else:
            return "Close connection"
    elif client_info["state"] == "waiting_password":
        if data.startswith("Password: "):
            password = data[10:].strip()
            username = client_info["username"]
            if username in users and users[username] == password:
                client_info["authenticated"] = True
                client_info["state"] = "authenticated"
                return f"Hi {username}, good to see you.\n"
            else:
                client_info["state"] = "waiting_username"  # Reset to retry login
                return "Failed to login.\n"
        else:
            return "Close connection"


def handle_command(data):
    if data.startswith("calculate:"):
        return handle_calculate(data[11:])
    elif data.startswith("max:"):
        return handle_max(
            data[6:-1]
        )  # We start from 6 and not 4 because we want to skip ( after max:. Also we skip the last character which is a )
    elif data.startswith("factors:"):
        return handle_factors(
            data[9:]
        )  # We start from 9 and not 8 because we want to skip the space after factors:
    elif data == "quit":
        return "quit"
    else:
        print("Invalid command, disconnecting from socket")  # Page 3 line 2
        return "quit"


def handle_calculate(expression):
    try:
        x, op, y = expression.split(" ")
        x, y = int(x), int(y)
        if op == "+":
            result = x + y
        elif op == "-":
            result = x - y
        elif op == "*":
            result = x * y
        elif op == "/":
            result = round(x / y, 2)
        elif op == "^":
            result = x**y
        if result > 2**31 - 1 or result < -(2**31):
            return "error: result is too big\n"
        return f"response: {result}\n"
    except:
        return "quit"


def handle_max(numbers):
    try:
        nums = list(map(int, numbers.split(" ")))
        return f"the maximum is {max(nums)}\n"
    except:
        return "quit"


def handle_factors(number):
    try:
        x = int(number)  # Number must be an integer, otherwise we wouldn't have factors
        factors = []
        divisor = 2
        while x > 1:
            while x % divisor == 0:
                if divisor not in factors:
                    factors.append(divisor)
                x //= divisor
            divisor += 1
        return f"the prime factors of {number} are: {', '.join(map(str, factors))}\n"
    except:
        return "quit"


def main():
    if len(sys.argv) < 2:
        print("Incorrect usage of program...")
        return
    users_file = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 1337
    users = load_users(users_file)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()

    inputs = [server_socket]
    client_info = {}
    run = True

    while run:
        rlist, wlist, elist = select.select(inputs, [], [])
        for s in rlist:
            try:
                if s is server_socket:  # Socket is the server socket
                    conn, addr = (
                        server_socket.accept()
                    )  # It does not block since select will pick the server only if there is a connection waiting
                    print(f"Connected by {addr}")
                    conn.setblocking(0)
                    inputs.append(conn)
                    client_info[conn] = {
                        "state": "waiting_username",
                        "username": "",
                        "authenticated": False,
                    }
                    conn.send(b"Welcome! Please log in.\n")
                else:
                    data = s.recv(1024).decode().strip()
                    if not data:  # Connection closed by the client
                        inputs.remove(s)
                        s.close()
                        if s in client_info:
                            del client_info[s]
                    else:
                        if client_info[s]["authenticated"]:
                            response = handle_command(data)
                            if response == "quit":
                                inputs.remove(s)
                                s.close()
                                if s in client_info:
                                    del client_info[s]
                            else:
                                s.send(response .encode())
                        else:
                            response = handle_login(data, client_info[s], users)
                            if response == "Close connection":
                                print("Invalid input, closing connection")
                                inputs.remove(s)
                                s.close()
                                if s in client_info:
                                    del client_info[s]
                            else:
                                s.send(response.encode())
            except (ConnectionResetError, BrokenPipeError):
                print("Client abruptly closed the connection.")
                inputs.remove(s)
                s.close()
                if s in client_info:
                    del client_info[s]
            except:
                print("Error has occured. Exiting...")
                run = False
                break

    for sock in inputs:  # Close all sockets
        sock.close()
        if sock in client_info:
            del client_info[sock]


if __name__ == "__main__":
    main()
