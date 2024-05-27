import copy
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
DEFAULT_WIDTH = 700  # Chiều rộng mặc định của cửa sổ 
DEFAULT_HEIGHT = 700  # Chiều cao mặc định của cửa sổ 

BG_COLOR = "#1CAAA8"  # Màu nền
LINE_COLOR = "#179187"  # Màu của các đường kẻ 
CIRC_COLOR = "#EFE7C8"  # Màu của hình tròn (O)
CROSS_COLOR = "#424242"  # Màu của hình chữ thập (X)

# Class Board định nghĩa bảng caro
class Board:
    def __init__(self, size):
        self.size = size
        self.squares = np.zeros((size, size))
        self.marked_sqrs = 0
        self.max_item_win = 5 if size > 5 else 3

    def final_state(self, marked_row, marked_col):
        # Kiểm tra trạng thái kết thúc của trò chơi
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # vertical, horizontal, main diagonal, anti-diagonal
        for dr, dc in directions:
            count = 0
            for delta in range(-self.max_item_win + 1, self.max_item_win):
                r = marked_row + delta * dr
                c = marked_col + delta * dc
                if 0 <= r < self.size and 0 <= c < self.size:
                    if self.squares[r][c] == self.squares[marked_row][marked_col]:
                        count += 1
                        if count == self.max_item_win:
                            return self.squares[marked_row][marked_col]
                    else:
                        count = 0
        return 0

    def mark_sqr(self, row, col, player):
        # Đánh dấu ô bởi người chơi
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        # Kiểm tra ô trống
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        # Lấy danh sách các ô trống
        empty_sqrs = [(r, c) for r in range(self.size) for c in range(self.size) if self.empty_sqr(r, c)]
        return empty_sqrs

    def is_full(self):
        # Kiểm tra xem bảng có đầy đủ chưa
        return self.marked_sqrs == self.size * self.size

