from datetime import datetime, timedelta
import json
import math
import os
import shutil
import sys
import time
from typing import Optional, Dict
import inspect

class Path:
    @staticmethod
    def local():
        # Inspect the call stack to find the frame of the script that imported this module
        frame = inspect.stack()[1]  # The calling frame (one level up the stack)
        module = inspect.getmodule(frame[0])
        
        # Get the directory of the script that imported this file
        if module and hasattr(module, '__file__'):
            return os.path.dirname(os.path.abspath(module.__file__))
        else:
            return os.getcwd()  # Fallback to current working directory if no module found

class Option:
    """
    Manages default values for settings within the script.

    Attributes:
        value (dict): Dictionary to store default configuration values.
    """
    value = {
        'duration_style': 'default',

        'step_count': 0,

        'progress_length': 30,
        'progress_fill': '█',
        'progress_decimals': 1,
        'progress_prefix': 'Progress:',
        'progress_suffix': '',
        'progress_eta_style': None,

        'progress_double_prefix1': 'Progress Current:',
        'progress_double_suffix1': '',
        'progress_double_prefix2': 'Progress Total:',
        'progress_double_suffix2': ''
    }

    @staticmethod
    def load(file_path: str) -> None:
        """
        Load default values from a JSON file.

        Args:
            file_path (str): Path to the JSON file. Should contain key-value
                             pairs like {"key1": "value1", "key2": "value2"}.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                Option.value.update(json.load(file))

    @staticmethod
    def set(key: str, value) -> None:
        """
        Set a default value for a given key.

        Args:
            key (str): The key for the default setting.
            value: The default value to store.
        """
        Option.value[key] = value

    @staticmethod
    def get(key: str, default=None):
        """
        Retrieve a default value.

        Args:
            key (str): Key to look up in defaults.
            default: Value to return if the key is not found.

        Returns:
            The value associated with the key, or the default if not found.
        """
        return Option.value.get(key, default)

    @staticmethod
    def save(file_path: str) -> None:
        """
        Save the current defaults to a JSON file.

        Args:
            file_path (str): Path to the JSON file.
        """
        with open(file_path, 'w') as file:
            json.dump(Option.value, file, indent=4)

class Configuration:
    """
    Manages configuration settings loaded from a JSON file.

    Attributes:
        config (dict): Dictionary to store configuration settings.
    """
    config = {}

    @staticmethod
    def load_from_file(file_path: str) -> None:
        """
        Load configuration settings from a JSON file.

        Args:
            file_path (str): Path to the JSON file. The file should contain key-value
                             pairs in the format {"key1": "value1", "key2": "value2"}.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                Configuration.config.update(json.load(file))
                # Load into defaults to override any existing default values
                for key, value in Configuration.config.items():
                    Option.set(key, value)

    @staticmethod
    def get(key: str, default=None):
        """
        Retrieve a configuration value.

        Args:
            key (str): Key to look up in the configuration.
            default: Default value to return if the key is not found.

        Returns:
            The value associated with the specified key, or the default if not found.
        """
        return Configuration.config.get(key, Option.get(key, default))

