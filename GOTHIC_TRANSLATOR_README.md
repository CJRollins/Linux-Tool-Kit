# Gothic Translator

A Python utility that translates **any form of Gothic** (by origin and epoch) into three output formats:
1. **Whispered Speech** (audio synthesis metadata)
2. **Whispered Tone** (written stylistic transformation)
3. **Lox** (Wren base language code)

## Features

### 🧟 Beacon Features (Por que no los dos?)
Display mystical beacons to guide your translations:
- **Goblin Beacon** 🔦 - A goblin guardian with flashlight illuminating the darkness
- **Lighthouse Beacon** 🏰 - A towering Gothic lighthouse guiding lost souls
- **Both Beacons** (default) - Activate both guardians for maximum mystique!
- **None** - Suppress beacon display if preferred

### Supported Gothic Forms
- **Historical Gothic** (4th-6th century) - Ancient Germanic language
- **Medieval Gothic** (5th-15th century) - Middle Ages variations
- **Victorian Gothic** (18th-19th century) - Dark romantic literature style
- **Architecture Gothic** - Structural and artistic terminology
- **Modern Gothic** - Contemporary usage and culture

### Output Formats

#### 1. Whispered Speech
Generates metadata for audio synthesis via OpenAI TTS API:
- Voice settings (speed: 0.8, pitch: -0.3)
- Whisper intensity (0-1.0 scale)
- Synthesis prompts for realistic whispered delivery

#### 2. Whispered Tone
Transforms text into a written whispered narrative:
- Adds whisper markers (`*whispers*`, `*softly*`, etc.)
- Includes atmospheric pauses (`*pauses ominously*`, etc.)
- Applies epoch-specific language transformations

#### 3. Lox Format
Converts text into valid Lox (Wren base language) code:
- Creates a `GothicTranslation` class
- Stores epoch and text data
- Includes methods for whispered output
- Generates executable Lox syntax

## Installation

```bash
cd /home/cj/Documents/Linux-Tool-Kit
chmod +x gothic_translator.py
```

**Requirements:** Python 3.7+

## Usage

### Basic Usage
```bash
python3 gothic_translator.py "Your Gothic text here"
```

### All Output Formats
```bash
python3 gothic_translator.py "Dark castle stands alone" --format all --tone mysterious
```

### Specific Output Format
```bash
# Whispered speech metadata
python3 gothic_translator.py "thy secrets" --format whisper_speech --tone dark

# Whispered written tone
python3 gothic_translator.py "mysterious shadows" --format whisper_tone --tone eerie

# Lox code
python3 gothic_translator.py "ancient tome" --format lox
```

### Beacon Options

Use the `--beacon` flag to control beacon display:

```bash
# Display both beacons (default)
python3 gothic_translator.py "text" --beacon both

# Display only goblin beacon with flashlight
python3 gothic_translator.py "text" --beacon goblin

# Display only lighthouse beacon
python3 gothic_translator.py "text" --beacon lighthouse

# Suppress all beacons
python3 gothic_translator.py "text" --beacon none
```

### Tones Available
- `mysterious` (default)
- `dark`
- `ancient`
- `eerie`
- `solemn`

### Output to File
```bash
python3 gothic_translator.py "text" --output result.txt
python3 gothic_translator.py "text" --format lox --output result.lox
```

### JSON Output
```bash
python3 gothic_translator.py "text" --json
python3 gothic_translator.py "text" --json --output result.json
```

## Examples

### Example 1: Both Beacons Active (Default)
```bash
$ python3 gothic_translator.py "The mysterious shadows whisper secrets" --format whisper_tone
```
**Output includes:**
```
⚡ GOBLIN BEACON ACTIVATED ⚡
   /\_/\
  ( o.o )  🔦 *shines flashlight*
   > ^ <
  /|   |\
 (_|   |_)
🌙 Beacon Guardian Awakens 🌙

✨ GOTHIC LIGHTHOUSE BEACON ✨
     ░▒▓█ ◐ █▓▒░
     ░▒▓█   █▓▒░
      ░▒▓███▓▒░
    [... lighthouse tower ...]
    🌊 Guiding Lost Souls Through Shadow 🌊
```