# Class AI định nghĩa trí tuệ nhân tạo
class AI:
    def __init__(self, level=1, player=2):
        self.level = level # Mức độ khó của AI, 0 là ngẫu nhiên, 1 là sử dụng thuật toán Alpha-Beta
        self.player = player  # Xác định người chơi là AI (giá trị 2)

    def rnd(self, board):
        # Chọn ngẫu nhiên một ô trống
        empty_sqrs = board.get_empty_sqrs() # Lấy danh sách các ô trống
        return random.choice(empty_sqrs) # Chọn ngẫu nhiên một ô trong danh sách các ô trống

    def alpha_beta(self, board, alpha, beta, maximizing, depth=3):
        # Thuật toán Alpha-Beta để tìm nước đi tốt nhất
        if depth == 0 or board.is_full(): # Kiểm tra độ sâu hoặc nếu bảng đã đầy
            return self.evaluate_board(board), None  # Trả về giá trị đánh giá của bảng và không có nước đi

        best_move = None # Khởi tạo nước đi tốt nhất
        if maximizing: # Nếu đang tối đa hóa
            max_eval = -99999 # Khởi tạo giá trị đánh giá tối thiểu
            empty_sqrs = board.get_empty_sqrs()  # Lấy danh sách các ô trống

            for (row, col) in empty_sqrs:  # Duyệt qua các ô trống
                temp_board = copy.deepcopy(board) # Tạo bản sao của bảng
                temp_board.mark_sqr(row, col, 1) # Đánh dấu ô bởi người chơi 1
                eval, _ = self.alpha_beta(temp_board, alpha, beta, False, depth - 1)  # Đệ quy với người chơi 2
                if eval > max_eval: # Nếu giá trị đánh giá lớn hơn giá trị tối đa hiện tại
                    max_eval = eval # Cập nhật giá trị tối đa
                    best_move = (row, col) # Cập nhật nước đi tốt nhất
                alpha = max(alpha, eval)  # Cập nhật alpha
                if alpha >= beta: # Cắt tỉa Alpha-Beta
                    break
            return max_eval, best_move # Trả về giá trị tối đa và nước đi tốt nhất
        else: # Nếu đang tối thiểu hóa
            min_eval = 99999 # Khởi tạo giá trị đánh giá tối đa
            empty_sqrs = board.get_empty_sqrs()  # Lấy danh sách các ô trống
 
            for (row, col) in empty_sqrs: # Duyệt qua các ô trống
                temp_board = copy.deepcopy(board) # Tạo bản sao của bảng
                temp_board.mark_sqr(row, col, self.player)  # Đánh dấu ô bởi người chơi AI
                eval, _ = self.alpha_beta(temp_board, alpha, beta, True, depth - 1)  # Đệ quy với người chơi 1
                if eval < min_eval: # Nếu giá trị đánh giá nhỏ hơn giá trị tối thiểu hiện tại
                    min_eval = eval  # Cập nhật giá trị tối thiểu
                    best_move = (row, col) # Cập nhật nước đi tốt nhất
                beta = min(beta, eval)  # Cập nhật beta
                if beta <= alpha: # Cắt tỉa Alpha-Beta
                    break
            return min_eval, best_move # Trả về giá trị tối thiểu và nước đi tốt nhất

    def evaluate_position(self, board, row, col, player):
        # Đánh giá vị trí trên bảng
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            for delta in range(-3, 1):
                r = row + delta * dr
                c = col + delta * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.squares[r][c] == player:
                        count += 1
                    elif board.squares[r][c] != 0:
                        count = 0
                        break
                else:
                    count = 0
                    break
            score += count
        return score

    def evaluate_board(self, board):
        # Đánh giá toàn bộ bảng
        score = 0
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == 1:
                    score += self.evaluate_position(board, row, col, 1)
                else:
                    score -= self.evaluate_position(board, row, col, 2)
        return score

    def eval(self, main_board):
        # Đánh giá và chọn nước đi tốt nhất
        if self.level == 0:
            # Nếu mức độ của AI là 0 (ngẫu nhiên), chọn một ô trống ngẫu nhiên
            move = self.rnd(main_board)
        else:
            # Nếu mức độ của AI không phải là 0, sử dụng thuật toán Alpha-Beta để tìm nước đi tốt nhất
            eval_value, move = self.alpha_beta(main_board, -99999, 99999, True, 3)
            # In ra vị trí ô được chọn và giá trị đánh giá của nước đi đó
            print(f'AI đã chọn đánh dấu ô ở vị trí {move} với giá trị đánh là: {eval_value}')
        return move

