#!/bin/bash

PSQL="psql --username=freecodecamp --dbname=number_guess -t --no-align -c"

echo -e "\n~~~~~ Number Guessing Game ~~~~~\n"
echo -e "Enter your username:"
read USERNAME

# check if username exists
USERNAME_CHECK=$($PSQL "SELECT username FROM games WHERE username = '$USERNAME'")

if [[ -z $USERNAME_CHECK ]]
then
  echo -e "\nWelcome, $USERNAME! It looks like this is your first time here."

else
  GAMES_PLAYED=$($PSQL "SELECT COUNT(game_id) FROM games WHERE username='$USERNAME'")
  BEST_GAME=$($PSQL "SELECT MIN(guess_count) FROM games WHERE username='$USERNAME'")
  echo -e "\nWelcome back, $USERNAME! You have played $GAMES_PLAYED games, and your best game took $BEST_GAME guesses."
fi

# generate random number
SECRET_NUMBER=$(( RANDOM % 1000 + 1 ))

GUESS_COUNT=0

echo -e "\nGuess the secret number between 1 and 1000:"
read GUESS

until [[ $GUESS == $SECRET_NUMBER ]]
do
  # check if input is valid
  if [[ ! $GUESS =~ ^[0-9]+$ ]]
  then
    echo -e "That is not an integer, guess again:"
    read GUESS
    ((GUESS_COUNT++))
  else
    if [[ $GUESS < $SECRET_NUMBER ]]
    then
      echo -e "It's higher than that, guess again:"
      read GUESS
      ((GUESS_COUNT++))
    else
      echo -e "It's lower than that, guess again:"
      read GUESS 
      ((GUESS_COUNT++))
    fi
  fi
done

# increment count when guess is correct
((GUESS_COUNT++))

# update database with game result
INSERT_GAME_RESULT=$($PSQL "INSERT INTO games(username, guess_count, secret_number) VALUES('$USERNAME', $GUESS_COUNT, $SECRET_NUMBER)")

echo -e "\nYou guessed it in $GUESS_COUNT tries. The secret number was $SECRET_NUMBER. Nice job!"