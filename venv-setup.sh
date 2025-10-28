#!/bin/bash

# ────────────────────────────────────────────────
# 🧰 PYTHON VENV BOOTSTRAP SCRIPT
# Auto-creates, activates, and configures a virtual environment
# Supports: pip upgrade, requirements.txt, dev tools, .gitignore
# Platform: Linux, macOS, Git Bash (Windows)
# Author: Mr. Fishermen's version (Ikora-assisted)
# ────────────────────────────────────────────────
# USAGE INSTRUCTIONS
# Save this as venv-setup.sh in your project root.
# ────────────────────────────────────────────────
#Run:

# chmod +x venv-setup.sh
# ./venv-setup.sh

# On Windows (Git Bash):
#  bash venv-setup.sh

# To Slide into your venv when using Git Bash:
# source  .venv/Scripts/activate




# ────────────────────────────────────────────────



set -e  # Exit immediately if a command fails

# 🧠 Step 1: Check for Python
echo "🔍 Checking for Python..."
if command -v python &>/dev/null; then
    PYTHON=python
elif command -v python3 &>/dev/null; then
    PYTHON=python3
else
    echo "❌ Python is not installed or not in PATH."
    exit 1
fi

# 🧱 Step 2: Create venv if missing
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment in .venv..."
    $PYTHON -m venv .venv || { echo "❌ Failed to create virtual environment."; exit 1; }
else
    echo "✅ Virtual environment already exists."
fi

# ⚡ Step 3: Activate venv (cross-platform)
echo "⚡ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# ⬆️ Step 4: Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# 📦 Step 5: Install project dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 requirements.txt found. Installing dependencies..."
    pip install -r requirements.txt
else
    echo "📋 No requirements.txt found."
    read -p "❓ Enter any packages you want to install (space-separated), or press Enter to skip: " CUSTOM_PKGS
    if [ -n "$CUSTOM_PKGS" ]; then
        echo "📦 Installing: $CUSTOM_PKGS"
        pip install $CUSTOM_PKGS
    else
        echo "⏭️  Skipping package installation."
    fi
fi

# 🛠️ Step 6: Offer dev tools
read -p "🧪 Install dev tools (black, pylint, isort)? [y/N]: " INSTALL_DEV
if [[ "$INSTALL_DEV" =~ ^[Yy]$ ]]; then
    pip install black pylint isort
    echo "✅ Dev tools installed."
else
    echo "⏭️  Dev tools skipped."
fi

# 📁 Step 7: Ensure .gitignore includes .venv/
if [ ! -f ".gitignore" ]; then
    echo ".gitignore not found. Creating one..."
    echo ".venv/" > .gitignore
    echo "✅ Added .venv/ to new .gitignore"
else
    if ! grep -qx ".venv/" .gitignore; then
        echo ".venv/" >> .gitignore
        echo "✅ Added .venv/ to existing .gitignore"
    else
        echo "✅ .venv/ already in .gitignore"
    fi
fi

# 🧠 Step 8: Show active interpreter
echo "🐍 Python interpreter now active: $(which python)"
echo "✅ Setup complete."
