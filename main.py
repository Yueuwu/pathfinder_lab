import tkinter as tk
from tkinter import ttk
import random
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.bi_a_star import BiAStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from pathfinding.finder.best_first import BestFirst
from pathfinding.finder.breadth_first import BreadthFirstFinder
import pathfinding.core.heuristic as heuristic
from pathfinding.finder.ida_star import IDAStarFinder

from lee_algorithm import LeeFinder


w = 640
h = 550
cell_size = 32

window = tk.Tk()
window.title('Поиск пути')

wx = window.winfo_screenwidth() // 2 - w // 2
wy = window.winfo_screenheight() // 2 - h // 2
window.geometry('{}x{}+{}+{}'.format(w, h, wx, wy))
window.resizable(False, False)

editor_mode = 'em_wall'

start_point = None
end_point = None
bw = w // 5
bh = 32
rows = (h-64)//cell_size
cols = w//cell_size

combobox = ttk.Combobox(window,
                        state='readonly',
                        values=['A*',
                                'Алгоритм Дейкстры (Dijkstra)',
                                'Поиск по первому наилучшему совпадению (Best-First)',
                                'Поиск в ширину (Breadth First Search (BFS))',
                                'Двунаправленный A* (Bi-directional A*)',
                                'A* с итеративным углублением (Iterative Deeping A* (IDA*))',
                                'Волновой алгоритм / Алгоритм Ли(Lee Algorithm)',])
