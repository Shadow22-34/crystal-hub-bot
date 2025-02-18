from discord.ext import commands
import discord
import datetime
from datetime import timedelta
from integration import hwid_data, script_database, save_scripts
from obfuscation import CrystalObfuscator

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.obfuscator = CrystalObfuscator()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def obfuscate(self, ctx, game_name: str):
        """Obfuscate a game script"""
        script = script_database["games"][game_name]["script"]
        obfuscated = await self.obfuscator.obfuscate(script)
        # Rest of obfuscation logic...

    @commands.hybrid_command()
    @commands.has_role("💎 Crystal Admin")
    async def givepremium(self, ctx, user: discord.Member, days: int = 30):
        """Grant premium access to a user"""
        buyer_role = ctx.guild.get_role(BUYER_ROLE_ID)
        if not buyer_role:
            await ctx.send("❌ Buyer role not found!")
            return

        user_id = str(user.id)
        hwid_data["users"][user_id] = {
            "hwid": None,
            "resets": 0,
            "expiry": (datetime.datetime.now() + timedelta(days=days)).isoformat()
        }
        await save_hwid_data()
        await user.add_roles(buyer_role)
        
        embed = discord.Embed(
            title="✅ Premium Access Granted",
            description=f"Granted premium to {user.mention} for {days} days",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.has_role("💎 Crystal Admin")
    async def blacklist(self, ctx, user: discord.Member):
        """Blacklist a user from Crystal Hub"""
        user_id = str(user.id)
        if user_id in hwid_data["blacklist"]:
            await ctx.send("❌ User is already blacklisted!")
            return
        
        hwid_data["blacklist"].append(user_id)
        await save_hwid_data()
        
        embed = discord.Embed(
            title="⛔ User Blacklisted",
            description=f"{user.mention} has been blacklisted",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot)) 
