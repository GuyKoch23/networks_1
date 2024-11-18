import struct


def sendall(sock, data):
    """Send all data to the socket reliably."""
    total_sent = 0
    while total_sent < len(data):
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total_sent += sent


def send_message(sock, message):
    """Send a message with a 4-byte length prefix."""
    encoded_message = message.encode()
    message_length = struct.pack("!I", len(encoded_message))  # 4-byte unsigned int
    sendall(sock, message_length + encoded_message)


def recvall(sock, num_bytes):
    """Receive an exact number of bytes."""
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if chunk == b"":
            raise RuntimeError("Socket connection broken")
        data += chunk
    return data


def recv_message(sock):
    """Receive a message with a 4-byte length prefix."""
    # Read the 4-byte length prefix
    message_length_bytes = recvall(sock, 4)
    message_length = struct.unpack("!I", message_length_bytes)[0]
    # Read the actual message
    return recvall(sock, message_length).decode()


def handle_input(sock):
    """Handle user input."""
    input_text = input("")
    if input_text == "quit":
        send_message(sock, "QUT")
        return "QUT"

    return input_text
