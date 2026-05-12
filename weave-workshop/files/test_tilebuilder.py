#!/usr/bin/env python3
"""Test script for TileBuilder interactive features."""

import tilebuilder

def main():
    tb = tilebuilder.TileBuilder()
    
    print("Welcome to the TileBuilder test interface!")
    print("Type 'help' for commands, 'quit' to exit.")
    print()
    
    while True:
        try:
            cmd = input("tilebuilder> ").strip().lower()
            if not cmd:
                continue
            if cmd in ['quit', 'exit', 'q']:
                break
            
            parts = cmd.split()
            cmd_name = parts[0]
            
            if cmd_name in ['move', 'go', 'walk']:
                if len(parts) < 2:
                    print("Move where? Try: move north")
                    continue
                direction = parts[1]
                distance = 1
                if len(parts) > 2 and parts[2].isdigit():
                    distance = int(parts[2])
                result = tb.move_player(direction, distance)
                print(result)
            
            elif cmd_name in ['travel', 'fasttravel', 'journey']:
                if len(parts) < 2:
                    print("Travel where? Try: travel monastery")
                    continue
                destination = " ".join(parts[1:])
                result = tb.fast_travel_to_landmark(destination)
                print(result)
            
            elif cmd_name in ['look', 'see', 'view']:
                result = tb.look_around()
                print(result)
            
            elif cmd_name == 'map':
                radius = 10
                if len(parts) > 1 and parts[1].isdigit():
                    radius = int(parts[1])
                result = tb.get_map_view(radius)
                print(result)
            
            elif cmd_name in ['help', '?']:
                print("""Available commands:
• move/go <direction> [distance] - Move in a direction (north, south, east, west, diagonals)
• travel/journey <landmark> - Fast travel to a landmark
• look/see - Describe your current location
• map [radius] - Show map view centered on you
• help/? - Show this help
• quit/exit - Exit the test interface""")
            
            else:
                print(f"Unknown command: {cmd_name}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()