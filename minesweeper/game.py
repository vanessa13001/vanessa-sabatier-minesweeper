import os
import json
import pygame
from .board import Board
from .gui import SelectionGroup, Input, Button, Label, InputDialogue
from .leaderboard import Leaderboard

icon = pygame.image.load('minesweeper/assets/mine_.png')
pygame.display.set_icon(icon)
pygame.mixer.init()
pygame.mixer.music.load('minesweeper/assets/Time_Trial.ogg')
pygame.mixer.music.play(-1)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def load_image(name, size=None):
    """Load image and optionally resize it."""
    path = os.path.join(ASSETS_DIR, name)
    try:
        image = pygame.image.load(path)
    except pygame.error as error:
        print('Cannot load image: ', path)
        raise SystemError(error)

    if size is not None:
        if isinstance(size, int):
            size = (size, size)
        image = pygame.transform.scale(image, size)

    return image

def load_font(name, size):
    path = os.path.join(ASSETS_DIR, name)
    try:
        font = pygame.font.Font(path, size)
    except pygame.error as error:
        print('Cannot load font: ', path)
        raise SystemError(error)
    return font

class Timer:
    """Execute event on timer.

    Parameters
    ----------
    on_time_event L callable
        Call this event on timer.
    """
    def __init__(self, on_time_event):
        self.on_time_event = on_time_event
        self.start_time = None
        self.interval = None
        self.running = False

    def start(self, interval):
        """Start timer now and trigger event after `interval`."""
        self.running = True
        self.interval = interval
        self.start_time = pygame.time.get_ticks()

    def check(self):
        """Check whether event occurred.

        Must be called continuously in the main loop."""
        if (self.running and
                pygame.time.get_ticks() - self.start_time >= self.interval):
            self.running = False
            self.on_time_event()

def create_count_tiles(tile_size, font_name):
    """Create tiles for mine counts.

    Additionally an empty tile without a digit is returned for 0

    Parameters
    ----------
    tile_size
        Size of tiles.
    font_name : string
        Font name to be found in resources directory. The size will be 0.9
        of `tile_size`.

    Returns
    -------
    tiles : list of pygame.Surface
        List of tiles containing 9 elements.
    """
    colors = [
        None,
        'Blue',
        'Dark Green',
        'Red',
        'Navy',
        'Brown',
        'Light Sea Green',
        'Black',
        'Dim Gray'
    ]

    font_size = int(tile_size * 0.9)
    font = load_font(font_name, font_size)

    empty_tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    center = empty_tile.get_rect().center

    tiles = [empty_tile.copy()]

    for count in range(1, 9):
        glyph = font.render(str(count), True, pygame.Color(colors[count]))
        width = glyph.get_rect().width

        glyph_center = (center[0] + int(0.15 * width), center[1])
        rect = glyph.get_rect(center=glyph_center)
        tile = empty_tile.copy()
        tile.blit(glyph, rect.topleft)
        tiles.append(tile)

    return tiles

def is_key_suitable_for_name(key_name):
    """Check if a key is suitable for name input."""
    return len(key_name) == 1 and key_name.isalnum() or key_name in ['-', '_']

def is_digit(key_name):
    """Check if a key is a digit."""
    return len(key_name) == 1 and key_name.isnumeric()

