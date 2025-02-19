from discord.ext import commands
import discord
from setup_wizard import SetupWizard

class SetupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        """Initialize Crystal Hub with an epic setup"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions!")
            return
            
        try:
            wizard = SetupWizard(self.bot)
            await wizard.start_setup(ctx)
        except Exception as e:
            await ctx.send(f"❌ Setup failed: {str(e)}")

async def setup(bot):
    await bot.add_cog(SetupCommands(bot)) 