combobox.place(width=w - w // 2, height=bh, x=bw + bw // 2, y=h - bh)
combobox.current(0)

diagonal = tk.BooleanVar()
diagonal.set(False)

checkbutton = tk.Checkbutton(text='По диагонали', variable=diagonal,
                             onvalue=True, offvalue=False)
checkbutton.place(x=w - bw + 10, y=h - 28)


class Cell():
    def __init__(self, _width, _height, _x, _y):
        self.type = 'empty'
        self.cell = tk.Button(window, state=tk.DISABLED, bg='white', bd=1)
        self.cell.place(width=_width, height=_height, x=_x, y=_y)
        self.cell.bind('<1>', self.left_click)

    def left_click(self, event):
        global editor_mode, start_point, end_point
        clear_path_cells()
        if editor_mode == 'em_wall':
            if self.type == 'empty':
                self.type = 'wall'
                self.cell.config(bg='#B97A57')
            elif self.type == 'wall':
                self.empty()

        elif editor_mode == 'em_start':
            if self.type == 'empty':
                self.type = 'start'
                self.cell.config(bg='green')
                if start_point is not None:  # начальная точка может быть только одна
                    start_point.empty()
                start_point = self
            elif self.type == 'start':
                self.empty()
                start_point = None

        elif editor_mode == 'em_end':
            if self.type == 'empty':
                self.type = 'end'
                self.cell.config(bg='red')
                if end_point is not None:  # конечная точка может быть только одна
                    end_point.empty()
                end_point = self
            elif self.type == 'end':
                self.empty()
                end_point = None

    def empty(self):
        self.type = 'empty'
        self.cell.config(bg='white')

    def draw_path_element(self):
        self.type = 'path_element'
        self.cell.config(bg='yellow')


labyrinth = []

# построение поля из кнопок
for i in range(rows):
    lab_row = []
    for j in range(cols):
        cell = Cell(cell_size, cell_size, j * cell_size, i * cell_size)
        lab_row.append(cell)
    labyrinth.append(lab_row)


# создание элемента границы поля
def create_wall_block(x, y):
    labyrinth[y][x].type = 'wall_block'  # нажатие на стену не изменит ее тип
    labyrinth[y][x].cell.config(state=tk.DISABLED, bg='#7C4E34')


# строки
for i in [0, rows - 1]:
    for j in range(cols):
        create_wall_block(j, i)
# столбцы
for j in [0, cols - 1]:
    for i in range(1, rows - 1):
        create_wall_block(j, i)


def button_create_wall():
    global editor_mode
    editor_mode = 'em_wall'
    button_wall.config(relief=tk.SUNKEN)
    button_sp.config(relief=tk.RAISED)
    button_ep.config(relief=tk.RAISED)


def button_start_point():
    global editor_mode
    editor_mode = 'em_start'
    button_wall.config(relief=tk.RAISED)
    button_sp.config(relief=tk.SUNKEN)
    button_ep.config(relief=tk.RAISED)


def button_end_point():
    global editor_mode
    editor_mode = 'em_end'
    button_wall.config(relief=tk.RAISED)
    button_sp.config(relief=tk.RAISED)
    button_ep.config(relief=tk.SUNKEN)


def button_random_walls():
    global start_point, end_point
    start_point = None
    end_point = None
    for e in range(1, rows - 1):
        for q in range(1, cols - 1):
            r = random.random()
            if r < 0.3:
                labyrinth[e][q].type = 'wall'
                labyrinth[e][q].cell.config(bg='#B97A57')
            else:
                labyrinth[e][q].empty()


def button_clear_cells():
    global start_point, end_point
    start_point = None
    end_point = None
    for e in range(1, rows - 1):
        for q in range(1, cols - 1):
            labyrinth[e][q].empty()


def clear_path_cells():
    for e in range(1, rows - 1):
        for q in range(1, cols - 1):
            if labyrinth[e][q].type == 'path_element':
                labyrinth[e][q].empty()


def button_path_finding():
    clear_path_cells()  # очистка старого пути
    # если указаны начальная и конечная точки
    if start_point is not None and end_point is not None:
        # создание массива данных на основе построенного лабиринта
        lab = []
        start_coord = None  # координаты начальной точки
        end_coord = None  # координаты конечной точки

        for e in range(rows):
            row = []
            for q in range(cols):
                if labyrinth[e][q].type == 'wall' or labyrinth[e][q].type == 'wall_block':
                    row.append(0)
                else:
                    row.append(1)
                    if labyrinth[e][q].type == 'start':
                        start_coord = {'x': q, 'y': e}
                    elif labyrinth[e][q].type == 'end':
                        end_coord = {'x': q, 'y': e}
            lab.append(row)
    print('combo', combobox.current())
    if combobox.current() == 0:
        finder = AStarFinder(diagonal_movement=diagonal.get(), heuristic=heuristic.manhattan)
    elif combobox.current() == 1:
        finder = DijkstraFinder(diagonal_movement=diagonal.get())
    elif combobox.current() == 2:
        finder = BestFirst(diagonal_movement=diagonal.get())
    elif combobox.current() == 3:
        finder = BreadthFirstFinder(diagonal_movement=diagonal.get())
    elif combobox.current() == 4:
        finder = BiAStarFinder(diagonal_movement=diagonal.get())
    elif combobox.current() == 5:
        finder = IDAStarFinder(diagonal_movement=diagonal.get())
    elif combobox.current() == 6:
        finder = LeeFinder()

    if 0 <= combobox.current() <= 5:
        grid = Grid(matrix=lab)
        start = grid.node(start_coord['x'], start_coord['y'])
        end = grid.node(end_coord['x'], end_coord['y'])
    else:
        grid = lab
        start = start_coord
        end = end_coord

    path, runs = finder.find_path(start, end, grid)

    print(combobox.get())  # название алгоритма
    if 0 <= combobox.current() <= 5:
    # вывод лабиринта и найденного пути в символьном виде
        print(grid.grid_str(path=path, start=start, end=end))
    # длина пути - путь минус начальная и конечная точки
    print('Длина пути: ', 0 if path == [] else len(path) - 2)
    print('Шагов: ', runs)
    print(path)  # координаты точек

    for e in range(1, len(path) - 1):
        labyrinth[path[e][1]][path[e][0]].draw_path_element()


button_wall = tk.Button(window, text='Установка стен', command=button_create_wall,
                        relief=tk.SUNKEN)
button_wall.place(width=bw, height=bh, x=0, y=h - bh * 2)
button_sp = tk.Button(window, text='Начальная точка', command=button_start_point)
button_sp.place(width=bw, height=bh, x=bw, y=h - bh * 2)
button_ep = tk.Button(window, text='Конечная точка', command=button_end_point)
button_ep.place(width=bw, height=bh, x=bw * 2, y=h - bh * 2)
button_rand = tk.Button(window, text='Случайно заполнить', command=button_random_walls)
button_rand.place(width=bw, height=bh, x=bw * 3, y=h - bh * 2)
button_clear = tk.Button(window, text='Очистить', command=button_clear_cells)
button_clear.place(width=bw, height=bh, x=bw * 4, y=h - bh * 2)

button_find = tk.Button(window, text='Найти путь', command=button_path_finding)
button_find.place(width=bw + bw // 2, height=bh, x=0, y=h - bh)

window.mainloop()
