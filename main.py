import random
import sqlite3
from datetime import datetime

# Database setup
def setup_database():
    conn = sqlite3.connect("number_guess.db")
    cursor = conn.cursor()

    # Create games table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            guess_count INTEGER NOT NULL,
            secret_number INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def main():
    # Set up the database
    conn = setup_database()
    cursor = conn.cursor()

    print("\n~~~~~ Number Guessing Game ~~~~~\n")
    username = input("Enter your username: ")

    # Check if username exists
    cursor.execute("SELECT username FROM games WHERE username = ?", (username,))
    user_check = cursor.fetchone()

    if not user_check:
        print(f"\nWelcome, {username}! It looks like this is your first time here.")
    else:
        cursor.execute("SELECT COUNT(game_id) FROM games WHERE username = ?", (username,))
        games_played = cursor.fetchone()[0]
        cursor.execute("SELECT MIN(guess_count) FROM games WHERE username = ?", (username,))
        best_game = cursor.fetchone()[0]
        print(f"\nWelcome back, {username}! You have played {games_played} games, and your best game took {best_game} guesses.")

    # Generate random number
    secret_number = random.randint(1, 1000)
    guess_count = 0

    print("\nGuess the secret number between 1 and 1000:")
    while True:
        try:
            guess = int(input())
            guess_count += 1

            if guess < secret_number:
                print("It's higher than that, guess again:")
            elif guess > secret_number:
                print("It's lower than that, guess again:")
            else:
                print(f"\nYou guessed it in {guess_count} tries. The secret number was {secret_number}. Nice job!")
                break
        except ValueError:
            print("That is not an integer, guess again:")

    # Insert game result into the database
    cursor.execute(
        "INSERT INTO games (username, guess_count, secret_number, date) VALUES (?, ?, ?, ?)",
        (username, guess_count, secret_number, datetime.now())
    )
    conn.commit()

    # Close the database connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
