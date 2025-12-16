#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# KMOM10 Typing Trainer – startpunkt
# Krav: inga klasser, inga list/dict comprehensions, ingen zip, inga lambda

import os
import sys
from typing_utils import (
    EASY_FILE,
    MEDIUM_FILE,
    HARD_FILE,
    SCORES_FILE,
    run_test,
    print_scores_grouped,
)

MENU_TEXT = (
    "\n1. Start typing test with file 'easy.txt'\n"
    "2. Start typing test with file 'medium.txt'\n"
    "3. Start typing test with file 'hard.txt'\n"
    "4. Print saved results from 'scores.txt'\n"
    "q. Quit program\n"
)

def ensure_workdir() -> None:
    """Ensure program is run from typing folder by adjusting sys.path for imports.
    Also verify that texts folder exists.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    texts_dir = os.path.join(base_dir, "texts")
    if not os.path.isdir(texts_dir):
        print("Missing 'texts' directory. Create 'texts' and add easy.txt/medium.txt/hard.txt.")
        sys.exit(1)

def prompt_menu_choice() -> str:
    choice = input(MENU_TEXT + ">>> ").strip()
    return choice

def start_flow(filename: str, difficulty: str) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "texts", filename)
    if not os.path.isfile(file_path):
        print("File not found:", file_path)
        return
    run_test(file_path, difficulty, SCORES_FILE)

def main() -> None:
    ensure_workdir()
    while True:
        choice = prompt_menu_choice()
        if choice == "1":
            start_flow(EASY_FILE, "easy")
        elif choice == "2":
            start_flow(MEDIUM_FILE, "medium")
        elif choice == "3":
            start_flow(HARD_FILE, "hard")
        elif choice == "4":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            scores_path = os.path.join(base_dir, SCORES_FILE)
            print_scores_grouped(scores_path)
        elif choice.lower() == "q":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, 4 or q.")

if __name__ == "__main__":
    main()
