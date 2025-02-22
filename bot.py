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

# Constants
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834
CONTROL_PANEL_CHANNEL_ID = 1340825360769613834
BUYER_ROLE_ID = 1340825360769613834
ADMIN_ROLE_ID = 1340825360769613834
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
        # Load server config
        try:
            async with aiofiles.open("server_config.json", "r") as f:
                content = await f.read()
                server_config = json.loads(content)
        except FileNotFoundError:
            server_config = {
                "admin_role_id": None,
                "buyer_role_id": None,
                "control_channel_id": None,
                "is_setup": False
            }
            async with aiofiles.open("server_config.json", "w") as f:
                await f.write(json.dumps(server_config, indent=4))
                
        # Load script database if not already loaded
        if not hasattr(bot, "script_database"):
            bot.script_database = script_database
            
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

# Trial system
trial_keys = {}
trial_users = {}

async def generate_trial_key():
    """Generate a 7-day trial key"""
    key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    expiry = datetime.datetime.now() + timedelta(days=7)
    trial_keys[key] = {
        "used": False,
        "expires": expiry.isoformat()
    }
    return key

@bot.tree.command(name="gettrial")
async def get_trial(interaction: discord.Interaction):
    """Get a 7-day trial key"""
    if str(interaction.user.id) in trial_users:
        await interaction.response.send_message("❌ You've already used a trial!", ephemeral=True)
        return
        
    key = await generate_trial_key()
    
    # DM the key to the user
    try:
        embed = discord.Embed(
            title="🎉 Your Trial Key",
            description=f"Here's your 7-day trial key: `{key}`\nUse `/redeem {key}` to activate!",
            color=discord.Color.green()
        )
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("✅ Trial key sent to your DMs!", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Couldn't DM you! Enable DMs and try again.", ephemeral=True)

@bot.tree.command(name="redeem")
async def redeem_trial(interaction: discord.Interaction, key: str):
    """Redeem a trial key"""
    if key not in trial_keys:
        await interaction.response.send_message("❌ Invalid key!", ephemeral=True)
        return
        
    if trial_keys[key]["used"]:
        await interaction.response.send_message("❌ Key already used!", ephemeral=True)
        return
        
    expiry = datetime.datetime.fromisoformat(trial_keys[key]["expires"])
    if expiry < datetime.datetime.now():
        await interaction.response.send_message("❌ Key expired!", ephemeral=True)
        return
        
    # Give trial role
    trial_role = discord.utils.get(interaction.guild.roles, name="Crystal Trial")
    if not trial_role:
        trial_role = await interaction.guild.create_role(
            name="Crystal Trial",
            color=discord.Color.blue(),
            reason="Trial role"
        )
    
    await interaction.user.add_roles(trial_role)
    trial_keys[key]["used"] = True
    trial_users[str(interaction.user.id)] = {
        "expires": expiry.isoformat(),
        "key": key
    }
    
    embed = discord.Embed(
        title="✅ Trial Activated",
        description="Your 7-day trial has started!\nUse `/getscript` to get started!",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
