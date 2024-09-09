import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

import sys


from PIL import Image, ImageTk





## Load Character image
def load_image(file_path, size):
    img = Image.open(file_path)
    img = img.resize(size, Image.NEAREST)  # NEAREST keeps the pixel art look
    return ImageTk.PhotoImage(img)

## resize_images
def resize_image(input_path, output_path, size=(50, 50)):
    with Image.open(input_path) as img:
        img = img.resize(size, Image.LANCZOS)  # Updated to use Image.LANCZOS
        img.save(output_path)

resize_image("start_game.png", "start_game_resized.png", size=(50, 50))
resize_image("up.png", "up_resized.png", size=(50, 50))
resize_image("left.png", "left_resized.png", size=(50, 50))
resize_image("down.png", "down_resized.png", size=(50, 50))
resize_image("right.png", "right_resized.png", size=(50, 50))
resize_image("solve.png", "solve_resized.png", size=(50, 50))



class Maze():
    def __init__(self, filename):

        with open(filename) as f:
            contents = f.read()
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determinar la altura y el ancho del laberinto.
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Mantener un registro de las paredes
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None


    def solve_maze_and_animate(self, frontier_class):
        """Solve the maze using the given frontier (Stack/Queue) and start the animation."""
        frontier = frontier_class()
        self.maze.solve(frontier)

        # Get the solution path (cells) from the maze
        if self.maze.solution:
            self.solution_path = self.maze.solution[1]
            # Animate character along the solution path
            self.animate_solution()


    def animate_solution(self):
        """Animate the character following the solution path."""
        if self.solution_path:
            next_step = self.solution_path.pop(0)
            self.move_character_to(next_step[1], next_step[0])
            # Schedule the next step in the animation
            self.window.after(300, self.animate_solution)  # Adjust speed as needed


    def move_character_to(self, col, row):
        """Move the character to the specified (col, row) position."""
        self.update_character(col * self.cell_size, row * self.cell_size)


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result





    def solve(self, frontier):
        start_time = time.perf_counter()  # Start timing

        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        frontier.add(start)

        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                
                end_time = time.perf_counter()  # End timing
                elapsed_time = end_time - start_time
                print(f"Time taken: {elapsed_time:.6f} seconds")
                return

            self.explored.add(node.state)

            # Add neighbors to the frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)



    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)




    #########



    def play(self):
        """
        Allows the user to play the maze by controlling the player until they choose to solve it.
        """
        player_pos = self.start
        print("Use W/A/S/D to move. Type 'solve' to let the algorithm solve the maze.")

        while True:
            self.print_with_player(player_pos)
            move = input("Move (W/A/S/D) or 'solve': ").lower()

            if move == "solve":
                # Update the starting point to the player's last position
                self.start = player_pos
                break

            new_pos = self.get_new_position(player_pos, move)
            if new_pos and not self.walls[new_pos[0]][new_pos[1]]:
                player_pos = new_pos

            if player_pos == self.goal:
                print("You reached the goal! Well done!")
                return
        
        self.choose_algorithm()




    def get_new_position(self, position, move):
        row, col = position
        if move == "w":
            return (row - 1, col)
        elif move == "s":
            return (row + 1, col)
        elif move == "a":
            return (row, col - 1)
        elif move == "d":
            return (row, col + 1)
        else:
            print("Invalid move. Use W, A, S, D.")
            return None

    def print_with_player(self, player_pos):
        """
        Prints the maze with the player's current position.
        """
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif (i, j) == player_pos:
                    print("P", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def choose_algorithm(self):
        """
        Allows the user to choose between StackFrontier and QueueFrontier to solve the maze.
        """
        while True:
            choice = input("Choose solving method (stack/queue): ").lower()
            if choice == "stack":
                frontier = StackFrontier()
                break
            elif choice == "queue":
                frontier = QueueFrontier()
                break
            else:
                print("Invalid choice. Type 'stack' or 'queue'.")

        print("Solving...")
        self.solve(frontier)
        print("Solution:")
        print("Estados explorados:",self.num_explored)
        print("Solución:")
        self.print()



class StackFrontier():
    
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class MazeApp:
    def __init__(self, maze_files):
        self.maze_files = maze_files
        self.current_level = 0
        self.cell_size = 50
        self.player_pos = (0, 0)
        
        # Create the main window
        self.window = tk.Tk()
        self.window.title("Maze Game")
        
        # Set the background to dark
        self.window.configure(bg='#1c1c1c')  # Dark background color

        # Create GUI components
        self.create_gui()

        # Example images, adapt them as needed
        self.character_img = load_image("pixel_character.png", size=(50, 50))  
        self.character_x = self.player_pos[1] * 50  
        self.character_y = self.player_pos[0] * 50  
        self.grass_img = load_image("grass.png", size=(50, 50))  
        self.tree_img = load_image("tree.png", size=(50, 50))  
        self.path_trace_img = load_image("trace.png", size=(50, 50))  
        self.goal_img = load_image("goal.png", size=(50, 50))  

        self.sprite_sheet = Image.open("pixel_character.png")
        self.frame_size = (48, 64)  # Assuming each frame is 50x50 pixels
        self.frames = self.load_frames()
        self.current_frame = 0
        

        # Initialize player position

        self.character_x = self.player_pos[1] * 50
        self.character_y = self.player_pos[0] * 50


    def load_frames(self):
        frames = []
        # Assuming the sprite sheet is laid out in a grid
        sheet_width, sheet_height = self.sprite_sheet.size
        cols = sheet_width // self.frame_size[0]
        rows = sheet_height // self.frame_size[1]

        for row in range(rows):
            for col in range(cols):
                left = col * self.frame_size[0]
                top = row * self.frame_size[1]
                right = left + self.frame_size[0]
                bottom = top + self.frame_size[1]
                frame = self.sprite_sheet.crop((left, top, right, bottom))
                frames.append(ImageTk.PhotoImage(frame))

        return frames



    def update_character(self, x, y):
        """
        Update the position of the character on the canvas.
        """


        self.canvas.delete("character")  # Clear old character position
        self.character_x = x
        self.character_y = y
        # self.canvas.create_image(x, y, anchor=tk.NW, image=self.character_img, tags="character")

        self.canvas.create_image(x, y, anchor=tk.NW, image=self.frames[self.current_frame], tags="character")

    def start_game(self):
        selected_level = self.level_var.get()
        self.current_level = self.maze_files.index(selected_level)
        self.load_level(self.current_level)

    def load_level(self, level_index):
        self.maze = Maze(self.maze_files[level_index])
        self.player_pos = self.maze.start
        self.canvas.config(width=self.maze.width * 50, height=self.maze.height * 50)
        self.draw_maze()
        self.update_character(self.character_x, self.character_y)  # Initial character position

    def clear_maze(self):
        self.canvas.delete("all")

    def next_level(self):
        if self.current_level < len(self.maze_files) - 1:
            self.current_level += 1
            messagebox.showinfo("Level Complete", "Proceeding to the next level!")
            self.load_level(self.current_level)
        else:
            messagebox.showinfo("Game Complete", "You completed all the levels!")
            self.window.quit()

    def create_gui(self):
        # Create Canvas for maze display
        self.canvas = tk.Canvas(self.window, width=800, height=600, bg='#333333')  # Dark canvas background
        self.canvas.pack()

        # Create control frame
        self.control_frame = tk.Frame(self.window, bg='#1c1c1c')  # Dark background for control frame
        self.control_frame.pack()

        # Style configuration for dark theme
        style = ttk.Style()
        style.theme_use("default")  # Use the default theme
        style.configure('TButton', font=('Helvetica', 12), padding=10, background='#333333', foreground='#ffffff')  # Dark button
        style.map('TButton', background=[('active', '#444444')], foreground=[('active', '#ffffff')])  # Hover effect

        # Load images for buttons
        start_img = ImageTk.PhotoImage(Image.open("start_game_resized.png"))
        up_img = ImageTk.PhotoImage(Image.open("up_resized.png"))
        left_img = ImageTk.PhotoImage(Image.open("left_resized.png"))
        down_img = ImageTk.PhotoImage(Image.open("down_resized.png"))
        right_img = ImageTk.PhotoImage(Image.open("right_resized.png"))
        solve_img = ImageTk.PhotoImage(Image.open("solve_resized.png"))

        # Create a menu to select levels
        self.level_var = tk.StringVar()
        self.level_var.set(self.maze_files[0])

        self.level_menu = tk.OptionMenu(self.control_frame, self.level_var, *self.maze_files)
        self.level_menu.config(bg='#333333', fg='#ffffff', activebackground='#444444', activeforeground='#ffffff')
        self.level_menu.grid(row=0, column=0, padx=5, pady=5)

        # Create buttons
        self.start_button = ttk.Button(self.control_frame, text="Start Game", image=start_img, compound="left", command=self.start_game)
        self.start_button.image = start_img  # Keep a reference to avoid garbage collection
        self.start_button.grid(row=0, column=1, padx=5, pady=5)

        # Control buttons with images
        self.up_button = ttk.Button(self.control_frame, image=up_img, command=lambda: self.move("up"))
        self.up_button.image = up_img
        self.up_button.grid(row=1, column=1, padx=5, pady=5)

        self.left_button = ttk.Button(self.control_frame, image=left_img, command=lambda: self.move("left"))
        self.left_button.image = left_img
        self.left_button.grid(row=2, column=0, padx=5, pady=5)

        self.down_button = ttk.Button(self.control_frame, image=down_img, command=lambda: self.move("down"))
        self.down_button.image = down_img
        self.down_button.grid(row=2, column=1, padx=5, pady=5)

        self.right_button = ttk.Button(self.control_frame, image=right_img, command=lambda: self.move("right"))
        self.right_button.image = right_img
        self.right_button.grid(row=2, column=2, padx=5, pady=5)

        self.solve_button = ttk.Button(self.control_frame, text="Solve", image=solve_img, compound="left", command=self.solve_maze)
        self.solve_button.image = solve_img
        self.solve_button.grid(row=1, column=2, padx=5, pady=5)


        self.window.bind("<w>", lambda event: self.move("up"))
        self.window.bind("<a>", lambda event: self.move("left"))
        self.window.bind("<s>", lambda event: self.move("down"))
        self.window.bind("<d>", lambda event: self.move("right"))

    def draw_maze(self):
        """
        Draw the maze on the canvas. Replaces empty cells with grass.
        """


        self.clear_maze()
        solution = self.maze.solution[1] if self.maze.solution is not None else None

        for i, row in enumerate(self.maze.walls):
            for j, col in enumerate(row):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                if col:
                    # If it's a wall, fill it with a color (or image if desired)
                    # self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill="#ffffff")
                    # self.canvas.create_image(x0, y0, anchor=tk.NW, image=self.grass_img)
                    self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill="black")

                    # self.canvas.create_image(x0, y0, anchor=tk.NW, image=self.grass_img)
                    self.canvas.create_image(x0, y0, anchor=tk.NW, image=self.tree_img)
                else:
                    # If it's an empty cell, place grass
                    self.canvas.create_image(x0, y0, anchor=tk.NW, image=self.grass_img)


                if (i, j) == self.maze.start:
                    # Red for the starting position

                    self.canvas.create_image(j * 50, i * 50, anchor=tk.NW, image=self.path_trace_img)  # Trace image
                    
                elif (i, j) == self.maze.goal:
                    # Green for the goal
                    self.canvas.create_image(j * 50, i * 50, anchor=tk.NW, image=self.goal_img)  # Goal image
                # elif (i, j) == self.player_pos:
                #     # Blue for the player's current position
                #     self.canvas.create_image(j * 50, i * 50, anchor=tk.NW, image=self.character_img)  # Player image
                elif solution is not None and (i, j) in solution:
                    # Yellow or a trace image for the solution path
                    self.canvas.create_image(j * 50, i * 50, anchor=tk.NW, image=self.path_trace_img)  # Trace image

        # Update the character's position on top of the maze
        self.update_character(self.player_pos[1] * 50, (self.player_pos[0] -.4) * 50)




                # Now overlay the solution path, start, goal, and player


    def move(self, direction):
            new_pos = self.get_new_position(self.player_pos, direction)
            if new_pos and not self.maze.walls[new_pos[0]][new_pos[1]]:
                self.player_pos = new_pos
                self.character_x = new_pos[1] * 50
                self.character_y = new_pos[0] * 50
                if (direction == "up"):
                    self.current_frame = 0
                    # self.current_frame = (self.current_frame) % len(self.frames)  # Change frame
                elif (direction == "down"):
                    self.current_frame = 6


                elif (direction == "right"):
                    self.current_frame = 3

                elif (direction == "left"):
                    self.current_frame = 9

                self.draw_maze()
                print(direction)
            if self.player_pos == self.maze.goal:
                messagebox.showinfo("Congrats!", "You reached the goal!")
                self.next_level()

    def get_new_position(self, position, direction):
        row, col = position
        if direction == "up":
            return (row - 1, col) if row > 0 else None
        elif direction == "down":
            return (row + 1, col) if row < self.maze.height - 1 else None
        elif direction == "left":
            return (row, col - 1) if col > 0 else None
        elif direction == "right":
            return (row, col + 1) if col < self.maze.width - 1 else None

    def solve_maze(self):
        self.maze.start = self.player_pos
        frontier_choice = messagebox.askquestion("Solve", "Choose 'yes' for StackFrontier, 'no' for QueueFrontier")
        frontier = StackFrontier() if frontier_choice == "yes" else QueueFrontier()

        try:
            self.maze.solve(frontier)
            messagebox.showinfo("Solved", f"Maze solved with {self.maze.num_explored} states explored!")
            self.draw_maze()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.window.mainloop()




if len(sys.argv) < 2:
    sys.exit("Usage: python maze_gui.py maze1.txt maze2.txt ...")

maze_files = sys.argv[1:]
app = MazeApp(maze_files)
app.run()
