import discord
from discord.ext import commands
from aiohttp import web
import asyncio
from urllib.parse import urlencode
import aiohttp
import random
import datetime
import os
from dotenv import load_dotenv
import json
import aiofiles
from datetime import timedelta
import base64
import cryptography
from cryptography.fernet import Fernet
import io
import hashlib
import platform
import uuid
from discord import app_commands

# Import our modules
from obfuscation import CrystalObfuscator
from integration import AutoIntegration, hwid_data, script_database, save_scripts
from control_panel import EnhancedControlPanel
from cogs.admin import AdminCommands
from cogs.scripts import ScriptManagement
from cogs.setup import SetupCommands

# Update these constants with your actual Discord IDs
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

# Replace these with your actual role IDs from your Discord server
CONTROL_PANEL_CHANNEL_ID = 1340825360769613834
BUYER_ROLE_ID = 1340825360769613834
ADMIN_ROLE_ID = 1340825360769613834

# At the top with your other imports
KEYS_FILE = "keys.json"

# HWID management
hwid_data = {
    "users": {},  # Store user HWIDs
    "resets": {},  # Track HWID resets
    "blacklist": []
}

try:
    with open("hwid_data.json", "r") as f:
        hwid_data = json.load(f)
except FileNotFoundError:
    with open("hwid_data.json", "w") as f:
        json.dump(hwid_data, f, indent=4)

async def save_hwid_data():
    async with aiofiles.open("hwid_data.json", "w") as f:
        await f.write(json.dumps(hwid_data, indent=4))

# Initialize keys structure
keys_data = {
    "generated": {},  # Store generated keys
    "activated": {}   # Store activated keys
}

# Load existing keys if file exists
try:
    with open(KEYS_FILE, 'r') as f:
        keys_data = json.load(f)
except FileNotFoundError:
    # Create file if it doesn't exist
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys_data, f, indent=4)

async def save_keys():
    async with aiofiles.open(KEYS_FILE, 'w') as f:
        await f.write(json.dumps(keys_data, indent=4))

load_dotenv()

async def load_configs():
    """Load all configuration files"""
    try:
        # Load HWID data
        if os.path.exists("hwid_data.json"):
            async with aiofiles.open("hwid_data.json", "r") as f:
                content = await f.read()
                hwid_data.update(json.loads(content))
        
        # Load script database
        if os.path.exists("scripts.json"):
            async with aiofiles.open("scripts.json", "r") as f:
                content = await f.read()
                script_database.update(json.loads(content))
        
        return True
    except Exception as e:
        print(f"Error loading configs: {e}")
        return False

class CrystalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            help_command=None
        )
        # Initialize our systems
        self.obfuscator = CrystalObfuscator()
        self.integration = AutoIntegration(self)
        self.script_database = script_database
        self.hwid_data = hwid_data
        
    async def setup_hook(self):
        # Initialize control panel after event loop is running
        self.control_panel = EnhancedControlPanel(self)
        
        # Load configurations
        await load_configs()
        
        # Load cogs
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.scripts")
        await self.load_extension("cogs.setup")
        await self.load_extension("cogs.support")
        await self.load_extension("cogs.help")
        
        # Sync commands
        await self.tree.sync()

# Initialize bot
bot = CrystalBot()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