class Game:
    """Main game class."""
    TILE_SIZE = 20
    GUI_WIDTH = 91
    HUD_HEIGHT = 30
    MARGIN = 20
    BG_COLOR = pygame.Color('Light Slate Gray')
    FIELD_BG_COLOR = pygame.Color('#d7dcdc')
    FIELD_LINES_COLOR = pygame.Color('#738383')
    GUI_FONT_COLOR = pygame.Color('Light Yellow')
    GUI_FONT_SIZE = 13
    DIGITS = {chr(c) for c in range(ord('0'), ord('9') + 1)}
    MAX_BOARD_DIMENSION = 50
    MIN_BOARD_DIMENSION_DISPLAY = 10
    MAX_NAME_LENGTH = 8
    DELAY_BEFORE_NAME_INPUT_MS = 1000

    difficulty_levels = ["BRONZE", "SILVER", "GOLD", "DIAMOND", "RUBY"]

    def __init__(self, state_file_path):
        try:
            with open(state_file_path) as state_file:
                state = json.load(state_file)
        except (IOError, json.JSONDecodeError):
            state = {}

        display_info = pygame.display.Info()
        self.max_cols = (int(0.95 * display_info.current_w) - self.GUI_WIDTH
                         - 3 * self.MARGIN) // self.TILE_SIZE
        self.max_rows = (int(0.95 * display_info.current_h) - self.HUD_HEIGHT
                         - 3 * self.MARGIN) // self.TILE_SIZE

        difficulty = state.get('difficulty', 'BRONZE')

        if "leaderboard" in state:
            leaderboard_data = state['leaderboard']
        else:
            leaderboard_data = {'BRONZE': [], 'SILVER': [], 'GOLD': [], 'DIAMOND': [], 'RUBY': []}

        self.n_rows = state.get('n_rows', 10)
        self.n_cols = state.get('n_cols', 10)
        self.n_mines = state.get('n_mines', 10)

        # Initialize self.board with a default tile image
        default_tile_image = load_image("tile.png", self.TILE_SIZE)
        mine_count_images = create_count_tiles(self.TILE_SIZE, "kenvector_future.ttf")
        mine_image = load_image('mine_.png', self.TILE_SIZE)
        flag_image = load_image('flag.png', self.TILE_SIZE)
        question_mark_image = load_image('Intero.png', self.TILE_SIZE)
        gui_font = load_font("delfino.ttf", self.GUI_FONT_SIZE)

        self.board = Board(
            self.n_rows, self.n_cols, self.n_mines,
            self.FIELD_BG_COLOR, self.FIELD_LINES_COLOR, self.TILE_SIZE,
            default_tile_image, mine_count_images, flag_image, mine_image,
            question_mark_image,  # Pass the question mark image
            on_status_change_callback=self.on_status_change)

        # Add this line to track the current completed level
        self.current_completed_level = state.get('current_completed_level', 'BRONZE')

        # Now, call set_difficulty to update the tile image
        self.set_difficulty(difficulty)

        self.screen = None
        self.screen_rect = None
        self.board_rect = None
        self.hud_rect = None
        self.gui_rect = None
        self.board_area_rect = None
        self.init_screen()

        self.difficulty_selector = SelectionGroup(
            gui_font,
            self.GUI_FONT_COLOR,
            "DIFFICULTY",
            ["BRONZE", "SILVER", "GOLD", "DIAMOND", "RUBY", "CUSTOM"],
            initial_value=state.get('difficulty', 'BRONZE'))

        self.difficulty_selector.rect.centerx = self.gui_rect.centerx
        self.difficulty_selector.rect.y = self.MARGIN
        self.difficulty_selector.callback = self.on_difficulty_change

        active_input = self.difficulty_selector.selected == "CUSTOM"
        self.width_input = Input(gui_font, self.GUI_FONT_COLOR,
                                 "WIDTH", self.n_cols,
                                 active_input=active_input,
                                 width=self.GUI_WIDTH, max_value_length=3,
                                 key_filter=is_digit,
                                 on_enter_callback=self.on_cols_enter)
        self.height_input = Input(gui_font, self.GUI_FONT_COLOR,
                                  "HEIGHT", self.n_rows, width=self.GUI_WIDTH,
                                  active_input=active_input,
                                  max_value_length=3,
                                  key_filter=is_digit,
                                  on_enter_callback=self.on_rows_enter)
        self.mines_input = Input(gui_font, self.GUI_FONT_COLOR,
                                 "MINES", self.n_mines, width=self.GUI_WIDTH,
                                 active_input=active_input,
                                 max_value_length=3,
                                 key_filter=is_digit,
                                 on_enter_callback=self.on_mines_enter)

        self.timer = Input(gui_font, self.GUI_FONT_COLOR,
                           "TIME", self.board.time)
        self.current_mines = Input(gui_font, self.GUI_FONT_COLOR,
                                   "MINES", self.board.n_mines)

        self.status = Label(gui_font, self.GUI_FONT_COLOR, "READY TO GO!")

        self.restart_button = Button(gui_font,
                                     self.GUI_FONT_COLOR,
                                     "RESTART",
                                     self.board.reset)

        self.show_leaderboard_button = Button(gui_font, self.GUI_FONT_COLOR,
                                              "LEADER BOARD",
                                              self.show_leaderboard)

        leaderboard_width = (
            self.GUI_WIDTH + 2 * self.MARGIN
            + self.MIN_BOARD_DIMENSION_DISPLAY * self.TILE_SIZE)
        self.leaderboard = Leaderboard(gui_font, self.GUI_FONT_COLOR,
                                       5, leaderboard_width,
                                       data=leaderboard_data)
        self.leaderboard_hint = Label(gui_font, self.GUI_FONT_COLOR,
                                      "CLICK TO CONTINUE")

        self.name_input = InputDialogue(gui_font, self.GUI_FONT_COLOR,
                                        "ENTER YOUR NAME",
                                        self.on_name_enter,
                                        max_length=self.MAX_NAME_LENGTH,
                                        key_filter=is_key_suitable_for_name)

        self.victory_time = Label(gui_font, self.GUI_FONT_COLOR, "")
        self.leaderboard_announcement = Label(
            gui_font, self.GUI_FONT_COLOR,
            "YOU MADE IT TO THE LEADERBOARD!")
        self.show_name_input_timer = Timer(self.show_name_input)

        self.place_gui()
        self.keep_running = None
        self.mode = "game"

    def init_screen(self):
        """Initialize screen and compute rectangles for different regions."""
        board_area_width = \
            max(self.n_cols, self.MIN_BOARD_DIMENSION_DISPLAY) * self.TILE_SIZE
        board_area_height = \
            max(self.n_rows, self.MIN_BOARD_DIMENSION_DISPLAY) * self.TILE_SIZE + 70  # Increase height here
        window_width = 3 * self.MARGIN + self.GUI_WIDTH + board_area_width
        window_height = 3 * self.MARGIN + self.HUD_HEIGHT + board_area_height

        self.board_area_rect = pygame.Rect(2 * self.MARGIN + self.GUI_WIDTH,
                                           2 * self.MARGIN + self.HUD_HEIGHT,
                                           board_area_width,
                                           board_area_height)

        self.board.rect.size = (self.n_cols * self.TILE_SIZE,
                                self.n_rows * self.TILE_SIZE)
        self.board.rect.center = self.board_area_rect.center

        self.hud_rect = pygame.Rect(2 * self.MARGIN + self.GUI_WIDTH,
                                    self.MARGIN,
                                    board_area_width,
                                    self.HUD_HEIGHT)

        self.screen = pygame.display.set_mode((window_width, window_height))
        self.screen_rect = self.screen.get_rect()

        # Load the background image
        self.background_image = load_image("backgroundV2.jpg", (window_width, window_height))

        # Load the "wasted" image
        self.wasted_image = load_image("wasted.png", (self.n_cols * self.TILE_SIZE, self.n_rows * self.TILE_SIZE))

        self.gui_rect = pygame.Rect(self.MARGIN,
                                    2 * self.MARGIN + self.HUD_HEIGHT,
                                    self.GUI_WIDTH,
                                    board_area_height)

    def set_difficulty(self, difficulty):
        """Adjust game parameters given difficulty.

        Custom difficulty is not handled in this function.
        """
        if difficulty == "BRONZE":
            self.n_rows = 10
            self.n_cols = 10
            self.n_mines = 10
            self.tile_color = "tile_bronze.png"
        elif difficulty == "SILVER":
            self.n_rows = 16
            self.n_cols = 16
            self.n_mines = 40
            self.tile_color = "tile_argent.png"
        elif difficulty == "GOLD":
            self.n_rows = 16
            self.n_cols = 30
            self.n_mines = 99
            self.tile_color = "tile_or.png"
        elif difficulty == "DIAMOND":
            self.n_rows = 24
            self.n_cols = 24
            self.n_mines = 150
            self.tile_color = "tile_diamant.png"
        elif difficulty == "RUBY":
            self.n_rows = 30
            self.n_cols = 30
            self.n_mines = 250
            self.tile_color = "tile_rubis.png"
        elif difficulty == "CUSTOM":
            self.tile_color = "tile_jade.png"

        # Load the tile image based on the selected color
        tile_image = load_image(self.tile_color, self.TILE_SIZE)
        self.board.set_tile_image(tile_image)  # Ensure that Board has a method to update the tile image

    def place_gui(self):
        """Place GUI element according to the current settings."""
        gui_x_offset = self.gui_rect.x - 10  # Offset by 10 pixels to the left

        self.width_input.rect.topleft = (
            gui_x_offset,  # Apply the offset
            self.difficulty_selector.rect.bottom
            + 0.2 * self.difficulty_selector.rect.height)
        self.height_input.rect.topleft = (
            gui_x_offset,  # Apply the offset
            self.width_input.rect.bottom + 0.4 * self.height_input.rect.height)
        self.mines_input.rect.topleft = (
            gui_x_offset,  # Apply the offset
            self.height_input.rect.bottom + 0.4 * self.width_input.rect.height)

        hud_width = self.place_hud()

        self.restart_button.rect.top = self.timer.rect.top
        self.restart_button.rect.centerx = 0.5 * (self.hud_rect.left
                                                + self.hud_rect.right
                                                - hud_width)

        self.show_leaderboard_button.rect.bottom = (self.screen_rect.height
                                                    - self.MARGIN)
        self.show_leaderboard_button.rect.centerx = (self.MARGIN
                                                     + 0.5 * self.GUI_WIDTH)

        screen_center = self.screen.get_rect().centerx
        self.status.rect.top = self.current_mines.rect.top
        self.status.rect.centerx = self.restart_button.rect.centerx

        self.leaderboard.rect.top = self.MARGIN + 0  # Adjust the position here
        self.leaderboard.rect.centerx = screen_center

        self.leaderboard_hint.rect.bottom = (self.screen_rect.height
                                            - self.MARGIN)
        self.leaderboard_hint.rect.centerx = self.screen_rect.centerx

        self.victory_time.rect.top = self.MARGIN
        self.victory_time.rect.centerx = self.screen_rect.centerx
        self.leaderboard_announcement.rect.top = (
            self.victory_time.rect.bottom
            + 0.4 * self.victory_time.rect.height)
        self.leaderboard_announcement.rect.centerx = self.screen_rect.centerx

        self.name_input.rect.top = (
            self.leaderboard_announcement.rect.bottom
            + self.leaderboard_announcement.rect.height)
        self.name_input.rect.centerx = self.screen_rect.centerx

    def place_hud(self):
        """Place timer and mines info and return width of this block."""
        hud_width = max(self.timer.rect.width, self.current_mines.rect.width)
        self.timer.rect.topleft = (self.hud_rect.right - hud_width,
                                self.hud_rect.top)
        self.current_mines.rect.topleft = (
            self.timer.rect.left,
            self.timer.rect.bottom + 0.4 * self.timer.rect.height)
        return hud_width

    def reset_game(self):
        """Reset the game."""
        self.board.reset(n_rows=self.n_rows,
                        n_cols=self.n_cols,
                        n_mines=self.n_mines)

    def show_leaderboard(self):
        """Change screen to leaderboard."""
        self.mode = "leaderboard"

    def show_name_input(self):
        """Change screen to name input."""
        self.mode = "name_input"
        self.victory_time.set_text("YOUR TIME IS {} SECONDS"
                                .format(self.board.time))
        self.name_input.set_value("")
        self.place_gui()

    def on_name_enter(self, name):
        """Handle name enter for the leaderboard."""
        if not name:
            return
        self.leaderboard.update(self.difficulty_selector.selected,
                                name,
                                self.board.time)
        self.mode = "leaderboard"

    def on_status_change(self, new_status):
        """Handle game status change."""
        if new_status == 'victory':
            # Update the completed level when the user wins
            self.current_completed_level = self.difficulty_selector.selected

        if new_status == 'game_over':
            self.status.set_text("WASTED!")
        elif new_status == 'victory':
            self.status.set_text("VICTORY!")
            if self.leaderboard.needs_update(self.difficulty_selector.selected,
                                            self.board.time):
                self.show_name_input_timer.start(
                    self.DELAY_BEFORE_NAME_INPUT_MS)
        elif new_status == 'before_start':
            self.status.set_text("READY TO GO!")
        else:
            self.status.set_text("GOOD LUCK!")

    def on_difficulty_change(self, difficulty):
        """Handle difficulty change."""
        self.height_input.active_input = False
        self.width_input.active_input = False
        self.mines_input.active_input = False
        self.set_difficulty(difficulty)  # Update the difficulty and tile color
        if difficulty == "CUSTOM":
            self.height_input.active_input = True
            self.width_input.active_input = True
            self.mines_input.active_input = True

        self.height_input.set_value(self.n_rows)
        self.width_input.set_value(self.n_cols)
        self.mines_input.set_value(self.n_mines)

        self.init_screen()
        self.place_gui()
        self.reset_game()

    def show_error_message(self, message):
        """Display an error window to the user."""
        # Create a surface for the error window
        error_surface = pygame.Surface((300, 100))
        error_surface.fill(pygame.Color('white'))

        # Create a rectangle for the border
        border_rect = error_surface.get_rect()
        pygame.draw.rect(error_surface, pygame.Color('black'), border_rect, 2)

        # Render the text of the message
        font = pygame.font.Font(None, 18)
        text = font.render(message, True, pygame.Color('black'))
        text_rect = text.get_rect(center=border_rect.center)  # Center the text in the box
        error_surface.blit(text, text_rect)

        # Display the error window
        self.screen.blit(error_surface, (self.screen_rect.width // 2 - 150, self.screen_rect.height // 2 - 50))
        pygame.display.flip()

        # Wait a short moment for the user to read the message
        pygame.time.wait(2000)

    def set_game_parameter(self, parameter, max_value, value):
        """Set either n_rows, n_cols, n_mines."""
        if not value:
            value = 1

        value = int(value)
        value = min(max(1, value), max_value)
        setattr(self, parameter, value)
        self.n_mines = min(self.n_mines, self.n_rows * self.n_cols - 1)
        self.mines_input.set_value(self.n_mines)
        self.init_screen()
        self.place_gui()
        self.reset_game()
        return value

    def on_rows_enter(self, value):
        """Handle n_rows input."""
        return self.set_game_parameter('n_rows',
                                       self.max_rows,
                                       value)

    def on_cols_enter(self, value):
        """Handle n_cols input."""
        return self.set_game_parameter('n_cols',
                                       self.max_cols,
                                       value)

    def on_mines_enter(self, value):
        """Hand n_mines input."""
        return self.set_game_parameter('n_mines',
                                       self.n_rows * self.n_cols - 1,
                                       value)

    def draw_all(self):
        """Draw all elements."""
        # Draw the background image
        self.screen.blit(self.background_image, (0, 0))

        if self.mode == "leaderboard":
            self.leaderboard.draw(self.screen)
            self.leaderboard_hint.draw(self.screen)
            pygame.display.flip()
            return
        elif self.mode == "name_input":
            self.victory_time.draw(self.screen)
            self.leaderboard_announcement.draw(self.screen)
            self.name_input.draw(self.screen)
            pygame.display.flip()
            return

        self.board.draw(self.screen)

        # Draw the "wasted" image if the game is over
        if self.board.game_status == 'game_over':
            self.screen.blit(self.wasted_image, self.board_area_rect.topleft)

        self.difficulty_selector.draw(self.screen)
        self.height_input.draw(self.screen)
        self.width_input.draw(self.screen)
        self.mines_input.draw(self.screen)

        self.timer.draw(self.screen)
        self.current_mines.draw(self.screen)
        self.status.draw(self.screen)

        self.restart_button.draw(self.screen)
        self.show_leaderboard_button.draw(self.screen)

        pygame.display.flip()

    def process_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keep_running = False
                break

            if self.mode == "leaderboard":
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mode = "game"
                break
            elif self.mode == "name_input":
                if event.type == pygame.KEYDOWN:
                    self.name_input.on_key_down(event)
                break

            if event.type == pygame.MOUSEBUTTONUP:
                self.difficulty_selector.on_mouse_up(event.button)
                self.height_input.on_mouse_up(event.button)
                self.width_input.on_mouse_up(event.button)
                self.mines_input.on_mouse_up(event.button)
                self.restart_button.on_mouse_up(event.button)
                self.show_leaderboard_button.on_mouse_up(event.button)
                self.board.on_mouse_up(event.button)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.board.on_mouse_down(event.button)
            elif event.type == pygame.KEYDOWN:
                self.height_input.on_key_down(event)
                self.width_input.on_key_down(event)
                self.mines_input.on_key_down(event)

    def start_main_loop(self):
        """Start main game loop."""
        clock = pygame.time.Clock()
        self.keep_running = True
        while self.keep_running:
            clock.tick(30)
            self.timer.set_value(self.board.time)
            self.current_mines.set_value(self.board.n_mines_left)
            self.place_hud()
            self.process_events()
            self.show_name_input_timer.check()
            self.draw_all()

    def save_state(self, state_file_path):
        """Save game state on disk."""
        state = {
            "difficulty": self.difficulty_selector.selected,
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "n_mines": self.n_mines,
            "leaderboard": self.leaderboard.data,
            "current_completed_level": self.current_completed_level  # Save the completed level
        }
        with open(state_file_path, "w") as state_file:
            json.dump(state, state_file)

def run(state_file_path):
    pygame.init()
    pygame.display.set_caption('Minesweeper')
    pygame.mouse.set_visible(True)
    game = Game(state_file_path)
    game.start_main_loop()
    game.save_state(state_file_path)