class ANSI:
    """
    ANSI Escape Codes for styling terminal text with colors, styles, and cursor controls.

    Provides codes for text formatting (e.g., bold, underline), foreground and background colors,
    256-color mode, and RGB colors. These codes work with compatible terminal emulators.
    """
    # Reset Styles
    RESET = '\033[0m'              # Reset all attributes
    RESET_BOLD = '\033[21m'        # Reset bold attribute
    RESET_DIM = '\033[22m'         # Reset dim attribute
    RESET_UNDERLINE = '\033[24m'   # Reset underline attribute
    RESET_BLINK = '\033[25m'       # Reset blink attribute
    RESET_REVERSE = '\033[27m'     # Reset reverse attribute
    RESET_HIDDEN = '\033[28m'      # Reset hidden attribute

    # Text Styles
    BOLD = '\033[1m'               # Bold text
    DIM = '\033[2m'                # Dim (faint) text
    ITALIC = '\033[3m'             # Italic text
    UNDERLINE = '\033[4m'          # Underlined text
    BLINK = '\033[5m'              # Blinking text
    REVERSE = '\033[7m'            # Reverse foreground and background colors
    HIDDEN = '\033[8m'             # Hidden text
    STRIKETHROUGH = '\033[9m'      # Strikethrough text

    # Foreground Colors (Normal)
    FG_BLACK = '\033[30m'          # Black text
    FG_RED = '\033[31m'            # Red text
    FG_GREEN = '\033[32m'          # Green text
    FG_YELLOW = '\033[33m'         # Yellow text
    FG_BLUE = '\033[34m'           # Blue text
    FG_MAGENTA = '\033[35m'        # Magenta text
    FG_CYAN = '\033[36m'           # Cyan text
    FG_WHITE = '\033[37m'          # White text

    # Foreground Colors (Bright)
    FG_BLACK_BRIGHT = '\033[90m'   # Bright black (gray) text
    FG_RED_BRIGHT = '\033[91m'     # Bright red text
    FG_GREEN_BRIGHT = '\033[92m'   # Bright green text
    FG_YELLOW_BRIGHT = '\033[93m'  # Bright yellow text
    FG_BLUE_BRIGHT = '\033[94m'    # Bright blue text
    FG_MAGENTA_BRIGHT = '\033[95m' # Bright magenta text
    FG_CYAN_BRIGHT = '\033[96m'    # Bright cyan text
    FG_WHITE_BRIGHT = '\033[97m'   # Bright white text

    # Background Colors (Normal)
    BG_BLACK = '\033[40m'          # Black background
    BG_RED = '\033[41m'            # Red background
    BG_GREEN = '\033[42m'          # Green background
    BG_YELLOW = '\033[43m'         # Yellow background
    BG_BLUE = '\033[44m'           # Blue background
    BG_MAGENTA = '\033[45m'        # Magenta background
    BG_CYAN = '\033[46m'           # Cyan background
    BG_WHITE = '\033[47m'          # White background

    # Background Colors (Bright)
    BG_BLACK_BRIGHT = '\033[100m'  # Bright black (gray) background
    BG_RED_BRIGHT = '\033[101m'    # Bright red background
    BG_GREEN_BRIGHT = '\033[102m'  # Bright green background
    BG_YELLOW_BRIGHT = '\033[103m' # Bright yellow background
    BG_BLUE_BRIGHT = '\033[104m'   # Bright blue background
    BG_MAGENTA_BRIGHT = '\033[105m'# Bright magenta background
    BG_CYAN_BRIGHT = '\033[106m'   # Bright cyan background
    BG_WHITE_BRIGHT = '\033[107m'  # Bright white background

    # 256-Color Mode Functions
    @staticmethod
    def fg_256(code: int) -> str:
        """
        Generate 256-color mode foreground color.

        Args:
            code (int): Color code between 0-255.

        Returns:
            str: ANSI escape code for the specified foreground color.

        Example:
            fg_256(196) returns the bright red color code.
        """
        return f'\033[38;5;{code}m'

    @staticmethod
    def bg_256(code: int) -> str:
        """
        Generate 256-color mode background color.

        Args:
            code (int): Background color code between 0-255.

        Returns:
            str: ANSI escape code for the specified background color.

        Example:
            bg_256(196) returns the bright red background code.
        """
        return f'\033[48;5;{code}m'

    # RGB Color Mode Functions
    @staticmethod
    def fg_rgb(r: int, g: int, b: int) -> str:
        """
        Generate RGB foreground color.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).

        Returns:
            str: ANSI escape code for the specified RGB color.

        Example:
            fg_rgb(255, 0, 0) returns a red foreground color.
        """
        return f'\033[38;2;{r};{g};{b}m'

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """
        Generate RGB background color.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).

        Returns:
            str: ANSI escape code for the specified RGB background color.

        Example:
            bg_rgb(0, 255, 0) returns a green background color.
        """
        return f'\033[48;2;{r};{g};{b}m'

    # Cursor Controls
    CURSOR_UP = '\033[A'           # Move cursor up by 1
    CURSOR_DOWN = '\033[B'         # Move cursor down by 1
    CURSOR_FORWARD = '\033[C'      # Move cursor forward (right) by 1
    CURSOR_BACK = '\033[D'         # Move cursor back (left) by 1

    @staticmethod
    def cursor_up(n: int) -> str:
        """Move cursor up by `n` lines."""
        return f'\033[{n}A'

    @staticmethod
    def cursor_down(n: int) -> str:
        """Move cursor down by `n` lines."""
        return f'\033[{n}B'

    @staticmethod
    def cursor_forward(n: int) -> str:
        """Move cursor forward (right) by `n` columns."""
        return f'\033[{n}C'

    @staticmethod
    def cursor_back(n: int) -> str:
        """Move cursor back (left) by `n` columns."""
        return f'\033[{n}D'

    @staticmethod
    def cursor_position(x: int, y: int) -> str:
        """Set cursor position to column `x` and row `y`."""
        return f'\033[{y};{x}H'

    # Erase Functions
    ERASE_LINE = '\033[K'           # Erase from cursor to end of line
    ERASE_LINE_END = '\033[0K'      # Erase from cursor to end of line
    ERASE_LINE_START = '\033[1K'    # Erase from cursor to start of line
    ERASE_LINE_ALL = '\033[2K'      # Erase entire line
    ERASE_SCREEN_END = '\033[0J'    # Erase from cursor to end of screen
    ERASE_SCREEN_START = '\033[1J'  # Erase from cursor to start of screen
    ERASE_SCREEN_ALL = '\033[2J'    # Erase entire screen
    ERASE_SCREEN_SAVED = '\033[3J'  # Erase saved screen

    # Save and Restore Cursor Position
    SAVE_CURSOR = '\033[s'          # Save cursor position
    RESTORE_CURSOR = '\033[u'       # Restore saved cursor position

    # Hide and Show Cursor
    HIDE_CURSOR = '\033[?25l'       # Hide cursor
    SHOW_CURSOR = '\033[?25h'       # Show cursor

    # Scroll Screen
    SCROLL_UP = '\033[S'            # Scroll screen up by 1 line
    SCROLL_DOWN = '\033[T'          # Scroll screen down by 1 line

    @staticmethod
    def scroll_up(n: int) -> str:
        """Scroll screen up by `n` lines."""
        return f'\033[{n}S'

    @staticmethod
    def scroll_down(n: int) -> str:
        """Scroll screen down by `n` lines."""
        return f'\033[{n}T'

