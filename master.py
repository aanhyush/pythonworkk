import random
import json
import requests
from flask import Flask, render_template, session,request
from flask.json import JSONEncoder

class Game:
    def __init__(self, max_guesses):
        self.secret_number = random.randint(1, 100)
        self.max_guesses = max_guesses
        self.num_guesses = 0
        self.game_over = False
        self.result = ""

    def guess(self, guess):
        try:
            guess = int(guess)
        except ValueError:
            self.result = "Please enter a valid integer."
            return
        
        self.num_guesses += 1
        
        if guess < self.secret_number:
            self.result = "Too low. Guess again."
        elif guess > self.secret_number:
            self.result = "Too high. Guess again."
        else:
            self.result = f"Congratulations! You guessed the number in {self.num_guesses} guesses!"
            self.game_over = True
        
        if self.num_guesses == self.max_guesses:
            self.result = f"Sorry, you ran out of guesses. The secret number was {self.secret_number}."
            self.game_over = True

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Game):
            return obj.__dict__
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.secret_key = 'some_secret_key'
app.json_encoder = CustomJSONEncoder

# Joke program
@app.route('/joke')
def joke():
    url = 'https://v2.jokeapi.dev/joke/Any'
    response = requests.get(url)
    joke = response.json()
    if joke['type'] == 'twopart':
        setup = joke['setup']
        punchline = joke['delivery']
    else:
        setup = joke['joke']
        punchline = ''
    return render_template('jokes.html', setup=setup, punchline=punchline)

# Scramble program
# Home page
@app.route('/scramble')
def scramble():
    return render_template('scramble/home.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    # List of words and hints
    word_list = [("python", "A high-level programming language"),
                 ("java", "An object-oriented programming language"),
                 ("javascript", "A scripting language for the web"),
                 ("ruby", "A dynamic, reflective, object-oriented language"),
                 ("perl", "A family of high-level, general-purpose, interpreted languages"),
                 ("php", "A popular server-side scripting language")]

    if request.method == 'POST':
        # Get user's guess
        guess = request.form['guess']

        # Get current word and hint
        word = session['word']
        hint = session['hint']

        # Check if the guess is correct
        if guess == word:
            return render_template('scramble/success.html', word=word)
        else:
            return render_template('scramble/failure.html', hint=hint, scrambled=scramble_word(word))

    # Pick a random word and hint from the list
    word, hint = random.choice(word_list)

    # Scramble the word
    scrambled = scramble_word(word)

    # Store the word and hint in the session
    session['word'] = word
    session['hint'] = hint

    return render_template('scramble/game.html', scrambled=scrambled, hint=hint)

# Helper function to scramble a word
def scramble_word(word):
    return ''.join(random.sample(word, len(word)))

# Number guessing game
@app.route('/number')
def number():
    return render_template('number.html')

@app.route('/play', methods=['POST'])
def play():
    max_guesses = 0
    difficulty = request.form['difficulty']
    
    if difficulty == 'easy':
        max_guesses = 10
    elif difficulty == 'medium':
        max_guesses = 7
    elif difficulty == 'hard':
        max_guesses = 5
    else:
        return render_template('number.html', message="Invalid difficulty level. Please choose either easy, medium, or hard.")
    
    game = Game(max_guesses)
    session['game'] = game
    return render_template('playnumber.html', max_guesses=max_guesses, game=game)

@app.route('/guess', methods=['POST'])
def guess():
    game_dict = session['game']
    game = Game(game_dict['max_guesses'])
    game.__dict__ = game_dict
    guess = request.form['guess']
    game.guess(guess)
    remaining_guesses = game.max_guesses - game.num_guesses
    
    if game.game_over:
        return render_template('resultnumber.html', result=game.result, max_guesses=game.max_guesses, remaining_guesses=remaining_guesses)

    else:
        session['game'] = game.__dict__
        return render_template('playnumber.html', max_guesses=game.max_guesses, game=game)

# Home page
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
