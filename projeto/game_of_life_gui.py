import tkinter as tk
import random

from game_of_life import (
    game_of_life_sequential,
    game_of_life_parallel
)


# =========================================================
# CONFIG
# =========================================================

GRID_ROWS = 80
GRID_COLS = 80

CELL_SIZE = 9

UPDATE_DELAY = 100

WORKER_COLORS = [
    "#FF5555",
    "#55AAFF",
    "#55FF55",
    "#FFFF55",
    "#FF55FF",
    "#55FFFF",
    "#FFA500",
    "#AAAAAA"
]


# =========================================================
# GUI
# =========================================================

class GameOfLifeGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Game of Life"
        )

        self.running = False

        self.grid = [
            [0 for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

        # =================================================
        # CANVAS
        # =================================================

        self.canvas = tk.Canvas(
            root,
            width=GRID_COLS * CELL_SIZE,
            height=GRID_ROWS * CELL_SIZE,
            bg="#202020"
        )

        self.canvas.pack(
            padx=10,
            pady=10
        )

        self.canvas.bind(
            "<Button-1>",
            self.toggle_cell
        )

        # =================================================
        # CONTROLS
        # =================================================

        controls = tk.Frame(root)

        controls.pack(pady=10)

        # MODE

        self.mode = tk.StringVar(
            value="Sequential"
        )

        tk.Radiobutton(
            controls,
            text="Sequential",
            variable=self.mode,
            value="Sequential"
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            controls,
            text="Parallel",
            variable=self.mode,
            value="Parallel"
        ).pack(side=tk.LEFT)

        # WORKERS

        tk.Label(
            controls,
            text="Workers:"
        ).pack(side=tk.LEFT)

        self.workers_entry = tk.Entry(
            controls,
            width=5
        )

        self.workers_entry.insert(0, "4")

        self.workers_entry.pack(
            side=tk.LEFT,
            padx=5
        )

        # =================================================
        # BUTTONS
        # =================================================

        self.start_button = tk.Button(
            controls,
            text="Start",
            command=self.toggle_running,
            width=10
        )

        self.start_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.next_button = tk.Button(
            controls,
            text="Next",
            command=self.next_step,
            width=10
        )

        self.next_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.random_button = tk.Button(
            controls,
            text="Random",
            command=self.randomize_grid,
            width=10
        )

        self.random_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.reset_button = tk.Button(
            controls,
            text="Reset",
            command=self.reset_grid,
            width=10
        )

        self.reset_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.draw_grid()

    # =====================================================
    # DRAW
    # =====================================================

    def draw_grid(self):

        self.canvas.delete("all")

        mode = self.mode.get()

        workers = int(
            self.workers_entry.get()
        )

        chunk_size = GRID_ROWS // workers

        for row in range(GRID_ROWS):

            # =============================================
            # COR DO WORKER
            # =============================================

            if mode == "Parallel":

                worker_id = min(
                    row // chunk_size,
                    workers - 1
                )

                worker_color = WORKER_COLORS[
                    worker_id % len(WORKER_COLORS)
                    ]

            else:

                worker_color = "#303030"

            for col in range(GRID_COLS):

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                alive = self.grid[row][col]

                # =========================================
                # CÉLULAS
                # =========================================

                if alive == 1:

                    fill = "#ffffff"

                else:

                    fill = "#202020"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline=worker_color,
                    width=1
                )

        # =============================================
        # LEGEND
        # =============================================

        if mode == "Parallel":
            self.draw_worker_legend(workers)

    # =====================================================
    # CELL TOGGLE
    # =====================================================

    def toggle_cell(self, event):

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if (
            row >= GRID_ROWS or
            col >= GRID_COLS
        ):
            return

        self.grid[row][col] = (
            1 - self.grid[row][col]
        )

        self.draw_grid()

    # =====================================================
    # NEXT STEP
    # =====================================================

    def next_step(self):

        mode = self.mode.get()

        if mode == "Sequential":

            self.grid = game_of_life_sequential(
                self.grid,
                1
            )

        else:

            workers = int(
                self.workers_entry.get()
            )

            self.grid = game_of_life_parallel(
                self.grid,
                1,
                workers
            )

        self.draw_grid()

    # =====================================================
    # AUTO RUN
    # =====================================================

    def run_loop(self):

        if not self.running:
            return

        self.next_step()

        self.root.after(
            UPDATE_DELAY,
            self.run_loop
        )

    # =====================================================
    # START / STOP
    # =====================================================

    def toggle_running(self):

        self.running = not self.running

        if self.running:

            self.start_button.config(
                text="Stop"
            )

            self.run_loop()

        else:

            self.start_button.config(
                text="Start"
            )

    # =====================================================
    # RESET
    # =====================================================

    def reset_grid(self):

        self.running = False

        self.start_button.config(
            text="Start"
        )

        self.grid = [
            [0 for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

        self.draw_grid()

    # =====================================================
    # RANDOM
    # =====================================================

    def randomize_grid(self):

        self.grid = [
            [
                random.randint(0, 1)
                for _ in range(GRID_COLS)
            ]
            for _ in range(GRID_ROWS)
        ]

        self.draw_grid()

def draw_worker_legend(self, workers):

    legend_x = 10
    legend_y = 10

    for i in range(workers):

        color = WORKER_COLORS[
            i % len(WORKER_COLORS)
        ]

        y = legend_y + (i * 25)

        self.canvas.create_rectangle(
            legend_x,
            y,
            legend_x + 20,
            y + 20,
            fill=color,
            outline="white"
        )

        self.canvas.create_text(
            legend_x + 80,
            y + 10,
            text=f"Worker {i}",
            fill="white",
            anchor="w"
        )

# =========================================================
# START GUI
# =========================================================

def run_gui():

    root = tk.Tk()

    GameOfLifeGUI(root)

    root.mainloop()