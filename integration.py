from typing import Optional
import aiohttp
import asyncio
from . import bot, hwid_data, script_database, save_scripts
from .obfuscation import CrystalObfuscator

class AutoIntegration:
    def __init__(self, bot):
        self.bot = bot
        self.update_lock = asyncio.Lock()
        self.script_cache = {}
