import socket
import sys


def handle_user_response(client_socket):
    user_input = input("> ")
    client_socket.send(user_input.encode())
    if user_input == "quit":
        return "quit"  # Return quit to break the loop in main


def main():
    # hostname = "127.0.0.1"
    # port = 12345

    hostname = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337

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

            if (
                "Welcome" in data  # Server says welcome, prompt for username input
                or "Enter your password"
                in data  # Server asks for password, prompt for password input
                or "good to see you"
                in data  # User logged in successfully, prompt for commands
                or "response"
                in data  # Server responded to a command, prompt for another command
                or "the maximum is" in data
                or "the prime factors" in data
                or "error: result is too big"
                in data  # Server responded with an error, prompt for another command
                or "Failed to login"
                in data  # User failed to login, he should try again
            ):
                if handle_user_response(client_socket) == "quit":
                    break

    except:
        print("Error has occured client exiting...")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
