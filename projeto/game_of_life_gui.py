import tkinter as tk
import random

try:
    from rpc_client import RPCClient
    RPC_AVAILABLE = True
except:
    RPC_AVAILABLE = False


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
    """
    Interface gráfica para o Game of Life.

    Permite executar o jogo em modo:
    - sequencial (local ou via RPC)
    - paralelo (local ou via RPC)

    A interface inclui:
    - grelha interativa clicável
    - controlo de execução (start/stop/next)
    - geração aleatória e reset
    - visualização de workers em modo paralelo
    """

    def __init__(self, root):
        """
        Inicializa a interface gráfica do Game of Life.

        Configura:
        - ligação RPC (se disponível)
        - grelha inicial
        - canvas de desenho
        - controlos de UI (botões, modos, inputs)
        - estado inicial da simulação

        Args:
            root (tk.Tk): janela principal do Tkinter
        """

        self.root = root

        self.root.title(
            "Distributed Game of Life"
        )

        self.rpc = None

        if RPC_AVAILABLE:

            try:
                self.rpc = RPCClient()
                print("Servidor RPC ligado")
                print("O Game of Life será iniciado remotamente.")

            except:
                print("Servidor RPC não disponível.")
                print("O Game of Life será iniciado localmente.")

        self.running = False

        self.grid = [
            [0 for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

        # =================================================
        # CANVAS
        # =================================================

        LEGEND_WIDTH = 180

        self.canvas = tk.Canvas(
            root,
            width=(GRID_COLS * CELL_SIZE) + LEGEND_WIDTH,
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
        """
        Renderiza a grelha atual no canvas.

        Cada célula é desenhada como um retângulo:
        - branco: célula viva
        - escuro: célula morta

        Em modo paralelo, cada linha é associada a um worker,
        colorindo os contornos para visualização da divisão do trabalho.
        """

        self.canvas.delete("all")

        mode = self.mode.get()

        workers = int(
            self.workers_entry.get()
        )

        chunk_size = max(
            1,
            GRID_ROWS // workers
        )

        for row in range(GRID_ROWS):

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

                fill = (
                    "#FFFFFF"
                    if alive == 1
                    else "#202020"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline=worker_color,
                    width=1
                )

        if mode == "Parallel":

            self.draw_worker_legend(
                workers
            )

    # =====================================================
    # TOGGLE CELL
    # =====================================================

    def toggle_cell(self, event):
        """
        Altera o estado de uma célula ao clicar na grelha.

        Converte coordenadas do clique em índices da grelha
        e alterna entre 0 (morto) e 1 (vivo).

        Args:
            event (tk.Event): evento de clique do rato
        """

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
        """
        Avança a simulação uma geração.

        Dependendo do modo selecionado:
        - Sequential: usa versão local ou RPC sequencial
        - Parallel: usa versão local ou RPC paralela

        Atualiza a grelha com o novo estado.
        """

        mode = self.mode.get()

        # ============================================
        # SEQUENTIAL
        # ============================================

        if mode == "Sequential":

            # RPC
            if self.rpc:

                response = self.rpc.request(
                    "game_of_life",
                    {
                        "grid": self.grid,
                        "generations": 1
                    }
                )

                if "result" in response:

                    self.grid = response["result"]

                else:

                    print(
                        "Erro RPC:",
                        response
                    )

            # LOCAL
            else:

                from game_of_life import (
                    game_of_life_sequential
                )

                self.grid = (
                    game_of_life_sequential(
                        self.grid,
                        1
                    )
                )

        # ============================================
        # PARALLEL
        # ============================================

        else:

            workers = int(
                self.workers_entry.get()
            )

            # RPC
            if self.rpc:

                response = self.rpc.request(
                    "game_of_life_parallel",
                    {
                        "grid": self.grid,
                        "generations": 1,
                        "workers": workers
                    }
                )

                if "result" in response:

                    self.grid = response["result"]

                else:

                    print(
                        "Erro RPC:",
                        response
                    )

            # LOCAL
            else:

                from game_of_life import (
                    game_of_life_parallel
                )

                self.grid = (
                    game_of_life_parallel(
                        self.grid,
                        1,
                        workers
                    )
                )

        self.draw_grid()

    # =====================================================
    # RUN LOOP
    # =====================================================

    def run_loop(self):
        """
        Loop automático de execução do Game of Life.

        Executa repetidamente `next_step()` enquanto a simulação
        estiver ativa, respeitando o atraso definido em UPDATE_DELAY.
        """

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
        """
        Alterna o estado de execução contínua da simulação.

        Inicia ou para o loop automático do Game of Life.
        Também atualiza o texto do botão Start/Stop.
        """

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
        """
        Reinicia a grelha para o estado vazio.

        - Para a simulação
        - Define todas as células como mortas
        - Atualiza a interface
        """

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
        """
        Preenche a grelha com valores aleatórios (0 ou 1).

        Usado para criar configurações iniciais rápidas
        para simulação do Game of Life.
        """

        self.grid = [
            [
                random.randint(0, 1)
                for _ in range(GRID_COLS)
            ]
            for _ in range(GRID_ROWS)
        ]

        self.draw_grid()

    # =====================================================
    # WORKER LEGEND
    # =====================================================


    def draw_worker_legend(self, workers):
        """
        Desenha uma legenda visual dos workers na interface.

        Cada worker recebe uma cor e é exibido numa barra lateral,
        permitindo visualizar a divisão do processamento no modo paralelo.

        Args:
            workers (int): número de workers ativos
        """

        legend_x = (GRID_COLS * CELL_SIZE) + 20
        legend_y = 20

        self.canvas.create_text(
            legend_x,
            0,
            text="Workers",
            fill="white",
            anchor="nw",
            font=("Arial", 12, "bold")
        )

        for i in range(workers):
            color = WORKER_COLORS[
                i % len(WORKER_COLORS)
                ]

            y = legend_y + (i * 30)

            self.canvas.create_rectangle(
                legend_x,
                y,
                legend_x + 20,
                y + 20,
                fill=color,
                outline="white"
            )

            self.canvas.create_text(
                legend_x + 30,
                y + 10,
                text=f"Worker {i}",
                fill="white",
                anchor="w"
            )



# =========================================================
# START GUI
# =========================================================

def run_gui():
    """
    Inicializa e executa a interface gráfica do Game of Life.

    Cria a janela principal Tkinter e inicia o loop da aplicação.
    """

    root = tk.Tk()

    GameOfLifeGUI(root)

    root.mainloop()