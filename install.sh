#!/usr/bin/env bash
# Installation rapide de xmail (https://github.com/terminalptx/xmail)
# Usage : curl -fsSL https://github.com/terminalptx/xmail/install.sh | bash      ou      bash install.sh
set -euo pipefail

REPO="https://github.com/terminalptx/xmail.git"
APP_DIR="$HOME/.local/share/xmail"
BIN_DIR="$HOME/bin"
VENV="$APP_DIR/venv"

say() { printf '\033[1;32m[xmail]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[xmail]\033[0m %s\n' "$*" >&2; exit 1; }

command -v python3 >/dev/null || die "python3 est requis."
command -v git >/dev/null     || die "git est requis."

# 1. holehe via pipx (comme l'ancienne méthode)
if ! command -v pipx >/dev/null; then
  say "pipx absent, tentative d'installation..."
  if command -v apt-get >/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y pipx
  else
    python3 -m pip install --user pipx
  fi
fi
pipx ensurepath >/dev/null 2>&1 || true
export PATH="$HOME/.local/bin:$PATH"

if command -v holehe >/dev/null; then
  say "holehe déjà installé."
else
  say "Installation de holehe..."
  pipx install holehe
fi

# 2. Récupération / mise à jour du dépôt
mkdir -p "$APP_DIR" "$BIN_DIR"
if [ -d "$APP_DIR/repo/.git" ]; then
  say "Mise à jour du dépôt..."
  git -C "$APP_DIR/repo" pull --ff-only
else
  say "Clonage du dépôt..."
  git clone --depth 1 "$REPO" "$APP_DIR/repo"
fi

# 3. Environnement isolé pour les dépendances Python de xmail.py
if [ ! -x "$VENV/bin/python" ]; then
  say "Création de l'environnement virtuel..."
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --upgrade pip requests dnspython

# 4. Lanceur ~/bin/xmail
cat > "$BIN_DIR/xmail" <<EOF
#!/usr/bin/env bash
export PATH="\$HOME/.local/bin:\$PATH"
exec "$VENV/bin/python" "$APP_DIR/repo/xmail.py" "\$@"
EOF
chmod +x "$BIN_DIR/xmail"

# 5. PATH (une seule fois)
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -f "$rc" ] || continue
  grep -q 'xmail-path' "$rc" 2>/dev/null || \
    echo 'export PATH=$HOME/bin:$HOME/.local/bin:$PATH  # xmail-path' >> "$rc"
done

say "Installation terminée. Ouvrez un nouveau terminal (ou: source ~/.bashrc) puis :"
say "  xmail nom@exemple.com"
say "Optionnel : export HIBP_API_KEY=...  et  SEARXNG_URL=https://..."
