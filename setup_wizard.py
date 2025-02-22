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

    async def setup_control_panel(self, channel, announcements, support, hwid_data):
        """Set up the control panel with all embeds"""
        await channel.purge(limit=100)

        # Welcome Banner
        welcome_embed = discord.Embed(
            title="",
            description="",
            color=discord.Color.purple()
        )
        welcome_embed.set_image(url="https://your-banner-image.png")
        await channel.send(embed=welcome_embed)

        # Status Dashboard
        status_embed = discord.Embed(
            title="🎮 Crystal Hub Dashboard",
            description="Welcome to your premium control center",
            color=discord.Color.purple()
        )
        status_embed.add_field(
            name="🔐 Security Status",
            value="```\n✓ HWID System: Online\n✓ Anti-Tamper: Active\n✓ Encryption: Enabled\n```",
            inline=True
        )
        status_embed.add_field(
            name="📊 Statistics",
            value=f"```\n• Premium Users: {len(hwid_data['users'])}\n• Uptime: 99.9%\n• Version: 1.0.0\n```",
            inline=True
        )
        await channel.send(embed=status_embed)
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Information Section
        info_embed = discord.Embed(
            title="ℹ️ Information",
            description="Everything you need to know about Crystal Hub",
            color=discord.Color.blue()
        )
        info_embed.add_field(
            name="🎮 Supported Games",
            value="• Basketball Legends\n• More coming soon...",
            inline=True
        )
        info_embed.add_field(
            name="🔧 Support",
            value="• 24/7 Support\n• Priority Updates\n• Exclusive Features",
            inline=True
        )
        await channel.send(embed=info_embed)

        # Quick Links
        links_embed = discord.Embed(
            title="🔗 Quick Links",
            description="Important resources at your fingertips",
            color=discord.Color.green()
        )
        links_embed.add_field(
            name="📚 Documentation",
            value="[View Documentation](https://docs.crystalhub.com)",
            inline=True
        )
        links_embed.add_field(
            name="📢 Announcements",
            value=f"Check {announcements.mention} for updates",
            inline=True
        )
        links_embed.add_field(
            name="🎫 Support",
            value=f"Visit {support.mention} for help",
            inline=True
        )
        await channel.send(embed=links_embed)

        # Footer
        footer_embed = discord.Embed(
            description="Crystal Hub Premium © 2024 - All rights reserved",
            color=discord.Color.purple()
        )
        await channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        await channel.send(embed=footer_embed)

        # Create the control panel with all views
        control_embed = discord.Embed(
            title="🎮 Control Panel",
            description="Access your premium features below",
            color=discord.Color.purple()
        )
        control_embed.add_field(
            name="🔑 Script Access",
            value="• Get your HWID-locked script\n• Auto-updates included\n• Premium features",
            inline=True
        )
        control_embed.add_field(
            name="🔄 HWID Management",
            value="• View your HWID\n• Reset when needed\n• Security status",
            inline=True
        )
        control_embed.add_field(
            name="📱 Quick Actions",
            value="Click the buttons below to access features",
            inline=False
        )
        await channel.send(embed=control_embed, view=ControlPanel())

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
        await self.setup_control_panel(channels["control"], channels["announcements"], channels["support"], hwid_data)
        
        # Final success message
        success_embed = discord.Embed(
            title="✅ Setup Complete",
            description="Crystal Hub has been successfully set up!",
            color=discord.Color.green()
        )
        await status_msg.edit(embed=success_embed) 
