# Cuthbert

### Prerequisites for setup
- Python
- `poetry`
- `pyenv`
- MongoDB server

### Setup
1. `pyenv install 3.9.0`
2. `pyenv shell`
3. `poetry install` (use flag `--no-dev` for prod)
4. `poetry shell`
5. Create a file called `.env`. in the root of the project and define the following:
```
CUTHBERT_TOKEN="TOKEN HERE"
GUILD_ID=id here
ROLE_MODERATOR=id here
ROLE_MUTE=id here
CHANNEL_PUBLIC_LOGS=id here
CHANNEL_PRIVATE_LOGS=id here
```

6. Set up mongodb on your system
7. `python main.py` - if everything was set up properly you're good to go!
