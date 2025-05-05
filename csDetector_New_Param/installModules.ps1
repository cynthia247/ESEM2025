# create virtual environment to avoid polluting global namespace
python3 -m venv .venv

# activate environment
.venv/Scripts./Activate.ps1

# install modules
pip install -r requirements.txt

# install convokit dependencies
python3 -m spacy download en_core_web_sm