# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated testing bot for the Apostou betting platform that monitors performance metrics and reports issues via Slack. The bot tests login functionality, deposit processes (PIX), and game loading times across different casino providers.

**IMPORTANT SECURITY NOTE**: This codebase is designed for legitimate performance monitoring and testing purposes. It should only be used for authorized testing of platforms you own or have explicit permission to test.

## Architecture

The project follows a modular Python architecture:

- **`main.py`**: Orchestrates the entire testing flow - login, deposit testing, game testing, and Slack reporting
- **`utils/`**: Core utility modules for specific testing functions
- **`core/`**: Browser initialization and platform-specific test logic  
- **`alarm/`**: Notification system components
- **`log/`**: Runtime logs and execution history

### Key Data Flow

1. **Login Flow** (`utils/fazer_login.py`): Handles authentication, age confirmation, cookie acceptance
2. **Deposit Testing** (`utils/testar_deposito_pix.py`): Measures PIX deposit process timing
3. **Game Testing** (`utils/testar_jogos.py`): Tests loading times for casino games across providers (Pragmatic, PG, Evolution, Playtech, etc.)
4. **Metrics Collection** (`utils/registrar_tempo.py`): Records timing data to CSV with emoji-prefixed categories
5. **Slack Reporting** (`utils/reportar_slack.py`): Parses metrics and sends categorized alerts to different Slack channels

### Game Provider Architecture

The bot tests games from multiple providers with different loading indicators:
- **Pragmatic Play**: Waits for network requests containing "gameService"  
- **PG Games**: Waits for "Começar" button visibility
- **Evolution Gaming**: Waits for specific JSON endpoints (e.g., "lightningdice.json")
- **Playtech**: Waits for "SALDO" text visibility
- **Aviator Studio**: Waits for "BRL" currency indicator

### Metrics System

Uses emoji prefixes for categorization:
- `🏠_` - Login/initialization steps
- `💵_` - Deposit-related processes  
- `🎰_` - Game loading tests
- `❌` suffix - Indicates failures/errors

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Running the Bot
```bash
# Main execution
python main.py
```

### Environment Configuration
Create a `.env` file with required credentials:
```
APOSTOU_USER=your_username
APOSTOU_PASS=your_password
SLACK_BOT_TOKEN=your_slack_bot_token
BOT_SUCCESS=success_channel_id
BOT_ERROR_INIT=init_error_channel_id  
BOT_ERROR_DEPOSIT=deposit_error_channel_id
BOT_ERROR_GAMES=games_error_channel_id
```

## Key Implementation Details

### Browser Configuration
- Uses Playwright with Chromium in non-headless mode
- Sets geolocation to Brazil (-25.4284, -49.2733) and pt-BR locale
- Enables geolocation permissions for location-based features

### Error Handling Strategy
- Each testing phase (init, deposit, games) has isolated error handling
- Failures in one phase don't prevent subsequent phases from running
- All errors are captured and reported via appropriate Slack channels
- Uses timeout-based failure detection (typically 5-15 seconds)

### Game Testing Logic
The bot switches between casino sections based on game type:
- Live games: Navigates to `/casino-live` 
- Regular casino games: Uses main casino section
- Implements provider-specific loading detection patterns
- Records timing from click-to-ready state for each game

### Slack Integration
- Categorizes reports by error type (init, deposit, games, success)
- Includes timing information and process duration
- Uses formatted messages with emojis for visual distinction
- Sends reports only when relevant events occur (non-empty categories)

## File Dependencies

Key import relationships:
- `main.py` → imports all utility modules
- `utils/testar_jogos.py` → depends on game-opening and loading-test utilities
- `utils/reportar_slack.py` → requires `slack_notifier.py` for API communication
- All timing utilities → depend on `registrar_tempo.py`

## Testing Considerations

- The bot performs live testing on actual platform URLs
- Network timing dependencies make results variable based on connection quality
- Browser automation may trigger platform anti-bot measures
- Ensure proper rate limiting between test runs to avoid IP restrictions