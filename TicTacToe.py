import tkinter as tk
import random

class ModeDialog(tk.Toplevel):
    def __init__(self, parent, on_choice):
        super().__init__(parent)
        self.title("Choose Game Mode")
        self.on_choice = on_choice
        self.geometry("300x120")
        self.resizable(False, False)
        self.grab_set()  # Make this dialog modal

        label = tk.Label(self, text="Choose game mode:", font=("Helvetica", 14))
        label.pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        pvp_btn = tk.Button(btn_frame, text="Player vs Player", width=15, command=self.choose_pvp)
        pvp_btn.pack(side="left", padx=10)

        pvc_btn = tk.Button(btn_frame, text="Player vs Computer", width=15, command=self.choose_pvc)
        pvc_btn.pack(side="right", padx=10)

    def choose_pvp(self):
        self.on_choice("pvp")
        self.destroy()

    def choose_pvc(self):
        self.on_choice("pvc")
        self.destroy()

class TicTacToeCanvas:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe Outline")

        self.canvas_size = 300
        self.cell_size = self.canvas_size // 3

        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False

        self.mode = None  # "pvp" or "pvc"
        self.current = "X"  # Always start with player X

        self.create_widgets()
        self.show_mode_dialog()

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.status_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        reset_btn = tk.Button(self.root, text="Reset", command=self.reset_game)
        reset_btn.pack(pady=10)

    def show_mode_dialog(self):
        self.dialog = ModeDialog(self.root, self.mode_chosen)
        self.root.wait_window(self.dialog)  # Wait for the dialog to close before continuing

    def mode_chosen(self, mode):
        self.mode = mode
        self.current = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.draw_grid()
        self.update_status(f"Player {self.current}'s turn")

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(1, 3):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.canvas_size, width=2, tags="grid")
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.canvas_size, y, width=2, tags="grid")

    def handle_click(self, event):
        if self.game_over or self.mode is None:
            return
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if self.board[row][col] == "":
            if self.mode == "pvc" and self.current == "O":
                # Ignore clicks when it's computer's turn
                return
            self.make_move(row, col, self.current)

            if self.mode == "pvc" and not self.game_over and self.current == "X":
                # After human move X, computer moves as O
                self.current = "O"
                self.root.after(300, self.computer_move)
            elif self.mode == "pvp" and not self.game_over:
                self.current = "O" if self.current == "X" else "X"
                self.update_status(f"Player {self.current}'s turn")

    def make_move(self, row, col, player):
        self.board[row][col] = player
        self.draw_mark(row, col, player)

        winner, line = self.check_winner()
        if winner:
            self.highlight_winning_line(line)
            self.update_status(f"Player {winner} wins!")
            self.game_over = True
            return
        elif self.is_board_full():
            self.update_status("It's a tie!")
            self.game_over = True
            return

    def draw_mark(self, row, col, player):
        x1 = col * self.cell_size + 20
        y1 = row * self.cell_size + 20
        x2 = (col + 1) * self.cell_size - 20
        y2 = (row + 1) * self.cell_size - 20
        if player == "X":
            # Draw blue cross
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill="blue", tags="mark")
            self.canvas.create_line(x1, y2, x2, y1, width=3, fill="blue", tags="mark")
        else:
            # Draw red circle
            self.canvas.create_oval(x1, y1, x2, y2, width=3, outline="red", tags="mark")

    def computer_move(self):
        if self.game_over:
            return
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.make_move(r, c, "O")

        if not self.game_over:
            self.current = "X"
            self.update_status(f"Player {self.current}'s turn")

    def check_winner(self):
        lines = []

        # Rows and columns
        for i in range(3):
            lines.append([(i, 0), (i, 1), (i, 2)])
            lines.append([(0, i), (1, i), (2, i)])

        # Diagonals
        lines.append([(0, 0), (1, 1), (2, 2)])
        lines.append([(0, 2), (1, 1), (2, 0)])

        for line in lines:
            vals = [self.board[r][c] for r, c in line]
            if vals[0] != "" and vals.count(vals[0]) == 3:
                return vals[0], line
        return None, None

    def highlight_winning_line(self, line):
        for r, c in line:
            x1 = c * self.cell_size
            y1 = r * self.cell_size
            x2 = (c + 1) * self.cell_size
            y2 = (r + 1) * self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#b3ffb3", outline="", tags="highlight")

        # Redraw marks on top
        self.canvas.delete("mark")
        for r in range(3):
            for c in range(3):
                if self.board[r][c] != "":
                    self.draw_mark(r, c, self.board[r][c])

    def is_board_full(self):
        return all(self.board[r][c] != "" for r in range(3) for c in range(3))

    def update_status(self, msg):
        self.status_label.config(text=msg)

    def reset_game(self):
        self.canvas.delete("mark")
        self.canvas.delete("highlight")
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.draw_grid()
        self.show_mode_dialog()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeCanvas(root)
    root.mainloop()
