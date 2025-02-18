import discord
import io
from . import bot, hwid_data, check_premium
from .integration import AutoIntegration

class EnhancedControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.integration = AutoIntegration(bot)
