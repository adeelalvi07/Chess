import socket
import threading

# Server setup
HOST = "192.168.1.6"  # Replace with the server's IP address
PORT = 5555

clients = []
turn = "White"
lock = threading.Lock()

# Game state management
def is_checkmate_or_stalemate():
    # Placeholder for checkmate/stalemate detection logic
    return ""

def handle_client(conn, player_id):
    global turn
    print(f"New connection from Player {player_id}")
    conn.sendall(f"You are {turn}".encode())
    turn = "Black" if turn == "White" else "White"

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Received from Player {player_id}: {data}")
            with lock:
                game_status = is_checkmate_or_stalemate()
                if game_status:
                    broadcast(game_status, None)
                else:
                    broadcast(data, conn)
    except Exception as e:
        print(f"Error with player {player_id}: {e}")
    finally:
        print(f"Closing connection with Player {player_id}")
        conn.close()
        clients.remove(conn)
        if len(clients) < 2:
            print("Shutting down server.")
            exit(0)

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.sendall(message.encode())
            except:
                client.close()
                clients.remove(client)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)
        print(f"Server started on {HOST}:{PORT}")

        while len(clients) < 2:
            conn, addr = server_socket.accept()
            print(f"Player {len(clients)} connected from {addr}")
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, len(clients) - 1)).start()

        print("Game started. No longer accepting connections.")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()