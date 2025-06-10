import sqlite3
import os

def test_database_setup():
    if not os.path.exists("data/flashcards.db"):
        raise AssertionError("Database not found.")
    conn = sqlite3.connect("data/flashcards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    assert "decks" in tables
    assert "cards" in tables
    conn.close()
    print("✔ test_database_setup passed")

if __name__ == "__main__":
    test_database_setup()
