import tkinter as tk


class Grid:
    """
    A simple grid class that can be used to create a grid to show some data

    Attributes:
        data (list): The data to be shown in the grid
            [x][y]
            if mode is color, then enter color names to fill the specific cell
            if mode is letter, then enter text to fill the specific cell (recommended to use only one letter)
        mode (str): The mode of the grid, either 'color' or 'letter'
        height (int): The height of the grid
        width (int): The width of the grid
        title (str): The title of the window
        bg_color (str): The background color of the grid
        font_family (str): The font family of letters if in letter mode

    Return:
         nothing

    Raise:
        TypeError: If the mode is not 'color' or 'letter'

    Samples:
        Grid([['light grey', 'light grey', 'black', 'white', 'dark grey'],
            ['light grey', 'black', 'dark grey', 'grey', 'white'],
            ['grey', 'light grey', 'light grey', 'grey', 'black'],
            ['black', 'grey', 'white', 'light grey', 'light grey'],
            ['dark grey', 'light grey', 'light grey', 'black', 'dark grey']],
            mode="color", height=800, width=800, title="Simple Grid", bg_color="white", font_family="Arial")

        :or:

        Grid([['a', 'b', 'c', 'd', 'e'],
            ['f', 'g', 'h', 'i', 'j'],
            ['k', 'l', 'm', 'n', 'o'],
            ['p', 'q', 'r', 's', 't'],
            ['u', 'v', 'w', 'x', 'y']],
            mode="letter", height=800, width=800, title="Alphabet", bg_color="white", font_family="Calibri")

        :or:

        Grid([['a', 'f', 'k', 'p'], ['b', 'g', 'l', 'q'], ['c', 'h', 'm', 'r']], "letter", 500, 600, "Random", "grey",
            "Calibri")

        :or:

        Grid([['red', 'green', 'blue', 'yellow', 'orange'], ['purple', 'pink', 'brown', 'black', 'white']])

    """

    def __init__(self, data: list, mode="color", height=800, width=800,
                 title="Simple Grid", bg_color="white", font_family="Arial"):
        if mode != "color" and mode != "letter":
            raise TypeError("mode must be either 'color' or 'letter'")

        root = tk.Tk()
        root.title(title)
        root.geometry(f"{width}x{height}")
        root.resizable(False, False)
        root.configure(bg=bg_color)

        canvas = tk.Canvas(root, height=height, width=width, bg=bg_color)
        canvas.pack()

        rows = len(data)
        columns = len(data[0])

        def drawField():
            for row in range(rows):
                for column in range(columns):
                    if mode == "color":
                        x1 = column * width / columns
                        y1 = row * height / rows
                        x2 = (column + 1) * width / columns
                        y2 = (row + 1) * height / rows
                        canvas.create_rectangle(x1, y1, x2, y2, fill=data[row][column])
                    elif mode == "letter":
                        x1 = column * width / columns
                        y1 = row * height / rows
                        x2 = (column + 1) * width / columns
                        y2 = (row + 1) * height / rows
                        if isinstance(data[row][column], list) and len(data[row][column]) == 2:
                            canvas.create_text(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2,
                                               text=str(data[row][column][0]), font=(font_family, int((x2-x1)/2)),
                                               fill=data[row][column][1])
                        else:
                            canvas.create_text(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2,
                                               text=str(data[row][column]), font=(font_family, int((x2-x1)/2)))

        drawField()

        root.mainloop()
