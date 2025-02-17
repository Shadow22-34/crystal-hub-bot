import discord
from discord.ext import commands
from aiohttp import web
import asyncio
from urllib.parse import urlencode
import aiohttp
import random
import datetime
import os
from dotenv import load_dotenv
import json
import aiofiles
from datetime import timedelta
import base64
import cryptography
from cryptography.fernet import Fernet
import io

# Update these constants
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

# At the top with your other imports
KEYS_FILE = "keys.json"

# Initialize keys structure
keys_data = {
    "generated": {},  # Store generated keys
    "activated": {}   # Store activated keys
}

# Load existing keys if file exists
try:
    with open(KEYS_FILE, 'r') as f:
        keys_data = json.load(f)
except FileNotFoundError:
    # Create file if it doesn't exist
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys_data, f, indent=4)

async def save_keys():
    async with aiofiles.open(KEYS_FILE, 'w') as f:
        await f.write(json.dumps(keys_data, indent=4))

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Create web app outside of function
app = web.Application()

# Generate a key (do this once and save it)
encryption_key = Fernet.generate_key()
print("Save this key:", encryption_key.decode())

# Your complete Crystal Hub script with key system
crystal_hub_script = """
-- Your entire script here (key system + Crystal Hub)
local HttpService = game:GetService("HttpService")
local UserInputService = game:GetService("UserInputService")
local USERNAME = "jiohasdas"
local CURRENT_TIME = "2025-02-17 19:37:41"

-- Rest of your Crystal Hub script...
"""

# Encrypt and save to JSON
def save_encrypted_script():
    f = Fernet(encryption_key)
    encrypted = f.encrypt(crystal_hub_script.encode())
    
    script_data = {
        "data": base64.b64encode(encrypted).decode()
    }
    
    with open("crystal_hub.json", "w") as f:
        json.dump(script_data, f)

# Call this when bot starts
save_encrypted_script()

async def handle_callback(request):
    try:
        code = request.query.get('code')
        if not code:
            return web.Response(text="No code provided")
        
        async with aiohttp.ClientSession() as session:
            token_url = "https://discord.com/api/oauth2/token"
            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI
            }
            
            async with session.post(token_url, data=data) as resp:
                if resp.status != 200:
                    return web.Response(text="Failed to get token")
                token_data = await resp.json()
                
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            async with session.get("https://discord.com/api/users/@me", headers=headers) as resp:
                if resp.status != 200:
                    return web.Response(text="Failed to get user info")
                user_data = await resp.json()
                
                user_id = int(user_data['id'])
                
                # Generate key
                key = f"CRYSTAL-{random.randint(100000, 999999)}"
                
                # Auto-activate the key when generated
                keys_data["generated"][key] = {
                    "user_id": str(user_id),
                    "username": user_data['username'],
                    "generated_at": datetime.datetime.now().isoformat(),
                    "activated": True,
                    "activated_at": datetime.datetime.now().isoformat(),
                    "expires_at": (datetime.datetime.now() + timedelta(days=7)).isoformat(),
                    "days_remaining": 7
                }
                await save_keys()
                
                # Create loader script with their key embedded
                loader_script = f"""
-- Crystal Hub Loader
print("💎 Loading Crystal Hub...")

local function LoadCrystalHub()
    local success, result = pcall(function()
        -- Use syn.request for better compatibility
        local request = syn and syn.request or http and http.request or http_request or request
        
        if not request then
            warn("❌ Exploit not supported! Missing HTTP functions")
            return
        end
        
        local response = request({{
            Url = "https://crystal-hub-bot.onrender.com/api/loader",
            Method = "GET"
        }})
        
        if response.StatusCode == 200 then
            local data = game:GetService("HttpService"):JSONDecode(response.Body)
            if data.success then
                loadstring(data.script)()
            else
                warn("❌ Failed to load Crystal Hub:", data.message)
            end
        else
            warn("❌ Failed to contact server:", response.StatusCode)
        end
    end)
    
    if not success then
        warn("❌ Error loading Crystal Hub:", result)
    end
end

-- Start loading
spawn(function()
    LoadCrystalHub()
end)
"""
                
                # Send to user
                user = await bot.fetch_user(int(user_id))
                if user:
                    try:
                        # Send key embed
                        key_embed = discord.Embed(
                            title="🔮 Crystal Hub Key",
                            description=f"Here's your key: `{key}`",
                            color=discord.Color.purple()
                        )
                        key_embed.add_field(
                            name="Instructions",
                            value="1. Copy your key\n2. Execute the loader script\n3. Enter key when prompted",
                            inline=False
                        )
                        await user.send(embed=key_embed)
                        
                        # Send script embed and file
                        script_embed = discord.Embed(
                            title="📜 Crystal Hub Loader",
                            description="Here's your loader script. Copy and paste it into your executor!",
                            color=discord.Color.purple()
                        )
                        script_file = discord.File(
                            io.StringIO(loader_script),
                            filename="crystal_hub_loader.lua"
                        )
                        await user.send(embed=script_embed, file=script_file)
                        
                        # Log to channel
                        channel = bot.get_channel(KEY_LOG_CHANNEL_ID)
                        if channel:
                            log_embed = discord.Embed(
                                title="New Key Generated",
                                description=f"User: {user.mention}\nKey: `{key}`",
                                color=discord.Color.blue(),
                                timestamp=datetime.datetime.now()
                            )
                            await channel.send(embed=log_embed)
                        
                        return web.Response(text="Success! Check your Discord DMs for your key and loader script.")
                    except Exception as e:
                        print(f"Error sending messages: {e}")
                        return web.Response(text="Error sending messages. Please ensure your DMs are open.")
                
                return web.Response(text="Could not find user.")
    except Exception as e:
        print(f"Error in callback: {e}")
        return web.Response(text="An error occurred")

