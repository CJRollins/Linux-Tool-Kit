#!/usr/bin/env bash
# install.sh — symlink Linux-Tool-Kit binaries into ~/.local/bin (or $TARGET_DIR).
#
# Usage:
#   ./install.sh             # link each script in bin/ into the target directory
#   ./install.sh uninstall   # remove only the symlinks this installer created
#   TARGET_DIR=/usr/local/bin sudo ./install.sh   # system-wide install
#
# Idempotent: re-running install is safe. Uninstall only removes its own
# symlinks — never deletes arbitrary files at the target.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$REPO_DIR/bin"
TARGET_DIR="${TARGET_DIR:-$HOME/.local/bin}"

if [[ ! -d "$BIN_DIR" ]]; then
    echo "error: $BIN_DIR does not exist — nothing to install" >&2
    exit 1
fi

action="${1:-install}"

case "$action" in
    install)
        mkdir -p "$TARGET_DIR"
        linked=0
        for src in "$BIN_DIR"/*; do
            [[ -f "$src" ]] || continue
            name=$(basename "$src")
            chmod +x "$src"
            ln -sf "$src" "$TARGET_DIR/$name"
            echo "linked: $TARGET_DIR/$name -> $src"
            linked=$((linked + 1))
        done

        if [[ $linked -eq 0 ]]; then
            echo "warning: no files found in $BIN_DIR" >&2
            exit 1
        fi

        # PATH sanity check
        case ":$PATH:" in
            *":$TARGET_DIR:"*)
                ;;
            *)
                echo
                echo "note: $TARGET_DIR is not on \$PATH."
                echo "      add this to your shell rc (~/.bashrc, ~/.zshrc, etc.):"
                echo "          export PATH=\"\$HOME/.local/bin:\$PATH\""
                ;;
        esac
        ;;

    uninstall)
        removed=0
        for src in "$BIN_DIR"/*; do
            [[ -f "$src" ]] || continue
            name=$(basename "$src")
            link="$TARGET_DIR/$name"
            # Only remove if the link still points at our copy.
            if [[ -L "$link" ]] && [[ "$(readlink -f "$link")" == "$(readlink -f "$src")" ]]; then
                rm "$link"
                echo "removed: $link"
                removed=$((removed + 1))
            fi
        done
        echo "$removed link(s) removed"
        ;;

    -h|--help|help)
        sed -n '2,12p' "$0" | sed 's/^# \?//'
        ;;

    *)
        echo "unknown action: $action" >&2
        echo "usage: $0 [install|uninstall|help]" >&2
        exit 2
        ;;
esac
