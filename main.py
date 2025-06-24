import random
from collections import defaultdict, Counter
from typing import List, Dict, Set


class WordleSolver:
    def __init__(self, potential_file: str = "potential.txt", acceptable_file: str = "acceptable.txt"):
        """Initialize the Wordle solver with word lists."""
        self.potential_words = self.load_words(potential_file)
        self.acceptable_words = self.load_words(acceptable_file)

        # Game state
        self.target_word = ""
        self.show_answer = False
        self.max_guesses = 6
        self.current_guess = 0

        # Game history for undo functionality
        self.game_history = []  # List of GameState objects
        self.current_possible_words = set(self.potential_words)

        # Initialize first game state
        self.reset_game()

    def load_words(self, filename: str) -> List[str]:
        """Load words from a file, filtering for 5-letter words."""
        try:
            with open(filename, 'r') as f:
                words = [word.strip().upper() for word in f.readlines()]
                return [word for word in words if len(word) == 5 and word.isalpha()]
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using sample words.")
            # Sample words for demonstration
            if "potential" in filename:
                return ["CRANE", "SLATE", "ROATE", "RAISE", "ADIEU", "AUDIO", "HOUSE", "MOUSE", "PHONE", "STONE"]
            else:
                return ["CRANE", "SLATE", "ROATE", "RAISE", "ADIEU", "AUDIO", "HOUSE", "MOUSE", "PHONE", "STONE",
                        "ABOUT", "WORLD", "WOULD", "THERE", "THEIR", "COULD", "OTHER", "AFTER", "FIRST", "NEVER"]

    def reset_game(self, new_target: str = None):
        """Reset the game state."""
        if new_target:
            self.target_word = new_target.upper()
        else:
            self.target_word = random.choice(self.potential_words)

        self.current_guess = 0
        self.current_possible_words = set(self.potential_words)
        self.game_history = []

        # Add initial state
        initial_state = GameState(
            guess_number=0,
            word_guessed="",
            letter_results=[],
            possible_words_before=set(self.potential_words),
            possible_words_after=set(self.potential_words)
        )
        self.game_history.append(initial_state)

    def evaluate_guess(self, guess: str, target: str) -> List[str]:
        """
        Evaluate a guess against the target word.
        Returns list of results: 'CORRECT', 'WRONG_POSITION', 'INCORRECT'
        """
        guess = guess.upper()
        target = target.upper()
        results = [''] * 5
        target_chars = list(target)
        guess_chars = list(guess)

        # First pass: mark correct positions
        for i in range(5):
            if guess_chars[i] == target_chars[i]:
                results[i] = 'CORRECT'
                target_chars[i] = None  # Mark as used
                guess_chars[i] = None  # Mark as processed

        # Second pass: mark wrong positions
        for i in range(5):
            if guess_chars[i] is not None:  # Not already processed
                if guess_chars[i] in target_chars:
                    results[i] = 'WRONG_POSITION'
                    # Mark first occurrence as used
                    target_chars[target_chars.index(guess_chars[i])] = None
                else:
                    results[i] = 'INCORRECT'

        return results

    def filter_words_by_guess(self, possible_words: Set[str], guess: str, results: List[str]) -> Set[str]:
        """Filter possible words based on guess results."""
        filtered_words = set()

        for word in possible_words:
            if self.word_matches_pattern(word, guess, results):
                filtered_words.add(word)

        return filtered_words

    def word_matches_pattern(self, word: str, guess: str, results: List[str]) -> bool:
        """Check if a word matches the pattern from a guess."""
        word = word.upper()
        guess = guess.upper()

        # Count letters in word and guess
        word_count = Counter(word)
        guess_count = Counter(guess)

        # Check each position
        for i in range(5):
            if results[i] == 'CORRECT':
                if word[i] != guess[i]:
                    return False
            elif results[i] == 'WRONG_POSITION':
                if word[i] == guess[i]:  # Letter shouldn't be in this position
                    return False
                if guess[i] not in word:  # Letter should be somewhere in word
                    return False
            elif results[i] == 'INCORRECT':
                # This is tricky - letter might still be in word if it appears elsewhere
                pass

        # More sophisticated check for INCORRECT letters
        for i in range(5):
            if results[i] == 'INCORRECT':
                letter = guess[i]
                # Count how many times this letter appears in correct/wrong positions
                required_count = sum(1 for j in range(5)
                                     if guess[j] == letter and results[j] in ['CORRECT', 'WRONG_POSITION'])

                # Word should have exactly this many of this letter
                if word_count[letter] != required_count:
                    return False

        return True

    def calculate_optimal_guess(self, possible_words: Set[str]) -> str:
        """Calculate the optimal guess that minimizes expected remaining words."""
        if len(possible_words) <= 2:
            return list(possible_words)[0]

        best_word = ""
        best_score = float('inf')

        # Consider all acceptable words as potential guesses
        for guess in self.acceptable_words:
            score = self.calculate_guess_score(guess, possible_words)
            if score < best_score:
                best_score = score
                best_word = guess

        return best_word

    def calculate_guess_score(self, guess: str, possible_words: Set[str]) -> float:
        """Calculate the expected number of remaining words after this guess."""
        pattern_counts = defaultdict(int)

        # For each possible target word, see what pattern this guess would produce
        for target in possible_words:
            results = self.evaluate_guess(guess, target)
            pattern = tuple(results)  # Convert to tuple for hashing
            pattern_counts[pattern] += 1

        # Calculate expected remaining words
        total_words = len(possible_words)
        expected_remaining = 0

        for pattern, count in pattern_counts.items():
            probability = count / total_words
            remaining_after_pattern = len(self.filter_words_by_guess(possible_words, guess, list(pattern)))
            expected_remaining += probability * remaining_after_pattern

        return expected_remaining

    def make_guess(self, word: str, is_user_guess: bool = True) -> Dict:
        """Make a guess and return the results."""
        word = word.upper()

        # Validate guess
        if is_user_guess and word not in [w.upper() for w in self.acceptable_words]:
            return {
                'valid': False,
                'message': f"'{word}' is not in the acceptable words list."
            }

        if self.current_guess >= self.max_guesses:
            return {
                'valid': False,
                'message': "Maximum number of guesses reached."
            }

        # Evaluate the guess
        results = self.evaluate_guess(word, self.target_word)

        # Filter possible words
        new_possible_words = self.filter_words_by_guess(self.current_possible_words, word, results)

        # Create game state
        self.current_guess += 1
        game_state = GameState(
            guess_number=self.current_guess,
            word_guessed=word,
            letter_results=results,
            possible_words_before=set(self.current_possible_words),
            possible_words_after=set(new_possible_words)
        )

        self.game_history.append(game_state)
        self.current_possible_words = new_possible_words

        # Check win condition
        is_correct = word == self.target_word
        game_over = is_correct or self.current_guess >= self.max_guesses

        return {
            'valid': True,
            'guess_number': self.current_guess,
            'word': word,
            'results': results,
            'possible_words_before': len(game_state.possible_words_before),
            'possible_words_after': len(game_state.possible_words_after),
            'is_correct': is_correct,
            'game_over': game_over,
            'won': is_correct,
            'message': self.format_guess_result(word, results, len(game_state.possible_words_after))
        }

    def format_guess_result(self, word: str, results: List[str], remaining_words: int) -> str:
        """Format the guess result for display."""
        result_symbols = {
            'CORRECT': '🟩',
            'WRONG_POSITION': '🟨',
            'INCORRECT': '⬜'
        }

        visual = ''.join(result_symbols[result] for result in results)
        return f"Guess {self.current_guess}: {word} {visual} - {remaining_words} words remaining"

    def undo_to_guess(self, guess_number: int) -> bool:
        """Undo to a specific guess number (0 = start of game)."""
        if guess_number < 0 or guess_number >= len(self.game_history):
            return False

        # Reset to the state after the specified guess
        target_state = self.game_history[guess_number]
        self.current_guess = guess_number
        self.current_possible_words = set(target_state.possible_words_after)

        # Remove later states from history
        self.game_history = self.game_history[:guess_number + 1]

        return True

    def get_computer_guess(self) -> str:
        """Get the computer's optimal guess."""
        return self.calculate_optimal_guess(self.current_possible_words)

    def toggle_answer_visibility(self):
        """Toggle whether the answer is shown."""
        self.show_answer = not self.show_answer

    def get_game_status(self) -> Dict:
        """Get current game status."""
        return {
            'current_guess': self.current_guess,
            'max_guesses': self.max_guesses,
            'target_word': self.target_word if self.show_answer else "Hidden",
            'show_answer': self.show_answer,
            'possible_words_count': len(self.current_possible_words),
            'game_over': self.current_guess >= self.max_guesses or
                         (len(self.game_history) > 1 and
                          self.game_history[-1].word_guessed == self.target_word)
        }

    def get_possible_words(self, guess_number: int = None) -> Set[str]:
        """Get possible words before/after a specific guess."""
        if guess_number is None:
            return self.current_possible_words

        if guess_number < 0 or guess_number >= len(self.game_history):
            return set()

        return self.game_history[guess_number].possible_words_after

    def get_game_history(self) -> List:
        """Get the game history."""
        return self.game_history[1:]  # Skip initial state


