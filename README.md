# Linux-Tool-Kit

A personal collection of small, focused command-line tools for Linux. Diagnostic
scripts that try not to lie. Stream filters that change the register of any
output. Built for one workstation, shared because pieces of it might be useful
elsewhere.

## Install

```bash
git clone https://github.com/CJRollins/Linux-Tool-Kit.git
cd Linux-Tool-Kit
./install.sh
```

`install.sh` symlinks each tool in `bin/` into `~/.local/bin`. Make sure that
directory is on your `$PATH`. To remove the symlinks later:

```bash
./install.sh uninstall
```

If you want them somewhere other than `~/.local/bin`, set `TARGET_DIR`:

```bash
TARGET_DIR=/usr/local/bin sudo ./install.sh
```

## Tools

### `auscultation`

A GPU driver diagnostic. Walks `/sys/class/drm` and `lspci` to determine which
kernel driver is bound to each DRM card, checks group membership and device
permissions for the current user, queries vendor tooling (`nvidia-smi`,
`glxinfo`, `rocm-smi`, `intel_gpu_top`), and reports honestly — including a
portability fallback for systems where `lspci -d ::CLASS` filtering doesn't
work.

Output is in a gothic register: *"the crimson familiar amdgpu is sealed to a
card at the loom."* The diagnostic logic and the prose are deliberately
separated; if you want plain output, pipe through `plainspeak` (coming) or
replace the print functions.

```bash
auscultation              # all GPUs
auscultation --amd        # AMD only
auscultation --nvidia
auscultation --intel
auscultation -h           # full options
```

### `gothicize`

A stream filter. Reads stdin, rewrites status glyphs (`✓ ⚠ ✗ ℹ`) and ~80 common
technical phrases into a gothic register, preserves ANSI colors, echoes
`=== headers ===` in ornamental form, and prints to stdout. Works on any text —
any script's output, any log file, any error stream.

```bash
apt update 2>&1   | gothicize
journalctl -b -1  | gothicize
make 2>&1         | gothicize --bare   # suppress the candle invocation
```

The lexicon is a Python list at the top of the file. Add your own mappings —
order matters (longer or more-specific phrases should come first, so they win
the match).

### `bless`

`gothicize`'s twin. Same machinery, opposite register — sunlit instead of
candlelit, blooms-and-suns instead of moons-and-crosses, *"received as gift"*
instead of *"answered the summoning."* Useful when a command falls over and you
want a softer landing.

```bash
some-failing-command 2>&1 | bless
```

Errors remain errors. The filter doesn't lie about what happened, it just
delivers the news the way a kind chaplain would.

## Extending the filters

`gothicize` and `bless` share a structure: a `SYMBOL_MAP` dict for status-glyph
substitution, a `PHRASE_MAP` list of `(regex, replacement)` pairs, and a
`_preserve_case` helper that echoes the casing of the matched word onto the
replacement.

To add your own vocabulary — project codenames, internal jargon, in-jokes —
edit either file's `PHRASE_MAP` and add entries near the top of the list so
they take precedence over more general matches. No restart, no config file, no
compile step.

A known quirk: replacements are applied independently, so phrases like
"GPU device" get both nouns rewritten and end up reading slightly redundant
(*"shining instrument instrument"*, *"metal familiar vessel"*). In both
registers, the redundancy reads as appropriately ceremonial; if it bothers you,
add a compound-phrase entry that matches both words and replaces them with one
term.

## Status

Personal toolkit. Used on one desktop (Ubuntu 25.10, kernel 7.0, AMD Granite
Ridge iGPU). Not broadly tested. Bug reports welcome on the issue tracker;
feature requests considered on their merits.

## License

MIT. See `LICENSE`.
