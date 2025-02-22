from discord.ext import commands
import discord

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="help")
    async def help_command(self, ctx):
        """Show available commands"""
        embed = discord.Embed(
            title="🌟 Crystal Hub Commands",
            description="Available commands for your role",
            color=discord.Color.purple()
        )
        
        # Admin Commands
        if ctx.author.guild_permissions.administrator:
            admin_cmds = """
            `/setup` - Initial server setup
            `/givepremium` - Grant premium access
            `/blacklist` - Manage blacklisted users
            `/addscript` - Add new scripts
            """
            embed.add_field(name="👑 Admin Commands", value=admin_cmds, inline=False)
        
        # Premium Commands
        buyer_role = discord.utils.get(ctx.guild.roles, name="⭐ Crystal Premium")
        if buyer_role in ctx.author.roles:
            premium_cmds = """
            `/getscript` - Get your HWID-locked script
            `/resethwid` - Reset your HWID
            `/support` - Get AI-powered support
            """
            embed.add_field(name="⭐ Premium Commands", value=premium_cmds, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommands(bot)) 