class GameState:
    """Represents the state of the game at a particular guess."""

    def __init__(self, guess_number: int, word_guessed: str, letter_results: List[str],
                 possible_words_before: Set[str], possible_words_after: Set[str]):
        self.guess_number = guess_number
        self.word_guessed = word_guessed
        self.letter_results = letter_results
        self.possible_words_before = possible_words_before
        self.possible_words_after = possible_words_after


def main():
    """Main game loop with interactive menu."""
    solver = WordleSolver()

    print("🎯 Wordle Solver 🎯")
    print("=" * 50)

    while True:
        print("\n📋 Menu:")
        print("1. Make your own guess")
        print("2. Get computer's optimal guess")
        print("3. Make computer's guess")
        print("4. Show/hide answer")
        print("5. Generate new game")
        print("6. Show game status")
        print("7. Show possible words")
        print("8. Show game history")
        print("9. Undo to previous guess")
        print("10. Quit")

        choice = input("\nEnter your choice (1-10): ").strip()

        if choice == '1':
            word = input("Enter your 5-letter guess: ").strip()
            if len(word) != 5:
                print("Please enter exactly 5 letters.")
                continue

            result = solver.make_guess(word, is_user_guess=True)
            if result['valid']:
                print(f"\n{result['message']}")
                if result['game_over']:
                    if result['won']:
                        print("🎉 Congratulations! You won!")
                    else:
                        print(f"😞 Game over! The word was: {solver.target_word}")
            else:
                print(f"❌ {result['message']}")

        elif choice == '2':
            if len(solver.current_possible_words) == 0:
                print("No possible words remaining!")
            else:
                optimal_guess = solver.get_computer_guess()
                print(f"💡 Computer's optimal guess: {optimal_guess}")

        elif choice == '3':
            if len(solver.current_possible_words) == 0:
                print("No possible words remaining!")
            else:
                optimal_guess = solver.get_computer_guess()
                print(f"🤖 Computer guesses: {optimal_guess}")
                result = solver.make_guess(optimal_guess, is_user_guess=False)
                if result['valid']:
                    print(f"\n{result['message']}")
                    if result['game_over']:
                        if result['won']:
                            print("🎉 Computer won!")
                        else:
                            print(f"😞 Game over! The word was: {solver.target_word}")
                else:
                    print(f"❌ {result['message']}")

        elif choice == '4':
            solver.toggle_answer_visibility()
            status = solver.get_game_status()
            print(f"Answer: {status['target_word']}")

        elif choice == '5':
            print("Choose new game option:")
            print("1. Random word")
            print("2. Choose specific word")
            sub_choice = input("Enter choice (1-2): ").strip()

            if sub_choice == '1':
                solver.reset_game()
                print("🎮 New game started with random word!")
            elif sub_choice == '2':
                word = input("Enter the target word: ").strip().upper()
                if len(word) == 5 and word in [w.upper() for w in solver.potential_words]:
                    solver.reset_game(word)
                    print(f"🎮 New game started!")
                else:
                    print("Invalid word. Must be 5 letters and in potential words list.")

        elif choice == '6':
            status = solver.get_game_status()
            print(f"\n📊 Game Status:")
            print(f"Guess: {status['current_guess']}/{status['max_guesses']}")
            print(f"Answer: {status['target_word']}")
            print(f"Possible words remaining: {status['possible_words_count']}")
            print(f"Game over: {status['game_over']}")

        elif choice == '7':
            print("Show possible words for which guess?")
            print("0. Current state")
            for i, state in enumerate(solver.get_game_history(), 1):
                print(f"{i}. After guess {i}: {state.word_guessed}")

            try:
                guess_num = int(input("Enter choice: "))
                if guess_num == 0:
                    words = solver.get_possible_words()
                    print(f"\n📝 Current possible words ({len(words)}):")
                else:
                    words = solver.get_possible_words(guess_num)
                    print(f"\n📝 Possible words after guess {guess_num} ({len(words)}):")

                if len(words) <= 20:
                    print(", ".join(sorted(words)))
                else:
                    word_list = sorted(words)
                    print(", ".join(word_list))
            except (ValueError, IndexError):
                print("Invalid choice.")

        elif choice == '8':
            history = solver.get_game_history()
            if not history:
                print("No guesses made yet.")
            else:
                print("\n📜 Game History:")
                for state in history:
                    result_symbols = {
                        'CORRECT': '🟩',
                        'WRONG_POSITION': '🟨',
                        'INCORRECT': '⬜'
                    }
                    visual = ''.join(result_symbols.get(r, '❓') for r in state.letter_results)
                    print(f"Guess {state.guess_number}: {state.word_guessed} {visual} "
                          f"({len(state.possible_words_before)} → {len(state.possible_words_after)} words)")

        elif choice == '9':
            history = solver.get_game_history()
            if not history:
                print("No guesses to undo.")
                continue

            print("Undo to which guess?")
            print("0. Start of game")
            for i, state in enumerate(history, 1):
                print(f"{i}. After {state.word_guessed}")

            try:
                guess_num = int(input("Enter choice: "))
                if solver.undo_to_guess(guess_num):
                    print(f"✅ Undone to guess {guess_num}")
                else:
                    print("❌ Invalid guess number")
            except ValueError:
                print("Invalid input.")

        elif choice == '10':
            print("Thanks for playing! 👋")
            break

        else:
            print("Invalid choice. Please enter 1-10.")


if __name__ == "__main__":
    main()
