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
        """Send the full version Crystal Hub script for testing"""
        try:
            basketball_script = """-- Crystal Hub Basketball Legends (Full Version)
local Library = loadstring(game:HttpGet("https://raw.githubusercontent.com/jiohasdas/CRYSTAL-HUB-SCRIPT/refs/heads/main/BASKETBALL%20LEGENDS"))()
local Window = Library.CreateLib("Crystal Hub", "Ocean")

-- Main Tab
local Main = Window:NewTab("Main")
local MainSection = Main:NewSection("Main Features")

MainSection:NewButton("Auto Farm", "Auto farms points for you", function()
    getgenv().Farm = true
    while getgenv().Farm do
        local args = {[1] = 1.5,[2] = CFrame.new(-3.03204, 0.0600014, 0.0467479),[3] = {["674"] = Vector3.new()},["s"] = 0.1}
        game:GetService("ReplicatedStorage").Shot:FireServer(unpack(args))
        wait()
    end
end)

MainSection:NewButton("Stop Auto Farm", "Stops the auto farm", function()
    getgenv().Farm = false
end)

-- Player Tab
local Player = Window:NewTab("Player")
local PlayerSection = Player:NewSection("Player Mods")

PlayerSection:NewSlider("WalkSpeed", "Changes your walkspeed", 500, 16, function(s)
    game.Players.LocalPlayer.Character.Humanoid.WalkSpeed = s
end)

PlayerSection:NewSlider("JumpPower", "Changes your jumppower", 500, 50, function(s)
    game.Players.LocalPlayer.Character.Humanoid.JumpPower = s
end)

-- Premium Features
local Premium = Window:NewTab("Premium")
local PremiumSection = Premium:NewSection("Premium Features")

PremiumSection:NewToggle("Infinite Stamina", "Never run out of stamina", function(state)
    if state then
        game:GetService("Players").LocalPlayer.PlayerGui.GameUI.Bottom.Stamina.Bar.Size = UDim2.new(1, 0, 1, 0)
    end
end)

PremiumSection:NewButton("Instant Score", "Score from anywhere", function()
    local args = {[1] = 2,[2] = CFrame.new(-3.03204, 0.0600014, 0.0467479),[3] = {["674"] = Vector3.new()},["s"] = 0.1}
    game:GetService("ReplicatedStorage").Shot:FireServer(unpack(args))
end)

-- Credits
local Credits = Window:NewTab("Credits")
local CreditsSection = Credits:NewSection("Crystal Hub Premium")
CreditsSection:NewLabel("Created by Crystal Hub Team")
"""
            
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
