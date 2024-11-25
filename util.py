import struct


def sendall(sock, data):
    """Sends data to socket, ensures reliability"""
    total_sent = 0
    while total_sent < len(data):
        cur_sent = sock.send(data[total_sent:])
        if cur_sent == 0:
            raise RuntimeError("Socket connection broken...")
        total_sent += cur_sent


def send_message(sock, msg):
    """Sends message to socket, packing with 4-bytes length indicator number"""
    encoded_msg = msg.encode()
    msg_length = struct.pack("!I", len(encoded_msg))
    sendall(sock, msg_length + encoded_msg)


def recvall(sock, bytes_amount):
    """Receives all bytes_amount reliably from socket"""
    data = b""
    while len(data) < bytes_amount:
        cur_chunk = sock.recv(bytes_amount - len(data))
        if cur_chunk == b"":
            raise RuntimeError("Socket connection broken...")
        data += cur_chunk
    return data


def recv_message(sock):
    """Receives message from socket, unpacking 4-bytes length indicator number"""
    msg_length_bytes = recvall(sock, 4)
    msg_length = struct.unpack("!I", msg_length_bytes)[0]
    return recvall(sock, msg_length).decode()


def handle_input(sock):
    """Handles user input"""
    input_text = input("")
    if input_text == "quit":
        send_message(sock, "QUT")
        return "QUT"

    return input_text
