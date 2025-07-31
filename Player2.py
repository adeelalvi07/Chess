import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk  # Add this import for image handling

# Chessboard setup
BOARD_SIZE = 8
TILE_SIZE = 80
pieces = {}

# Network setup
HOST = "192.168.1.6"  # Replace with the server's IP address
PORT = 5555

class ChessClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Online Chess")
        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE * TILE_SIZE, height=BOARD_SIZE * TILE_SIZE)
        self.canvas.pack()

        self.board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.player_color = None
        self.turn = None

        self.selected_piece = None
        self.selected_pos = None
        self.highlighted_tiles = []
        self.stop_threads = False  # Flag for stopping threads

        self.piece_images = self.load_images()  # Load images
        self.setup_board()
        self.bind_events()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

    def load_images(self):
        images = {}
        # White pieces
        images['K'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/1.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['Q'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/2.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['P'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/6.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['B'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/3.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['N'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/4.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['R'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/5.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        # Black pieces
        images['k'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/1a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['q'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/2a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['p'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/6a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['b'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/3a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['n'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/4a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        images['r'] = ImageTk.PhotoImage(Image.open("C:/Uni/3rd/Computer Networks project/5a.png").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS))
        return images

    def setup_board(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                color = "white" if (i + j) % 2 == 0 else "#D2B48C"  # Dull brown color
                self.canvas.create_rectangle(j * TILE_SIZE, i * TILE_SIZE,
                                             (j + 1) * TILE_SIZE, (i + 1) * TILE_SIZE,
                                             fill=color, tags=f"tile_{i}_{j}")
        self.initialize_pieces()

    def initialize_pieces(self):
        for i in range(BOARD_SIZE):
            self.add_piece("P", 6, i)  # White pawns
            self.add_piece("p", 1, i)  # Black pawns

        order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for i, piece in enumerate(order):
            self.add_piece(piece, 7, i)
            self.add_piece(piece.lower(), 0, i)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_tile_click)

    def add_piece(self, piece, row, col):
        x, y = col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2
        pieces[(row, col)] = self.canvas.create_image(x, y, image=self.piece_images[piece], anchor='center')
        self.board[row][col] = piece

    def flip_coordinates(self, row, col):
        return BOARD_SIZE - 1 - row, BOARD_SIZE - 1 - col

    def connect_to_server(self):
        try:
            self.socket.connect((HOST, PORT))
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to connect to server: {e}")
            self.root.quit()

    def receive_data(self):
        while not self.stop_threads:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break

                if "You are" in data:
                    self.player_color = "White" if "White" in data else "Black"
                    self.turn = "White" if self.player_color == "White" else "Black"
                    self._update_message(f"You are {self.player_color}.")
                elif "MOVE" in data:
                    _, src, dst = data.split()
                    self.process_opponent_move(src, dst)
                elif "Your turn" in data:
                    self.turn = self.player_color
                    self._update_message("Your turn.")
                elif "CHECK" in data:
                    self._update_message("Check!")
                elif "CHECKMATE" in data:
                    self._update_message(f"Checkmate! {self.opponent_color()} wins. Game Over.")
                    self.stop_threads = True
                    self.root.quit()
                elif "STALEMATE" in data:
                    self._update_message("Stalemate! Game Over.")
                    self.stop_threads = True
                    self.root.quit()
            except Exception as e:
                self._update_message(f"Connection lost: {e}")
                break

    def opponent_color(self):
        return "White" if self.player_color == "Black" else "Black"

    def _update_message(self, message):
        self.root.after(0, lambda: messagebox.showinfo("Game Info", message))

    def move_piece(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst

        # Flip coordinates for Player 2
        if self.player_color == "Black":
            src_row, src_col = self.flip_coordinates(src_row, src_col)
            dst_row, dst_col = self.flip_coordinates(dst_row, dst_col)

        piece = self.board[src_row][src_col]
        if (dst_row, dst_col) in pieces:
            self.canvas.delete(pieces[(dst_row, dst_col)])
            del pieces[(dst_row, dst_col)]

        self.board[dst_row][dst_col] = piece
        self.board[src_row][src_col] = " "

        self.canvas.delete(pieces[(src_row, src_col)])
        del pieces[(src_row, src_col)]

        x, y = dst_col * TILE_SIZE + TILE_SIZE // 2, dst_row * TILE_SIZE + TILE_SIZE // 2
        pieces[(dst_row, dst_col)] = self.canvas.create_image(x, y, image=self.piece_images[piece], anchor='center')

    def process_opponent_move(self, src, dst):
        src_col, src_row = ord(src[0]) - 97, 8 - int(src[1])
        dst_col, dst_row = ord(dst[0]) - 97, 8 - int(dst[1])

        # Flip coordinates for Player 2
        if self.player_color == "Black":
            src_row, src_col = self.flip_coordinates(src_row, src_col)
            dst_row, dst_col = self.flip_coordinates(dst_row, dst_col)

        self.move_piece((src_row, src_col), (dst_row, dst_col))
        self.turn = self.player_color

    def on_tile_click(self, event):
        if self.turn != self.player_color:
            return

        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE

        # Flip coordinates for Player 2
        if self.player_color == "Black":
            row, col = self.flip_coordinates(row, col)

        if self.selected_piece:
            if (row, col) in [(highlight[0], highlight[1]) for highlight in self.highlighted_tiles if len(highlight) > 1]:
                self.move_piece(self.selected_pos, (row, col))  # Perform the move
                self.send_move(self.selected_pos, (row, col))  # Send move to the server
                self.clear_highlights()
                self.selected_piece = None
                self.selected_pos = None
                self.turn = None  # End turn

                if self.is_pawn_promotion(row, col):
                    self.promote_pawn(row, col)

                self.check_game_state()
            else:
                self.clear_highlights()
                self.selected_piece = None
                self.selected_pos = None
        elif self.board[row][col] != " ":
            piece = self.board[row][col]
            if (piece.isupper() and self.player_color == "White") or (piece.islower() and self.player_color == "Black"):
                self.selected_piece = piece
                self.selected_pos = (row, col)
                self.highlight_moves(row, col)

    def send_move(self, src, dst):
        if self.player_color == "Black":
            src = self.flip_coordinates(*src)
            dst = self.flip_coordinates(*dst)

        move = f"MOVE {chr(97 + src[1])}{8 - src[0]} {chr(97 + dst[1])}{8 - dst[0]}"
        self.socket.send(move.encode())

    def clear_highlights(self):
        for row, col in self.highlighted_tiles:
            tile = self.canvas.find_withtag(f"tile_{row}_{col}")
            if tile:
                self.canvas.itemconfig(tile, outline="")
        self.highlighted_tiles = []

    def highlight_tile(self, row, col):
        tile = self.canvas.find_withtag(f"tile_{row}_{col}")
        if tile:
            self.canvas.itemconfig(tile, outline="blue", width=3)
            self.highlighted_tiles.append((row, col))

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.stop_threads = True
        if hasattr(self, 'receive_thread'):
            self.receive_thread.join()
        self.socket.close()
        self.root.destroy()

if __name__ == "__main__":
    client = ChessClient()
    client.run()