### Example 2: Goblin Beacon Only
```bash
$ python3 gothic_translator.py "Ancient power" --format lox --beacon goblin
```
Displays only the goblin guardian with flashlight
```bash
$ python3 gothic_translator.py "The mysterious shadows whisper secrets" --format whisper_tone
```
**Output:**
```
*pauses ominously* *whispers* "The mysterious shadows whisper secrets..."
```

### Example 3: Lox Generation with Lighthouse
```bash
$ python3 gothic_translator.py "Ancient power" --format lox
```
**Output:**
```lox
// Gothic Translation to Lox
var gothicEpoch = "modern"
var originalText = "Ancient power"

class GothicTranslation {
  init(text, epoch) {
    this.text = text
    this.epoch = epoch
    this.whispered = this.toWhispered()
  }
  
  toWhispered() {
    return "*whispers* " + this.text
  }
  
  display() {
    System.print("Epoch: " + this.epoch)
    System.print("Text: " + this.text)
    System.print("Whispered: " + this.whispered())
  }
}

var gothic = GothicTranslation.new(originalText, gothicEpoch)
gothic.display()
```

### Example 3: Whispered Speech for Audio Synthesis
```bash
$ python3 gothic_translator.py "Hear the ancient call" --format whisper_speech --tone solemn --json
```
**Output includes:**
- Synthesis prompt for OpenAI TTS
- Voice settings (speed, pitch, whisper intensity)
- Ready for integration with TTS API

## Epoch Detection

The translator automatically detects the Gothic epoch based on content:
- **Historical**: Contains historical Gothic characters (þ, ƕ, 𐌰, etc.)
- **Medieval**: Contains medieval words (thee, thou, hath, doth)
- **Victorian**: Contains Gothic atmosphere words (mysterious, shadow, darkness, spectral)
- **Architecture**: Contains building terminology (arch, vault, buttress, gargoyle)
- **Modern**: Default classification for contemporary usage

## Integration with OpenAI TTS

To use whispered speech output with OpenAI's TTS API:

```python
import openai
from gothic_translator import GothicTranslator

translator = GothicTranslator()
result = translator.to_whispered_speech("your text", tone="mysterious")
prompt = result['synthesis_prompt']

# Use with OpenAI API
response = openai.Audio.create(
    model="tts-1",
    voice="shimmer",
    input=prompt,
    speed=result['voice_settings']['speed']
)
```

## Integration with Lox/Wren

The generated Lox code is valid syntax and can be executed in any Wren interpreter:

```bash
# Using wren-cli (if installed)
wren result.lox
```

## Command-Line Arguments

```
usage: gothic_translator.py [-h] [--format {whisper_speech,whisper_tone,lox,all}]
                           [--tone {mysterious,dark,ancient,eerie,solemn}]
                           [--beacon {goblin,lighthouse,both,none}]
                           [--output OUTPUT] [--json]
                           text

positional arguments:
  text                  Gothic text to translate

optional arguments:
  -h, --help            show this help message and exit
  --format {whisper_speech,whisper_tone,lox,all}
                        Output format (default: all)
  --tone {mysterious,dark,ancient,eerie,solemn}
                        Tone for whispered speech (default: mysterious)
  --beacon {goblin,lighthouse,both,none}
                        Beacons to display (default: both)
  --output OUTPUT, -o OUTPUT
                        Output file (optional)
  --json                Output as JSON
```

## Files

- `gothic_translator.py` - Main translator script
- `GOTHIC_TRANSLATOR_README.md` - This file

## Author

Created with the GitHub Copilot CLI

## License

Free to use and modify
