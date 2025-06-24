# Wordle Solver Web Interface

A modern web-based interface for the Wordle solver that resembles the original Wordle UI while incorporating all the solver functionality.

## Features

- **Wordle-like UI**: Clean, modern interface that looks and feels like the original Wordle
- **Interactive Game Board**: Visual representation of guesses with color-coded feedback
- **User Guesses**: Enter your own 5-letter words with validation
- **Computer Assistance**: Get optimal guesses or let the computer play
- **Game Management**: Start new games with random or custom words
- **Undo Functionality**: Return to any previous guess state
- **Game History**: View all previous guesses and their results
- **Possible Words**: See how many words remain possible after each guess
- **Answer Toggle**: Show/hide the target word
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure word files are present**:
   - `potential.txt` - List of potential target words
   - `acceptable.txt` - List of acceptable guess words

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:8000
   ```

## How to Use

### Basic Gameplay
1. **Enter a guess**: Type a 5-letter word in the input field
2. **Submit**: Click "Submit" or press Enter
3. **View results**: See color-coded feedback (green = correct, yellow = wrong position, gray = incorrect)
4. **Continue**: Make up to 6 guesses to find the word

### Solver Features
- **Get Optimal Guess**: See what the computer thinks is the best next guess
- **Computer Guess**: Let the computer make the next guess automatically
- **Show Answer**: Toggle visibility of the target word
- **New Game**: Start a fresh game with a random or custom word

### Advanced Features
- **Undo**: Return to any previous guess state
- **History**: View all previous guesses and their statistics
- **Possible Words**: See how many words remain possible after each guess
- **Game Status**: Monitor current guess number and remaining possibilities

## File Structure

```
WordleSolver/
├── app.py                 # Flask web application
├── main.py               # Original Wordle solver logic
├── requirements.txt      # Python dependencies
├── acceptable.txt        # Acceptable guess words
├── potential.txt         # Potential target words
├── templates/
│   └── index.html       # Main HTML template
└── static/
    ├── css/
    │   └── style.css    # CSS styles
    └── js/
        └── script.js    # JavaScript functionality
```

## API Endpoints

The web interface communicates with the backend through these API endpoints:

- `GET /api/game/status` - Get current game status
- `POST /api/game/new` - Start a new game
- `POST /api/game/guess` - Make a guess
- `GET /api/game/optimal-guess` - Get computer's optimal guess
- `POST /api/game/computer-guess` - Make computer's guess
- `GET /api/game/toggle-answer` - Toggle answer visibility
- `POST /api/game/undo` - Undo to a specific guess
- `GET /api/game/history` - Get game history
- `GET /api/game/possible-words/<guess_number>` - Get possible words for a guess

## Technical Details

- **Backend**: Flask web framework with RESTful API
- **Frontend**: Vanilla JavaScript with modern CSS
- **Styling**: Responsive design with CSS Grid and Flexbox
- **Animations**: CSS transitions and keyframes for smooth interactions
- **Word Lists**: Uses the original `potential.txt` and `acceptable.txt` files

## Browser Compatibility

The web interface works on all modern browsers:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## Troubleshooting

- **Port already in use**: Change the port in `app.py` (line 108)
- **Word files not found**: Ensure `potential.txt` and `acceptable.txt` are in the project directory
- **Dependencies not installed**: Run `pip install -r requirements.txt`
