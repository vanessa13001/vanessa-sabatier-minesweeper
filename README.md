# Minesweeper

A classic Minesweeper game implemented using Pygame.

## Installation

1. Install Python 3 and Pygame library.
2. Clone the repository and navigate to the project directory.

## Usage

1. Run the `run.py` script to start the game.
2. Use the left mouse button to open tiles and the right mouse button to mark tiles as mines (flags).
3. The game has different difficulty levels (Bronze, Silver, Gold, Diamond, Ruby) that can be selected from the GUI.
4. The game automatically saves the current state and loads it when the game is restarted.

## API

The main game logic is implemented in the `game.py` file, which includes the following classes:

- `Game`: The main game class that handles the game loop, user input, and game state management.
- `Timer`: A class that executes an event after a specified time interval.
- `create_count_tiles`: A function that creates the tile images for the mine counts.

The `board.py` file contains the `Board` class, which represents the game board and handles the game logic, such as opening tiles, marking mines, and detecting game over conditions.

The `gui.py` file includes various GUI elements, such as `Label`, `Button`, `SelectionGroup`, `Input`, and `InputDialogue`, which are used to create the game's user interface.

The `leaderboard.py` file contains the `Leaderboard` class, which manages the high scores for each difficulty level.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## Production
- Sabatier Vanessa : charger du Back-End ( chef de projet)
- Naël Paoli : charger du Front-End assets design et musique

## License

This project is licensed under the [MIT License](LICENSE).

## Testing

The game can be tested by running the `run.py` script and interacting with the game interface. No automated tests are currently provided.
