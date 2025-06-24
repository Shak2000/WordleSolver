// Global variables
let currentRow = 0;
let currentTile = 0;
let gameOver = false;

// DOM elements
const board = document.getElementById('board');
const wordInput = document.getElementById('wordInput');
const submitGuess = document.getElementById('submitGuess');
const optimalGuess = document.getElementById('optimalGuess');
const computerGuess = document.getElementById('computerGuess');
const toggleAnswer = document.getElementById('toggleAnswer');
const newGame = document.getElementById('newGame');
const undoButton = document.getElementById('undoButton');
const showHistory = document.getElementById('showHistory');
const showPossibleWords = document.getElementById('showPossibleWords');

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    initializeBoard();
    loadGameStatus();
    setupEventListeners();
});

function initializeBoard() {
    board.innerHTML = '';
    for (let i = 0; i < 6; i++) {
        const row = document.createElement('div');
        row.className = 'row';
        row.id = `row-${i}`;
        
        for (let j = 0; j < 5; j++) {
            const tile = document.createElement('div');
            tile.className = 'tile';
            tile.id = `tile-${i}-${j}`;
            row.appendChild(tile);
        }
        
        board.appendChild(row);
    }
}

function setupEventListeners() {
    // Input handling
    wordInput.addEventListener('input', function(e) {
        const value = e.target.value.toUpperCase();
        e.target.value = value;
        
        if (value.length === 5) {
            submitGuess.disabled = false;
        } else {
            submitGuess.disabled = true;
        }
    });

    wordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && wordInput.value.length === 5) {
            submitUserGuess();
        }
    });

    // Button event listeners
    submitGuess.addEventListener('click', submitUserGuess);
    optimalGuess.addEventListener('click', getOptimalGuess);
    computerGuess.addEventListener('click', makeComputerGuess);
    toggleAnswer.addEventListener('click', toggleAnswerVisibility);
    newGame.addEventListener('click', showNewGameModal);
    undoButton.addEventListener('click', showUndoModal);
    showHistory.addEventListener('click', showHistoryModal);
    showPossibleWords.addEventListener('click', showPossibleWordsModal);

    // Modal event listeners
    document.getElementById('randomWord').addEventListener('click', startRandomGame);
    document.getElementById('customWord').addEventListener('click', showCustomWordInput);
    document.getElementById('startCustomGame').addEventListener('click', startCustomGame);
    document.getElementById('undoToStart').addEventListener('click', () => undoToGuess(0));
}

async function loadGameStatus() {
    try {
        const response = await fetch('/api/game/status');
        const status = await response.json();
        updateGameStatus(status);
        updateBoardFromHistory();
    } catch (error) {
        showMessage('Error loading game status', 'error');
    }
}

async function submitUserGuess() {
    const word = wordInput.value.trim();
    if (word.length !== 5) {
        showMessage('Please enter exactly 5 letters', 'error');
        return;
    }

    try {
        const response = await fetch('/api/game/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ word: word, is_user_guess: true })
        });

        const result = await response.json();
        
        if (result.valid) {
            displayGuessResult(result);
            wordInput.value = '';
            submitGuess.disabled = true;
            
            if (result.game_over) {
                gameOver = true;
                if (result.won) {
                    showMessage('🎉 Congratulations! You won!', 'success');
                } else {
                    showMessage(`😞 Game over! The word was: ${result.target_word}`, 'error');
                }
            }
        } else {
            showMessage(result.message, 'error');
            shakeRow(currentRow);
        }
        
        loadGameStatus();
    } catch (error) {
        showMessage('Error submitting guess', 'error');
    }
}

