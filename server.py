import socket
import threading

# Server settings
HOST = '127.0.0.1'  # Server IP address
PORT = 8000  # Server port
FILE_PATH = 'data.txt'  # path to dictionary of passwords
KEEPALIVE_TIMEOUT = 60  # Keepalive timeout in seconds

# Clients dictionary to keep track of their progress
clients = {}

# Lock for clients dictionary to ensure thread-safety
clients_lock = threading.Lock()


def handle_client(conn, addr):
    """Handle individual client connections"""
    print(f'[SERVER] New client connected: {addr}')
    with clients_lock:
        clients[addr] = 0  # Initialize client's progress to 0

    while True:
        try:
            data = conn.recv(1024).decode()  # Receive data from client
            if not data:
                break
            # Process received data here
            # Update client's progress in clients dictionary

            with clients_lock:
                clients[addr] += 1
                print(f'[SERVER] Received data from {addr}: {data}')
                print(f'[SERVER] Progress of {addr}: {clients[addr]}')

            # Broadcast message to all clients when one client has found the answer
            if 'answer' in data:
                with clients_lock:
                    for client_addr in clients:
                        client_conn = clients[client_addr]
                        client_conn.sendall('[SERVER] Answer found by another client'.encode())

        except Exception as e:
            print(f'[SERVER] Error handling client {addr}: {e}')
            break

    # Remove client from clients dictionary when the connection is closed
    with clients_lock:
        clients.pop(addr)
    print(f'[SERVER] Client {addr} disconnected')
    conn.close()


def main():
    """Main server function"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)  # Allow up to 2 clients to connect --> need to change it to 6

    print(f'[SERVER] Server started on {HOST}:{PORT}')

    while True:
        conn, addr = server_socket.accept()
        conn.settimeout(KEEPALIVE_TIMEOUT)
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    main()
