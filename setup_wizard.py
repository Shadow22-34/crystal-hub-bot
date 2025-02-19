import discord
from discord.ext import commands

class SetupWizard:
    def __init__(self, bot):
        self.bot = bot

    async def create_roles(self, guild):
        """Create necessary roles"""
        roles = {}
        
        # Create admin role
        roles["admin"] = await guild.create_role(
            name="💎 Crystal Admin",
            color=discord.Color.red(),
            permissions=discord.Permissions(administrator=True),
            hoist=True
        )
        
        # Create buyer role
        roles["buyer"] = await guild.create_role(
            name="⭐ Crystal Premium",
            color=discord.Color.purple(),
            hoist=True
        )
        
        return roles

    async def create_channels(self, guild, roles):
        """Create necessary channels"""
        channels = {}
        
        # Create category
        category = await guild.create_category("🌟 CRYSTAL HUB", position=0)
        
        # Set up permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            roles["buyer"]: discord.PermissionOverwrite(read_messages=True),
            roles["admin"]: discord.PermissionOverwrite(read_messages=True, manage_messages=True)
        }
        
        # Create channels
        channels["control"] = await category.create_text_channel(
            "🎮┃control-panel",
            overwrites=overwrites,
            topic="Crystal Hub Premium Control Panel"
        )
        
        channels["announcements"] = await category.create_text_channel(
            "📢┃announcements",
            overwrites=overwrites
        )
        
        channels["support"] = await category.create_text_channel(
            "🎫┃support",
            overwrites=overwrites
        )
        
        return channels

    async def setup_control_panel(self, channel):
        """Set up the control panel"""
        embed = discord.Embed(
            title="🌟 Welcome to Crystal Hub",
            description="Your premium script hub experience",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🔑 Getting Started",
            value="Use `/getscript` to access your premium scripts",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Security",
            value="Your scripts are HWID locked for maximum security",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Features",
            value="• Premium Scripts\n• Auto-Updates\n• 24/7 Support\n• Exclusive Features",
            inline=False
        )
        
        await channel.send(embed=embed)

    async def start_setup(self, ctx):
        """Start the setup process"""
        # Send initial message
        setup_embed = discord.Embed(
            title="🚀 Crystal Hub Setup",
            description="Setting up your premium experience...",
            color=discord.Color.blue()
        )
        status_msg = await ctx.send(embed=setup_embed)
        
        # Create roles
        setup_embed.description = "Creating roles..."
        await status_msg.edit(embed=setup_embed)
        roles = await self.create_roles(ctx.guild)
        
        # Create channels
        setup_embed.description = "Creating channels..."
        await status_msg.edit(embed=setup_embed)
        channels = await self.create_channels(ctx.guild, roles)
        
        # Setup control panel
        setup_embed.description = "Setting up control panel..."
        await status_msg.edit(embed=setup_embed)
        await self.setup_control_panel(channels["control"])
        
        # Final success message
        success_embed = discord.Embed(
            title="✅ Setup Complete",
            description="Crystal Hub has been successfully set up!",
            color=discord.Color.green()
        )
        await status_msg.edit(embed=success_embed) 
