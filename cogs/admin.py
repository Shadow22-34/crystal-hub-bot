from discord.ext import commands
import discord
from .. import bot, script_database, save_scripts
from ..obfuscation import CrystalObfuscator

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.obfuscator = CrystalObfuscator()
    
    async def setup(bot):
        await bot.add_cog(AdminCommands(bot))
