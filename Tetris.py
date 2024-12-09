import tkinter as tk
import random
import os

# Game configurations
GAME_WIDTH = 800
GAME_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = GAME_WIDTH // BLOCK_SIZE
ROWS = GAME_HEIGHT // BLOCK_SIZE
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],        # O
    [[1, 1, 1, 1]],          # I
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]
COLORS = ["red", "green", "blue", "orange", "purple", "cyan", "yellow"]
LEADERBOARD_FILE = "leaderboard.txt"

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris Mania")

        # Canvas for the game board
        self.canvas = tk.Canvas(root, width=GAME_WIDTH, height=GAME_HEIGHT, bg="black")
        self.canvas.grid(row=0, column=0, rowspan=3)

        # Canvas for upcoming blocks
        self.next_canvas = tk.Canvas(root, width=120, height=200, bg="black")
        self.next_canvas.grid(row=0, column=1)

        # Game state
        self.running = False
        self.score = 0
        self.level = 1
        self.grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_shape = None
        self.current_color = None
        self.current_pos = (0, 0)
        self.upcoming_shapes = []
        self.upcoming_colors = []

        # Buttons and labels
        self.start_button = tk.Button(root, text="Start", command=self.start_game, width=10)
        self.start_button.grid(row=1, column=1)

        self.pause_button = tk.Button(root, text="Pause", command=self.pause_game, width=10)
        self.pause_button.grid(row=2, column=1)

        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.grid(row=3, column=0, columnspan=2)

        self.speed = 450  # Speed of falling blocks in ms

    def start_game(self):
        if not self.running:
            self.running = True
            self.spawn_shape()
            self.generate_next_shapes()
            self.update_game()

    def pause_game(self):
        self.running = not self.running
        if self.running:
            self.update_game()

    def restart_game(self):
        self.running = False
        self.score = 0
        self.level = 1
        self.speed = 500
        self.grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.canvas.delete("all")
        self.next_canvas.delete("all")
        self.update_score(0)
        self.start_game()

    def spawn_shape(self):
        if not self.upcoming_shapes:
            self.generate_next_shapes()
        self.current_shape = self.upcoming_shapes.pop(0)
        self.current_color = self.upcoming_colors.pop(0)
        self.current_pos = (0, COLUMNS // 2 - len(self.current_shape[0]) // 2)

    def generate_next_shapes(self):
        while len(self.upcoming_shapes) < 2:
            self.upcoming_shapes.append(random.choice(SHAPES))
            self.upcoming_colors.append(random.choice(COLORS))
        self.draw_next_shapes()

    def draw_next_shapes(self):
        self.next_canvas.delete("all")
        for index, (shape, color) in enumerate(zip(self.upcoming_shapes, self.upcoming_colors)):
            for i, row in enumerate(shape):
                for j, val in enumerate(row):
                    if val:
                        x = j * BLOCK_SIZE + 10
                        y = i * BLOCK_SIZE + (index * 100) + 10
                        self.next_canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=color, outline="black")

    def draw_shape(self):
        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val:
                    x = (self.current_pos[1] + j) * BLOCK_SIZE
                    y = (self.current_pos[0] + i) * BLOCK_SIZE
                    self.canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=self.current_color, outline="black")

    def move_shape(self, dx, dy):
        new_pos = (self.current_pos[0] + dy, self.current_pos[1] + dx)
        if self.valid_position(new_pos):
            self.current_pos = new_pos

    def drop_shape(self):
        while self.valid_position((self.current_pos[0] + 1, self.current_pos[1])):
            self.current_pos = (self.current_pos[0] + 1, self.current_pos[1])

    def rotate_shape(self):
        new_shape = [list(row) for row in zip(*self.current_shape[::-1])]
        if self.valid_position(self.current_pos, new_shape):
            self.current_shape = new_shape

    def valid_position(self, pos, shape=None):
        if shape is None:
            shape = self.current_shape
        for i, row in enumerate(shape):
            for j, val in enumerate(row):
                if val:
                    x, y = pos[1] + j, pos[0] + i
                    if x < 0 or x >= COLUMNS or y >= ROWS or (y >= 0 and self.grid[y][x]):
                        return False
        return True

    def lock_shape(self):
        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val:
                    x = self.current_pos[1] + j
                    y = self.current_pos[0] + i
                    if y >= 0:
                        self.grid[y][x] = self.current_color
        self.clear_lines()
        self.spawn_shape()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared_lines = ROWS - len(new_grid)
        self.grid = [[None] * COLUMNS for _ in range(cleared_lines)] + new_grid
        self.update_canvas()
        self.update_score(cleared_lines * 100)
        if cleared_lines > 0:
            self.increase_level()

    def update_canvas(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    self.canvas.create_rectangle(
                        x * BLOCK_SIZE, y * BLOCK_SIZE,
                        (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                        fill=color, outline="black")

    def update_score(self, points):
        self.score += points
        self.score_label.config(text=f"Score: {self.score}")

    def increase_level(self):
        self.level = 1 + self.score // 500
        self.speed = max(100, 500 - (self.level - 1) * 50)

    def update_game(self):
        if not self.running:
            return
        if self.valid_position((self.current_pos[0] + 1, self.current_pos[1])):
            self.move_shape(0, 1)
        else:
            self.lock_shape()
            if not self.valid_position(self.current_pos):
                self.running = False
                self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2, text="Game Over", fill="white", font=("Arial", 24))
                return
        self.update_canvas()
        self.draw_shape()
        self.root.after(self.speed, self.update_game)

    def key_pressed(self, event):
        if not self.running:
            return
        if event.keysym == "Left":
            self.move_shape(-1, 0)
        elif event.keysym == "Right":
            self.move_shape(1, 0)
        elif event.keysym == "Down":
            self.move_shape(0, 1)
        elif event.keysym == "Up":
            self.rotate_shape()
        elif event.keysym == "space":
            self.drop_shape()

def main():
    root = tk.Tk()
    game = Tetris(root)
    root.bind("<Key>", game.key_pressed)
    root.mainloop()

if __name__ == "__main__":
    main()
