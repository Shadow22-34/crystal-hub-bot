import discord
import io
from integration import hwid_data, AutoIntegration

def check_premium(user):
    return str(user.id) in hwid_data["users"]

class EnhancedControlPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.integration = AutoIntegration(bot)
        
    async def generate_embed(self) -> discord.Embed:
        """Generate the control panel embed"""
        embed = discord.Embed(
            title="Welcome to your premium control center",
            color=0x2b2d31
        )
        
        # Security Status
        status = (
            "✓ HWID System: Online\n"
            "✓ Anti-Tamper: Active\n"
            "✓ Encryption: Enabled"
        )
        embed.add_field(name="🔒 Security Status", value=status, inline=True)
        
        # Statistics
        stats = (
            f"• Premium Users: {len(hwid_data['users'])}\n"
            f"• Uptime: {self.bot.uptime}\n"
            f"• Version: 1.0.0"
        )
        embed.add_field(name="📊 Statistics", value=stats, inline=True)
        
        # Separator
        embed.add_field(name="", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
        
        # Features
        features = (
            "**🔑 Script Access**\n"
            "• HWID-locked premium script\n"
            "• Auto-updates included\n"
            "• Premium features\n\n"
            "**🔄 HWID Management**\n"
            "• View your HWID\n"
            "• Reset when needed\n"
            "• Security status"
        )
        embed.add_field(name="Available Features", value=features, inline=False)
        
        return embed
    
    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.green, row=0)
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_premium(interaction.user):
            await interaction.response.send_message("❌ Premium required!", ephemeral=True)
            return
            
        # Create loading message
        loading_embed = discord.Embed(
            title="🎮 Generating Your Script",
            description="Please wait while we prepare your premium script...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        try:
            # Generate script
            script = await generate_user_script(interaction.user.id)
            
            # Create success embed
            success_embed = discord.Embed(
                title="✅ Script Generated Successfully",
                description="Your premium script is ready! Check your DMs.",
                color=discord.Color.green()
            )
            
            # Send script via DM
            await interaction.user.send(
                file=discord.File(
                    io.StringIO(script),
                    filename="crystal_hub_premium.lua"
                )
            )
            
            await interaction.edit_original_response(embed=success_embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Script Generation Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed) 
