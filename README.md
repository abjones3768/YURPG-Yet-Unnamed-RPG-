# YURPG-Yet-Unnamed-RPG-
hehe

Here are the instructions to run the game on linux (does not work on jupyter due to their hardware not having an audio device):

1. Install project files into a directory

2. cd into the directory with project files

3. Set up current folder to run pygame with these commands:

python -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install pygame-ce

4. Now run the game with this:

python main.py