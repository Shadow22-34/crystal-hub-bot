from discord.ext import commands
import discord
import openai
import os

class SupportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        openai.api_key = os.getenv('OPENAI_API_KEY')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        if message.channel.id != SUPPORT_CHANNEL_ID:
            return
            
        try:
            response = await openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Crystal Hub's support assistant."},
                    {"role": "user", "content": message.content}
                ]
            )
            
            embed = discord.Embed(
                title="🤖 Crystal Support",
                description=response.choices[0].message.content,
                color=discord.Color.blue()
            )
            await message.reply(embed=embed)
            
        except Exception as e:
            await message.reply("❌ Sorry, I couldn't process your request. Please try again later.")

async def setup(bot):
    await bot.add_cog(SupportSystem(bot)) 
