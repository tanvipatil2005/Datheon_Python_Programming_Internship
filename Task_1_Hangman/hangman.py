import os
import random

# ASCII art stages from 6 lives left (index 0) down to 0 lives left (index 6)
HANGMAN_STAGES = [
    """
       +---+
       |   |
           |
           |
           |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
           |
           |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
       |   |
           |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
      /|   |
           |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
      /|\\  |
           |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
      /|\\  |
      /    |
           |
    =========
    """,
    """
       +---+
       |   |
       O   |
      /|\\  |
      / \\  |
           |
    =========
    """
]

def load_words(filename="words.txt"):
    """Loads words from the downloaded text file, or uses a fallback list."""
    fallback_words = [
        "PYTHON", "DEVELOPER", "ALGORITHM", "VARIABLE", "FUNCTION",
        "COMPILER", "TERMINAL", "DATABASE", "KEYBOARD", "INTERFACE"
    ]
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            words = [line.strip().upper() for line in file if line.strip().isalpha() and len(line.strip()) >= 4]
            if words:
                return words
    return fallback_words

def get_initial_hints(secret_word):
    """Reveals 1 unique letter for words <= 6 chars, or 2 unique letters for longer words."""
    unique_letters = list(set(secret_word))
    if len(unique_letters) <= 2:
        return set()
    num_hints = 2 if len(secret_word) >= 7 else 1
    return set(random.sample(unique_letters, num_hints))

def play_single_round(words):
    """Runs one complete round of Hangman."""
    secret_word = random.choice(words)
    hint_letters = get_initial_hints(secret_word)
    guessed_letters = set(hint_letters)
    max_mistakes = 6
    mistakes = 0

    print("\n" + "=" * 45)
    print("      NEW ROUND - CONSOLE HANGMAN GAME")
    print("=" * 45)
    if hint_letters:
        print(f"Hint provided! Revealed letter(s): {', '.join(sorted(hint_letters))}")

    while mistakes < max_mistakes:
        print(HANGMAN_STAGES[mistakes])

        masked_word = " ".join([letter if letter in guessed_letters else "_" for letter in secret_word])
        print(f"Word ({len(secret_word)} letters): {masked_word}")
        print(f"Attempts Left: {max_mistakes - mistakes}")
        print(f"Revealed / Guessed: {', '.join(sorted(guessed_letters)) if guessed_letters else 'None'}")
        print("-" * 45)

        # Win condition
        if "_" not in masked_word:
            print(f"\nCONGRATULATIONS! You guessed the word: {secret_word}")
            return

        guess = input("Guess a single letter: ").strip().upper()

        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Please enter a single alphabet letter.\n")
            continue

        if guess in guessed_letters:
            print(f"'{guess}' is already revealed/guessed. No life deducted!\n")
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"Good job! '{guess}' is in the word.\n")
        else:
            mistakes += 1
            print(f"Wrong guess! '{guess}' is not in the word.\n")

    # Defeat screen
    print(HANGMAN_STAGES[max_mistakes])
    print("=" * 45)
    print("GAME OVER! You ran out of attempts.")
    print(f"The secret word was: {secret_word}")
    print("=" * 45)

def main():
    words = load_words()
    while True:
        play_single_round(words)
        while True:
            again = input("\nCan you play again? (y/n): ").strip().lower()
            if again in ("y", "n"):
                break
            print("Invalid choice! Please enter 'y' for Yes or 'n' for No.")
        if again == "n":
            print("\nThanks for playing Hangman! Goodbye.")
            break

if __name__ == "__main__":
    main()