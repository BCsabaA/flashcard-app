import sqlite3
import logging
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Learning App")
        self.root.geometry("800x600")
        
        self.setup_logging()
        self.setup_database()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def setup_logging(self):
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Application started.")

    def setup_database(self):
        self.conn = sqlite3.connect("data/flashcards.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        self.conn.commit()
        logging.info("Database initialized with 'decks' table.")

    def create_deck(self):
        name = simpledialog.askstring("Create Deck", "Enter deck name:")
        if name:
            try:
                self.cursor.execute("INSERT INTO decks (name) VALUES (?)", (name,))
                self.conn.commit()
                self.status.set(f"Deck '{name}' created.")
                logging.info(f"Deck '{name}' created.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Deck name must be unique.")
                logging.warning(f"Deck creation failed: '{name}' already exists.")

    def delete_deck(self):
        name = simpledialog.askstring("Delete Deck", "Enter deck name to delete:")
        if name:
            self.cursor.execute("DELETE FROM decks WHERE name = ?", (name,))
            self.conn.commit()
            self.status.set(f"Deck '{name}' deleted.")
            logging.info(f"Deck '{name}' deleted.")

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        deck_menu = tk.Menu(menubar, tearoff=0)
        deck_menu.add_command(label="Create Deck", command=self.create_deck)
        deck_menu.add_command(label="Delete Deck", command=self.delete_deck)
        menubar.add_cascade(label="Deck", menu=deck_menu)

        self.root.config(menu=menubar)

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        placeholder_label = ttk.Label(self.main_frame, text="Main area (placeholder)")
        placeholder_label.pack(expand=True)

    def create_status_bar(self):
        self.status = tk.StringVar()
        self.status.set("Ready")

        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_closing(self):
        logging.info("Application closed.")
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

