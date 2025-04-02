import os
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps

import discord
from discord.ext import commands
from mcp.server import Server
from mcp.types import Tool, TextContent, EmptyResult
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-mcp-server")

# Discord bot setup
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

# Initialize Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize MCP server
app = Server("discord-server")

# Store Discord client reference
discord_client = None

@bot.event
async def on_ready():
    global discord_client
    discord_client = bot
    logger.info(f"Logged in as {bot.user.name}")

# Helper function to ensure Discord client is ready
def require_discord_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not discord_client:
            raise RuntimeError("Discord client not ready")
        return await func(*args, **kwargs)
    return wrapper

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available Discord tools."""
    return [
        # Server Information Tools
        Tool(
            name="get_server_info",
            description="Get information about a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="list_members",
            description="Get a list of members in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of members to fetch",
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="list_all_channels",
            description="List all channels (text, voice, category, etc.) in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="get_channel_info",
            description="Get detailed information about a specific channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID of the channel"
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="edit_channel",
            description="Edit a channel's settings (name, topic, position, category)",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID of the channel to edit"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the channel"
                    },
                    "topic": {
                        "type": "string",
                        "description": "New topic for the channel (text channels only)"
                    },
                    "position": {
                        "type": "integer",
                        "description": "New position for the channel"
                    },
                    "category_id": {
                        "type": "string",
                        "description": "ID of the new category for the channel"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the edit"
                    }
                },
                "required": ["channel_id"]
            }
        ),
        # Role Management Tools
        Tool(
            name="add_role",
            description="Add a role to a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User to add role to"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Role ID to add"
                    }
                },
                "required": ["server_id", "user_id", "role_id"]
            }
        ),
        Tool(
            name="remove_role",
            description="Remove a role from a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User to remove role from"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Role ID to remove"
                    }
                },
                "required": ["server_id", "user_id", "role_id"]
            }
        ),
        Tool(
            name="list_roles",
            description="List all roles in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="create_role",
            description="Create a new role in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the new role"
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color code for the role (e.g., #FF0000)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for creating the role"
                    }
                },
                "required": ["server_id", "name"]
            }
        ),
        Tool(
            name="delete_role",
            description="Delete a role from a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "ID of the role to delete"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for deleting the role"
                    }
                },
                "required": ["server_id", "role_id"]
            }
        ),
        Tool(
            name="edit_role",
            description="Edit a role's settings (name, color)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "ID of the role to edit"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the role"
                    },
                    "color": {
                        "type": "string",
                        "description": "New hex color code for the role (e.g., #00FF00)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for editing the role"
                    }
                },
                "required": ["server_id", "role_id"]
            }
        ),
        # Channel Management Tools
        Tool(
            name="create_text_channel",
            description="Create a new text channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "Channel name"
                    },
                    "category_id": {
                        "type": "string",
                        "description": "Optional category ID to place channel in"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Optional channel topic"
                    }
                },
                "required": ["server_id", "name"]
            }
        ),
        Tool(
            name="delete_channel",
            description="Delete a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID of channel to delete"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for deletion"
                    }
                },
                "required": ["channel_id"]
            }
        ),
        # Thread Management Tools
        Tool(
            name="create_thread",
            description="Create a new thread from a message or in a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID of the channel to create the thread in (required if message_id not provided)"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "ID of the message to create the thread from (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the new thread"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content for the initial message (required for forum channels)"
                    },
                    "auto_archive_duration": {
                        "type": "integer",
                        "enum": [60, 1440, 4320, 10080],
                        "description": "Duration in minutes before auto-archiving (60, 1440, 4320, 10080)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="delete_thread",
            description="Delete a thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "ID of the thread to delete"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for deletion"
                    }
                },
                "required": ["thread_id"]
            }
        ),
        Tool(
            name="archive_thread",
            description="Archive a thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "ID of the thread to archive"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for archiving"
                    }
                },
                "required": ["thread_id"]
            }
        ),
        Tool(
            name="unarchive_thread",
            description="Unarchive a thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "ID of the thread to unarchive"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for unarchiving"
                    }
                },
                "required": ["thread_id"]
            }
        ),
        # Message Reaction Tools
        Tool(
            name="add_reaction",
            description="Add a reaction to a message",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "Message to react to"
                    },
                    "emoji": {
                        "type": "string",
                        "description": "Emoji to react with (Unicode or custom emoji ID)"
                    }
                },
                "required": ["channel_id", "message_id", "emoji"]
            }
        ),
        Tool(
            name="add_multiple_reactions",
            description="Add multiple reactions to a message",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "Message to react to"
                    },
                    "emojis": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Emoji to react with (Unicode or custom emoji ID)"
                        },
                        "description": "List of emojis to add as reactions"
                    }
                },
                "required": ["channel_id", "message_id", "emojis"]
            }
        ),
        Tool(
            name="remove_reaction",
            description="Remove a reaction from a message",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "Message to remove reaction from"
                    },
                    "emoji": {
                        "type": "string",
                        "description": "Emoji to remove (Unicode or custom emoji ID)"
                    }
                },
                "required": ["channel_id", "message_id", "emoji"]
            }
        ),
        Tool(
            name="send_message",
            description="Send a message to a specific channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    }
                },
                "required": ["channel_id", "content"]
            }
        ),
        Tool(
            name="read_messages",
            description="Read recent messages from a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of messages to fetch (max 100)",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about a Discord user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Discord user ID"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="moderate_message",
            description="Delete a message and optionally timeout the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel ID containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "ID of message to moderate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for moderation"
                    },
                    "timeout_minutes": {
                        "type": "number",
                        "description": "Optional timeout duration in minutes",
                        "minimum": 0,
                        "maximum": 40320  # Max 4 weeks
                    }
                },
                "required": ["channel_id", "message_id", "reason"]
            }
        ),
        # Application Command Tools
        Tool(
            name="list_global_commands",
            description="List all global application commands registered for the bot.",
            inputSchema={"type": "object", "properties": {}} # No input needed
        ),
        Tool(
            name="list_guild_commands",
            description="List all application commands registered for the bot in a specific guild.",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID to list commands for."
                    }
                },
                "required": ["server_id"]
            }
        ),
    ]

@app.call_tool()
@require_discord_client
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle Discord tool calls with error handling."""
    try:
        # --- Existing Tool Handlers ---
        if name == "send_message":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            message = await channel.send(arguments["content"])
            return [TextContent(type="text", text=f"Message sent successfully. Message ID: {message.id}")]

        elif name == "read_messages":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            limit = min(int(arguments.get("limit", 10)), 100)
            messages = []
            async for message in channel.history(limit=limit):
                reaction_data = [
                    {"emoji": str(reaction.emoji), "count": reaction.count}
                    for reaction in message.reactions
                ]
                messages.append({
                    "id": str(message.id),
                    "author": str(message.author),
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "reactions": reaction_data
                })
            # Corrected reaction formatting
            formatted_messages = []
            for m in messages:
                reaction_strs = [f"{r['emoji']}({r['count']})" for r in m['reactions']]
                reactions_text = ', '.join(reaction_strs) if reaction_strs else 'No reactions'
                formatted_messages.append(
                    f"{m['author']} ({m['timestamp']}): {m['content']}\n"
                    f"Reactions: {reactions_text}"
                )
            message_list = "\n".join(formatted_messages)
            return [TextContent(type="text", text=f"Retrieved {len(messages)} messages:\n\n{message_list}")]

        elif name == "get_user_info":
            user = await discord_client.fetch_user(int(arguments["user_id"]))
            user_info = {
                "id": str(user.id),
                "name": user.name,
                "discriminator": user.discriminator,
                "bot": user.bot,
                "created_at": user.created_at.isoformat()
            }
            return [TextContent(type="text", text=f"User information:\n" + "\n".join(f"{k}: {v}" for k, v in user_info.items()))]

        elif name == "moderate_message":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            message = await channel.fetch_message(int(arguments["message_id"]))
            await message.delete(reason=arguments.get("reason", "Message deleted via MCP"))
            if "timeout_minutes" in arguments and arguments["timeout_minutes"] > 0:
                if isinstance(message.author, discord.Member):
                    duration = discord.utils.utcnow() + datetime.timedelta(minutes=arguments["timeout_minutes"])
                    await message.author.timeout(duration, reason=arguments["reason"])
                    return [TextContent(type="text", text=f"Message deleted and user timed out for {arguments['timeout_minutes']} minutes.")]
            return [TextContent(type="text", text="Message deleted successfully.")]

        elif name == "get_server_info":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            info = {
                "name": guild.name,
                "id": str(guild.id),
                "owner_id": str(guild.owner_id),
                "member_count": guild.member_count,
                "created_at": guild.created_at.isoformat(),
                "description": guild.description,
                "premium_tier": guild.premium_tier,
                "explicit_content_filter": str(guild.explicit_content_filter)
            }
            return [TextContent(type="text", text=f"Server Information:\n" + "\n".join(f"{k}: {v}" for k, v in info.items()))]

        elif name == "list_members":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            limit = min(int(arguments.get("limit", 100)), 1000)
            members = []
            async for member in guild.fetch_members(limit=limit):
                members.append({
                    "id": str(member.id),
                    "name": member.name,
                    "nick": member.nick,
                    "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                    "roles": [str(role.id) for role in member.roles[1:]]  # Skip @everyone
                })
            member_list = "\n".join([f"{m['name']} (ID: {m['id']}, Roles: {', '.join(m['roles'])})" for m in members])
            return [TextContent(type="text", text=f"Server Members ({len(members)}):\n{member_list}")]

        elif name == "list_all_channels":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            logger.info(f"Raw guild.channels content for list_all_channels: {guild.channels}") # Added logging
            all_channels = [
                {"name": channel.name, "id": str(channel.id), "type": str(channel.type)}
                for channel in guild.channels
            ]
            channel_list_str = "\n".join([f"- {ch['name']} (ID: {ch['id']}, Type: {ch['type']})" for ch in all_channels])
            return [TextContent(type="text", text=f"All Channels ({len(all_channels)}):\n{channel_list_str}")]

        elif name == "get_channel_info":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            info = {
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "category_id": str(channel.category_id) if channel.category_id else None,
                "created_at": channel.created_at.isoformat(),
            }
            if isinstance(channel, discord.TextChannel):
                info["topic"] = channel.topic
            return [TextContent(type="text", text=f"Channel Information:\n" + "\n".join(f"{k}: {v}" for k, v in info.items()))]

        elif name == "edit_channel":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            edit_args = {}
            if "name" in arguments:
                edit_args["name"] = arguments["name"]
            if "topic" in arguments and isinstance(channel, discord.TextChannel):
                edit_args["topic"] = arguments["topic"]
            if "position" in arguments:
                edit_args["position"] = arguments["position"]
            if "category_id" in arguments:
                category = channel.guild.get_channel(int(arguments["category_id"]))
                if category and isinstance(category, discord.CategoryChannel):
                    edit_args["category"] = category
            await channel.edit(**edit_args, reason=arguments.get("reason", "Channel edited via MCP"))
            return [TextContent(type="text", text=f"Channel #{channel.name} (ID: {channel.id}) edited successfully.")]

        elif name == "add_role":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            member = await guild.fetch_member(int(arguments["user_id"]))
            role = guild.get_role(int(arguments["role_id"]))
            if not role:
                return [TextContent(type="text", text=f"Role with ID {arguments['role_id']} not found.")]
            await member.add_roles(role, reason="Role added via MCP")
            return [TextContent(type="text", text=f"Added role {role.name} to user {member.name}")]

        elif name == "remove_role":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            member = await guild.fetch_member(int(arguments["user_id"]))
            role = guild.get_role(int(arguments["role_id"]))
            if not role:
                return [TextContent(type="text", text=f"Role with ID {arguments['role_id']} not found.")]
            await member.remove_roles(role, reason="Role removed via MCP")
            return [TextContent(type="text", text=f"Removed role {role.name} from user {member.name}")]

        elif name == "list_roles":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            roles = [
                {"name": role.name, "id": str(role.id), "color": str(role.color)}
                for role in guild.roles if not role.is_default()  # Exclude @everyone
            ]
            role_list_str = "\n".join([f"- {r['name']} (ID: {r['id']}, Color: {r['color']})" for r in roles])
            return [TextContent(type="text", text=f"Roles ({len(roles)}):\n{role_list_str}")]

        elif name == "create_role":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            role_args = {"name": arguments["name"]}
            if "color" in arguments:
                try:
                    role_args["color"] = discord.Color(int(arguments["color"].lstrip('#'), 16))
                except ValueError:
                    return [TextContent(type="text", text="Invalid color format. Use hex code (e.g., #FF0000).")]
            new_role = await guild.create_role(**role_args, reason=arguments.get("reason", "Role created via MCP"))
            return [TextContent(type="text", text=f"Created role '{new_role.name}' (ID: {new_role.id})")]

        elif name == "delete_role":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            role = guild.get_role(int(arguments["role_id"]))
            if not role:
                return [TextContent(type="text", text=f"Role with ID {arguments['role_id']} not found.")]
            await role.delete(reason=arguments.get("reason", "Role deleted via MCP"))
            return [TextContent(type="text", text=f"Deleted role '{role.name}' (ID: {arguments['role_id']}) successfully.")]

        elif name == "edit_role":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            role = guild.get_role(int(arguments["role_id"]))
            if not role:
                return [TextContent(type="text", text=f"Role with ID {arguments['role_id']} not found.")]
            edit_args = {}
            if "name" in arguments:
                edit_args["name"] = arguments["name"]
            if "color" in arguments:
                try:
                    edit_args["color"] = discord.Color(int(arguments["color"].lstrip('#'), 16))
                except ValueError:
                    return [TextContent(type="text", text="Invalid color format. Use hex code (e.g., #00FF00).")]
            await role.edit(**edit_args, reason=arguments.get("reason", "Role edited via MCP"))
            return [TextContent(type="text", text=f"Role '{role.name}' (ID: {role.id}) edited successfully.")]

        elif name == "create_text_channel":
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            category = None
            if "category_id" in arguments:
                category = guild.get_channel(int(arguments["category_id"]))
            channel = await guild.create_text_channel(
                name=arguments["name"],
                category=category,
                topic=arguments.get("topic"),
                reason="Channel created via MCP"
            )
            return [TextContent(type="text", text=f"Created text channel #{channel.name} (ID: {channel.id})")]

        elif name == "delete_channel":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            await channel.delete(reason=arguments.get("reason", "Channel deleted via MCP"))
            return [TextContent(type="text", text="Deleted channel successfully")]

        elif name == "create_thread":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            thread_name = arguments["name"]
            content = arguments.get("content")
            auto_archive_duration = arguments.get("auto_archive_duration")
            reason = arguments.get("reason", "Thread created via MCP")

            if "message_id" in arguments:
                message = await channel.fetch_message(int(arguments["message_id"]))
                thread = await message.create_thread(
                    name=thread_name,
                    auto_archive_duration=auto_archive_duration,
                    reason=reason
                )
            elif isinstance(channel, discord.ForumChannel):
                if not content:
                    return [TextContent(type="text", text="Content is required when creating a thread in a forum channel.")]
                thread = await channel.create_thread(
                    name=thread_name,
                    content=content,
                    auto_archive_duration=auto_archive_duration,
                    reason=reason
                )
            elif isinstance(channel, discord.TextChannel):
                thread = await channel.create_thread(
                    name=thread_name,
                    auto_archive_duration=auto_archive_duration,
                    reason=reason
                )
            else:
                return [TextContent(type="text", text="Invalid channel type for creating a thread.")]
            return [TextContent(type="text", text=f"Created thread '{thread.name}' (ID: {thread.id})")]

        elif name == "delete_thread":
            thread = await discord_client.fetch_channel(int(arguments["thread_id"]))
            if isinstance(thread, discord.Thread):
                await thread.delete(reason=arguments.get("reason", "Thread deleted via MCP"))
                return [TextContent(type="text", text=f"Deleted thread '{thread.name}' (ID: {arguments['thread_id']}).")]
            return [TextContent(type="text", text=f"Channel ID {arguments['thread_id']} is not a thread.")]

        elif name == "archive_thread":
            thread = await discord_client.fetch_channel(int(arguments["thread_id"]))
            if isinstance(thread, discord.Thread):
                await thread.edit(archived=True, reason=arguments.get("reason", "Thread archived via MCP"))
                return [TextContent(type="text", text=f"Archived thread '{thread.name}' (ID: {thread.id}).")]
            return [TextContent(type="text", text=f"Channel ID {arguments['thread_id']} is not a thread.")]

        elif name == "unarchive_thread":
            thread = await discord_client.fetch_channel(int(arguments["thread_id"]))
            if isinstance(thread, discord.Thread):
                await thread.edit(archived=False, reason=arguments.get("reason", "Thread unarchived via MCP"))
                return [TextContent(type="text", text=f"Unarchived thread '{thread.name}' (ID: {thread.id}).")]
            return [TextContent(type="text", text=f"Channel ID {arguments['thread_id']} is not a thread.")]

        elif name == "add_reaction":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            message = await channel.fetch_message(int(arguments["message_id"]))
            await message.add_reaction(arguments["emoji"])
            return [TextContent(type="text", text=f"Added reaction {arguments['emoji']} to message")]

        elif name == "add_multiple_reactions":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            message = await channel.fetch_message(int(arguments["message_id"]))
            for emoji in arguments["emojis"]:
                await message.add_reaction(emoji)
            return [TextContent(type="text", text=f"Added reactions: {', '.join(arguments['emojis'])} to message")]

        elif name == "remove_reaction":
            channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
            message = await channel.fetch_message(int(arguments["message_id"]))
            await message.remove_reaction(arguments["emoji"], discord_client.user)
            return [TextContent(type="text", text=f"Removed reaction {arguments['emoji']} from message")]

        # Application Command Handlers
        elif name == "list_global_commands":
            commands_data = await discord_client.http.get_global_commands()
            command_list = [f"- {cmd['name']} (ID: {cmd['id']}, Type: {cmd.get('type', 1)})" for cmd in commands_data] # Type 1 is CHAT_INPUT
            return [TextContent(
                type="text",
                text=f"Global Application Commands ({len(command_list)}):\n" + "\n".join(command_list)
            )]

        elif name == "list_guild_commands":
            guild_id = int(arguments["server_id"])
            commands_data = await discord_client.http.get_guild_commands(guild_id)
            command_list = [f"- {cmd['name']} (ID: {cmd['id']}, Type: {cmd.get('type', 1)})" for cmd in commands_data] # Type 1 is CHAT_INPUT
            return [TextContent(
                type="text",
                text=f"Guild Application Commands for {guild_id} ({len(command_list)}):\n" + "\n".join(command_list)
            )]

        raise ValueError(f"Unknown tool: {name}")

    except discord.Forbidden:
        return [TextContent(type="text", text="Bot lacks permission to perform this action. Please check its roles and permissions in the server.")]
    except discord.NotFound:
        return [TextContent(type="text", text="Resource not found. Please check the provided IDs (e.g., server_id, channel_id, user_id).")]
    except ValueError as ve:
        return [TextContent(type="text", text=f"Value error: {str(ve)}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"An unexpected error occurred: {str(e)}")]

async def main():
    # Start Discord bot in the background
    asyncio.create_task(bot.start(DISCORD_TOKEN))

    # Run MCP server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())