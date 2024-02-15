from __future__ import annotations

import csv
import sys
import time
from typing import Dict, List, NamedTuple, Optional, Tuple, Union


class Edge(NamedTuple):
    a: str
    b: str
    c: str


class Puzzle(NamedTuple):
    left: Edge
    right: Edge
    top: Edge
    bottom: Edge

    def __str__(self):
        puzzle = f" __{self.top.a}__{self.top.b}__{self.top.c}__ \n"
        puzzle += f"{self.left.a}|          |{self.right.a}\n"
        puzzle += f"{self.left.b}|          |{self.right.b}\n"
        puzzle += f"{self.left.c}|__________|{self.right.c}\n"
        puzzle += f"   {self.bottom.a}   {self.bottom.b}   {self.bottom.c}   \n"
        return puzzle


class LetterBoxedSolver:
    def __init__(
        self,
        wordlist: Optional[List] = None,
        max_chain: int = -1,
        max_iterations: int = -1,
    ):
        # Our word graph is initiated with a blank letter
        # so we can just branch off of that when searching
        self.word_graph = LetterNode("")
        self.max_chain = max_chain
        self.max_iterations = max_iterations

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

    def are_all_letters_used(self, puzzle: Puzzle, words: List[str]) -> bool:
        """
        are_all_letters_used checks to see if all the letters in the
        puzzle are used at least once in the words provided
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

    def search(self, puzzle: Puzzle) -> List[List[str]]:
        complete_list: List[List[str]] = []
        in_progress_lists: List[List[Tuple[str, Edge]]] = []
        current_list: Tuple[List[str], Edge] = ([], None)

        puzzle_solutions: Dict[str, bool] = {}

        while True:
            current_words = current_list[0]
            current_edge = current_list[1]

            if len(current_words) == 0:
                node = self.word_graph
            else:
                last_letter = current_words[-1][-1]
                node = self.word_graph.get(last_letter)

            results = node.search(puzzle, current_edge=current_edge)
            if results is None and len(in_progress_lists) == 0:
                break
            elif results is None:
                current_list = in_progress_lists.pop(0)
                continue

            # print("results", results)
            for result in results:
                word = result[0]
                edge = result[1]

                # Avoid repeat words in the same chain
                if word in current_words:
                    continue

                word_list = current_list[0].copy()
                word_list.append(word)

                leaf = [word_list, edge]

                if self.are_all_letters_used(puzzle, word_list):
                    # Perform a duplicates check to ensure that
                    # some combination of other edges aren't
                    # reported as a unique answer - while it would
                    # be, we don't report edges in our solver
                    # so it would look like a duplicate. This would
                    # occur in some scenarios where a letter is
                    # duplicated on multiple edges.
                    smashed_words = "_".join(word_list)
                    if smashed_words not in puzzle_solutions:
                        complete_list.append(leaf)
                        puzzle_solutions[smashed_words] = True
                else:
                    # If we limit the chain size, aka how many
                    # word solutions we'll accept, then we
                    # check here if we'll have to match or
                    # exceed that don't even consider it.
                    if self.max_chain > -1:
                        if len(word_list) < self.max_chain:
                            in_progress_lists.append(leaf)
                    else:
                        in_progress_lists.append(leaf)

            if len(in_progress_lists) == 0:
                break

            current_list = in_progress_lists.pop(0)

        # Now that we have the list, limit it to just the words,
        # and let's sort it by lowest amount of words, with the
        # least number of letters leading.
        complete_list = [leaf[0] for leaf in complete_list]
        complete_list.sort(key=lambda x: (len(x), sum([len(word) for word in x])))

        return complete_list

    @staticmethod
    def LoadFromFile(filepath: str) -> LetterBoxedSolver:
        with open(filepath, "r") as file:
            solver = LetterBoxedSolver()
            reader = csv.reader(file)

            for row in reader:
                word = row[0]

                # Clean the word just in case; limit to lowercase
                # and eliminate spaces.
                word = word.strip().lower().replace(" ", "")

                solver.add(word)
            print("done")

        return solver


class LetterNode:
    def __init__(self, letter: str, terminal: bool = False):
        self.letter = letter
        self.terminal = terminal
        self.nodes: Dict[str, LetterNode] = {}

    def word(self) -> bool:
        """
        word returns if a node is demarcated as a word;
        nodes can be marked as such if its a leaf node
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
        self.nodes[node.letter] = node

    def get(self, letter: Union[LetterNode, str]) -> Optional[LetterNode]:
        """
        get retrieves the node by a given LetterNode or letter
        if one is available; otherwise it returns None.
        """
        if isinstance(letter, LetterNode):
            if letter.letter in self.nodes:
                return self.nodes[letter.letter]
            else:
                return None
        elif isinstance(letter, str):
            if letter in self.nodes:
                return self.nodes[letter]
            else:
                return None
        else:
            raise TypeError("node must be of type LetterNode or str")

    def search(
        self, puzzle: Puzzle, current_edge: Optional[Edge] = None
    ) -> List[Tuple[str, Edge]]:
        """
        search accepts a given puzzle, the current edge (which can
        be None for the initial start) and returns a list of all
        possible words that can be spelled with the available
        letters of the puzzle.
        """
        search_results: List[str] = []
        # If our current node is marked as a word, we can return
        # that portion of the word from just this node
        if self.word():
            search_results.append((self.letter, current_edge))

        # Isolate the next edges we can choose from
        if current_edge is not None:
            next_edges = [edge for edge in puzzle if edge != current_edge]
        else:
            next_edges = puzzle

        # For each edge choose-able we can select a single letter
        # from each of the remaining edges at a time. So for each
        # edge we choose each letter, searching with that as our
        # current_edge
        for edge in next_edges:
            for letter in edge:
                current_node = self.get(letter)
                if current_node is None:
                    continue

                results = current_node.search(puzzle, edge)

                # Combine words if any are returned with the current
                # node's letter
                for result in results:
                    word = self.letter + result[0]
                    last_edge = result[1]
                    search_results.append((word, last_edge))

        return search_results


def query_side(side: str) -> Edge:
    edge_raw = input(f"Enter the {side} side:\n")
    edge_raw.strip().lower().replace(" ", "")
    edge = [letter for letter in edge_raw]
    if len(edge) != 3:
        print("Invalid edge")
        return query_side()
    return Edge(edge[0], edge[1], edge[2])


def query_puzzle() -> Puzzle:
    left = query_side("left")
    right = query_side("right")
    top = query_side("top")
    bottom = query_side("bottom")

    puzzle = Puzzle(left, right, top, bottom)

    print("Puzzle:")
    print(puzzle)

    check = input("Is this puzzle correct (y/n)?\n")
    if check == "y" or check == "yes":
        return puzzle
    else:
        return query_puzzle()


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        print("Please provide a word list")
        exit(1)
    else:
        solver = LetterBoxedSolver.LoadFromFile(arguments[1])
        print("Wordlist loaded")

    solver.max_chain = 2

    puzzle = query_puzzle()

    print(puzzle)

    # Time the next portion
    begin = time.time()

    # Search for all possible words and print them
    # sorted by length, largest first
    words = solver.search(puzzle)

    end = time.time()

    print(f"Possible answers: ({len(words)})")
    print(f"Took {end - begin} seconds")
    print("Top ten answers:")
    for i in range(10):
        if i >= len(words):
            break
        print(f"\t{i+1} - {words[i]}")
