import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PositionalGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Позиционная игра (3 хода)")
        self.root.geometry("1350x800")

        self.M = {}

        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self.root, padding=10, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        ttk.Label(left_frame, text="Функция W(x,y,z)", font=("Arial", 12, "bold")).pack()

        self.payoff_entries = {}
        for x in [1, 2]:
            for y in [1, 2]:
                for z in [1, 2]:
                    frame = ttk.Frame(left_frame)
                    frame.pack(anchor=tk.W, pady=2)
                    label = ttk.Label(frame, text=f"W({x},{y},{z}) =", width=12)
                    label.pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT)
                    self.payoff_entries[(x, y, z)] = entry
                    default_values = {
                        (1, 1, 1): 1, (1, 1, 2): 2,
                        (1, 2, 1): -3, (1, 2, 2): 4,
                        (2, 1, 1): -5, (2, 1, 2): 0,
                        (2, 2, 1): -1, (2, 2, 2): 8
                    }
                    entry.insert(0, str(default_values.get((x, y, z), 0)))

        ttk.Label(left_frame, text="Настройка памяти игроков", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        ttk.Label(left_frame, text="Ход Y (игрок 2):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.memory_y = tk.StringVar(value="knows_x")
        ttk.Radiobutton(left_frame, text="Знает X", variable=self.memory_y, value="knows_x").pack(anchor=tk.W)
        ttk.Radiobutton(left_frame, text="Не знает X", variable=self.memory_y, value="none").pack(anchor=tk.W)

        ttk.Label(left_frame, text="Ход Z (игрок 1):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.memory_z = tk.StringVar(value="full")
        ttk.Radiobutton(left_frame, text="Знает X и Y", variable=self.memory_z, value="full").pack(anchor=tk.W)
        ttk.Radiobutton(left_frame, text="Знает только X", variable=self.memory_z, value="only_x").pack(anchor=tk.W)
        ttk.Radiobutton(left_frame, text="Знает только Y", variable=self.memory_z, value="only_y").pack(anchor=tk.W)
        ttk.Radiobutton(left_frame, text="Не знает ничего", variable=self.memory_z, value="none").pack(anchor=tk.W)

        ttk.Button(left_frame, text="Построить и решить", command=self.solve_game).pack(pady=15)

        solution_frame = ttk.LabelFrame(left_frame, text="Решение игры", padding=5)
        solution_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        self.solution_text = tk.Text(solution_frame, height=12, width=35, font=("Courier", 9))
        scrollbar_sol = ttk.Scrollbar(solution_frame, orient=tk.VERTICAL, command=self.solution_text.yview)
        self.solution_text.configure(yscrollcommand=scrollbar_sol.set)
        self.solution_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_sol.pack(side=tk.RIGHT, fill=tk.Y)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(9, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=tree_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def read_payoffs(self):
        for (x, y, z), entry in self.payoff_entries.items():
            try:
                val = float(entry.get())
            except:
                val = 0
            self.M[(x, y, z)] = val

    def build_game_tree(self):
        G = nx.DiGraph()
        labels = {}

        G.add_node("P1_root")
        labels["P1_root"] = "A"

        for x in [1, 2]:
            node_p2 = f"P2_after_x{x}"
            G.add_node(node_p2)
            G.add_edge("P1_root", node_p2, label=f"x={x}")
            labels[node_p2] = f"B\n(x={x})"

            for y in [1, 2]:
                node_p1_again = f"P1_after_x{x}_y{y}"
                G.add_node(node_p1_again)
                G.add_edge(node_p2, node_p1_again, label=f"y={y}")
                labels[node_p1_again] = f"A\n(x={x},y={y})"

                for z in [1, 2]:
                    terminal = f"term_x{x}_y{y}_z{z}"
                    G.add_node(terminal)
                    G.add_edge(node_p1_again, terminal, label=f"z={z}")
                    payoff = self.M.get((x, y, z), 0)
                    labels[terminal] = f"{payoff:.1f}"

        return G, labels

    def get_info_sets(self):
        info_sets = {}
        memory_y = self.memory_y.get()
        memory_z = self.memory_z.get()

        info_sets["A (первый ход)"] = ["P1_root"]

        if memory_y == "none":
            y_nodes = [f"P2_after_x{x}" for x in [1, 2]]
            info_sets["Y (не знает X)"] = y_nodes
        else:
            for x in [1, 2]:
                info_sets[f"Y при X={x}"] = [f"P2_after_x{x}"]

        if memory_z == "full":
            for x in [1, 2]:
                for y in [1, 2]:
                    info_sets[f"Z при X={x},Y={y}"] = [f"P1_after_x{x}_y{y}"]
        elif memory_z == "only_x":
            for x in [1, 2]:
                nodes = [f"P1_after_x{x}_y{y}" for y in [1, 2]]
                info_sets[f"Z (знает X={x})"] = nodes
        elif memory_z == "only_y":
            for y in [1, 2]:
                nodes = [f"P1_after_x{x}_y{y}" for x in [1, 2]]
                info_sets[f"Z (знает Y={y})"] = nodes
        else:
            nodes = [f"P1_after_x{x}_y{y}" for x in [1, 2] for y in [1, 2]]
            info_sets["Z (не знает ничего)"] = nodes

        return info_sets

    def get_hierarchical_pos(self, G):
        pos = {}

        pos["P1_root"] = (0, 3.5)

        x_positions = [-1.0, 1.0]
        for i, x in enumerate([1, 2]):
            pos[f"P2_after_x{x}"] = (x_positions[i], 2.5)

        for x in [1, 2]:
            x_center = -1.0 if x == 1 else 1.0
            y_positions = [-0.5, 0.5]
            for i, y in enumerate([1, 2]):
                pos[f"P1_after_x{x}_y{y}"] = (x_center + y_positions[i], 1.5)

        for x in [1, 2]:
            for y in [1, 2]:
                parent = pos[f"P1_after_x{x}_y{y}"]
                z_positions = [-0.3, 0.3]
                for i, z in enumerate([1, 2]):
                    pos[f"term_x{x}_y{y}_z{z}"] = (parent[0] + z_positions[i], 0.5)

        return pos

    def draw_tree(self, G, labels):
        self.ax.clear()

        pos = self.get_hierarchical_pos(G)
        info_sets = self.get_info_sets()

        for edge in G.edges():
            start, end = edge
            if start in pos and end in pos:
                x1, y1 = pos[start]
                x2, y2 = pos[end]

                edge_label = ""
                for u, v, data in G.edges(data=True):
                    if u == start and v == end:
                        edge_label = data.get("label", "")
                        break

                rad = 0.1
                self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                                 arrowprops=dict(arrowstyle="->", color="gray",
                                                 lw=1, connectionstyle=f"arc3,rad={rad}"))

                if edge_label:
                    mid_x = (x1 + x2) / 2 - 0.15
                    mid_y = (y1 + y2) / 2 + 0.08
                    self.ax.text(mid_x, mid_y, edge_label, ha='center', va='center',
                                 fontsize=6, color='darkred', weight='bold')

        node_to_set = {}
        set_to_color = {}
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'darkcyan']
        color_idx = 0

        for set_name, nodes in info_sets.items():
            color = colors[color_idx % len(colors)]
            set_to_color[set_name] = color
            for node in nodes:
                node_to_set[node] = set_name
            color_idx += 1

        for node, (x, y) in pos.items():
            if node.startswith("term_"):
                square = plt.Rectangle((x - 0.15, y - 0.15), 0.3, 0.3,
                                       facecolor='lightgreen', edgecolor='black',
                                       linewidth=1.5, zorder=3)
                self.ax.add_patch(square)
            else:
                circle = plt.Circle((x, y), 0.20, facecolor='lightblue',
                                    edgecolor='black', linewidth=1.5, zorder=3)
                self.ax.add_patch(circle)

            if node in node_to_set and not node.startswith("term_"):
                color = set_to_color[node_to_set[node]]
                dotted_circle = plt.Circle((x, y), 0.27, facecolor='none',
                                           edgecolor=color, linestyle='dashed',
                                           linewidth=1.8, alpha=0.9, zorder=2)
                self.ax.add_patch(dotted_circle)

        for node, (x, y) in pos.items():
            label = labels.get(node, "")
            if node.startswith("term_"):
                self.ax.text(x, y, label, ha='center', va='center', fontsize=9,
                             weight='bold', zorder=4)
            else:
                self.ax.text(x, y, label, ha='center', va='center', fontsize=8,
                             weight='bold', zorder=4)

        legend_elements = []
        added_colors = set()
        for set_name, nodes in info_sets.items():
            color = set_to_color[set_name]
            if color not in added_colors:
                short_name = set_name[:28]
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                  markerfacecolor='none',
                                                  markeredgecolor=color,
                                                  markersize=8, linestyle='dashed',
                                                  label=short_name))
                added_colors.add(color)

        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                          markerfacecolor='lightblue',
                                          markeredgecolor='black',
                                          markersize=8, label='Узел игрока'))
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor='lightgreen',
                                             edgecolor='black', label='Результат игры'))

        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper left', fontsize=7,
                           framealpha=0.9, bbox_to_anchor=(0.01, 0.99))

        self.ax.set_title("Дерево позиционной игры", fontsize=12, weight='bold')
        self.ax.set_xlim(-2.2, 2.2)
        self.ax.set_ylim(0.0, 4.2)
        self.ax.axis('off')
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()

    def build_normal_form(self):
        memory_y = self.memory_y.get()
        memory_z = self.memory_z.get()

        p1_strategies = []
        p1_names = []

        if memory_z == "full":
            # При полной памяти у игрока A 8 стратегий:
            # Стратегия = (x, z1, z2, z3) где:
            # x - выбор на первом ходу (2 варианта)
            # z1 - выбор Z при (x=1,y=1) или (x=2,y=1) в зависимости от x
            # z2 - выбор Z при (x=1,y=2) или (x=2,y=2) в зависимости от x
            # z3 - выбор Z для другой пары?

            # ПРАВИЛЬНО: 8 стратегий = 2 (выбор X) * 4 (выборы Z для двух возможных Y)
            # Но так как X уже выбран, то для каждого X нужно 2^2=4 варианта Z
            # Итого: 2 * 4 = 8
            for x in [1, 2]:
                for z_if_y1 in [1, 2]:  # Z когда Y=1
                    for z_if_y2 in [1, 2]:  # Z когда Y=2
                        p1_strategies.append((x, z_if_y1, z_if_y2))
                        p1_names.append(f"({x},{z_if_y1}{z_if_y2})")
        elif memory_z == "only_x":
            # Знает только X: 2 (X) * 2^2 = 8 стратегий
            for x in [1, 2]:
                for z1 in [1, 2]:  # z при y=1
                    for z2 in [1, 2]:  # z при y=2
                        p1_strategies.append((x, z1, z2))
                        p1_names.append(f"({x},{z1}{z2})")
        elif memory_z == "only_y":
            # Знает только Y: нужно знать Y, но X выбирает игрок A
            # Стратегия = (x, z1, z2) где z1 - при Y=1, z2 - при Y=2
            # Нужно 2 * 2^2 = 8 стратегий
            for x in [1, 2]:
                for z_if_y1 in [1, 2]:  # Z когда Y=1
                    for z_if_y2 in [1, 2]:  # Z когда Y=2
                        p1_strategies.append((x, z_if_y1, z_if_y2))
                        p1_names.append(f"({x},{z_if_y1}{z_if_y2})")
        else:  # memory_z == "none"
            # Не знает ничего: просто выбирает X и Z
            for x in [1, 2]:
                for z in [1, 2]:
                    p1_strategies.append((x, z))
                    p1_names.append(f"({x},{z})")

        # Стратегии игрока 2 (Y)
        if memory_y == "knows_x":
            p2_strategies = [(1, 1), (1, 2), (2, 1), (2, 2)]
            p2_names = ["(1,1)", "(1,2)", "(2,1)", "(2,2)"]
        else:
            p2_strategies = [1, 2]
            p2_names = ["1", "2"]

        payoff_matrix = np.zeros((len(p1_strategies), len(p2_strategies)))

        for i, p1strat in enumerate(p1_strategies):
            if memory_z == "full":
                x, z_if_y1, z_if_y2 = p1strat
            elif memory_z == "only_x":
                x, z1, z2 = p1strat
            elif memory_z == "only_y":
                x, z_if_y1, z_if_y2 = p1strat
            else:  # none
                x, z = p1strat

            for j, p2strat in enumerate(p2_strategies):
                if memory_y == "knows_x":
                    y1, y2 = p2strat
                    y = y1 if x == 1 else y2
                else:
                    y = p2strat

                if memory_z == "full":
                    # Игрок A знает Y, поэтому выбирает z в зависимости от y
                    z = z_if_y1 if y == 1 else z_if_y2
                elif memory_z == "only_x":
                    # Игрок A знает только X, не знает Y
                    z = z1 if x == 1 else z2
                elif memory_z == "only_y":
                    # Игрок A знает Y, но не знает X? Противоречие - X он выбрал сам
                    # Значит он знает и X (который выбрал) и Y
                    z = z_if_y1 if y == 1 else z_if_y2
                else:  # none
                    z = z

                payoff_matrix[i, j] = self.M.get((x, y, z), 0)

        return payoff_matrix, p1_names, p2_names

    def display_matrix(self, matrix, p1_names, p2_names):
        output = []
        col_width = 5
        space = 1

        header = " " * 12
        for name in p2_names:
            header += f"{name:>{col_width}}{' ' * space}"
        output.append(header)
        output.append("-" * (12 + (col_width + space) * len(p2_names)))

        for i in range(len(p1_names)):
            row_str = f"A-{i:2} {p1_names[i]:7} |"
            for j in range(len(p2_names)):
                row_str += f"{matrix[i, j]:{col_width}.1f}{' ' * space}"
            output.append(row_str)

        matrix_text_str = "\n".join(output)

        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("Матрица выигрышей")
        matrix_window.geometry("900x600")

        text_frame = ttk.Frame(matrix_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, font=("Courier", 9), wrap=tk.NONE)
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_x = ttk.Scrollbar(matrix_window, orient=tk.HORIZONTAL, command=text_widget.xview)

        text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        text_widget.insert(tk.END, matrix_text_str)
        text_widget.configure(state=tk.DISABLED)

        ttk.Button(matrix_window, text="Закрыть", command=matrix_window.destroy).pack(pady=5)

    def remove_duplicate_rows(self, matrix, p1_names):
        rows, cols = matrix.shape
        to_remove = []
        for i in range(rows):
            for k in range(i+1, rows):
                if np.array_equal(matrix[i], matrix[k]):
                    to_remove.append(k)

        if to_remove:
            keep_rows = [i for i in range(rows) if i not in to_remove]
            new_matrix = matrix[keep_rows, :]
            new_names = [p1_names[i] for i in keep_rows]
            return new_matrix, new_names, len(to_remove)
        return matrix, p1_names, 0

    def remove_dominated_rows(self, matrix, p1_names):
        rows, cols = matrix.shape
        dominated = []
        for i in range(rows):
            for k in range(rows):
                if i == k:
                    continue
                if all(matrix[k, j] >= matrix[i, j] for j in range(cols)):
                    if any(matrix[k, j] > matrix[i, j] for j in range(cols)):
                        dominated.append(i)
                        break

        if dominated:
            keep_rows = [i for i in range(rows) if i not in dominated]
            new_matrix = matrix[keep_rows, :]
            new_names = [p1_names[i] for i in keep_rows]
            return new_matrix, new_names, len(dominated)
        return matrix, p1_names, 0

    def solve_mixed_2x2(self, matrix, p1_names, p2_names):
        a11, a12 = matrix[0, 0], matrix[0, 1]
        a21, a22 = matrix[1, 0], matrix[1, 1]

        denom = a11 + a22 - a12 - a21

        if abs(denom) < 0.0001:
            return None, None, None, None, None, True

        p = (a22 - a21) / denom
        V = (a11 * a22 - a12 * a21) / denom
        r = (a22 - a12) / denom

        return p, 1 - p, r, 1 - r, V, False

    def solve_simplex(self, matrix, p1_names, p2_names):
        from scipy.optimize import linprog

        rows, cols = matrix.shape

        c = np.zeros(rows + 1)
        c[-1] = -1

        A_ub = np.zeros((cols, rows + 1))
        for j in range(cols):
            for i in range(rows):
                A_ub[j, i] = -matrix[i, j]
            A_ub[j, -1] = 1
        b_ub = np.zeros(cols)

        A_eq = np.zeros((1, rows + 1))
        A_eq[0, :rows] = 1
        b_eq = np.array([1])

        bounds = [(0, None) for _ in range(rows)] + [(None, None)]

        result1 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs')

        if not result1.success:
            return None, None, None, False, False, []

        p = result1.x[:rows]
        V = result1.x[-1]

        c2 = np.zeros(cols + 1)
        c2[-1] = 1

        A_ub2 = np.zeros((rows, cols + 1))
        for i in range(rows):
            for j in range(cols):
                A_ub2[i, j] = matrix[i, j]
            A_ub2[i, -1] = -1
        b_ub2 = np.zeros(rows)

        A_eq2 = np.zeros((1, cols + 1))
        A_eq2[0, :cols] = 1
        b_eq2 = np.array([1])

        bounds2 = [(0, None) for _ in range(cols)] + [(None, None)]

        result2 = linprog(c2, A_ub=A_ub2, b_ub=b_ub2, A_eq=A_eq2, b_eq=b_eq2,
                          bounds=bounds2, method='highs')

        q = None
        optimal_p2_strategies = []

        if result2.success:
            q = result2.x[:cols]

            for j in range(cols):
                payoff = np.dot(p, matrix[:, j])
                if abs(payoff - V) < 0.001:
                    optimal_p2_strategies.append(j)

        return p, q, V, result1.success, result2.success, optimal_p2_strategies

    def format_strategy_vector(self, probs):
        if probs is None:
            return "(все стратегии)"
        formatted = ", ".join(f"{p:.4f}" for p in probs)
        return f"({formatted})"

    def solve_matrix_game(self, matrix, p1_names, p2_names):
        output = []

        output.append(f"РАЗМЕР МАТРИЦЫ: {matrix.shape[0]} x {matrix.shape[1]}")
        output.append("")

        original_p1_names = p1_names.copy()
        original_p2_names = p2_names.copy()

        row_mins = np.min(matrix, axis=1)
        max_of_mins = np.max(row_mins)
        best_rows = np.where(row_mins == max_of_mins)[0]

        col_maxs = np.max(matrix, axis=0)
        min_of_maxs = np.min(col_maxs)
        best_cols = np.where(col_maxs == min_of_maxs)[0]

        if abs(max_of_mins - min_of_maxs) < 0.001:
            V = max_of_mins

            output.append(f"\nСЕДЛОВАЯ ТОЧКА НАЙДЕНА")
            output.append(f"Цена игры V = {V:.3f}")

            # Вывод оптимальных чистых стратегий (без вероятностей)
            output.append(f"\nОптимальные стратегии A (чистые):")
            for i in best_rows:
                output.append(f"   {p1_names[i]}")

            output.append(f"\nОптимальные стратегии B (чистые):")
            for j in best_cols:
                output.append(f"   {p2_names[j]}")

            # Векторы вероятностей
            p1_vec = np.zeros(len(p1_names))
            p2_vec = np.zeros(len(p2_names))
            for i in best_rows:
                p1_vec[i] = 1.0 / len(best_rows)
            for j in best_cols:
                p2_vec[j] = 1.0 / len(best_cols)

            output.append(f"\n{'=' * 35}")
            output.append(f"ОПТИМАЛЬНЫЕ СТРАТЕГИИ (векторы вероятностей):")
            output.append(f"{'=' * 35}")
            output.append(f"A: {self.format_strategy_vector(p1_vec)}")
            output.append(f"B: {self.format_strategy_vector(p2_vec)}")
            return "\n".join(output)

        output.append(f"\n{'=' * 35}")
        output.append(f"РЕШЕНИЕ В СМЕШАННЫХ СТРАТЕГИЯХ")
        output.append(f"{'=' * 35}")

        rows, cols = matrix.shape

        total_removed = 0
        while True:
            matrix, p1_names, removed_dup = self.remove_duplicate_rows(matrix, p1_names)
            matrix, p1_names, removed_dom = self.remove_dominated_rows(matrix, p1_names)
            total_removed += removed_dup + removed_dom
            if removed_dup == 0 and removed_dom == 0:
                break

        if total_removed > 0:
            output.append(f"\nУДАЛЕНИЕ НЕВЫГОДНЫХ СТРАТЕГИЙ")
            output.append(f"Удалено строк A: {total_removed}")
            output.append(f"Размер после сокращения: {matrix.shape[0]} x {matrix.shape[1]}\n")

        rows, cols = matrix.shape
        p_vec_full = np.zeros(len(original_p1_names))
        q_vec_full = np.zeros(len(original_p2_names))

        if rows == 2 and cols == 2:
            result = self.solve_mixed_2x2(matrix, p1_names, p2_names)
            if result[5] == True:
                output.append(f"\nВЫРОЖДЕННАЯ ИГРА")
                a11, a12 = matrix[0, 0], matrix[0, 1]
                output.append(f"Цена игры V = {a11:.4f}")
                p_vec_full[:] = 1.0 / len(original_p1_names)
                q_vec_full[:] = 1.0 / len(original_p2_names)
            else:
                p, q, r, s, V, _ = result

                output.append(f"Цена игры V = {V:.4f}")
                output.append(f"\nОптимальная стратегия A:")
                output.append(f"   {p1_names[0]}")
                output.append(f"   {p1_names[1]}")
                output.append(f"\nОптимальная стратегия B:")
                output.append(f"   {p2_names[0]}")
                output.append(f"   {p2_names[1]}")

                for idx, name in enumerate(original_p1_names):
                    if name == p1_names[0]:
                        p_vec_full[idx] = p
                    elif name == p1_names[1]:
                        p_vec_full[idx] = q

                for idx, name in enumerate(original_p2_names):
                    if name == p2_names[0]:
                        q_vec_full[idx] = r
                    elif name == p2_names[1]:
                        q_vec_full[idx] = s

            output.append(f"\n{'=' * 35}")
            output.append(f"ОПТИМАЛЬНЫЕ СТРАТЕГИИ (векторы вероятностей):")
            output.append(f"{'=' * 35}")
            output.append(f"A: {self.format_strategy_vector(p_vec_full)}")
            output.append(f"B: {self.format_strategy_vector(q_vec_full)}")
            return "\n".join(output)

        try:
            p, q, V, success1, success2, optimal_p2 = self.solve_simplex(matrix, p1_names, p2_names)

            if success1 and p is not None:

                output.append(f"Цена игры V = {V:.4f}")

                nonzero_p = [i for i in range(len(p)) if p[i] > 0.01]
                if len(nonzero_p) > 2:
                    output.append(f"\nВОЗМОЖНО МНОЖЕСТВО ОПТИМАЛЬНЫХ СТРАТЕГИЙ A")
                    output.append(f"Ненулевые вероятности у {len(nonzero_p)} стратегий")

                output.append(f"\nОптимальная смешанная стратегия A:")
                for i in range(rows):
                    if p[i] > 0.001:
                        output.append(f"   {p1_names[i]}")

                for idx, name in enumerate(original_p1_names):
                    for i, p_name in enumerate(p1_names):
                        if name == p_name and i < len(p):
                            p_vec_full[idx] = p[i]

                if optimal_p2 and len(optimal_p2) > 1:
                    output.append(f"\nОптимальная смешанная стратегия B:")
                    for j in optimal_p2:
                        output.append(f"   {p2_names[j]}")
                    for j in optimal_p2:
                        q_vec_full[j] = 1.0 / len(optimal_p2)
                elif q is not None:
                    output.append(f"\nОптимальная смешанная стратегия B:")
                    for j in range(cols):
                        if q[j] > 0.001:
                            output.append(f"   {p2_names[j]}")
                    for idx, name in enumerate(original_p2_names):
                        for j, q_name in enumerate(p2_names):
                            if name == q_name and j < len(q):
                                q_vec_full[idx] = q[j]

                output.append(f"\n{'=' * 35}")
                output.append(f"ОПТИМАЛЬНЫЕ СТРАТЕГИИ (векторы вероятностей):")
                output.append(f"{'=' * 35}")
                output.append(f"P1: {self.format_strategy_vector(p_vec_full)}")
                output.append(f"P2: {self.format_strategy_vector(q_vec_full)}")
                return "\n".join(output)
            else:
                output.append(f"\nСимплекс-метод не дал решения")

        except Exception as e:
            output.append(f"\nОшибка симплекс-метода: {e}")

        output.append(f"\n--- ПРИБЛИЖЕННОЕ РЕШЕНИЕ ---")
        output.append(f"Лучшие чистые стратегии A:")
        for i in best_rows:
            output.append(f"   {p1_names[i]}")

        p_approx = np.zeros(len(original_p1_names))
        q_approx = np.zeros(len(original_p2_names))
        for i in best_rows:
            p_approx[i] = 1.0 / len(best_rows) if len(best_rows) > 1 else 1.0
        for j in best_cols:
            q_approx[j] = 1.0 / len(best_cols) if len(best_cols) > 1 else 1.0

        output.append(f"\n{'=' * 35}")
        output.append(f"ПРИБЛИЖЕННЫЕ ОПТИМАЛЬНЫЕ СТРАТЕГИИ (векторы вероятностей):")
        output.append(f"{'=' * 35}")
        output.append(f"A: {self.format_strategy_vector(p_approx)}")
        output.append(f"B: {self.format_strategy_vector(q_approx)}")

        return "\n".join(output)

    def solve_game(self):
        self.read_payoffs()
        G, labels = self.build_game_tree()
        self.draw_tree(G, labels)

        matrix, p1_names, p2_names = self.build_normal_form()
        self.display_matrix(matrix, p1_names, p2_names)

        solution = self.solve_matrix_game(matrix, p1_names, p2_names)
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.insert(1.0, solution)


if __name__ == "__main__":
    root = tk.Tk()
    app = PositionalGameGUI(root)
    root.mainloop()