async function getOptimalGuess() {
    try {
        const response = await fetch('/api/game/optimal-guess');
        const result = await response.json();
        
        if (result.success) {
            showMessage(`💡 Computer's optimal guess: ${result.guess}`, 'info');
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('Error getting optimal guess', 'error');
    }
}

async function makeComputerGuess() {
    try {
        const response = await fetch('/api/game/computer-guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();
        
        if (result.valid) {
            displayGuessResult(result);
            
            if (result.game_over) {
                gameOver = true;
                if (result.won) {
                    showMessage('🎉 Computer won!', 'success');
                } else {
                    showMessage(`😞 Game over! The word was: ${result.target_word}`, 'error');
                }
            }
        } else {
            showMessage(result.message, 'error');
        }
        
        loadGameStatus();
    } catch (error) {
        showMessage('Error making computer guess', 'error');
    }
}

function displayGuessResult(result) {
    const row = document.getElementById(`row-${result.guess_number - 1}`);
    const tiles = row.children;
    
    // Fill in the word
    for (let i = 0; i < 5; i++) {
        tiles[i].textContent = result.word[i];
        tiles[i].classList.add('filled');
    }
    
    // Animate and color the tiles
    setTimeout(() => {
        for (let i = 0; i < 5; i++) {
            tiles[i].classList.add('flip');
            
            setTimeout(() => {
                tiles[i].classList.remove('flip');
                
                if (result.results[i] === 'CORRECT') {
                    tiles[i].classList.add('correct');
                } else if (result.results[i] === 'WRONG_POSITION') {
                    tiles[i].classList.add('wrong-position');
                } else {
                    tiles[i].classList.add('incorrect');
                }
            }, 300);
        }
    }, 500);
    
    showMessage(result.message, 'success');
}

async function toggleAnswerVisibility() {
    try {
        const response = await fetch('/api/game/toggle-answer');
        const result = await response.json();
        
        const targetWordElement = document.getElementById('targetWord');
        const toggleButton = document.getElementById('toggleAnswer');
        
        if (result.show_answer) {
            targetWordElement.textContent = result.target_word;
            toggleButton.textContent = 'Hide Answer';
        } else {
            targetWordElement.textContent = 'Hidden';
            toggleButton.textContent = 'Show Answer';
        }
    } catch (error) {
        showMessage('Error toggling answer visibility', 'error');
    }
}

function showNewGameModal() {
    document.getElementById('newGameModal').style.display = 'block';
}

function showCustomWordInput() {
    document.getElementById('customWordInput').style.display = 'flex';
}

async function startRandomGame() {
    try {
        const response = await fetch('/api/game/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });

        const result = await response.json();
        
        if (result.success) {
            resetGame();
            showMessage(result.message, 'success');
            closeModal('newGameModal');
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('Error starting new game', 'error');
    }
}

async function startCustomGame() {
    const word = document.getElementById('customWordField').value.trim().toUpperCase();
    
    if (word.length !== 5) {
        showMessage('Please enter exactly 5 letters', 'error');
        return;
    }

    try {
        const response = await fetch('/api/game/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target_word: word })
        });

        const result = await response.json();
        
        if (result.success) {
            resetGame();
            showMessage(result.message, 'success');
            closeModal('newGameModal');
            document.getElementById('customWordField').value = '';
            document.getElementById('customWordInput').style.display = 'none';
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('Error starting custom game', 'error');
    }
}

function showUndoModal() {
    loadUndoOptions();
    document.getElementById('undoModal').style.display = 'block';
}

async function loadUndoOptions() {
    try {
        const response = await fetch('/api/game/history');
        const history = await response.json();
        
        const undoButtons = document.getElementById('undoButtons');
        undoButtons.innerHTML = '';
        
        history.forEach((item, index) => {
            const button = document.createElement('button');
            button.className = 'undo-btn';
            button.textContent = `After ${item.word_guessed} (${item.possible_words_after} words)`;
            button.onclick = () => undoToGuess(index + 1);
            undoButtons.appendChild(button);
        });
    } catch (error) {
        showMessage('Error loading undo options', 'error');
    }
}

async function undoToGuess(guessNumber) {
    try {
        const response = await fetch('/api/game/undo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guess_number: guessNumber })
        });

        const result = await response.json();
        
        if (result.success) {
            resetGame();
            showMessage(result.message, 'success');
            closeModal('undoModal');
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('Error undoing guess', 'error');
    }
}

function showHistoryModal() {
    loadHistory();
    document.getElementById('historyModal').style.display = 'block';
}

async function loadHistory() {
    try {
        const response = await fetch('/api/game/history');
        const history = await response.json();
        
        const historyContent = document.getElementById('historyContent');
        historyContent.innerHTML = '';
        
        if (history.length === 0) {
            historyContent.innerHTML = '<p>No guesses made yet.</p>';
            return;
        }
        
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const word = document.createElement('div');
            word.className = 'history-word';
            word.textContent = item.word_guessed;
            
            const result = document.createElement('div');
            result.className = 'history-result';
            
            item.letter_results.forEach(letterResult => {
                const resultTile = document.createElement('div');
                resultTile.className = `result-tile ${letterResult.toLowerCase().replace('_', '-')}`;
                resultTile.textContent = letterResult === 'CORRECT' ? '🟩' : 
                                       letterResult === 'WRONG_POSITION' ? '🟨' : '⬜';
                result.appendChild(resultTile);
            });
            
            const stats = document.createElement('div');
            stats.className = 'history-stats';
            stats.textContent = `${item.possible_words_before} → ${item.possible_words_after} words`;
            
            historyItem.appendChild(word);
            historyItem.appendChild(result);
            historyItem.appendChild(stats);
            historyContent.appendChild(historyItem);
        });
    } catch (error) {
        showMessage('Error loading history', 'error');
    }
}

function showPossibleWordsModal() {
    loadPossibleWordsOptions();
    document.getElementById('possibleWordsModal').style.display = 'block';
}

async function loadPossibleWordsOptions() {
    try {
        const response = await fetch('/api/game/history');
        const history = await response.json();
        
        const historySelect = document.getElementById('historySelect');
        historySelect.innerHTML = '<option value="0">Current state</option>';
        
        history.forEach((item, index) => {
            const option = document.createElement('option');
            option.value = index + 1;
            option.textContent = `After guess ${index + 1}: ${item.word_guessed}`;
            historySelect.appendChild(option);
        });
        
        loadPossibleWords(0);
    } catch (error) {
        showMessage('Error loading possible words options', 'error');
    }
}

document.getElementById('historySelect').addEventListener('change', function() {
    loadPossibleWords(parseInt(this.value));
});

async function loadPossibleWords(guessNumber) {
    try {
        const response = await fetch(`/api/game/possible-words/${guessNumber}`);
        const result = await response.json();
        
        const possibleWordsContent = document.getElementById('possibleWordsContent');
        
        if (result.count === 0) {
            possibleWordsContent.innerHTML = '<p>No possible words.</p>';
            return;
        }
        
        const wordsList = document.createElement('div');
        wordsList.className = 'words-list';
        
        result.words.forEach(word => {
            const wordItem = document.createElement('div');
            wordItem.className = 'word-item';
            wordItem.textContent = word;
            wordsList.appendChild(wordItem);
        });
        
        possibleWordsContent.innerHTML = '';
        possibleWordsContent.appendChild(wordsList);
        
        const countInfo = document.createElement('p');
        countInfo.textContent = `${result.count} possible words`;
        countInfo.style.marginTop = '10px';
        countInfo.style.fontWeight = '600';
        possibleWordsContent.appendChild(countInfo);
    } catch (error) {
        showMessage('Error loading possible words', 'error');
    }
}

function updateGameStatus(status) {
    document.getElementById('currentGuess').textContent = status.current_guess;
    document.getElementById('possibleWordsCount').textContent = status.possible_words_count;
    document.getElementById('targetWord').textContent = status.target_word;
    
    gameOver = status.game_over;
    
    // Update button states
    submitGuess.disabled = gameOver;
    optimalGuess.disabled = gameOver;
    computerGuess.disabled = gameOver;
    wordInput.disabled = gameOver;
}

async function updateBoardFromHistory() {
    try {
        const response = await fetch('/api/game/history');
        const history = await response.json();
        
        // Clear board
        for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 5; j++) {
                const tile = document.getElementById(`tile-${i}-${j}`);
                tile.textContent = '';
                tile.className = 'tile';
            }
        }
        
        // Fill in history
        history.forEach((item, index) => {
            const row = document.getElementById(`row-${index}`);
            const tiles = row.children;
            
            for (let i = 0; i < 5; i++) {
                tiles[i].textContent = item.word_guessed[i];
                tiles[i].classList.add('filled');
                
                if (item.letter_results[i] === 'CORRECT') {
                    tiles[i].classList.add('correct');
                } else if (item.letter_results[i] === 'WRONG_POSITION') {
                    tiles[i].classList.add('wrong-position');
                } else {
                    tiles[i].classList.add('incorrect');
                }
            }
        });
    } catch (error) {
        console.error('Error updating board from history:', error);
    }
}

function resetGame() {
    currentRow = 0;
    currentTile = 0;
    gameOver = false;
    
    // Clear input
    wordInput.value = '';
    submitGuess.disabled = true;
    
    // Clear board
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 5; j++) {
            const tile = document.getElementById(`tile-${i}-${j}`);
            tile.textContent = '';
            tile.className = 'tile';
        }
    }
    
    // Re-enable inputs
    submitGuess.disabled = false;
    optimalGuess.disabled = false;
    computerGuess.disabled = false;
    wordInput.disabled = false;
    
    loadGameStatus();
}

function shakeRow(rowIndex) {
    const row = document.getElementById(`row-${rowIndex}`);
    row.classList.add('shake');
    setTimeout(() => {
        row.classList.remove('shake');
    }, 500);
}

function showMessage(text, type) {
    const messageContainer = document.getElementById('messageContainer');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    messageContainer.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 5000);
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
