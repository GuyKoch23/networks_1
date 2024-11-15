import socket
import sys

def main():
    hostname = '127.0.0.1' # sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = 12345 #int(sys.argv[2]) if len(sys.argv) > 2 else 1337
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((hostname, port))

    try:
        while True:
            # Receive data from server
            data = client_socket.recv(1024).decode()
            if not data:
                break  # Connection closed by the server
            
            # Print the server's message
            print(data, end="")

            # Server prompts for input (username, password, or command)
            if "Welcome" in data or "Password: " in data or "good to see you" in data or "response" in data:
                user_input = input("> ")
                client_socket.send(user_input.encode())

            # If the server says "Goodbye!", end the session
            if "Goodbye!" in data:
                break
    except KeyboardInterrupt:
        print("Client exiting...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
