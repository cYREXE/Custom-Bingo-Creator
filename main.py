import tkinter as tk
from tkinter import messagebox
import random
import textwrap

GRID_SIZE = 5
FREE_SPACE = "FREE"
DEFAULT_SQUARE_SIZE = 100
MAX_FONT_SIZE = 16
MIN_FONT_SIZE = 8

# Hardcoded Templates
TEMPLATES = {
    "Title": [

    ],

}


# Core Bingo Game Logic
class BingoGame:
    def __init__(self, root, title, card):
        self.root = root
        self.root.geometry("600x600") 
        self.title = title
        self.card = card
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.squares = {}  # To store square references
        self.colors = {}  # To track square colors
        self.root.bind("<Configure>", self.update_canvas)
        self.canvas.bind("<Button-1>", self.handle_click)  # Bind clicks to the canvas
        self.update_canvas(None)

    def update_canvas(self, event):
        """Update the canvas elements when the window is resized."""
        self.canvas.delete("all")
        self.square_size = max(
            min(self.canvas.winfo_width() // GRID_SIZE, self.canvas.winfo_height() // GRID_SIZE),
            20,
        )
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x0 = col * self.square_size
                y0 = row * self.square_size
                x1 = x0 + self.square_size
                y1 = y0 + self.square_size

                # Draw the square
                square = self.canvas.create_rectangle(
                    x0, y0, x1, y1, fill="white", outline="black"
                )
                self.squares[(row, col)] = (square, x0, y0, x1, y1)
                self.colors[(row, col)] = "white"

                # Add text to the square
                text = self.card[row][col]
                max_width = max(int(self.square_size / 10), 1)
                wrapped_text = wrap_text(text, max_width)
                font_size = get_font_size(self.canvas, wrapped_text, self.square_size)
                self.canvas.create_text(
                    (x0 + x1) / 2,
                    (y0 + y1) / 2,
                    text=wrapped_text,
                    font=(f"Arial", font_size),
                    fill="black",
                    justify="center",
                )

    def handle_click(self, event):
        """Handle mouse click and determine which square was clicked."""
        for (row, col), (square, x0, y0, x1, y1) in self.squares.items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self.toggle_square(row, col)
                break

    def toggle_square(self, row, col):
        """Toggle the color of a square when clicked."""
        current_color = self.colors[(row, col)]
        new_color = "yellow" if current_color == "white" else "white"
        self.canvas.itemconfig(self.squares[(row, col)][0], fill=new_color)
        self.colors[(row, col)] = new_color

        if self.check_bingo():
            self.flash_bingo()

    def check_bingo(self):
        """Check if there is a Bingo."""
        # Check rows and columns
        for i in range(GRID_SIZE):
            if all(self.colors[(i, j)] == "yellow" for j in range(GRID_SIZE)):
                self.bingo_line = [(i, j) for j in range(GRID_SIZE)]
                return True
            if all(self.colors[(j, i)] == "yellow" for j in range(GRID_SIZE)):
                self.bingo_line = [(j, i) for j in range(GRID_SIZE)]
                return True

        # Check diagonals
        if all(self.colors[(i, i)] == "yellow" for i in range(GRID_SIZE)):
            self.bingo_line = [(i, i) for i in range(GRID_SIZE)]
            return True
        if all(self.colors[(i, GRID_SIZE - i - 1)] == "yellow" for i in range(GRID_SIZE)):
            self.bingo_line = [(i, GRID_SIZE - i - 1) for i in range(GRID_SIZE)]
            return True

        return False

    def flash_bingo(self):
        """Flash the Bingo row, column, or diagonal green."""
        self.flash_state = True
        self.flash_line()

    def flash_line(self):
        """Toggle the color of the Bingo line."""
        color = "green" if self.flash_state else "yellow"
        for row, col in self.bingo_line:
            self.canvas.itemconfig(self.squares[(row, col)][0], fill=color)
        self.flash_state = not self.flash_state
        self.root.after(500, self.flash_line)


# Utility Functions
def create_bingo_card(contents):
    """Create a Bingo card grid from a list of contents with randomized placement."""
    if len(contents) > GRID_SIZE**2 - 1:
        selected_contents = random.sample(contents, GRID_SIZE**2 - 1)
    else:
        selected_contents = contents[:]

    random.shuffle(selected_contents)  # Shuffle the selected items for random placement

    card = []
    for i in range(GRID_SIZE):
        card.append([""] * GRID_SIZE)

    mid = GRID_SIZE // 2
    index = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if row == mid and col == mid:
                card[row][col] = FREE_SPACE  # Center square is always "FREE"
            else:
                card[row][col] = selected_contents[index]
                index += 1

    return card

def wrap_text(text, max_width):
    """Wrap text into multiple lines to fit within a square."""
    if max_width <= 0:
        max_width = 1
    return textwrap.fill(text, width=max_width)


def get_font_size(canvas, text, square_size):
    """Calculate the font size to fit the text within a dynamically sized square."""
    font_size = MAX_FONT_SIZE
    while font_size >= MIN_FONT_SIZE:
        temp_id = canvas.create_text(0, 0, text=text, font=(f"Arial", font_size))
        bbox = canvas.bbox(temp_id)
        canvas.delete(temp_id)

        if bbox[2] - bbox[0] <= square_size - 10 and bbox[3] - bbox[1] <= square_size - 10:
            return font_size
        font_size -= 1
    return font_size


# Screens
def main_menu():
    """Display the initial screen with options to Host or Join a Game."""
    root = tk.Tk()
    root.title("Bingo Game")

    tk.Label(root, text="Welcome to Bingo!", font=("Arial", 24)).pack(pady=20)

    tk.Button(root, text="Host a Game", font=("Arial", 16), command=lambda: (root.destroy(), template_selection())).pack(pady=10)

    root.mainloop()


def template_selection():
    """Allow the user to choose a template or create a custom card."""
    template_window = tk.Tk()
    template_window.title("Choose a Template")

    tk.Label(template_window, text="Choose a Bingo Template or Create Your Own:", font=("Arial", 14)).pack(pady=10)

    for template_name, items in TEMPLATES.items():
        tk.Button(
            template_window,
            text=template_name,
            font=("Arial", 12),
            command=lambda name=template_name, items=items: use_template(template_window, name, items)
        ).pack(pady=5)

    tk.Button(
        template_window,
        text="Create Custom Card",
        font=("Arial", 12),
        command=lambda: (template_window.destroy(), setup_page())
    ).pack(pady=10)

    template_window.mainloop()


def use_template(template_window, title, items):
    """Use a selected template to start the game."""
    template_window.destroy()
    root = tk.Tk()
    root.title(title)
    card = create_bingo_card(items)
    BingoGame(root, title, card)
    root.mainloop()


def setup_page():
    """Display the setup page for entering title and contents."""
    def submit_details():
        title = title_entry.get()
        contents = contents_text.get("1.0", tk.END).strip().splitlines()

        if not title or len(contents) < GRID_SIZE**2 - 1:
            messagebox.showerror("Error", "Please provide a title and at least 24 items.")
            return

        setup_window.destroy()
        root = tk.Tk()
        root.title("Bingo Game")
        card = create_bingo_card(contents)
        BingoGame(root, title, card)
        root.mainloop()

    setup_window = tk.Tk()
    setup_window.title("Bingo Setup")

    tk.Label(setup_window, text="Bingo Title:", font=("Arial", 14)).pack(pady=5)
    title_entry = tk.Entry(setup_window, font=("Arial", 14), width=30)
    title_entry.pack(pady=5)

    tk.Label(setup_window, text="Bingo Items (one per line):", font=("Arial", 14)).pack(pady=5)
    contents_text = tk.Text(setup_window, font=("Arial", 12), width=30, height=10)
    contents_text.pack(pady=5)

    tk.Button(setup_window, text="Create Bingo Card", font=("Arial", 14), command=submit_details).pack(pady=10)

    setup_window.mainloop()


# Run the Application
main_menu()
