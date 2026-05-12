"""Web interface for grace_ — giving you eyes on the terminal system.

Run as: python web.py
Open: http://localhost:5000
"""
import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import our existing modules
from state import read_state, WORLDS_DIR, tail_events
from souls import load as load_souls
import tilebuilder

app = Flask(__name__)
CORS(app)

# Store the TileBuilder instance
tilebuilder_instance = None

def get_tilebuilder():
    """Get or create the TileBuilder instance."""
    global tilebuilder_instance
    if tilebuilder_instance is None:
        try:
            tilebuilder_instance = tilebuilder.TileBuilder()
        except (ValueError, FileNotFoundError):
            tilebuilder_instance = None
    return tilebuilder_instance

@app.route('/')
def index():
    """Main web interface."""
    return render_template('index.html')

@app.route('/api/state')
def api_state():
    """Get current state data."""
    state = read_state()
    souls_data = load_souls()
    tb = get_tilebuilder()
    
    return jsonify({
        'state': state,
        'souls': souls_data,
        'tilebuilder': {
            'available': tb is not None,
            'position': tb.player_pos if tb else None,
            'world_seed': tb.world_seed if tb else None
        }
    })

@app.route('/api/world')
def api_world():
    """Get world data."""
    tb = get_tilebuilder()
    if not tb:
        return jsonify({'error': 'No world available'})
    
    return jsonify({
        'world': tb.world_data,
        'map_view': tb.get_map_view(15),
        'position': tb.player_pos
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    """Execute a command."""
    data = request.get_json()
    command = data.get('command', '').strip().lower()
    
    tb = get_tilebuilder()
    if not tb:
        return jsonify({'error': 'No world available'})
    
    # Parse command like in grace_.py
    parts = command.split()
    if not parts:
        return jsonify({'response': 'Empty command'})
    
    cmd = parts[0]
    
    if cmd in ["move", "go", "walk"]:
        if len(parts) < 2:
            response = "Move where? Try: move north, move south, etc."
        else:
            direction = parts[1]
            distance = 1
            if len(parts) > 2 and parts[2].isdigit():
                distance = int(parts[2])
            response = tb.move_player(direction, distance)
    
    elif cmd in ["travel", "fasttravel", "journey"]:
        if len(parts) < 2:
            response = "Travel where? Try: travel monastery, travel castle"
        else:
            destination = " ".join(parts[1:])
            response = tb.fast_travel_to_landmark(destination)
    
    elif cmd in ["look", "see", "view"]:
        response = tb.look_around()
    
    elif cmd == "map":
        radius = 10
        if len(parts) > 1 and parts[1].isdigit():
            radius = int(parts[1])
        response = tb.get_map_view(radius)
    
    elif cmd in ["help", "?"]:
        response = """Available commands:
• move/go <direction> [distance] - Move in a direction (north, south, east, west, diagonals)
• travel/journey <landmark> - Fast travel to a landmark
• look/see - Describe your current location
• map [radius] - Show map view centered on you
• help/? - Show this help"""
    
    else:
        response = f"Unknown command: {cmd}. Type 'help' for available commands."
    
    return jsonify({'response': response})

@app.route('/api/events')
def api_events():
    """Get recent events."""
    events = tail_events(20)  # Get more events for web view
    return jsonify({'events': events})

if __name__ == '__main__':
    # Create templates directory
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create static directory
    static_dir = Path(__file__).parent / 'static'
    static_dir.mkdir(exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)