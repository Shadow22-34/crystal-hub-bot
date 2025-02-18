from discord.ext import commands
import discord
import datetime
import io
import aiofiles
import json

class ScriptManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command()
    @commands.has_role("💎 Crystal Admin")
    async def addscript(self, ctx, name: str, *, code: str):
        """Add a new script to the database"""
        if name in script_database["games"]:
            confirm_view = ConfirmView()
            embed = discord.Embed(
                title="⚠️ Script Exists",
                description=f"Script '{name}' already exists. Update it?",
                color=discord.Color.yellow()
            )
            msg = await ctx.send(embed=embed, view=confirm_view)
            await confirm_view.wait()
            
            if not confirm_view.value:
                await msg.edit(content="Operation cancelled.", view=None)
                return
                
        script_database["games"][name] = {
            "script": code,
            "version": "1.0.0",
            "last_updated": datetime.datetime.now().isoformat()
        }
        await save_scripts()
        
        embed = discord.Embed(
            title="✅ Script Added",
            description=f"Added script: {name}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.has_role("⭐ Crystal Premium")
    async def getscript(self, ctx, game: str):
        """Get your HWID-locked script"""
        if game not in script_database["games"]:
            await ctx.send("❌ Script not found!")
            return
            
        user_id = str(ctx.author.id)
        if user_id not in hwid_data["users"]:
            await ctx.send("❌ You need to set up your HWID first!")
            return
            
        script = script_database["games"][game]["script"]
        whitelisted_script = await self.bot.integration.integrate_whitelist(script, user_id)
        obfuscated = await self.bot.obfuscator.obfuscate(whitelisted_script)
        
        file = discord.File(
            io.StringIO(obfuscated),
            filename=f"crystal_{game}.lua"
        )
        await ctx.author.send("🎮 Here's your script!", file=file)
        await ctx.send("✅ Script sent to your DMs!")

    @commands.hybrid_command()
    @commands.has_role("💎 Crystal Admin")
    async def givescript(self, ctx):
        """Send the full version Crystal Hub script"""
        try:
            # Load the full version script from JSON
            async with aiofiles.open("full_version_scripts.json", "r") as f:
                content = await f.read()
                scripts = json.loads(content)
            
            basketball_script = scripts.get("basketball_legends", {}).get("script", "")
            
            if not basketball_script:
                await ctx.send("❌ Full version script not found!")
                return
            
            # Send the script file
            file = discord.File(
                io.StringIO(basketball_script),
                filename="crystal_hub_basketball_full.lua"
            )
            await ctx.author.send("🎮 Here's the full version script:", file=file)
            await ctx.send("✅ Script sent to your DMs!")
        
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(ScriptManagement(bot)) 
