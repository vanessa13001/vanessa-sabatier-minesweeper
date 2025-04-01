# Minesweeper

## Installation

To install the Minesweeper game, follow these steps:

1. Clone the repository:
```
git clone https://github.com/your-username/minesweeper.git
```
2. Navigate to the project directory:
```
cd minesweeper
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

To run the Minesweeper game, execute the following command:

```
python game.py
```

This will start the game and display the main window.

## API

The main game class is `Game`, which provides the following methods:

- `reset_game()`: Resets the game to the initial state.
- `show_leaderboard()`: Switches the screen to display the leaderboard.
- `show_name_input()`: Switches the screen to display the name input dialogue.
- `on_name_enter(name)`: Handles the name input for the leaderboard.
- `on_status_change(new_status)`: Handles changes in the game status.
- `on_difficulty_change(difficulty)`: Handles changes in the game difficulty.
- `show_error_message(message)`: Displays an error message to the user.
- `save_state(state_file_path)`: Saves the current game state to a file.

The `Board` class manages the game board, and the `Leaderboard` class handles the leaderboard functionality.

## Production
Naël Paoli - Back-End
Vanessa Sabatier - Front-End et Cheffe de projet.
## Contributing

If you would like to contribute to the Minesweeper project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure that the code passes all tests.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Testing

To run the tests for the Minesweeper project, execute the following command:

```
python -m unittest discover tests
```

This will run all the test cases defined in the `tests` directory.
