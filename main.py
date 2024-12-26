import random
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game', methods=['POST'])
def game():
    conn = setup_database()
    cursor = conn.cursor()

    username = request.form['username']

    # Check if username exists
    cursor.execute("SELECT username FROM games WHERE username = ?", (username,))
    user_check = cursor.fetchone()

    if not user_check:
        welcome_message = f"Welcome, {username}! It looks like this is your first time here."
        games_played = 0
        best_game = "N/A"
    else:
        cursor.execute("SELECT COUNT(game_id) FROM games WHERE username = ?", (username,))
        games_played = cursor.fetchone()[0]
        cursor.execute("SELECT MIN(guess_count) FROM games WHERE username = ?", (username,))
        best_game = cursor.fetchone()[0]
        welcome_message = f"Welcome back, {username}! You have played {games_played} games, and your best game took {best_game} guesses."

    # Generate random number
    secret_number = random.randint(1, 1000)
    conn.commit()

    return render_template('game.html', username=username, welcome_message=welcome_message, secret_number=secret_number, guess_count=0)

@app.route('/guess', methods=['POST'])
def guess():
    guess = request.form['guess']
    username = request.form['username']
    secret_number = int(request.form['secret_number'])
    guess_count = int(request.form['guess_count'])

    # Retrieve previous guesses from the session or initialize a new list
    previous_guesses = request.form.getlist('previous_guesses')

    try:
        guess = int(guess)
        guess_count += 1
        previous_guesses.append(str(guess))

        if guess < secret_number:
            return render_template('game.html', username=username, message="It's higher than that, guess again:", secret_number=secret_number, guess_count=guess_count, previous_guesses=previous_guesses)
        elif guess > secret_number:
            return render_template('game.html', username=username, message="It's lower than that, guess again:", secret_number=secret_number, guess_count=guess_count, previous_guesses=previous_guesses)
        else:
            # Insert game result into the database
            conn = setup_database()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO games (username, guess_count, secret_number, date) VALUES (?, ?, ?, ?)",
                (username, guess_count, secret_number, datetime.now().isoformat())
            )
            conn.commit()

            return render_template('game.html', username=username, message=f"Congrats! You guessed it in {guess_count} tries. The secret number was {secret_number}.", secret_number=secret_number, guess_count=guess_count, previous_guesses=previous_guesses, game_over=True)
    except ValueError:
        return render_template('game.html', username=username, message="Please enter a valid integer guess.", secret_number=secret_number, guess_count=guess_count, previous_guesses=previous_guesses)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))