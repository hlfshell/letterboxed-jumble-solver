from __future__ import annotations

import csv
import sys
from typing import List, Optional, Union


class JumbleSolver:
    def __init__(self, wordlist: Optional[List] = None):
        # Our word graph is initiated with a blank letter
        # so we can just branch off of that when searching
        self.word_graph = LetterNode("")

        if wordlist is not None:
            for word in wordlist:
                self.add_word(word)

    def add(self, word: str):
        """
        add_word appends a word to our internal tree graph
        of possible words.
        """
        letters: List[str] = list(word)

        current_node = self.word_graph

        for letter in letters:
            # If we have a node for this letter
            # already, utilize it
            node = current_node.get(letter)

            # If not, create a fresh node
            if node is None:
                node = LetterNode(letter)
                current_node.add(node)

            # ...and continue onto the next letter
            current_node = node

        # Mark the leaf node as terminal, in case
        # another word builds off of it. ie; do->dog
        current_node.terminal = True

    def search(self, word: str) -> List[str]:
        """
        search accepts a word and performs a query across the
        tree starting with root node. It returns a list of all
        possible words
        """
        return self.word_graph.search(list(word))

    @staticmethod
    def LoadFromFile(filename: str) -> JumbleSolver:
        with open(filename, "r") as file:
            solver = JumbleSolver()
            reader = csv.reader(file)

            for row in reader:
                word = row[0]

                # Clean the word just in case; limit to lowercase
                # and eliminate spaces.
                word = word.strip().lower().replace(" ", "")

                solver.add(word)

        return solver


class LetterNode:
    def __init__(self, letter: str, terminal: bool = False) -> None:
        self.letter = letter
        self.terminal = terminal
        self.nodes: List[LetterNode] = []

    def word(self) -> bool:
        """
        word returns if a node is demarcated as a word;
        nodes can be markes as such if its a leaf node
        *or* if its a marked "terminal", aka the end of
        a smaller word ie: sad->sadder - sad is a word
        despite not being a leaf node, as many words
        build off of those three letters.
        """
        return len(self.nodes) == 0 or self.terminal

    def add(self, node: LetterNode):
        """
        add appends a node to our current node
        """
        self.nodes.append(node)

    def get(self, letter: Union[LetterNode, str]) -> Optional[LetterNode]:
        """
        get returns the requested node (be it a node or a string
        letter) if it exists, or None otherwise.
        """
        for node in self.nodes:
            if isinstance(letter, LetterNode):
                if node == letter:
                    return node
            elif isinstance(letter, str):
                if node.letter == letter:
                    return node
            else:
                raise TypeError("node must be of type LetterNode or str")

        return None

    def search(self, letters: List[str]) -> List[str]:
        """
        search accepts a set of letters and then performs a query
        down our node's branches for words that utilize those
        letters. To do this, we traverse each possible letter
        combination recursively. Every time we meet a terminal
        (leaf or demarcated terminal) node, we have found a word.
        We then return up the recursive chain to form the words
        discovered throughout our burrowing.
        """
        words: List[str] = []
        # If our current node is marked as a word, we can return
        # that portion of the word from just this node
        if self.word():
            words.append(self.letter)

        # We iterate through each letter available as our
        # next target levels through  the tree
        for index, letter in enumerate(letters):
            current_node = self.get(letter)
            # If the current node does not exist, we must
            # skip it as there is nothing more to search
            if current_node is None:
                continue

            # Ignoring our current letter, isolate all remaining
            # letters
            remaining_letters = letters[:index] + letters[index + 1 :]

            # Search the current target node with the remaining
            # letters
            found_words = current_node.search(remaining_letters)

            # Combine words if any were returned with the current
            # node's letter.
            for word in found_words:
                word = self.letter + word
                if word not in words:
                    words.append(word)

        return words

    def __str__(self) -> str:
        nodestrings = ""
        for node in self.nodes:
            nodestrings += f"({node})"
        return f"({self.letter})->[{nodestrings}]"

    def __eq__(self, other: LetterNode) -> bool:
        return self.letter == other.letter


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        print("Please provide a word list")
        exit(1)
    else:
        solver = JumbleSolver.LoadFromFile(arguments[1])
        print("Wordlist loaded")

    while True:
        # Prompt the user to enter a word
        word = input("Enter a word: ")
        # Set the word to lower case, strip spaces
        word = word.lower().strip().replace(" ", "")

        # Search for all possible words and print them
        # sorted by length, largest first
        words = solver.search(word)
        words.sort(key=len, reverse=True)
        print(f"Possible words: ({len(words)})")
        print(words)
