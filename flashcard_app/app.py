import sqlite3
import logging
import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

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
        self.deck_var = tk.StringVar()
        self.deck_selector = ttk.Combobox(self.root, textvariable=self.deck_var, state='readonly')
        self.deck_selector.pack(fill='x', padx=10, pady=5)
        self.deck_selector.bind("<<ComboboxSelected>>", self.on_deck_selected)

        self.card_listbox = tk.Listbox(self.root)
        self.card_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        self.load_decks_into_selector()


    def load_cards_for_deck(self):
        self.card_listbox.delete(0, tk.END)
        deck_name = self.deck_var.get()
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        result = self.cursor.fetchone()
        if not result:
            return
        deck_id = result[0]
        self.cursor.execute("SELECT id, question FROM cards WHERE deck_id = ?", (deck_id,))
        for card_id, question in self.cursor.fetchall():
            self.card_listbox.insert(tk.END, f"{card_id}: {question}")


    def load_decks_into_selector(self):
        self.cursor.execute("SELECT name FROM decks")
        deck_names = [row[0] for row in self.cursor.fetchall()]
        self.deck_selector['values'] = deck_names
        if deck_names:
            self.deck_selector.set(deck_names[0])
            self.on_deck_selected()

    def on_deck_selected(self, event=None):
        self.status.set(f"Deck selected: {self.deck_var.get()}")
        logging.info(f"Deck selected: {self.deck_var.get()}")
        self.load_cards_for_deck()


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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()
        logging.info("Cards table created or verified.")


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

    def get_selected_deck_id(self):
        deck_name = self.deck_var.get()
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_card(self):
        deck_id = self.get_selected_deck_id()
        if deck_id is None:
            return
        q = simpledialog.askstring("Add Card", "Enter question:")
        a = simpledialog.askstring("Add Card", "Enter answer:")
        if q and a:
            self.cursor.execute("INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)", (deck_id, q, a))
            self.conn.commit()
            logging.info(f"Card added to deck {deck_id}: {q}")
            self.load_cards_for_deck()

    def edit_card(self):
        selected = self.card_listbox.curselection()
        if not selected:
            return
        card_text = self.card_listbox.get(selected[0])
        card_id = int(card_text.split(":")[0])
        self.cursor.execute("SELECT question, answer FROM cards WHERE id = ?", (card_id,))
        q, a = self.cursor.fetchone()
        new_q = simpledialog.askstring("Edit Card", "Edit question:", initialvalue=q)
        new_a = simpledialog.askstring("Edit Card", "Edit answer:", initialvalue=a)
        if new_q and new_a:
            self.cursor.execute("UPDATE cards SET question = ?, answer = ? WHERE id = ?", (new_q, new_a, card_id))
            self.conn.commit()
            logging.info(f"Card {card_id} updated.")
            self.load_cards_for_deck()

    def delete_card(self):
        selected = self.card_listbox.curselection()
        if not selected:
            return
        card_text = self.card_listbox.get(selected[0])
        card_id = int(card_text.split(":")[0])
        self.cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        self.conn.commit()
        logging.info(f"Card {card_id} deleted.")
        self.load_cards_for_deck()


    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        deck_menu = tk.Menu(menubar, tearoff=0)
        deck_menu.add_command(label="Create Deck", command=self.create_deck)
        deck_menu.add_command(label="Delete Deck", command=self.delete_deck)
        deck_menu.add_separator()
        deck_menu.add_command(label="Add Card", command=self.add_card)
        deck_menu.add_command(label="Edit Selected Card", command=self.edit_card)
        deck_menu.add_command(label="Delete Selected Card", command=self.delete_card)
        deck_menu.add_separator()
        deck_menu.add_command(label="Export Deck to CSV", command=self.export_deck_to_csv)
        deck_menu.add_command(label="Import Cards from CSV", command=self.import_cards_from_csv)

        menubar.add_cascade(label="Deck", menu=deck_menu)

        self.root.config(menu=menubar)

    def export_deck_to_csv(self):
        deck_name = self.deck_var.get()
        if not deck_name:
            return
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        deck_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT question, answer FROM cards WHERE deck_id = ?", (deck_id,))
        cards = self.cursor.fetchall()

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        with open(file_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["question", "answer"])
            writer.writerows(cards)

        self.status.set(f"Exported {len(cards)} cards to {file_path}")
        logging.info(f"Exported deck {deck_name} to {file_path}")

    def import_cards_from_csv(self):
        deck_name = self.deck_var.get()
        if not deck_name:
            return
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
        deck_id = self.cursor.fetchone()[0]

        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        imported = 0
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'question' in row and 'answer' in row:
                        self.cursor.execute("INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
                                            (deck_id, row['question'], row['answer']))
                        imported += 1
            self.conn.commit()
        except Exception as e:
            self.status.set(f"Import failed: {str(e)}")
            logging.error(f"Import failed from {file_path}: {e}")
            return

        self.status.set(f"Imported {imported} cards from {file_path}")
        logging.info(f"Imported {imported} cards into deck {deck_name} from {file_path}")
        self.load_cards_for_deck()


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

