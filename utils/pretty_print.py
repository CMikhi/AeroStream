#!/usr/bin/env python3
"""
ASCII Art Pretty Printer

This script reads ASCII art from logo.txt and prints it with customizable colors and sizes.
Features:
- Color customization using ANSI color codes
- Resizing capabilities (scale up/down)
- Multiple color themes
- Custom color options

# Basic usage with default white color
python3 pretty_print.py

# Colorful rainbow effect
python3 pretty_print.py --color rainbow

# Small red logo with bold style
python3 pretty_print.py --color red --scale 0.3 --style bold

# Large bright cyan logo
python3 pretty_print.py --color bright_cyan --scale 2.0

# Fire effect with medium size
python3 pretty_print.py --color fire --scale 0.7

# List all available colors
python3 pretty_print.py --list-colors

# Preview different color themes
python3 pretty_print.py --preview

# Use a different ASCII file
python3 pretty_print.py --file my_logo.txt --color ocean

"""

import argparse
import os
import sys
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'

class ASCIIArtPrinter:
    """Class to handle ASCII art printing with colors and resizing"""
    
    def __init__(self, logo_file: str = "logo.txt"):
        self.logo_file = logo_file
        self.ascii_lines = []
        self.load_ascii_art()
    
    def load_ascii_art(self):
        """Load ASCII art from file"""
        try:
            with open(self.logo_file, 'r', encoding='utf-8') as f:
                self.ascii_lines = [line.rstrip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: Could not find {self.logo_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {self.logo_file}: {e}")
            sys.exit(1)
    
    def get_color_themes(self):
        """Get predefined color themes"""
        return {
            'red': Colors.RED,
            'green': Colors.GREEN,
            'blue': Colors.BLUE,
            'yellow': Colors.YELLOW,
            'magenta': Colors.MAGENTA,
            'cyan': Colors.CYAN,
            'white': Colors.WHITE,
            'bright_red': Colors.BRIGHT_RED,
            'bright_green': Colors.BRIGHT_GREEN,
            'bright_blue': Colors.BRIGHT_BLUE,
            'bright_yellow': Colors.BRIGHT_YELLOW,
            'bright_magenta': Colors.BRIGHT_MAGENTA,
            'bright_cyan': Colors.BRIGHT_CYAN,
            'bright_white': Colors.BRIGHT_WHITE,
            'rainbow': 'rainbow',  # Special case for rainbow effect
            'fire': 'fire',  # Special case for fire effect
            'ocean': 'ocean',  # Special case for ocean effect
        }
    
    def apply_rainbow_effect(self, text: str) -> str:
        """Apply rainbow color effect to text"""
        rainbow_colors = [
            Colors.RED, Colors.YELLOW, Colors.GREEN, 
            Colors.CYAN, Colors.BLUE, Colors.MAGENTA
        ]
        colored_text = ""
        color_index = 0
        
        for char in text:
            if char != ' ':
                colored_text += rainbow_colors[color_index % len(rainbow_colors)] + char
                color_index += 1
            else:
                colored_text += char
        
        return colored_text + Colors.RESET
    
    def apply_fire_effect(self, text: str, line_num: int) -> str:
        """Apply fire color effect (red to yellow gradient)"""
        fire_colors = [Colors.BRIGHT_RED, Colors.RED, Colors.YELLOW, Colors.BRIGHT_YELLOW]
        color = fire_colors[line_num % len(fire_colors)]
        
        colored_text = ""
        for char in text:
            if char != ' ':
                colored_text += color + char
            else:
                colored_text += char
        
        return colored_text + Colors.RESET
    
    def apply_ocean_effect(self, text: str, line_num: int) -> str:
        """Apply ocean color effect (blue to cyan gradient)"""
        ocean_colors = [Colors.BLUE, Colors.BRIGHT_BLUE, Colors.CYAN, Colors.BRIGHT_CYAN]
        color = ocean_colors[line_num % len(ocean_colors)]
        
        colored_text = ""
        for char in text:
            if char != ' ':
                colored_text += color + char
            else:
                colored_text += char
        
        return colored_text + Colors.RESET
    
    def resize_ascii(self, scale_factor: float) -> List[str]:
        """Resize ASCII art by scaling factor"""
        if scale_factor == 1.0:
            return self.ascii_lines
        
        resized_lines = []
        
        if scale_factor > 1.0:
            # Scale up - duplicate characters horizontally and lines vertically
            h_scale = int(scale_factor)
            v_scale = int(scale_factor)
            
            for line in self.ascii_lines:
                # Expand horizontally
                expanded_line = ""
                for char in line:
                    expanded_line += char * h_scale
                
                # Expand vertically
                for _ in range(v_scale):
                    resized_lines.append(expanded_line)
        
        else:
            # Scale down - sample lines and characters
            v_step = int(1 / scale_factor)
            h_step = int(1 / scale_factor)
            
            for i in range(0, len(self.ascii_lines), v_step):
                line = self.ascii_lines[i]
                sampled_line = ""
                for j in range(0, len(line), h_step):
                    sampled_line += line[j]
                resized_lines.append(sampled_line)
        
        return resized_lines
    
    def print_ascii(self, color: str = 'white', scale: float = 1.0, style: str = ''):
        """Print ASCII art with specified color and scale"""
        color_themes = self.get_color_themes()
        
        # Get resized ASCII
        ascii_to_print = self.resize_ascii(scale)
        
        # Apply style if specified
        style_code = ''
        if style:
            style_mapping = {
                'bold': Colors.BOLD,
                'dim': Colors.DIM,
                'underline': Colors.UNDERLINE,
                'blink': Colors.BLINK,
                'reverse': Colors.REVERSE,
            }
            style_code = style_mapping.get(style.lower(), '')
        
        # Print with color
        for line_num, line in enumerate(ascii_to_print):
            if color == 'rainbow':
                print(style_code + self.apply_rainbow_effect(line))
            elif color == 'fire':
                print(style_code + self.apply_fire_effect(line, line_num))
            elif color == 'ocean':
                print(style_code + self.apply_ocean_effect(line, line_num))
            elif color in color_themes:
                color_code = color_themes[color]
                print(f"{style_code}{color_code}{line}{Colors.RESET}")
            else:
                # Try to use as direct color code
                print(f"{style_code}{color}{line}{Colors.RESET}")
    
    def list_colors(self):
        """List available colors"""
        themes = self.get_color_themes()
        print("Available colors:")
        for theme_name in themes.keys():
            print(f"  - {theme_name}")
    
    def show_preview(self):
        """Show a preview of different color options"""
        themes = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'rainbow', 'fire', 'ocean']
        
        # Show just the first few lines for preview
        preview_lines = self.ascii_lines[:5] if len(self.ascii_lines) > 5 else self.ascii_lines
        original_lines = self.ascii_lines
        self.ascii_lines = preview_lines
        
        for theme in themes:
            print(f"\n--- {theme.upper()} ---")
            self.print_ascii(color=theme)
        
        # Restore original lines
        self.ascii_lines = original_lines

def main():
    parser = argparse.ArgumentParser(description='Print ASCII art with colors and resizing')
    parser.add_argument('--color', '-c', default='white', 
                       help='Color theme (use --list-colors to see options)')
    parser.add_argument('--scale', '-s', type=float, default=1.0,
                       help='Scale factor (1.0=original, 2.0=double size, 0.5=half size)')
    parser.add_argument('--style', choices=['bold', 'dim', 'underline', 'blink', 'reverse'],
                       help='Text style')
    parser.add_argument('--file', '-f', default='logo.txt',
                       help='ASCII art file to load (default: logo.txt)')
    parser.add_argument('--list-colors', action='store_true',
                       help='List available colors')
    parser.add_argument('--preview', action='store_true',
                       help='Show preview of different colors')
    
    args = parser.parse_args()
    
    # Create printer instance
    printer = ASCIIArtPrinter(args.file)
    
    if args.list_colors:
        printer.list_colors()
        return
    
    if args.preview:
        printer.show_preview()
        return
    
    # Print the ASCII art
    printer.print_ascii(color=args.color, scale=args.scale, style=args.style)

if __name__ == "__main__":
    main()