"""
Minesweeper Game Launcher

This script initializes and runs the Minesweeper game, using a predefined
state directory to save or load game progress.

Modules:
    - os: Provides functionalities to interact with the operating system.
    - minesweeper: The game module that contains the run function.

Usage:
    Run this script directly to start the game.
"""

import os
import minesweeper

if __name__ == '__main__':
    minesweeper.run(os.path.join(os.path.dirname(__file__), 'state'))
