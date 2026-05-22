import sqlite3
import os


def create_database():
    if os.path.exists('users.db'):
        os.remove('users.db')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('DELETE FROM users')

    users = [
        ('user1', 'user123', 'user'),
        ('user2', 'user456', 'user'),
        ('123', '123', 'admin'),
        ('manager', 'manager123', 'admin')
    ]

    cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)

    conn.commit()
    conn.close()
    print("=" * 50)
    print("БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
    print("=" * 50)
    print("Тестовые пользователи:")
    print("  📌 user1 / user123 (роль: user)")
    print("  📌 user2 / user456 (роль: user)")
    print("  📌 123 / 123 (роль: admin)")
    print("  📌 manager / manager123 (роль: admin)")
    print("=" * 50)


def get_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()
    return user


def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, username, role, created_at FROM users ORDER BY id')
    users = cursor.fetchall()

    conn.close()
    return users


def add_user(username, password, role):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, password, role))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    success = cursor.rowcount > 0

    conn.close()
    return success


if __name__ == "__main__":
    create_database()