class Color:
    """
    Provides color utilities for generating ANSI and hex color codes.

    Methods:
        ansi(color_name: str) -> str:
            Returns the ANSI code for a specified foreground color name.
        ansi_bg(color_name: str) -> str:
            Returns the ANSI code for a specified background color name.
        hex(color_name: str) -> str:
            Returns the hexadecimal color code for a specified color name.
        ansi_extended(code: int) -> str:
            Generates ANSI extended color code (256-color mode).
        ansi_background_extended(code: int) -> str:
            Generates ANSI extended background color code (256-color mode).
    """

    map_text = {
        # Reset Styles
        "reset": ANSI.RESET,

        # Foreground Colors (Normal)
        "red": ANSI.FG_RED,
        "yellow": ANSI.FG_YELLOW,
        "green": ANSI.FG_GREEN,
        "cyan": ANSI.FG_CYAN,
        "blue": ANSI.FG_BLUE,
        "magenta": ANSI.FG_MAGENTA,
        "black": ANSI.FG_BLACK,
        "white": ANSI.FG_WHITE,

        # Foreground Colors (Bright)
        "red_bright": ANSI.FG_RED_BRIGHT,
        "green_bright": ANSI.FG_GREEN_BRIGHT,
        "cyan_bright": ANSI.FG_CYAN_BRIGHT,
        "blue_bright": ANSI.FG_BLUE_BRIGHT,
        "magenta_bright": ANSI.FG_MAGENTA_BRIGHT,
        "black_bright": ANSI.FG_BLACK_BRIGHT,
        "white_bright": ANSI.FG_WHITE_BRIGHT,
    }

    @staticmethod
    def text(color_name: str) -> str:
        """
        Get the ANSI code for a specified foreground color name.

        Args:
            color_name (str): Name of the color (e.g., "red", "blue_bright").

        Returns:
            str: ANSI escape code for the specified foreground color, or reset if not found.

        Example:
            ansi("red") returns "\033[31m" (ANSI code for red).
        """
        return Color.map_text.get(color_name, ANSI.RESET)

    map_text_bg = {
        # Reset Styles
        "reset": ANSI.RESET,

        # Background Colors (Normal)
        "red": ANSI.BG_RED,
        "yellow": ANSI.BG_YELLOW,
        "green": ANSI.BG_GREEN,
        "cyan": ANSI.BG_CYAN,
        "blue": ANSI.BG_BLUE,
        "magenta": ANSI.BG_MAGENTA,
        "black": ANSI.BG_BLACK,
        "white": ANSI.BG_WHITE,

        # Background Colors (Bright)
        "red_bright": ANSI.BG_RED_BRIGHT,
        "green_bright": ANSI.BG_GREEN_BRIGHT,
        "cyan_bright": ANSI.BG_CYAN_BRIGHT,
        "blue_bright": ANSI.BG_BLUE_BRIGHT,
        "magenta_bright": ANSI.BG_MAGENTA_BRIGHT,
        "black_bright": ANSI.BG_BLACK_BRIGHT,
        "white_bright": ANSI.BG_WHITE_BRIGHT,
    }

    @staticmethod
    def text_bg(color_name: str) -> str:
        """
        Get the ANSI code for a specified background color name.

        Args:
            color_name (str): The name of the background color. Supported colors include:
                              "red", "yellow", "green", "cyan", "blue", "magenta", "black",
                              "white", and their bright counterparts such as "red_bright".

        Returns:
            str: ANSI escape code for the specified background color. Default to `ANSI.RESET`
                 if the color name is not found.
        """
        return Color.map_text_bg.get(color_name, ANSI.RESET)

    map_hex = {
        # Reds
        "light_red": "#FF6666",
        "red": "#FF0000",
        "dark_red": "#8B0000",

        # Oranges
        "light_orange": "#FFD580",
        "orange": "#FFA500",
        "dark_orange": "#FF8C00",

        # Yellows
        "light_yellow": "#FFFF66",
        "yellow": "#FFFF00",
        "dark_yellow": "#9B870C",

        # Greens
        "light_green": "#66FF66",
        "green": "#00FF00",
        "lime": "#32CD32",
        "dark_green": "#006400",

        # Cyans
        "light_cyan": "#66FFFF",
        "cyan": "#00FFFF",
        "dark_cyan": "#008B8B",
        "teal": "#008080",

        # Blues
        "light_blue_steel": "#9BD0F1",
        "blue_steel": "#1F77B4",
        "dark_blue_steel": "#124668",
        "light_blue": "#6666FF",
        "blue": "#0000FF",
        "dark_blue": "#00008B",
        "navy": "#000080",

        # Purples
        "pink": "#FFC0CB",
        "light_magenta": "#FF66FF",
        "magenta": "#FF00FF",
        "dark_magenta": "#8B008B",
        "purple": "#800080",

        # Browns
        "brown": "#A52A2A",
        "maroon": "#800000",

        # Grays/Neutral
        "white": "#FFFFFF",
        "gray_90": "#E6E6E6",
        "gray_80": "#CCCCCC",
        "gray_70": "#B3B3B3",
        "gray_60": "#999999",
        "gray_50": "#808080",
        "gray": "#808080",
        "gray_40": "#666666",
        "gray_dark": "#4F4F4F",
        "gray_30": "#4D4D4D",
        "black_bright": "#333333",
        "gray_20": "#333333",
        "gray_10": "#1A1A1A",
        "black": "#000000",
    }

    @staticmethod
    def hex(color_name: str) -> str:
        """
        Get the hexadecimal color code for a specified color name.

        Args:
            color_name (str): Name of the color (e.g., "light_blue").

        Returns:
            str: Hex color code for the specified color.

        Example:
            hex("light_blue") returns "#6666FF".
        """
        return Color.map_hex.get(color_name, "#FFFFFF")  # Default to white if not found

    @staticmethod
    def text_extended(code: int) -> str:
        """
        Generate ANSI extended color code (256-color mode).

        Args:
            code (int): Color code between 0-255.

        Returns:
            str: ANSI escape code for the specified extended color. Used for a wider color range
                 supported by ANSI 256-color codes.
        """
        return ANSI.fg_256(code)

    @staticmethod
    def text_background_extended(code: int) -> str:
        """
        Generate ANSI extended background color code (256-color mode).

        Args:
            code (int): Background color code between 0-255.

        Returns:
            str: ANSI escape code for the specified extended background color. Used for a wider
                 color range supported by ANSI 256-color codes for backgrounds.
        """
        return ANSI.bg_256(code)

TERMINAL_WIDTH_DEFAULT = 80
TERMINAL_WIDTH_DEFAULT_HALF = math.floor(TERMINAL_WIDTH_DEFAULT * 0.5)

class Terminal:
    @staticmethod
    def get_width() -> int:
        """
        Get the current terminal width, returning a default if unavailable.

        Returns:
            int: Width of the terminal in characters, defaults to TERMINAL_WIDTH_DEFAULT if unable to retrieve size.
        """
        try:
            return shutil.get_terminal_size().columns
        except OSError:
            return TERMINAL_WIDTH_DEFAULT  # Default width if unable to get terminal size

    @staticmethod
    def get_line_wrap_count(length: int, terminal_width: int) -> dict:
        """
        Calculate how many lines a wrapped progress bar would occupy, subtracting one line for better fit.

        Args:
            length (int): Length of the text.
            terminal_width (int): Width of the terminal.

        Returns:
            dict: Debug string and line count for the wrapped text.
        """
        value = math.ceil(length / terminal_width)
        debug_print = f"l{length} t{terminal_width} v{value}"
        return {'print': debug_print, 'value': value}

