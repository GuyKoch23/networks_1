import socket
import select
import sys
import pandas as pd

def load_users(filename):
    # df = pd.read_csv(filename, sep=' ', header=None)
    # users = dict(zip(df[0], df[1]))
    # print(users)
    users = {}
    with open(filename, 'r') as f:
        for line in f:
            print(line.strip().split())
            username, password = line.strip().split()
            users[username] = password
    return users

def handle_login(data, client_info, users):
    if client_info["state"] == "waiting_username":
        if data.startswith("User: "):
            client_info["username"] = data[6:].strip()
            client_info["state"] = "waiting_password"
            return "Password: "
        else:
            return "Error: Please enter User: <username>\n"
    elif client_info["state"] == "waiting_password":
        if data.startswith("Password: "):
            password = data[9:].strip()
            username = client_info["username"]
            if username in users and users[username] == password:
                client_info["authenticated"] = True
                client_info["state"] = "authenticated"
                return f"Hi {username}, good to see you.\n"
            else:
                client_info["state"] = "waiting_username"  # Reset to retry login
                return "Failed to login\n"
        else:
            return "Error: Please enter Password: <password>\n"

def handle_command(data):
    if data.startswith("calculate:"):
        return handle_calculate(data[10:])
    elif data.startswith("max:"):
        return handle_max(data[4:])
    elif data.startswith("factors:"):
        return handle_factors(data[8:])
    elif data == "quit":
        return "Goodbye!\n"
    else:
        return "Error: Invalid command\n"

def handle_calculate(expression):
    try:
        x, op, y = expression.split()
        x, y = int(x), int(y)
        if op == '+':
            result = x + y
        elif op == '-':
            result = x - y
        elif op == '*':
            result = x * y
        elif op == '/':
            result = round(x / y, 2)
        elif op == '^':
            result = x ** y
        if result > 2**31 - 1 or result < -2**31:
            return "error: result is too big\n"
        return f"response: {result}\n"
    except:
        return "error: invalid calculation\n"

def handle_max(numbers):
    try:
        nums = list(map(int, numbers.split()))
        return f"the maximum is {max(nums)}\n"
    except:
        return "error: invalid max calculation\n"

def handle_factors(number):
    try:
        x = int(number)
        factors = []
        divisor = 2
        while x > 1:
            while x % divisor == 0:
                factors.append(divisor)
                x //= divisor
            divisor += 1
        return f"the prime factors of {number} are: {', '.join(map(str, factors))}\n"
    except:
        return "error: invalid factors calculation\n"

def main():
    if len(sys.argv) < 2:
        print("Incorrect usage of program...")
        return
    users_file = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 1337
    users = load_users(users_file)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen()
    print(f"Server listening...")

    inputs = [server_socket]
    client_info = {}

    while True:
        readable, _, _ = select.select(inputs, [], [])
        for s in readable:
            if s is server_socket:
                conn, addr = server_socket.accept()
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
                if not data:
                    inputs.remove(s)
                    s.close()
                    del client_info[s]
                else:
                    if client_info[s]["authenticated"]:
                        response = handle_command(data)
                        if response == "Goodbye!\n":
                            s.send(response.encode())
                            inputs.remove(s)
                            s.close()
                            del client_info[s]
                        else:
                            s.send(response.encode())
                    else:
                        response = handle_login(data, client_info[s], users)
                        s.send(response.encode())

if __name__ == "__main__":
    main()
