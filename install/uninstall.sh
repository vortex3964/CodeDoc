#!/usr/bin/env bash
set -euo pipefail

# CodeDoc uninstaller
# removes the install dir, the launcher and the PATH lines the installer added

APP="codedoc"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$APP"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"

rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/$APP"

# remove the lines the installer added to shell config files
for cfg in \
    "$HOME/.bashrc" \
    "$HOME/.bash_profile" \
    "$HOME/.profile" \
    "${ZDOTDIR:-$HOME}/.zshrc" \
    "$HOME/.zshenv" \
    "$HOME/.config/fish/config.fish"; do

    if [[ -f "$cfg" ]]; then
        tmp="$(mktemp)"
        if grep -vx "# $APP" "$cfg" \
            | grep -vx "export PATH=$BIN_DIR:\$PATH" \
            | grep -vx "fish_add_path $BIN_DIR" > "$tmp"; then
            :
        fi
        mv "$tmp" "$cfg"
    fi
done

echo "$APP uninstalled"