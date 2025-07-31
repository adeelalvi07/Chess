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

    def on_tile_click(self, event):
        if self.turn != self.player_color:
            return

        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE

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

    def is_pawn_promotion(self, row, col):
        piece = self.board[row][col]
        return (piece == "P" and row == 0) or (piece == "p" and row == BOARD_SIZE - 1)

    def promote_pawn(self, row, col):
        new_piece = simpledialog.askstring("Promotion", "Promote to (Q, R, N, B):")
        if new_piece not in ["Q", "R", "N", "B"]:
            new_piece = "Q"  # Default promotion to Queen

        promoted_piece = new_piece if self.board[row][col].isupper() else new_piece.lower()
        self.board[row][col] = promoted_piece

        # Update the piece on the board visually
        self.canvas.delete(pieces[(row, col)])
        x, y = col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2
        pieces[(row, col)] = self.canvas.create_image(x, y, image=self.piece_images[promoted_piece], anchor='center')

    def check_game_state(self):
        if self.is_checkmate(self.opponent_color()):
            self._update_message(f"Checkmate! {self.player_color} wins.")
            self.stop_threads = True
            self.root.quit()
        elif self.is_stalemate(self.opponent_color()):
            self._update_message("Stalemate! Game Over.")
            self.stop_threads = True
            self.root.quit()
        elif self.is_king_in_check(self.opponent_color()):
            self._update_message("Check!")

    def is_checkmate(self, color):
        if not self.is_king_in_check(color):
            return False
        return not any(self.get_all_possible_moves(color))

    def is_stalemate(self, color):
        if self.is_king_in_check(color):
            return False
        return not any(self.get_all_possible_moves(color))

    def is_king_in_check(self, color):
        king_pos = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if (color == "White" and piece == "K") or (color == "Black" and piece == "k"):
                    king_pos = (row, col)
                    break
        if not king_pos:
            return False

        opponent_moves = self.get_all_possible_moves(self.opponent_color())
        return king_pos in opponent_moves

    def get_all_possible_moves(self, color):
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if (color == "White" and piece.isupper()) or (color == "Black" and piece.islower()):
                    all_moves.extend(self.get_piece_moves(row, col))
        return all_moves

    def get_piece_moves(self, row, col):
        valid_moves = []
        self.selected_piece = self.board[row][col]
        self.selected_pos = (row, col)
        self.highlight_moves(row, col)
        valid_moves = self.highlighted_tiles[:]
        self.clear_highlights()
        self.selected_piece = None
        self.selected_pos = None
        return valid_moves

    def highlight_moves(self, row, col):
        self.clear_highlights()
        piece = self.board[row][col]

        if piece.lower() == "p":
            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1

            next_row = row + direction
            if 0 <= next_row < BOARD_SIZE and self.board[next_row][col] == " ":
                self.highlight_tile(next_row, col)
                two_steps_row = row + 2 * direction
                if row == start_row and self.board[two_steps_row][col] == " ":
                    self.highlight_tile(two_steps_row, col)

            if col > 0 and self.board[next_row][col - 1] != " " and self.board[next_row][col - 1].islower() != piece.islower():
                self.highlight_tile(next_row, col - 1)
            if col < BOARD_SIZE - 1 and self.board[next_row][col + 1] != " " and self.board[next_row][col + 1].islower() != piece.islower():
                self.highlight_tile(next_row, col + 1)

        elif piece.lower() == "r":
            self.highlight_straight_lines(row, col, piece)

        elif piece.lower() == "b":
            self.highlight_diagonals(row, col, piece)

        elif piece.lower() == "q":
            self.highlight_straight_lines(row, col, piece)
            self.highlight_diagonals(row, col, piece)

        elif piece.lower() == "n":
            moves = [
                (row + 2, col + 1), (row + 2, col - 1),
                (row - 2, col + 1), (row - 2, col - 1),
                (row + 1, col + 2), (row + 1, col - 2),
                (row - 1, col + 2), (row - 1, col - 2),
            ]
            for r, c in moves:
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and (self.board[r][c] == " " or self.board[r][c].islower() != piece.islower()):
                    self.highlight_tile(r, c)

        elif piece.lower() == "k":
            moves = [
                (row + 1, col), (row - 1, col),
                (row, col + 1), (row, col - 1),
                (row + 1, col + 1), (row - 1, col - 1),
                (row + 1, col - 1), (row - 1, col + 1)
            ]
            for r, c in moves:
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and (self.board[r][c] == " " or self.board[r][c].islower() != piece.islower()):
                    self.highlight_tile(r, c)

    def highlight_straight_lines(self, row, col, piece):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.board[r][c] == " ":
                        self.highlight_tile(r, c)
                    elif self.board[r][c].islower() != piece.islower():
                        self.highlight_tile(r, c)
                        break
                    else:
                        break
                else:
                    break

    def highlight_diagonals(self, row, col, piece):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.board[r][c] == " ":
                        self.highlight_tile(r, c)
                    elif self.board[r][c].islower() != piece.islower():
                        self.highlight_tile(r, c)
                        break
                    else:
                        break
                else:
                    break

    def highlight_tile(self, row, col):
        tile = self.canvas.find_withtag(f"tile_{row}_{col}")
        if tile:
            self.canvas.itemconfig(tile, outline="blue", width=3)
            self.highlighted_tiles.append((row, col))

    def move_piece(self, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst

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

    def send_move(self, src, dst):
        move = f"MOVE {chr(97 + src[1])}{8 - src[0]} {chr(97 + dst[1])}{8 - dst[0]}"
        self.socket.send(move.encode())

    def process_opponent_move(self, src, dst):
        src_col, src_row = ord(src[0]) - 97, 8 - int(src[1])
        dst_col, dst_row = ord(dst[0]) - 97, 8 - int(dst[1])
        self.move_piece((src_row, src_col), (dst_row, dst_col))
        self.turn = self.player_color

    def clear_highlights(self):
        for row, col in self.highlighted_tiles:
            tile = self.canvas.find_withtag(f"tile_{row}_{col}")
            if tile:
                self.canvas.itemconfig(tile, outline="")
        self.highlighted_tiles = []

    def on_closing(self):
        self.stop_threads = True
        if hasattr(self, 'receive_thread'):
            self.receive_thread.join()
        self.socket.close()
        self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    client = ChessClient()
    client.run()