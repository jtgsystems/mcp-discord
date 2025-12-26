# Discord MCP Server - Project Documentation

## Overview

This project provides a Discord integration for the Model Context Protocol (MCP), enabling MCP clients like Claude Desktop to interact with Discord servers through a comprehensive set of tools and capabilities.

## Architecture

### Core Components

**Package Structure:**
- `src/discord_mcp/` - Main package directory
  - `__init__.py` - Package entry point with main() function
  - `server.py` - MCP server implementation with Discord bot integration

**Key Technologies:**
- **discord.py** (>=2.6.4) - Discord API wrapper for Python
- **mcp** (>=1.25.0) - Model Context Protocol implementation
- **Python** (>=3.10) - Minimum required Python version

### MCP Server Design

The server operates as a Discord bot that exposes Discord functionality through MCP tools. It uses asynchronous execution with `asyncio` and implements proper error handling and graceful shutdown.

## Available Tools

### Server Information Tools
- `get_server_info` - Retrieves detailed server information including name, member count, roles, and channels
- `list_members` - Lists server members with their roles and status

### Message Management Tools
- `send_message` - Sends messages to specified channels
- `read_messages` - Reads recent message history from channels
- `add_reaction` - Adds emoji reactions to messages
- `add_multiple_reactions` - Adds multiple reactions to a single message
- `remove_reaction` - Removes reactions from messages
- `moderate_message` - Deletes messages and applies timeouts to users

### Channel Management Tools
- `create_text_channel` - Creates new text channels
- `delete_channel` - Removes existing channels

### Role Management Tools
- `add_role` - Assigns roles to users
- `remove_role` - Removes roles from users

### Webhook Management Tools
- `create_webhook` - Creates new webhooks for channels
- `list_webhooks` - Lists all webhooks in a channel
- `send_webhook_message` - Sends messages via webhooks
- `modify_webhook` - Updates webhook settings
- `delete_webhook` - Deletes webhooks

## Setup and Configuration

### Prerequisites

1. **Discord Bot Setup:**
   - Create application at [Discord Developer Portal](https://discord.com/developers/applications)
   - Create bot and obtain token
   - Enable privileged intents:
     - MESSAGE CONTENT INTENT
     - PRESENCE INTENT
     - SERVER MEMBERS INTENT
   - Generate OAuth2 URL and invite bot to server

2. **Environment Requirements:**
   - Python 3.10 or higher
   - For Python 3.13+: Install `audioop-lts` library

### Installation Methods

#### Via Smithery (Recommended)
```bash
npx -y @smithery/cli install @hanweg/mcp-discord --client claude
```

#### Manual Installation
```bash
git clone https://github.com/hanweg/mcp-discord.git
cd mcp-discord
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Claude Desktop Configuration

Add to Claude Desktop config file:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "discord": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-discord",
        "run",
        "mcp-discord"
      ],
      "env": {
        "DISCORD_TOKEN": "your_bot_token"
      }
    }
  }
}
```

## Development

### Project Structure
```
mcp-discord/
├── src/
│   └── discord_mcp/
│       ├── __init__.py      # Package initialization and main entry point
│       └── server.py         # MCP server and Discord bot implementation
├── pyproject.toml           # Project metadata and dependencies
├── requirements.txt         # Dependency specifications
├── README.md               # User-facing documentation
├── CLAUDE.md              # This file - project documentation
├── LICENSE                # MIT License
├── Dockerfile             # Container configuration
└── smithery.yaml          # Smithery registry configuration
```

### Dependencies

**Core Dependencies:**
- `discord.py>=2.6.4` - Discord API client library
- `mcp>=1.25.0` - Model Context Protocol SDK

**Build System:**
- Hatchling - Modern Python build backend

### Running the Server

**Direct Execution:**
```bash
mcp-discord
```

**Via uv:**
```bash
uv run mcp-discord
```

**With Environment Variables:**
```bash
DISCORD_TOKEN=your_token mcp-discord
```

## Features and Capabilities

### Message Operations
- Send and read messages across channels
- React to messages with emojis (single or multiple)
- Remove reactions
- Delete messages as moderation action
- Send formatted messages via webhooks

### Server Management
- Query server information and statistics
- List members with role information
- Create and delete channels
- Manage user roles

### Webhook Integration
- Create webhooks for automated messaging
- List existing webhooks
- Send messages with custom usernames and avatars
- Modify webhook configurations
- Delete webhooks when no longer needed

### Moderation Tools
- Delete inappropriate messages
- Apply timeouts to users
- Remove reactions from messages

## Security Considerations

- **Token Security:** Discord bot token must be kept secure and never committed to version control
- **Permissions:** Bot requires appropriate Discord permissions for each operation
- **Privileged Intents:** Server requires MESSAGE CONTENT, PRESENCE, and SERVER MEMBERS intents
- **Rate Limiting:** Discord API rate limits apply to all operations

## Error Handling

The server implements:
- Graceful shutdown on KeyboardInterrupt
- Exception catching with error reporting
- Memory debugging with tracemalloc
- PyNaCl warning suppression (voice features not used)

## Docker Support

Dockerfile is provided for containerized deployment. Environment variables should be passed at runtime for security.

## Distribution

The package is distributed through:
- **PyPI:** Can be installed with pip/uv
- **Smithery:** Available via Smithery registry
- **GitHub:** Source code and releases

## Repository Information

- **Primary Repository:** https://github.com/hanweg/mcp-discord
- **Author:** Hanweg Altimer
- **License:** MIT License
- **Version:** 0.1.0

## Future Enhancements

Potential areas for expansion:
- Voice channel support
- Scheduled message sending
- Advanced moderation tools
- Server analytics and insights
- Role hierarchy management
- Bulk message operations
- Event logging and monitoring

## Support and Contribution

For issues, feature requests, or contributions, please visit the GitHub repository.

## Notes for Claude

When working with this codebase:
- The server runs asynchronously using Discord.py's async architecture
- All Discord operations are exposed as MCP tools
- Bot token is required via DISCORD_TOKEN environment variable
- Server requires appropriate Discord permissions for operations
- Supports Python 3.10+ with special considerations for 3.13+
