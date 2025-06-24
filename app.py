from flask import Flask, render_template, request, jsonify
from main import WordleSolver
import os

app = Flask(__name__)

# Global solver instance
solver = WordleSolver()

@app.route('/')
def index():
    """Main page with Wordle UI."""
    return render_template('index.html')

@app.route('/api/game/status')
def get_game_status():
    """Get current game status."""
    return jsonify(solver.get_game_status())

@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Start a new game."""
    data = request.get_json()
    target_word = data.get('target_word', None)
    
    if target_word:
        if len(target_word) == 5 and target_word.upper() in [w.upper() for w in solver.potential_words]:
            solver.reset_game(target_word.upper())
            return jsonify({'success': True, 'message': 'New game started with custom word'})
        else:
            return jsonify({'success': False, 'message': 'Invalid word. Must be 5 letters and in potential words list.'})
    else:
        solver.reset_game()
        return jsonify({'success': True, 'message': 'New game started with random word'})

@app.route('/api/game/guess', methods=['POST'])
def make_guess():
    """Make a guess."""
    data = request.get_json()
    word = data.get('word', '').strip().upper()
    is_user_guess = data.get('is_user_guess', True)
    
    if len(word) != 5:
        return jsonify({'valid': False, 'message': 'Please enter exactly 5 letters.'})
    
    result = solver.make_guess(word, is_user_guess=is_user_guess)
    return jsonify(result)

@app.route('/api/game/optimal-guess')
def get_optimal_guess():
    """Get the computer's optimal guess."""
    if len(solver.current_possible_words) == 0:
        return jsonify({'success': False, 'message': 'No possible words remaining!'})
    
    optimal_guess = solver.get_computer_guess()
    return jsonify({'success': True, 'guess': optimal_guess})

@app.route('/api/game/computer-guess', methods=['POST'])
def make_computer_guess():
    """Make the computer's optimal guess."""
    if len(solver.current_possible_words) == 0:
        return jsonify({'valid': False, 'message': 'No possible words remaining!'})
    
    optimal_guess = solver.get_computer_guess()
    result = solver.make_guess(optimal_guess, is_user_guess=False)
    return jsonify(result)

@app.route('/api/game/toggle-answer')
def toggle_answer():
    """Toggle answer visibility."""
    solver.toggle_answer_visibility()
    status = solver.get_game_status()
    return jsonify({'show_answer': status['show_answer'], 'target_word': status['target_word']})

@app.route('/api/game/undo', methods=['POST'])
def undo_guess():
    """Undo to a specific guess."""
    data = request.get_json()
    guess_number = data.get('guess_number', 0)
    
    success = solver.undo_to_guess(guess_number)
    if success:
        return jsonify({'success': True, 'message': f'Undone to guess {guess_number}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid guess number'})

@app.route('/api/game/history')
def get_history():
    """Get game history."""
    history = solver.get_game_history()
    return jsonify([{
        'guess_number': state.guess_number,
        'word_guessed': state.word_guessed,
        'letter_results': state.letter_results,
        'possible_words_before': len(state.possible_words_before),
        'possible_words_after': len(state.possible_words_after)
    } for state in history])

@app.route('/api/game/possible-words/<int:guess_number>')
def get_possible_words(guess_number):
    """Get possible words for a specific guess number."""
    if guess_number == 0:
        words = list(solver.get_possible_words())
    else:
        words = list(solver.get_possible_words(guess_number))
    
    return jsonify({
        'guess_number': guess_number,
        'words': sorted(words),
        'count': len(words)
    })

@app.route('/api/game/current-possible-words')
def get_current_possible_words():
    """Get current possible words."""
    words = list(solver.current_possible_words)
    return jsonify({
        'words': sorted(words),
        'count': len(words)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
