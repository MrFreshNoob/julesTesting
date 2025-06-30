import sqlite3

def init_db():
    conn = sqlite3.connect('game_store.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            gamertag TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            friend_code TEXT UNIQUE NOT NULL
        )
    ''')

    # Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            genre TEXT,
            release_date TEXT,
            developer TEXT,
            image_url TEXT
        )
    ''')

    # Purchases table (associates users and games they own)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')

    # Friends table (many-to-many relationship for users)
    # status: 'pending', 'accepted'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id_1 INTEGER NOT NULL,
            user_id_2 INTEGER NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (user_id_1, user_id_2),
            FOREIGN KEY (user_id_1) REFERENCES users (id),
            FOREIGN KEY (user_id_2) REFERENCES users (id)
        )
    ''')

    # Add some dummy game data
    sample_games = [
        ('CyberRevolt 2077', 'A futuristic open-world RPG.', 59.99, 'RPG', '2023-10-26', 'Future Studios', 'static/images/cyber_revolt.png'),
        ('Pixel Raiders', 'A retro-style platformer adventure.', 19.99, 'Platformer', '2023-05-15', 'Retro Games Inc.', 'static/images/pixel_raiders.png'),
        ('Galaxy Warriors Online', 'A massively multiplayer space combat game.', 39.99, 'MMO', '2024-01-10', 'Cosmic Interactive', 'static/images/galaxy_warriors.png'),
        ('Mystic Forest Chronicles', 'An enchanting puzzle-adventure game.', 29.99, 'Puzzle', '2023-11-01', 'Enigma Games', 'static/images/mystic_forest.png'),
        ('Speed Kingdom', 'A high-octane racing game.', 49.99, 'Racing', '2023-08-20', 'Nitro Works', 'static/images/speed_kingdom.png')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO games (title, description, price, genre, release_date, developer, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_games)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized with tables and sample game data.")
