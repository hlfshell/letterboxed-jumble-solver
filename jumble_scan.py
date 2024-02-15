import csv
import sys
from typing import List


def build_base_letter_count(word: str) -> dict[str, int]:
    """
    build_base_letter_count builds a dictionary of letters
    and their counts from a given word.
    """
    letter_count: dict[str, int] = {}

    for letter in word:
        if letter in letter_count:
            letter_count[letter] += 1
        else:
            letter_count[letter] = 1

    return letter_count


def word_composition_check(base_letters: dict[str, int], word: str) -> bool:
    """
    word_composition_check confirms that a given word can
    be formed from letters within the base word, without
    letter re-use. Smaller words is allowed.
    This is accomplished by moving through the word list and
    comparing it to the base letters count dict. If the letter
    from a word X is not in the dict, then the word cannot
    exist; return False. If the letter is in the dict,
    decrement the count. If the count is less than 0, we have
    used that letter too often and thus the word cannot exist;
    return False. If we make it through this process, then the
    word must be possible with our available letters, and we
    return True.
    """
    for letter in word:
        if letter not in base_letters:
            return False
        else:
            base_letters[letter] -= 1

            if base_letters[letter] < 0:
                return False

    return True


def jumble_solve(filename: str, base_word: str) -> List[str]:
    """
    jumble_solve scans through the given wordlist and
    determines what words are possible out of it. It
    solves the jumble while loading the word list as
    opposed to my other solution, which creates a
    reusable graph approach. For single use or longer
    jumbles, this is faster.
    """

    # Get base letter count
    base_letters = build_base_letter_count(base_word)

    # Load our word list
    words: List[str] = []
    with open(filename, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            word = row[0]
            word = word.strip().lower().replace(" ", "")

            # Note - dict({}) is a performant way to copy a
            # shallow dict, since we don't want to actually
            # modify the count in our scoped base_letters
            if word_composition_check(dict(base_letters), word):
                words.append(word)

    return words


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        print("Please provide a word list")
        exit(1)

    wordlist = arguments[1]

    while True:
        # Prompt the user to enter a word
        word = input("Enter a word: ")
        # Set the word to lower case, strip spaces
        word = word.lower().strip().replace(" ", "")

        # Search for all possible words and print them
        # sorted by length, largest first
        words = jumble_solve(wordlist, word)
        words.sort(key=len, reverse=True)
        print(f"Possible words: ({len(words)})")
        print(words)