class Timer:
    """
    A simple timer class with customizable defaults for start and elapsed time.
    """
    def __init__(self, start_time: Optional[datetime] = None):
        self.start_time = start_time or datetime.now()

    def start(self):
        """
        Start the timer.
        """
        self.start_time = datetime.now()

    def elapsed(self) -> timedelta:
        """
        Return the time elapsed since the timer started.

        Returns:
            timedelta: The time elapsed.

        Raises:
            ValueError: If the timer hasn't been started yet.
        """
        if not self.start_time:
            raise ValueError("Timer has not been started.")
        return datetime.now() - self.start_time

    def reset(self):
        """
        Reset the timer to its initial state.
        """
        self.start_time = None

class Format:
    """
    Utilities for formatting time, duration, and plurals.
    """

    @staticmethod
    def text_color(color: str, text: str) -> str:
        """Wraps text in ANSI color codes for terminal display."""
        text_color = Color.text(color)
        text_color_reset = Color.text('reset')
        return f"{text_color}{text.replace('[[COLOR_ON]]', text_color).replace('[[COLOR_OFF]]', text_color_reset)}{text_color_reset}"

    @staticmethod
    def plural_suffix(number: int, string_root: str, string_singular: str, string_plural: str) -> str:
        """
        Returns the appropriate singular or plural suffix based on the number.

        Args:
            number (int): The number to evaluate.
            string_root (str): The root of the word to which the suffix will be appended.
            string_singular (str): The suffix to use if the number is singular.
            string_plural (str): The suffix to use if the number is plural.

        Returns:
            str: The concatenated string with the appropriate singular or plural suffix.

        Example:
            plural_suffix(1, "director", "y", "ies") returns "directory".
            plural_suffix(5, "director", "y", "ies") returns "directories".
        """
        return f"{string_root}{string_singular}" if number == 1 else f"{string_root}{string_plural}"

    @staticmethod
    def date(date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format a datetime object to a specified string format.

        Args:
            date (datetime): The datetime object to format.
            format_str (str): The format string for strftime.

        Returns:
            str: Formatted date string.

        Example:
            date(datetime(2024, 11, 12), "%Y-%m-%d") returns "2024-11-12".
        """
        return date.strftime(format_str)

    @staticmethod
    def duration(duration: timedelta, style: Optional[str] = None) -> str:
        """
        Format a timedelta into a string based on the specified style.

        Args:
            duration (timedelta): The duration to format.
            style (Optional[str]): Format style -
                        'default' for the format "2d 04:30:15",
                        'symbol' for the format "2d 4h 30m 15s" (using time unit symbols),
                        'word' for the format "2 days 4 hours 30 minutes 15 seconds" (using full words).

        Returns:
            str: Formatted duration string.

        Example:
            duration(timedelta(days=2, hours=4, minutes=30), style='symbol') returns "2d 4h 30m".
        """
        if not isinstance(duration, timedelta):
            return 'Invalid duration input. Please provide a timedelta object.'

        is_negative = duration.total_seconds() < 0
        if is_negative:
            duration = abs(duration)  # Work with positive duration for formatting

        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        style = style if style else Option.get('duration_style')

        if style in ['symbol', 'word']:
            # Define units and select singular or plural suffix based on style
            units = [("d", days, " day", " days"),
                    ("h", hours, " hour", " hours"),
                    ("m", minutes, " minute", " minutes"),
                    ("s", seconds, " second", " seconds")]

            parts = [
                f"{value}{unit if style == 'symbol' else (singular if value == 1 else plural)}"
                for unit, value, singular, plural in units if value or (unit == "s" and not any(u[1] for u in units[:-1]))
            ]

            formatted_duration = " ".join(parts)
            return f"-{formatted_duration}" if is_negative else formatted_duration

        else:
            # Default format: "2d 04:30:15"
            formatted_duration = f"{days}d {hours:02}:{minutes:02}:{seconds:02}" if days > 0 else f"{hours:02}:{minutes:02}:{seconds:02}"
            return f"-{formatted_duration}" if is_negative else formatted_duration

        # Raise an error if the style is not recognized
        raise ValueError('Invalid style format specified. Use "default", "symbol", or "word".')

    @staticmethod
    def eta(iteration: int, total: int, start_time: datetime, style: Optional[str] = None) -> str:
        """
        Calculate ETA based on current iteration and total,
        using the specified format style.

        Args:
            iteration (int): Current iteration number.
            total (int): Total iterations.
            start_time (datetime): Start time to calculate elapsed time.
            style (Optional[str]): Format style - 'default', 'symbol', or 'word'.

        Returns:
            str: ETA in the specified format, or an empty string if not enough data.
        """
        if not start_time or iteration <= 0:
            return ''

        elapsed_time = datetime.now() - start_time
        seconds_per_iteration = elapsed_time.total_seconds() / iteration
        eta_seconds = (total - iteration) * seconds_per_iteration
        eta_time = timedelta(seconds=round(eta_seconds))

        # Use Format.duration to format eta_time with the chosen style
        return Format.duration(eta_time, style=style)

class Status:
    @staticmethod
    def text_color(status_type: str) -> str:
        """
        Get the ANSI color code based on the status type.

        Args:
            status_type (str): Status type (Info, Success, Notice, Warning, Error, Debug).

        Returns:
            str: ANSI color code for the status type.
        """
        color_map = {
            "Info": "cyan",
            "Success": "blue_bright",
            "Notice": "yellow",
            "Warning": "yellow",
            "Error": "red",
            "Debug": "green"
        }

        return color_map.get(status_type, "reset")

class Print:
    """
    Provides printing utilities with color-coded statuses, titles, and step management.

    Attributes:
        step_current (int): Current step number.
        debug_level (int): Current debug level for filtering messages.

    Methods:
        color(color: str, text: str) -> None:
            Print text with the specified ANSI color.
        status(status_type: str, message: str, debug_level: int = None) -> None:
            Print a color-coded status message.
        title(text: str, width: int = 80, flank_char: str = '=', color: str = 'magenta') -> None:
            Print a formatted title.
        step(text: str = '') -> None:
            Manage step printing with optional description.
    """

    step_current = 0
    step_text = ""
    debug_level = 0

    @staticmethod
    def color(color: str, text: str) -> None:
        """
        Print text in the specified ANSI color in the terminal.

        Args:
            color (str): ANSI color code.
            text (str): Text to print in the specified color.

        Example:
            Print.color(Color.ansi("red"), "Error message in red.")
        """
        print(Format.text_color(color, text))

    @staticmethod
    def status(status_type: str, message: str, debug_level: int = 1) -> None:
        """
        Print a color-coded status message, filtering based on debug levels if specified.

        Args:
            status_type (str): Type of status ("Info", "Success", etc.).
            message (str): Message to display.
            debug_level (int, optional): Debug level, only displays if level <= `Print.debug_level`.

        Example:
            Print.status("Info", "Operation started.")
        """
        # Check if the message is a debug message and if it meets the debug level requirement
        if status_type == "Debug" and (debug_level is not None and Print.debug_level is not None):
            if debug_level > Print.debug_level:
                return

        # Get the color for the current status type
        color = Status.text_color(status_type)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        Print.color(color, f"[[COLOR_OFF]][{timestamp}][[COLOR_ON]] [{status_type}] {message}")

    @staticmethod
    def title(text: str, width: int = TERMINAL_WIDTH_DEFAULT, flank_char: str = '=', color: str = Status.text_color("Info")) -> None:
        """
        Print a centered title with a specified width, flank character, and color.

        Args:
            text (str): Title text.
            width (int): Total width of the line (default 80).
            flank_char (str): Character to flank the title (default "=").
            color (str): text color name for the title.

        Example:
            Print.title("Chapter 1: Introduction")
        """
        width_terminal = Terminal.get_width()
        width_line=min(width_terminal, width)

        # Print rows of flank characters
        full_flank_row = flank_char * width_line
        Print.color(color, f"{full_flank_row}\n{text}\n[[COLOR_ON]]{full_flank_row}\n")

    @staticmethod
    def title_sub(text: str, width: int = TERMINAL_WIDTH_DEFAULT, flank_char: str = '-', color: str = Status.text_color("Info")) -> None:
        """Prints a subtitle using `Print.title` with modified flank character."""
        Print.title(text, width, flank_char, color)

    @staticmethod
    def step(text: str = '') -> None:
        """
        Manage step printing.

        Args:
            text (str): Description of the current step.

        Returns:
            None
        """
        if text:
            Print.step_current += 1
            Print.step_text = text

        Print.title_sub(f"{'Begin' if text else 'End'} ([[COLOR_OFF]]Step {Print.step_current} of {Option.get('step_count')}[[COLOR_ON]]): {Print.step_text}[[COLOR_ON]]{'...' if text else '.'}")

    @staticmethod
    def step_sub(substep_index_current: int, substep_index_max: int, text: str) -> None:
        """
        Print information on substeps within the current step.

        Args:
            substep_index_current (int): Current substep index.
            substep_index_max (int): Maximum number of substeps.
            text (str): Description of the substep.

        Returns:
            None
        """
        Print.status("Info", f"([[COLOR_OFF]]Step {Print.step_current} of {Option.get('step_count')}, Substep {substep_index_current} of {substep_index_max}[[COLOR_ON]]) {text}...")

class Log:
    """
    Logging utility with support for multiple log levels and optional file output.

    Attributes:
        LOG_LEVELS (list): Supported log levels.
        default_log_file (Optional[str]): Default file path for logging if none specified.

    Methods:
        log(message: str, level: str = "Info", to_file: Optional[str] = None) -> None:
            Log a message with a timestamp, level, and optional file.
        set_default_log_file(file_path: str) -> None:
            Set the default log file path.
    """

    LOG_LEVELS = ["Info", "Success", "Notice", "Error", "Debug"]
    default_log_file: Optional[str] = None  # Default file path for logging

    @staticmethod
    def log(message: str, level: str = "Info", to_file: Optional[str] = None) -> None:
        """
        Log a message with a timestamp and level, optionally to a file.

        Args:
            message (str): Message to log.
            level (str): Log level (e.g., "Info", "Error").
            to_file (Optional[str]): File to write log to, uses default if None.

        Example:
            Log.log("Application started", level="Info")
        """
        if level not in Log.LOG_LEVELS:
            level = "Info"

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} [{level}] {message}"

        # Determine the file to log to: use `to_file` if provided, otherwise fall back to `default_log_file`
        log_file = to_file or Log.default_log_file

        if log_file:
            with open(log_file, "a") as file:
                file.write(log_message + "\n")
        else:
            Print.status(level, log_message)

    @classmethod
    def set_default_log_file(cls, file_path: str) -> None:
        """
        Set the default file for logging.

        Args:
            file_path (str): Path of the default log file.

        Example:
            Log.set_default_log_file("/path/to/logfile.log")
        """
        cls.default_log_file = file_path

class InputHandler:
    """
    Handles user input with validation for specific types, e.g., integers.

    Methods:
        get_integer(prompt: str, default: Optional[int] = None) -> int:
            Prompt for integer input with an optional default value.
    """

    @staticmethod
    def get_integer(prompt: str, default: Optional[int] = None) -> int:
        """
        Prompt for an integer input, with optional default value.

        Args:
            prompt (str): Prompt message to display.
            default (Optional[int]): Default value if input is empty.

        Returns:
            int: Valid integer input or default if input is empty.

        Example:
            InputHandler.get_integer("Enter a number", default=5)
        """
        while True:
            try:
                user_input = input(prompt)
                if user_input == "" and default is not None:
                    return default
                return int(user_input)
            except ValueError:
                Print.status("Error", "Invalid input. Please enter a valid integer.")

class Progress:
    """
    Progress bar utilities for displaying single or double progress bars with optional ETA.

    Attributes:
        previous_progress_bar_length (int): Length of the last printed progress bar for clearing.
        previous_progress_bar_double_length_1 (int): Length of first double progress bar.
        previous_progress_bar_double_length_2 (int): Length of second double progress bar.

    Methods:
        print_single(iteration, total, prefix, suffix, decimals, length, fill, custom_suffix) -> None:
            Display a single progress bar with optional ETA.
        print_double(iteration1, total1, iteration2, total2, ...) -> None:
            Display two synchronized progress bars with ETAs.
    """

    start_time1 = 0
    start_time2 = 0

    previous_progress_bar_length = 0  # Tracks the length of the last printed output
    previous_progress_bar_double_length_1 = 0  # Tracks the length of the last printed output
    previous_progress_bar_double_length_2 = 0  # Tracks the length of the last printed output

    @staticmethod
    def get_components(
        iteration: int,
        total: int,
        length: Optional[int] = None,
        fill: Optional[str] = None,
        decimals: Optional[int] = None,
        custom_suffix: Optional[str] = None,
        eta_style: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> Dict[str, str]:
        """Generate components for a progress bar.

        Args:
            iteration (int): Current iteration count.
            total (int): Total iterations for completion.
            length (Optional[int]): Length of the progress bar.
            fill (Optional[str]): Character to fill the bar.
            decimals (Optional[int]): Decimal places for the percentage.
            custom_suffix (Optional[str]): Additional custom text to display at the end.
            eta_style (Optional[str]): Style format for the ETA display.
            start_time (Optional[datetime]): Start time for ETA calculation.

        Returns:
            dict[str, str]: Dictionary containing the progress bar components.
        """
        # Use defaults if parameters are None
        length = length if length is not None else Option.get('progress_length')
        fill = fill if fill is not None else Option.get('progress_fill')
        decimals = decimals if decimals is not None else Option.get('progress_decimals')
        eta_style = eta_style if eta_style is not None else Option.get('progress_eta_style')

        filled_length = int(length * iteration // total)

        return {
            'bar': f"|{fill * filled_length}{'-' * (length - filled_length)}|",
            'percent': f"{100 * (iteration / float(total)):.{decimals}f}%",

            # Format custom suffix if provided
            'custom_suffix': custom_suffix.format(i=iteration, total=total) if custom_suffix else '',
            # Calculate ETA

            'eta': Format.eta(iteration, total, start_time, style=eta_style)
        }

    @staticmethod
    def print_single(
        iteration: int,
        total: int,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        decimals: Optional[int] = None,
        length: Optional[int] = None,
        fill: Optional[str] = None,
        custom_suffix: Optional[str] = None,
        eta_style: Optional[str] = None
    ) -> None:
        """
        Display a progress bar in the terminal with optional ETA and custom suffix.

        Args:
            iteration (int): Current iteration count.
            total (int): Total iterations for completion.
            prefix (Optional[str]): Text prefix for progress bar.
            suffix (Optional[str]): Text suffix after the progress bar.
            decimals (Optional[int]): Decimal places for percentage.
            length (Optional[int]): Length of the progress bar.
            fill (Optional[str]): Character to fill the bar.
            custom_suffix (Optional[str]): Additional custom text.
            eta_style (Optional[str]): Style for the ETA display.

        Example:
            Progress.print_single(3, 10, prefix="Loading", length=20)
        """
        global previous_progress_bar_length

        # Initialize previous_lines as a dictionary with expected keys
        previous_lines = {'print': '', 'value': 0}

        if iteration != 0:
            previous_lines = Terminal.get_line_wrap_count(previous_progress_bar_length, Terminal.get_width())
            for _ in range(previous_lines['value']):
                sys.stdout.write('\033[F')  # Cursor up a line
        else:
            Progress.start_time1 = datetime.now()

        # Use the components function to get the parts of the progress bar
        components = Progress.get_components(
            iteration=iteration,
            total=total,
            length=length,
            fill=fill,
            decimals=decimals,
            custom_suffix=custom_suffix,
            eta_style=eta_style,
            start_time=Progress.start_time1
        )

        # Use defaults if parameters are None
        prefix = prefix if prefix is not None else Option.get('progress_prefix', 'Progress:')
        suffix = suffix if suffix is not None else Option.get('progress_suffix', '')

        # Construct the final progress bar string from components
        bar = (
            f"\r{prefix} {components['bar']} {components['percent']}"
            f"{' ' + suffix if suffix else ''}"
            f"{' ' + components['custom_suffix'] if components['custom_suffix'] else ''}"
            f"{' ' + components['eta'] if components['eta'] else ''}"
        )

        print(bar, end='\r\n')  # Newline added here for separation after each update

        if iteration == total:
            previous_progress_bar_length = 0
            print()  # Move to the next line on completion
        else:
            previous_progress_bar_length = len(bar.replace('\n', '').replace('\r', ''))

    @staticmethod
    def print_double(
        iteration1: int,
        total1: int,
        iteration2: int,
        total2: int,
        prefix1: Optional[str] = None,
        suffix1: Optional[str] = None,
        prefix2: Optional[str] = None,
        suffix2: Optional[str] = None,
        decimals: Optional[int] = None,
        length: Optional[int] = None,
        fill: Optional[str] = None,
        custom_suffix1: Optional[str] = None,
        custom_suffix2: Optional[str] = None,
        eta_style: Optional[str] = None
    ) -> None:
        """
        Display two synchronized progress bars with optional ETAs and custom suffixes.

        Args:
            iteration1 (int): Current iteration count for first bar.
            total1 (int): Total for first bar.
            iteration2 (int): Current count for second bar.
            total2 (int): Total for second bar.
            prefix1 (Optional[str]): Prefix for first bar.
            suffix1 (Optional[str]): Suffix for first bar.
            prefix2 (Optional[str]): Prefix for second bar.
            suffix2 (Optional[str]): Suffix for second bar.
            decimals (Optional[int]): Decimal places for percentage.
            length (Optional[int]): Length of each bar.
            fill (Optional[str]): Fill character.
            custom_suffix1 (Optional[str]): Custom text for first bar.
            custom_suffix2 (Optional[str]): Custom text for second bar.
            eta_style (Optional[str]): Style for the ETA display.

        Example:
            Progress.print_double(3, 10, 2, 5, prefix1="Task", prefix2="Overall")
        """
        global previous_progress_bar_double_length_1
        global previous_progress_bar_double_length_2

        previous_lines = 0

        if iteration1 != 0:
            width_terminal = Terminal.get_width()
            previous_lines = Terminal.get_line_wrap_count(previous_progress_bar_double_length_1, width_terminal)['value']
            previous_lines += Terminal.get_line_wrap_count(previous_progress_bar_double_length_2, width_terminal)['value']
            for _ in range(previous_lines):
                sys.stdout.write('\033[F' + ' ' * width_terminal + '\r')  # Cursor up a line
        else:
            Progress.start_time1 = datetime.now()

        if not iteration2:
            Progress.start_time2 = datetime.now()

        # Use the components function to get parts for both progress bars
        components1 = Progress.get_components(
            iteration=iteration1, total=total1,
            length=length, fill=fill, decimals=decimals,
            custom_suffix=custom_suffix1,
            eta_style=eta_style,
            start_time=Progress.start_time1
        )

        components2 = Progress.get_components(
            iteration=iteration2, total=total2,
            length=length, fill=fill, decimals=decimals,
            custom_suffix=custom_suffix2,
            eta_style=eta_style,
            start_time=Progress.start_time2
        )

        # Use defaults if parameters are None
        prefix1 = prefix1 if prefix1 is not None else Option.get('progress_double_prefix1', 'Progress Current:')
        suffix1 = suffix1 if suffix1 is not None else Option.get('progress_double_suffix1', '')
        prefix2 = prefix2 if prefix2 is not None else Option.get('progress_double_prefix2', 'Progress Total:')
        suffix2 = suffix2 if suffix2 is not None else Option.get('progress_double_suffix2', '')

        # Calculate dynamic widths based on the longest component for alignment
        width_prefix = max(len(prefix1), len(prefix2))
        width_percent = max(len(components1['percent']), len(components2['percent']))
        width_suffix = max(len(suffix1), len(suffix2))
        width_suffix_custom = max(len(components1['custom_suffix']), len(components2['custom_suffix']))
        width_eta = max(len(components1['eta']), len(components2['eta']))

        # Align components by setting widths and concatenating
        line1 = (
            f"{prefix1.ljust(width_prefix)} {components1['bar']} {components1['percent'].rjust(width_percent)}"
            f"{' ' + suffix1.ljust(width_suffix) if suffix1 else ''}"
            f"{' ' + components1['custom_suffix'].ljust(width_suffix_custom) if components1['custom_suffix'] else ''}"
            f"{' ' + components1['eta'].rjust(width_eta) if components1['eta'] else ''}"
        )
        line2 = (
            f"{prefix2.ljust(width_prefix)} {components2['bar']} {components2['percent'].rjust(width_percent)}"
            f"{' ' + suffix2.ljust(width_suffix) if suffix2 else ''}"
            f"{' ' + components2['custom_suffix'].ljust(width_suffix_custom) if components2['custom_suffix'] else ''}"
            f"{' ' + components2['eta'].rjust(width_eta) if components2['eta'] else ''}"
        )

        print(f"{line1}\n{line2}", end='\r\n')  # Newline added here for separation after each update

        if iteration1 == total1:
            previous_progress_bar_double_length_1 = 0
            previous_progress_bar_double_length_2 = 0
            print()

        if iteration1 != total1 or iteration2 != total2:
            previous_progress_bar_double_length_1 = len(line1.replace('\n', '').replace('\r', ''))
            previous_progress_bar_double_length_2 = len(line2.replace('\n', '').replace('\r', ''))

    @staticmethod
    def print_double_group(
        iteration1: int, total1: int,
        iteration2: int, total2: int,
        type_string_root: str, type_string_singular: str, type_string_plural: str,
        eta_style: Optional[str] = None
    ) -> None:
        """
        Displays a dual progress bar with type-based custom suffixes for each.

        Args:
            iteration1 (int): Current iteration count for the first progress bar.
            total1 (int): Total iterations for the first progress bar.
            iteration2 (int): Current iteration count for the second progress bar.
            total2 (int): Total iterations for the second progress bar.
            type_string_root (str): Root of the type string for custom suffixes.
            type_string_singular (str): Singular suffix form for the type.
            type_string_plural (str): Plural suffix form for the type.

        Returns:
            None
        """
        Progress.print_double(
            iteration1, total1,
            iteration2, total2,
            custom_suffix1=f"({{i}} of {{total}} {Format.plural_suffix(total1, type_string_root, type_string_singular, type_string_plural)})",
            custom_suffix2=f"({{i}} of {{total}} {Format.plural_suffix(total2, type_string_root, type_string_singular, type_string_plural)})",
            eta_style=eta_style)

class Test:
    """
    Provides test functions to demonstrate the utilities in the module.

    Methods:
        test_print_status() -> None:
            Display various statuses with Print.status to test status messages.
        test_print_title() -> None:
            Display titles and subtitles to test title formatting.
        test_format_duration() -> None:
            Test various durations using Format.duration.
        test_print_progress_bar() -> None:
            Demonstrate single and double progress bars.
    """

    @staticmethod
    def test_print_status() -> None:
        """
        Runs a test sequence displaying various statuses using the `Print.status` function.

        This function simulates different types of statuses with sample messages
        to demonstrate the visual output of the `Print.status` function.

        Args:
            None

        Returns:
            None
        """
        Print.step("Test Status Messages")

        # Display various status messages
        Print.status("Info", "This is an informational message.")
        Print.status("Success", "Operation completed successfully.")
        Print.status("Notice", "Please note the following changes.")
        Print.status("Error", "An error occurred during processing.")
        Print.status("Debug", "Debug information: variable x = 42", debug_level=1)
        Print.status("Debug", "Another debug message that shouldn't display.", debug_level=2)

        print()
        Print.step()

    @staticmethod
    def test_print_title() -> None:
        """
        Runs a test sequence displaying various titles and subtitles using
        `Print.title` and `Print.title_sub` functions to verify formatting and display.

        This function demonstrates how different title styles appear with varied widths,
        colors, and flank characters.

        Args:
            None

        Returns:
            None
        """
        Print.step("Test Title")

        test_count_total = 9

        # Display main titles with different configurations
        Print.step_sub(1, test_count_total, "Primary Title - Default Settings")
        Print.title("Primary Title - Default Settings")

        Print.step_sub(2, test_count_total, "Primary Title - Custom Width")
        Print.title("Primary Title - Custom Width", width=60)

        Print.step_sub(3, test_count_total, "Primary Title - Custom Flank Char")
        Print.title("Primary Title - Custom Flank Char", flank_char="~")

        Print.step_sub(4, test_count_total, "Primary Title - Custom Color")
        Print.title("Primary Title - Custom Color", color="magenta")

        Print.step_sub(5, test_count_total, "Primary Title - Custom Width & Flank")
        Print.title("Primary Title - Custom Width & Flank Char", width=50, flank_char="#")

        # Display subtitles using Print.title_sub
        Print.step_sub(6, test_count_total, "Secondary Title - Default Settings")
        Print.title_sub("Secondary Title - Default Settings")

        Print.step_sub(7, test_count_total, "Secondary Title - Custom Width")
        Print.title_sub("Secondary Title - Custom Width", width=60)

        Print.step_sub(8, test_count_total, "Secondary Title - Custom Flank Char")
        Print.title_sub("Secondary Title - Custom Flank Char", flank_char="~")

        Print.step_sub(8, test_count_total, "Secondary Title - Custom Color")
        Print.title_sub("Secondary Title - Custom Flank Char", color="magenta")

        Print.step()

    @staticmethod
    def test_format_duration() -> None:
        """
        Runs a test sequence displaying various formatted durations using the `Format.duration` function.

        This function checks how different durations are formatted in 'default', 'symbol', and 'word' styles
        to verify correctness, including edge cases.

        Args:
            None

        Returns:
            None
        """
        Print.step("Test Format Duration")

        # Define test cases with various timedelta inputs
        test_cases = [
            (timedelta(seconds=0), "Zero duration"),
            (timedelta(seconds=45), "Short duration (seconds only)"),
            (timedelta(minutes=5), "Short duration (minutes)"),
            (timedelta(hours=3), "Medium duration (hours)"),
            (timedelta(days=1), "Long duration (days only)"),
            (timedelta(days=2, hours=4, minutes=30, seconds=15), "Mixed long duration"),
            (timedelta(days=-1, hours=-5, minutes=-30), "Negative duration")
        ]

        # Run tests in both 'default', 'symbol', and 'word' styles
        for i, (duration, description) in enumerate(test_cases, start=1):
            Print.step_sub(i, len(test_cases), f"{description}")
            Print.status("Info", "Default")
            Print.status("Info", f"{description}: [[COLOR_OFF]]{Format.duration(duration, 'default')}[[COLOR_ON]] (default)")
            Print.status("Info", "Symbol")
            Print.status("Info", f"{description}: [[COLOR_OFF]]{Format.duration(duration, 'symbol')}[[COLOR_ON]] (symbol)")
            Print.status("Info", "Word")
            Print.status("Info", f"{description}: [[COLOR_OFF]]{Format.duration(duration, 'word')}[[COLOR_ON]] (word)\n")

        Print.step()

    @staticmethod
    def print_progress_bar_mock(text_max: int, eta_style: Optional[str] = None) -> None:
        """
        Demonstration function that displays a simulated single progress bar.

        Args:
            text_max (int): The maximum number of iterations to display in the mock.

        Returns:
            None
        """
        for i in range(text_max):
            # Update Progress Bar after fetching each repository's issues
            Progress.print_single(i, text_max - 1, custom_suffix=f"({{i}} of {{total}} {Format.plural_suffix(text_max, 'integer', '', 's')})", eta_style=eta_style)
            time.sleep(0.1)

    @staticmethod
    def print_progress_bar_double_mock(text_max: int, num_tests_processed: int, num_tests: int, eta_style: Optional[str] = None) -> None:
        """
        Demonstration function that displays two synchronized mock progress bars.

        Args:
            text_max (int): The maximum iterations for each progress bar.
            num_tests_processed (int): The count of processed tests.
            num_tests (int): The total number of tests.

        Returns:
            None
        """
        for i in range(text_max):
            Progress.print_double(
                i, text_max - 1,
                num_tests_processed * (text_max - 1) + i, num_tests * (text_max - 1),
                custom_suffix1=f"({{i}} of {{total}} {Format.plural_suffix(text_max, 'integer', '', 's')})",
                custom_suffix2=f"({{i}} of {{total}} {Format.plural_suffix(num_tests * (text_max - 1), 'integer', '', 's')})",
                eta_style=eta_style
            )

            time.sleep(0.1)

    @staticmethod
    def test_print_progress_bar() -> None:
        """
        Runs a test sequence displaying both single and double progress bars with different ETA styles.

        This function simulates progress using mock functions to test the visual output of the `Progress.print_single`
        and `Progress.print_double` functions, iterating over 'default', 'symbol', and 'word' styles. It displays a
        single progress bar first, followed by a double progress bar to demonstrate their usage.

        Args:
            None

        Returns:
            None
        """
        test_styles = ['default', 'symbol', 'word']
        text_max = 2**6 - 1

        num_tests = len(test_styles) * 2

        Print.step("Test Progress Bar")

        for i, style in enumerate(test_styles, start=1):
            Print.step_sub(i, num_tests, f"Test Progress Bar Single, Style: `[[COLOR_OFF]]{style}[[COLOR_ON]]`")
            Test.print_progress_bar_mock(text_max, eta_style=style)

        num_tests_processed = 0

        for i, style in enumerate(test_styles, start=1):
            Print.step_sub(i + len(test_styles), num_tests, f"Test Progress Bar Double, Style: `[[COLOR_OFF]]{style}[[COLOR_ON]]`")
            Test.print_progress_bar_double_mock(text_max, num_tests_processed, len(test_styles), eta_style=style)
            num_tests_processed += 1

        Print.step()

if __name__ == "__main__":
    # Define test functions to run
    tests = [
        Test.test_print_status,
        Test.test_print_title,
        Test.test_format_duration,
        Test.test_print_progress_bar
    ]

    # Set step_max to the total number of tests
    Option.set('step_count', len(tests))

    Print.title("Begin Test Print Utils")

    # Run each test in the list
    for test_func in tests:
        test_func()

    Print.title("End Test Print Utils")
