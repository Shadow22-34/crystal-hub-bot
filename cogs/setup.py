from discord.ext import commands
import discord
from ..setup_wizard import SetupWizard

class SetupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wizard = SetupWizard(bot)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        """Initialize Crystal Hub"""
        await self.wizard.start_setup(ctx)

async def setup(bot):
    await bot.add_cog(SetupCommands(bot)) 
