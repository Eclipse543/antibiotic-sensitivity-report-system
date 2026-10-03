import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "ast_system.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Patient/sample information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            sample_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            age INTEGER,
            sex TEXT,
            specimen TEXT NOT NULL,
            ward TEXT,
            collection_date TEXT
        )
    """)

    # Bacterial isolates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS isolates (
            isolate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            organism TEXT NOT NULL,
            FOREIGN KEY (sample_id)
                REFERENCES samples(sample_id)
        )
    """)

    # Antibiotic susceptibility testing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ast_results (
            ast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            isolate_id INTEGER NOT NULL,
            antibiotic TEXT NOT NULL,
            zone_diameter REAL,
            interpretation TEXT,
            FOREIGN KEY (isolate_id)
                REFERENCES isolates(isolate_id),

	    UNIQUE (isolate_id, antibiotic)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
