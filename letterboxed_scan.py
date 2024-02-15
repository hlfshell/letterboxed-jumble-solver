import sys
from time import time
from typing import Dict, List, Optional

from letterboxed import Edge, Puzzle, query_puzzle


def are_all_letters_used(puzzle: Puzzle, words: List[str]) -> bool:
    """
    are_all_letters_used checks to see if all letters in the puzzle
    are used at least once in the words provided
    """
    used: Dict[Edge, Dict[str, bool]] = {}
    used[puzzle.left] = {
        puzzle.left.a: False,
        puzzle.left.b: False,
        puzzle.left.c: False,
    }
    used[puzzle.right] = {
        puzzle.right.a: False,
        puzzle.right.b: False,
        puzzle.right.c: False,
    }
    used[puzzle.top] = {
        puzzle.top.a: False,
        puzzle.top.b: False,
        puzzle.top.c: False,
    }
    used[puzzle.bottom] = {
        puzzle.bottom.a: False,
        puzzle.bottom.b: False,
        puzzle.bottom.c: False,
    }

    for word in words:
        for letter in word:
            for edge in puzzle:
                if letter in edge:
                    used[edge][letter] = True

    # Determine if there are any letters not used
    for edge in used:
        for letter in used[edge]:
            if not used[edge][letter]:
                return False

    return True


def word_composition_check(
    remainder: str, puzzle: Puzzle, current_edge: Optional[Edge]
) -> bool:
    """
    Checks to see if the word can be composed of individual
    letters from each edge in the puzzle without repeats
    """
    letter = remainder[0]
    remainder = remainder[1:]
    for edge in puzzle:
        if current_edge == edge:
            continue
        if letter in edge:
            if len(remainder) != 0:
                composable = word_composition_check(remainder, puzzle, edge)
                if composable:
                    return True
            else:
                return True

    return False


def solve(puzzle: Puzzle, wordlist: List[str]) -> List[List[str]]:
    solutions: List[List[str]] = []

    # valid_words is a alphabet delimited list of words that
    # are valid; this is used to limit the search space
    # on our second word search
    valid_words: Dict[str, List[str]] = {}

    for word in wordlist:
        if not word_composition_check(word, puzzle, None):
            continue

        if word[0] not in valid_words:
            valid_words[word[0]] = []
        valid_words[word[0]].append(word)

    # Now scan through all words in valid_words for the
    # second word to try and solve the puzzle
    for letter in valid_words:
        for word in valid_words[letter]:
            last_letter = word[-1]

            if last_letter not in valid_words:
                continue

            for next_word in valid_words[last_letter]:
                if next_word == word:
                    continue

                if are_all_letters_used(puzzle, [word, next_word]):
                    if solutions.count([word, next_word]) == 0:
                        solutions.append([word, next_word])

    solutions.sort(key=lambda x: sum([len(word) for word in x]))

    return solutions


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        print("Please provide a word list")
        exit(1)

    puzzle = query_puzzle()

    print(puzzle)

    # with open("words_list.txt", "r") as f:
    with open(arguments[1], "r") as f:
        # with open("test.txt", "r") as f:
        wordlist = f.readlines()
        wordlist = [word.strip().lower().replace(" ", "") for word in wordlist]

    begin = time()
    solutions = solve(puzzle, wordlist)
    end = time()

    print(f"Found {len(solutions)} solutions in {end - begin} seconds.")
    for i in range(10):
        if i >= len(solutions):
            break
        print(f"\t{i+1} - {solutions[i]}")
