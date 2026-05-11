#!/usr/bin/env python3
"""
Gothic Translator: Convert Gothic text (all forms and epochs) into:
1. Whispered speech (audio via OpenAI Whisper TTS)
2. Whispered tone (written style)
3. Lox (Wren base language syntax)

Supports:
- Historical Gothic (4th-6th century)
- Medieval Gothic
- Victorian Gothic
- Gothic architecture terminology
- Modern Gothic culture/style
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple
from enum import Enum


class GothicEpoch(Enum):
    """Classification of Gothic forms by epoch"""
    HISTORICAL = "historical"      # 4th-6th century
    MEDIEVAL = "medieval"          # 5th-15th century
    VICTORIAN = "victorian"        # 18th-19th century
    ARCHITECTURE = "architecture"  # Structural/artistic terminology
    MODERN = "modern"              # Contemporary usage


class GothicTranslator:
    """Main translator class"""

    # ASCII Art Beacons
    GOBLIN_BEACON = """
    ⚡ GOBLIN BEACON ACTIVATED ⚡
       /\\_/\\
      ( o.o )  🔦 *shines flashlight*
       > ^ <
      /|   |\\
     (_|   |_)
    🌙 Beacon Guardian Awakens 🌙
    """

    LIGHTHOUSE_BEACON = """
    ═══════════════════════════════════
         ✨ GOTHIC LIGHTHOUSE BEACON ✨
    ═══════════════════════════════════
             ░▒▓█ ◐ █▓▒░
             ░▒▓█   █▓▒░
              ░▒▓███▓▒░
              ░▒▓███▓▒░
               ░▒▓█▓▒░
                ░▒█▒░
                ░▒█▒░
               ▓██████▓
              ▓██████████▓
             ░▓████████████▓░
            ░░▓█████████████▓░░
           ░░░▓█████████████▓░░░
          ░ ░ ░▓███████████▓░ ░ ░
         ░░ ░░ ░▓██████████▓░ ░░ ░░
        ═══════════════════════════════════
    🌊 Guiding Lost Souls Through Shadow 🌊
    ═══════════════════════════════════
    """

    BEACON_PULSE = ["◐", "◑", "◕", "◔"]

    # Historical Gothic vocabulary (4th-6th century)
    HISTORICAL_GOTHIC = {
        "þ": "th",
        "ƕ": "hv",
        "𐌰": "a",
        "𐌱": "b",
        "𐌲": "g",
        "𐌳": "d",
    }

    # Victorian/Archaic Gothic English patterns
    VICTORIAN_PATTERNS = {
        r"\byou\b": "thee",
        r"\byour\b": "thy",
        r"\bis\b": "doth be",
        r"\bwill\b": "shall",
        r"\bcan\b": "may",
    }

    # Whispered tone modifiers
    WHISPER_MODIFIERS = {
        "mysterious": "a shrouded mystery...",
        "dark": "draped in shadow...",
        "ancient": "echoing through centuries...",
        "eerie": "unsettling whispers...",
        "solemn": "grave and solemn...",
    }

    # Lox language constructs (Wren base)
    LOX_KEYWORDS = {
        "class": "class",
        "function": "fun",
        "variable": "var",
        "return": "return",
        "if": "if",
        "else": "else",
        "for": "for",
        "while": "while",
        "break": "break",
        "continue": "continue",
    }

    def __init__(self, show_beacons=False):
        """Initialize the translator"""
        self.detected_epoch = None
        self.show_beacons = show_beacons

    def display_goblin_beacon(self):
        """Display the goblin beacon guardian"""
        print(self.GOBLIN_BEACON)

    def display_lighthouse_beacon(self):
        """Display the lighthouse beacon"""
        print(self.LIGHTHOUSE_BEACON)

    def display_both_beacons(self):
        """Display both the goblin and lighthouse beacons"""
        print(self.GOBLIN_BEACON)
        print("\n" + "═" * 60 + "\n")
        print(self.LIGHTHOUSE_BEACON)

    def detect_epoch(self, text: str) -> GothicEpoch:
        """Detect the epoch/form of Gothic input"""
        text_lower = text.lower()

        # Check for historical Gothic markers
        if any(char in text for char in "þƕ𐌰𐌱"):
            self.detected_epoch = GothicEpoch.HISTORICAL
            return self.detected_epoch

        # Check for Medieval markers
        if re.search(r"\b(hath|doth|thee|thou|thine)\b", text_lower):
            self.detected_epoch = GothicEpoch.MEDIEVAL
            return self.detected_epoch

        # Check for Victorian Gothic markers
        if re.search(
            r"\b(mysterious|shadow|darkness|melancholy|spectral|nocturnal|macabre)\b",
            text_lower,
        ):
            self.detected_epoch = GothicEpoch.VICTORIAN
            return self.detected_epoch

        # Check for architecture terminology
        if re.search(
            r"\b(arch|vault|buttress|gargoyle|spire|nave|transept|ribbed)\b",
            text_lower,
        ):
            self.detected_epoch = GothicEpoch.ARCHITECTURE
            return self.detected_epoch

        # Default to modern
        self.detected_epoch = GothicEpoch.MODERN
        return self.detected_epoch

    def to_whispered_speech(self, text: str, tone: str = "mysterious") -> Dict:
        """
        Convert text to whispered speech format
        Returns metadata for audio synthesis
        """
        epoch = self.detect_epoch(text)

        # Create whisper prompt
        whisper_prompt = f"Speak this in a whispered tone, {tone}. Text: {text}"

        result = {
            "format": "whispered_speech",
            "epoch": epoch.value,
            "original_text": text,
            "synthesis_prompt": whisper_prompt,
            "tone": tone,
            "voice_settings": {
                "speed": 0.8,  # Slower for dramatic effect
                "pitch": -0.3,  # Deeper for mystique
                "whisper_intensity": 0.7,  # 0.0 = normal, 1.0 = heavy whisper
            },
            "instructions": f"Use OpenAI TTS API with model='tts-1', voice='shimmer', text='{whisper_prompt}'",
        }

        return result

    def to_whispered_tone_written(self, text: str) -> str:
        """
        Convert text to whispered written tone (stylistic transformation)
        """
        epoch = self.detect_epoch(text)
        result = text

        # Apply epoch-specific transformations
        if epoch == GothicEpoch.VICTORIAN or epoch == GothicEpoch.MEDIEVAL:
            for pattern, replacement in self.VICTORIAN_PATTERNS.items():
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Add whispered markers
        lines = result.split(". ")
        whispered_lines = [
            f'*whispers* "{line}..."' if i % 2 == 0 else f'*softly* "{line}..."'
            for i, line in enumerate(lines)
        ]
        result = " ".join(whispered_lines)

        # Add mystery and atmosphere
        mood_phrases = [
            "*pauses ominously*",
            "*voice trails off*",
            "*speaks barely audibly*",
            "*a hushed tone*",
        ]
        for i, phrase in enumerate(mood_phrases):
            if i < len(whispered_lines):
                whispered_lines[i] = f"{phrase} {whispered_lines[i]}"

        return "\n".join(whispered_lines)

    def to_lox(self, text: str) -> str:
        """
        Convert text to Lox (Wren base language) syntax
        Treats Gothic text as a Lox program/data structure
        """
        epoch = self.detect_epoch(text)

        # Create Lox code structure
        lox_code = [
            "// Gothic Translation to Lox",
            f'var gothicEpoch = "{epoch.value}"',
            f'var originalText = "{self._escape_lox_string(text)}"',
            "",
            "class GothicTranslation {",
            "  init(text, epoch) {",
            "    this.text = text",
            "    this.epoch = epoch",
            "    this.whispered = this.toWhispered()",
            "  }",
            "",
            "  toWhispered() {",
            '    return "*whispers* " + this.text',
            "  }",
            "",
            "  display() {",
            f'    System.print("Epoch: " + this.epoch)',
            f'    System.print("Text: " + this.text)',
            f'    System.print("Whispered: " + this.whispered())',
            "  }",
            "}",
            "",
            "var gothic = GothicTranslation.new(originalText, gothicEpoch)",
            "gothic.display()",
        ]

        return "\n".join(lox_code)

    def _escape_lox_string(self, text: str) -> str:
        """Escape special characters for Lox strings"""
        return (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

    def translate(
        self, text: str, output_format: str = "all", tone: str = "mysterious"
    ) -> Dict:
        """
        Main translation method
        Args:
            text: Input Gothic text
            output_format: 'whisper_speech', 'whisper_tone', 'lox', or 'all'
            tone: Tone for whispered speech
        """
        epoch = self.detect_epoch(text)

        result = {
            "input": text,
            "detected_epoch": epoch.value,
            "outputs": {},
        }

        if output_format in ["whisper_speech", "all"]:
            result["outputs"]["whisper_speech"] = self.to_whispered_speech(text, tone)

        if output_format in ["whisper_tone", "all"]:
            result["outputs"]["whisper_tone"] = self.to_whispered_tone_written(text)

        if output_format in ["lox", "all"]:
            result["outputs"]["lox"] = self.to_lox(text)

        return result


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Gothic Translator: Convert Gothic text to whispered speech, whispered tone, or Lox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gothic_translator.py "Ancient text" --format all --tone mysterious
  python gothic_translator.py "thee and thou" --format whisper_tone
  python gothic_translator.py "Dark castle" --format lox --output output.lox
        """,
    )

    parser.add_argument("text", help="Gothic text to translate")
    parser.add_argument(
        "--format",
        choices=["whisper_speech", "whisper_tone", "lox", "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "--tone",
        choices=["mysterious", "dark", "ancient", "eerie", "solemn"],
        default="mysterious",
        help="Tone for whispered speech (default: mysterious)",
    )
    parser.add_argument(
        "--output", "-o", help="Output file (optional)", type=str
    )
    parser.add_argument(
        "--beacon",
        choices=["goblin", "lighthouse", "both", "none"],
        default="both",
        help="Display beacon(s): goblin, lighthouse, both, or none (default: both)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    # Translate
    translator = GothicTranslator(show_beacons=args.beacon != "none")
    result = translator.translate(args.text, args.format, args.tone)

    # Format output
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        output = format_readable_output(result, show_beacons=args.beacon)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"✓ Translation saved to {args.output}")
    else:
        print(output)


def format_readable_output(result: Dict, show_beacons: str = None) -> str:
    """Format result for human reading"""
    lines = []

    # Display beacons if requested
    if show_beacons == "both":
        lines.append("\n" + ("═" * 60))
        lines.append(GothicTranslator.GOBLIN_BEACON)
        lines.append("═" * 60)
        lines.append(GothicTranslator.LIGHTHOUSE_BEACON)
        lines.append("═" * 60)
    elif show_beacons == "goblin":
        lines.append("\n" + ("═" * 60))
        lines.append(GothicTranslator.GOBLIN_BEACON)
        lines.append("═" * 60)
    elif show_beacons == "lighthouse":
        lines.append("\n" + ("═" * 60))
        lines.append(GothicTranslator.LIGHTHOUSE_BEACON)
        lines.append("═" * 60)

    lines.append("=" * 60)
    lines.append("GOTHIC TRANSLATOR")
    lines.append("=" * 60)
    lines.append(f"\nInput: {result['input']}")
    lines.append(f"Detected Epoch: {result['detected_epoch']}")
    lines.append("\n" + "-" * 60)

    for format_type, content in result["outputs"].items():
        lines.append(f"\n[{format_type.upper()}]")
        lines.append("-" * 40)

        if isinstance(content, dict):
            # Whisper speech metadata
            lines.append(f"Tone: {content.get('tone', 'N/A')}")
            lines.append(f"Synthesis Prompt: {content.get('synthesis_prompt', 'N/A')}")
            lines.append(f"Voice Settings: {json.dumps(content.get('voice_settings', {}), indent=2)}")
        else:
            # Whisper tone or Lox
            lines.append(content)

        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    main()