# Class Game định nghĩa giao diện và logic của trò chơi
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classic Caro")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        self.canvas = tk.Canvas(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.size = 5
        self.sqsize = DEFAULT_WIDTH // self.size
        self.radius = self.sqsize // 4
        self.offset = self.sqsize // 4
        self.line_width = self.offset // 2
        self.circ_width = self.offset // 2
        self.cross_width = self.offset // 2

        self.board = Board(self.size)
        self.ai = AI()
        self.player = 1
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()
        self.create_menu()
        self.canvas.bind("<Button-1>", self.handle_click)

    def create_menu(self):
        # Tạo menu chọn chế độ và kích thước bảng
        menu_frame = tk.Frame(self)
        menu_frame.pack(side=tk.TOP)

        mode_label = tk.Label(menu_frame, text="Mode:")
        mode_label.pack(side=tk.LEFT)

        self.mode_var = tk.StringVar(value="ai")
        pvp_radio = tk.Radiobutton(menu_frame, text="Player vs Player", variable=self.mode_var, value="pvp", command=self.change_gamemode)
        pvp_radio.pack(side=tk.LEFT)
        ai_radio = tk.Radiobutton(menu_frame, text="Player vs AI", variable=self.mode_var, value="ai", command=self.change_gamemode)
        ai_radio.pack(side=tk.LEFT)

        size_label = tk.Label(menu_frame, text="Board Size:")
        size_label.pack(side=tk.LEFT)

        self.size_var = tk.IntVar(value=5)
        size5_radio = tk.Radiobutton(menu_frame, text="5x5", variable=self.size_var, value=5, command=self.change_size)
        size5_radio.pack(side=tk.LEFT)
        size7_radio = tk.Radiobutton(menu_frame, text="7x7", variable=self.size_var, value=7, command=self.change_size)
        size7_radio.pack(side=tk.LEFT)
        size11_radio = tk.Radiobutton(menu_frame, text="11x11", variable=self.size_var, value=11, command=self.change_size)
        size11_radio.pack(side=tk.LEFT)

        reset_button = tk.Button(menu_frame, text="Reset", command=self.reset)
        reset_button.pack(side=tk.LEFT)

    def change_gamemode(self):
        # Thay đổi chế độ chơi
        self.gamemode = self.mode_var.get()

    def change_size(self):
        # Thay đổi kích thước bảng
        self.size = self.size_var.get()
        self.sqsize = DEFAULT_WIDTH // self.size
        self.radius = self.sqsize // 4
        self.offset = self.sqsize // 4
        self.line_width = self.offset // 2
        self.circ_width = self.offset // 2
        self.cross_width = self.offset // 2
        self.reset()

    def show_lines(self):
        # Hiển thị các đường kẻ trên bảng
        self.canvas.delete("all")
        for col in range(1, self.size):
            x = col * self.sqsize
            self.canvas.create_line(x, 0, x, DEFAULT_HEIGHT, fill=LINE_COLOR, width=self.line_width)
        for row in range(1, self.size):
            y = row * self.sqsize
            self.canvas.create_line(0, y, DEFAULT_WIDTH, y, fill=LINE_COLOR, width=self.line_width)

    def draw_fig(self, row, col):
        # Vẽ ký hiệu X hoặc O
        if self.player == 1:
            start_desc = (col * self.sqsize + self.offset, row * self.sqsize + self.offset)
            end_desc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.sqsize - self.offset)
            self.canvas.create_line(*start_desc, *end_desc, fill=CROSS_COLOR, width=self.cross_width)

            start_asc = (col * self.sqsize + self.offset, row * self.sqsize + self.sqsize - self.offset)
            end_asc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.offset)
            self.canvas.create_line(*start_asc, *end_asc, fill=CROSS_COLOR, width=self.cross_width)
        elif self.player == 2:
            center = (col * self.sqsize + self.sqsize // 2, row * self.sqsize + self.sqsize // 2)
            self.canvas.create_oval(center[0] - self.radius, center[1] - self.radius,
                                    center[0] + self.radius, center[1] + self.radius,
                                    outline=CIRC_COLOR, width=self.circ_width)

    def make_move(self, row, col):
        # Thực hiện nước đi
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        # Chuyển lượt chơi
        self.player = self.player % 2 + 1

    def is_over(self, row, col):
        # Kiểm tra trò chơi kết thúc hay chưa
        result = self.board.final_state(row, col)
        if result != 0:
            winner = "Player 1" if result == 1 else "Player 2"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            return True
        elif self.board.is_full():
            messagebox.showinfo("Game Over", "It's a draw!")
            return True
        return False

    def reset(self):
        # Đặt lại trò chơi
        self.board = Board(self.size)
        self.ai = AI()
        self.player = 1
        self.running = True
        self.show_lines()

    def handle_click(self, event):
        # Xử lý sự kiện click chuột
        col = event.x // self.sqsize
        row = event.y // self.sqsize
        if self.board.empty_sqr(row, col) and self.running:
            self.make_move(row, col)
            if self.is_over(row, col):
                self.running = False
            if self.gamemode == 'ai' and self.player == self.ai.player and self.running:
                row, col = self.ai.eval(self.board)
                self.make_move(row, col)
                if self.is_over(row, col):
                    self.running = False

if __name__ == '__main__':
    game = Game()
    game.mainloop()
