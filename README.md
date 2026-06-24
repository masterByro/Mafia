# Mafia 2.0

A Discord bot that runs live Mafia games (inspired by Town of Salem). Players receive private channels and role-specific buttons/dropdowns; the bot manages day/night phases, voting, trials, and win tracking.

This repo also contains **Mafia 1.0** (an older version).

---

## What you need


| Account / resource                  | Purpose                                                                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Discord bot**                     | Runs the game. Created in the [Discord Developer Portal](https://discord.com/developers/applications).                                     |
| **Game host (Discord user)**        | Starts/stops the game and advances phases. Must match the hard-coded host ID in `main.py` (see [Host configuration](#host-configuration)). |
| **Player accounts (Discord users)** | Regular (non-bot) members of your server. Every non-bot member in the server becomes a player when `!start` is run.                        |
| **Discord server (guild)**          | Where the game is played. The bot expects to be in **one server** and uses the first server it sees (`bot.guilds[0]`).                     |


**Minimum players:** 4 (role distribution scales up to 11+; see `Mafia_2.0/playerCreation.py`).

---

## Discord setup

### 1. Create the bot application

1. Go to [Discord Developer Portal → Applications](https://discord.com/developers/applications).
2. Click **New Application**, give it a name (e.g. `Mafia Bot`), and create it.
3. Open **Bot** in the sidebar:
  - Click **Reset Token** / **View Token** and copy the token. You will put this in `.env` (see [Run the bot](#run-the-bot)).
  - Under **Privileged Gateway Intents**, enable:
    - **Message Content Intent** (required — the bot reads `!` commands)
    - **Server Members Intent** (required — the bot lists members and assigns roles)
4. Open **OAuth2 → URL Generator**:
  - **Scopes:** `bot`
  - **Bot Permissions** (minimum set the code relies on):
    - View Channels
    - Send Messages
    - Send Messages in Threads
    - Read Message History
    - Manage Channels *(creates/deletes game channels and categories)*
    - Manage Roles *(assigns the Dead role when players die)*
  - Copy the generated invite URL and open it in a browser to add the bot to your server.

### 2. Prepare your Discord server

Before starting a game:

1. **Create a `Dead` role** in Server Settings → Roles.
  - The bot looks up a role named exactly `Dead` and assigns it to eliminated players.
  - Place it **below** the bot’s highest role so the bot can manage it.
  - You do not need to assign it manually — the bot adds/removes it during the game.
2. **Add players** — invite everyone who will play as regular Discord users (not bots).
3. **Use a dedicated server or category** (recommended). When `!start` runs, the bot creates:
  - `#courtyard` — public town square (read-only for `@everyone`, bot can post)
  - `#dead-chat` — visible to dead players (and Medium at night)
  - `#mafia-chat` — visible to mafia at night
  - Category **Mafia Players** with per-player channels:
    - `#<player-name>` — private role info and actions
    - `#<player-name>-will` — private will channel
4. **Bot role position** — the bot’s role must be high enough to:
  - Create and delete channels
  - Edit channel permission overwrites
  - Assign the `Dead` role to members

### 3. Host configuration

The game host is controlled by a Discord user ID in `Mafia_2.0/main.py`:

```python
BYRO_ID = 240752638273126400
```

Replace this with **your** Discord user ID:

1. In Discord, enable **Developer Mode** (Settings → Advanced → Developer Mode).
2. Right-click your username → **Copy User ID**.
3. Paste that number as `BYRO_ID` in `main.py`.

Only the host can run `!start`, `!end`, `!n`, and `!debugplayers`.

Optional: in `Mafia_2.0/playerCreation.py`, `ALLOW_BYRO_AS_PLAYER` controls whether the host is included in the player pool when the game starts.

---

## Local setup

### Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended; 3.9 and below will fail on type hints and recent `discord.py` dependencies)
- **pip**

### Virtual environment

Create and activate a venv inside `Mafia_2.0` so dependencies stay isolated from your system Python.

**Windows (PowerShell):**

```powershell
cd Mafia_2.0
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd Mafia_2.0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use any installed 3.10+ interpreter for the `py -3.12` / `python3` step (e.g. `py -3.10`, `py -3.13`).

Dependencies: `discord.py`, `python-dotenv`.

Reactivate the venv whenever you open a new terminal: run the `Activate.ps1` or `source` command above before starting the bot.

### Environment variables

Create `Mafia_2.0/.env` (this file is git-ignored):

```env
DISCORD_TOKEN=your_bot_token_here
```

Never commit your bot token.

---

## Run the bot

With the venv activated:

```bash
cd Mafia_2.0
python main.py
```

When the bot connects you should see:

```
<BotName>#1234 has connected to Discord!
Players: <count>
 Ready to rumble!
```

The player count is all non-bot members in the first guild the bot is in.

### Bot commands


| Command         | Who           | Description                                                     |
| --------------- | ------------- | --------------------------------------------------------------- |
| `!start`        | Host          | Assigns roles, creates channels, sends role info, begins Day 1  |
| `!end`          | Host          | Deletes game channels and removes the `Dead` role from everyone |
| `!n`            | Host          | Toggle day ↔ night (resolves night actions when moving to day)  |
| `!list`         | Anyone        | Lists alive/dead players (roles hidden for living players)      |
| `!m <message>`  | Killing roles | Set a murder note (Mafioso, Serial Killer, Jester, Jailor)      |
| `!wins`         | Anyone        | Show the win leaderboard (`wins.json`)                          |
| `!debugplayers` | Host          | Show all player roles (testing/cheat sheet)                     |


Most player actions (votes, night targets, Mayor reveal, Jailor execute, etc.) use **buttons and dropdowns** posted in private player channels — not chat commands.

### Typical session flow

1. Start the bot and confirm it is online in your server.
2. Have all players join the server.
3. Host runs `!start` in any channel the bot can read.
4. Players read their role in their private channel and use UI controls during day/night.
5. Host runs `!n` to end each phase when ready (night has a 90-second countdown in `#courtyard`, but does not auto-advance).
6. When the game finishes, host runs `!end` to clean up channels.

Win counts are persisted in `wins.json` at the repo root (created automatically on first run).

---

## Role reference

Full role descriptions and action priority order are in `[Mafia_2.0/info.txt](Mafia_2.0/info.txt)`.

---

## Troubleshooting


| Problem                          | Likely cause                                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Bot does not respond to `!start` | Message Content Intent disabled, or you are not the configured host (`BYRO_ID`)                         |
| `Players: 0` on startup          | Server Members Intent disabled, or no human members in the server                                       |
| Error about `Dead` role          | Create a server role named exactly `Dead` before starting                                               |
| Bot cannot create channels       | Missing **Manage Channels** permission or role hierarchy too low                                        |
| Bot cannot assign Dead role      | Missing **Manage Roles** permission or bot role below the `Dead` role                                   |
| Wrong server used                | Bot is in multiple servers; it always uses `bot.guilds[0]` — use a bot invite scoped to one test server |
| `TypeVarTuple` / `default` error | Python is too old for installed packages — recreate the venv with **Python 3.10+** and reinstall deps   |
| `unsupported operand type(s) for \|` | Same as above — the code uses `Role \| None` type hints, which require **Python 3.10+**              |


Logs are written to `Mafia_2.0/discord.log` while the bot runs.