@bot.command(name='time')
async def check_time(ctx):
    # Create initial embed
    initial_embed = discord.Embed(
        title="🔮 Crystal Hub Key Verification",
        description="Please enter your Crystal Hub key to check its status...",
        color=discord.Color.from_rgb(147, 112, 219)
    )
    initial_embed.set_thumbnail(url="https://i.imgur.com/YourLogo.png")
    initial_embed.add_field(name="Instructions", value="Type your key in the chat", inline=False)
    initial_embed.set_footer(text="Crystal Hub Premium | Automatic Key System", icon_url="https://i.imgur.com/YourIcon.png")
    
    await ctx.send(embed=initial_embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        key_msg = await bot.wait_for('message', check=check, timeout=30.0)
        key = key_msg.content
        
        if key in keys_data["generated"]:
            key_data = keys_data["generated"][key]
            now = datetime.datetime.now()
            
            status_embed = discord.Embed(color=discord.Color.from_rgb(147, 112, 219))
            status_embed.set_author(name="Crystal Hub Premium", icon_url="https://i.imgur.com/YourIcon.png")
            
            if key_data["activated"]:
                expires_at = datetime.datetime.fromisoformat(key_data["expires_at"])
                time_remaining = expires_at - now
                
                days = time_remaining.days
                hours = time_remaining.seconds // 3600
                minutes = (time_remaining.seconds % 3600) // 60
                
                if now > expires_at:
                    status_embed.title = "❌ Key Expired"
                    status_embed.description = "This key has expired. Please contact support for assistance."
                    status_embed.color = discord.Color.red()
                else:
                    status_embed.title = "✅ Premium Key Active"
                    status_embed.add_field(
                        name="Time Remaining",
                        value=f"```\n{days}d {hours}h {minutes}m```",
                        inline=False
                    )
                    status_embed.add_field(
                        name="Expiration",
                        value=f"<t:{int(expires_at.timestamp())}:F>",
                        inline=False
                    )
            else:
                status_embed.title = "⚠️ Key Not Activated"
                status_embed.description = "This key has not been activated yet. Launch Crystal Hub to activate."
                status_embed.color = discord.Color.yellow()
            
            status_embed.add_field(name="Key", value=f"```{key}```", inline=False)
            status_embed.add_field(
                name="Owner",
                value=f"<@{key_data['user_id']}>",
                inline=True
            )
            status_embed.set_footer(text="Crystal Hub Premium • Premium Key System")
            
            await ctx.send(embed=status_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Invalid Key",
                description="The key you entered does not exist in our database.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
            
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ Time's Up!",
            description="Key verification timed out. Please try again.",
            color=discord.Color.red()
        )
        await ctx.send(embed=timeout_embed)

async def handle_activate(request):
    try:
        data = await request.json()
        key = data.get('key')
        
        if key in keys_data["generated"]:
            if not keys_data["generated"][key]["activated"]:
                # Set activation time and expiry
                now = datetime.datetime.now()
                keys_data["generated"][key]["activated"] = True
                keys_data["generated"][key]["activated_at"] = now.isoformat()
                keys_data["generated"][key]["expires_at"] = (now + timedelta(days=7)).isoformat()
                
                # Calculate time remaining
                expires_at = datetime.datetime.fromisoformat(keys_data["generated"][key]["expires_at"])
                days_remaining = (expires_at - now).days
                
                keys_data["generated"][key]["days_remaining"] = days_remaining
                await save_keys()
                
                return web.json_response({
                    "success": True, 
                    "message": "Key activated for 7 days",
                    "days_remaining": days_remaining
                })
            else:
                return web.json_response({"success": False, "message": "Key already activated"})
        return web.json_response({"success": False, "message": "Invalid key"})
    except Exception as e:
        return web.json_response({"success": False, "message": str(e)})

async def check_expired_keys():
    while True:
        now = datetime.datetime.now()
        for key in keys_data["generated"]:
            key_data = keys_data["generated"][key]
            if key_data["activated"]:
                expires_at = datetime.datetime.fromisoformat(key_data["expires_at"])
                key_data["days_remaining"] = (expires_at - now).days
                if now > expires_at:
                    key_data["activated"] = False
                    key_data["expired"] = True
        await save_keys()
        await asyncio.sleep(3600)  # Check every hour

async def handle_keys(request):
    now = datetime.datetime.now()
    
    for key, data in keys_data["generated"].items():
        if data["activated"]:
            expires_at = datetime.datetime.fromisoformat(data["expires_at"])
            data["days_remaining"] = (expires_at - now).days
            if now > expires_at:
                data["activated"] = False
                data["expired"] = True
        
        # Always include activation status
        if "activated" not in data:
            data["activated"] = False
        if "expired" not in data:
            data["expired"] = False
            
    await save_keys()
    return web.json_response(keys_data)

async def handle_script(request):
    key = request.query.get('key')
    
    if not key or key not in keys_data["generated"]:
        return web.json_response({
            "success": False,
            "message": "Invalid key"
        })
        
    if not keys_data["generated"][key]["activated"]:
        return web.json_response({
            "success": False,
            "message": "Key not activated"
        })
    
    try:
        with open("script.json", "r") as f:
            script_data = json.load(f)
            
        # Decrypt script
        f = Fernet(key)
        encrypted = base64.b64decode(script_data["data"])
        script = f.decrypt(encrypted).decode()
        
        return web.json_response({
            "success": True,
            "script": script
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "message": str(e)
        })

async def handle_loader(request):
    try:
        with open("crystal_hub.json", "r") as f:
            script_data = json.load(f)
            
        # Decrypt script
        f = Fernet(encryption_key)
        encrypted = base64.b64decode(script_data["data"])
        script = f.decrypt(encrypted).decode()
        
        return web.json_response({
            "success": True,
            "script": script
        })
    except FileNotFoundError:
        # If file doesn't exist, create it
        save_encrypted_script()
        return web.json_response({
            "success": True,
            "message": "Script regenerated, please try again"
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "message": str(e)
        })

async def start_server():
    # Add routes to the app
    app.router.add_get('/api/discord/redirect', handle_callback)
    app.router.add_get('/api/keys', handle_keys)
    app.router.add_post('/api/activate', handle_activate)
    app.router.add_get('/api/script', handle_script)
    app.router.add_get('/api/loader', handle_loader)
    
    # Create the encrypted script file
    save_encrypted_script()
    print("✅ Encrypted script saved to crystal_hub.json")
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()
    print(f"✅ OAuth2 callback server started")
    
    # Start the expiry checker
    asyncio.create_task(check_expired_keys())

@bot.event
async def on_ready():
    print(f'✅ Bot is logged in as {bot.user}')
    await start_server()
    print("✅ Server fully initialized")

bot.run(os.getenv('DISCORD_TOKEN'))
