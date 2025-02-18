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
import hashlib
import platform
import uuid

# Update these constants
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

# New constants for premium system
CONTROL_PANEL_CHANNEL_ID = 1234567890  # Replace with your channel ID
BUYER_ROLE_ID = 1234567890  # Replace with your role ID
ADMIN_ROLE_ID = 1234567890  # Replace with your admin role ID

# At the top with your other imports
KEYS_FILE = "keys.json"

# HWID management
hwid_data = {
    "users": {},  # Store user HWIDs
    "resets": {}  # Track HWID resets
}

try:
    with open("hwid_data.json", "r") as f:
        hwid_data = json.load(f)
except FileNotFoundError:
    with open("hwid_data.json", "w") as f:
        json.dump(hwid_data, f, indent=4)

async def save_hwid_data():
    async with aiofiles.open("hwid_data.json", "w") as f:
        await f.write(json.dumps(hwid_data, indent=4))

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

# Add better logging
def log_message(category, message, error=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{category}] {message}")
    if error:
        print(f"[{timestamp}] [{category}] ERROR: {str(error)}")

# Your complete Crystal Hub script - EXACTLY as provided
crystal_hub_script = """
local HttpService = game:GetService("HttpService")
local UserInputService = game:GetService("UserInputService")
local USERNAME = "jiohasdas"
local CURRENT_TIME = "2025-02-17 19:37:41"

local function log(category, message, ...)
    print(string.format("[%s] [%s] %s", CURRENT_TIME, category, string.format(message, ...))) 
end

log("INIT", "Starting Crystal Scripts Key System")

local lib, win
local success, result = pcall(function()
    lib = loadstring(game:HttpGet('https://raw.githubusercontent.com/dawid-scripts/UI-Libs/main/Vape.txt'))()
    win = lib:Window("Crystal Scripts - Key System", Color3.fromRGB(255, 134, 236), Enum.KeyCode.RightControl)
    return true
end)

if not success then
    warn("Failed to load UI Library:", result)
    return
end

local verifyTab = win:Tab("Key System")
local request = syn and syn.request or http and http.request or http_request or request
log("HTTP", "Request method initialized")

local function autoFixKey(key)
    log("AUTOFIX", "Raw key input: %s", key)
    key = key:gsub("%s+", "")
    key = key:gsub("[^%w%-]", "")
    key = key:upper()
    
    if not key:match("^CRYSTAL%-") then
        local numbers = key:match("(%d+)")
        if numbers then
            key = "CRYSTAL-" .. numbers
        end
    end
    
    log("AUTOFIX", "Fixed key: %s", key)
    return key
end

local statusLabel = verifyTab:Label("Welcome to Crystal Scripts")
_G.CurrentKey = ""
local keyDisplay = verifyTab:Label("Current Key: None")

local function updateKeyDisplay()
    if keyDisplay then
        keyDisplay:set("Current Key: " .. (_G.CurrentKey ~= "" and _G.CurrentKey or "None"))
    end
end

local function checkKey(key)
    log("VERIFY", "Starting key verification for: %s", key)
    
    local response = request({
        Url = "https://crystal-hub-bot.onrender.com/api/keys",
        Method = "GET"
    })
    
    if response.StatusCode == 200 then
        local success, keysData = pcall(function()
            return HttpService:JSONDecode(response.Body)
        end)
        
        if success and keysData.generated[key] then
            local keyData = keysData.generated[key]
            
            if keyData.expired then
                return false, "Key has expired"
            end
            
            if not keyData.activated then
                local activateResponse = request({
                    Url = "https://crystal-hub-bot.onrender.com/api/activate",
                    Method = "POST",
                    Headers = {
                        ["Content-Type"] = "application/json"
                    },
                    Body = HttpService:JSONEncode({key = key})
                })
                
                if activateResponse.StatusCode == 200 then
                    return true, "Key activated for 7 days"
                end
            else
                return true, string.format("Key active (%d days remaining)", keyData.days_remaining)
            end
        end
    end
    return false, "Invalid key"
end

local function submitKey()
    if _G.CurrentKey == "" then
        if statusLabel then
            statusLabel:set("❌ No key found!")
        end
        return
    end
    
    log("SUBMIT", "Submitting key: %s", _G.CurrentKey)
    if statusLabel then
        statusLabel:set("⌛ Verifying key...")
    end
    
    local success, message = checkKey(_G.CurrentKey)
    log("SUBMIT", "Verification result: " .. tostring(success))
    
    if success then
        if statusLabel then
            statusLabel:set("✅ " .. message)
        end
        
        print("\\n=== SUCCESSFUL KEY ENTRY ===")
        print("Time:", CURRENT_TIME)
        print("User:", USERNAME)
        print("Key:", _G.CurrentKey)
        print("Status: CORRECT")
        print("===========================\\n")
        
        task.wait(1)
        
        for _, v in pairs(game:GetService("CoreGui"):GetChildren()) do
            if v:IsA("ScreenGui") and (v.Name:match("Crystal") or v.Name:match("Vape")) then
                v.Enabled = false
                for _, c in pairs(v:GetDescendants()) do
                    if c:IsA("Frame") or c:IsA("TextLabel") or c:IsA("TextButton") or c:IsA("ImageLabel") then
                        c.Visible = false
                    end
                end
            end
        end
        
        _G.CurrentKey = nil
        win = nil
        lib = nil
        verifyTab = nil
        statusLabel = nil
        keyDisplay = nil
        
        task.wait(0.5)
        loadstring(game:HttpGet("https://raw.githubusercontent.com/jiohasdas/CRYSTAL-HUB-SCRIPT/refs/heads/main/BASKETBALL%20LEGENDS"))()
    else
        if statusLabel then
            statusLabel:set("❌ " .. message)
            task.wait(2)
            statusLabel:set("Please try another key")
        end
    end
end

local function autoPasteAndFix()
    local success, clipboard = pcall(function()
        return getclipboard()
    end)
    
    if success and clipboard and clipboard ~= "" then
        log("AUTOPASTE", "Got clipboard content")
        _G.CurrentKey = autoFixKey(clipboard)
        updateKeyDisplay()
        if statusLabel then
            statusLabel:set("✅ Key auto-pasted and fixed!")
        end
        return true
    end
    return false
end

verifyTab:Button("📋 Auto-Paste & Fix Key", function()
    if not autoPasteAndFix() then
        if statusLabel then
            statusLabel:set("❌ No valid key in clipboard!")
        end
    end
end)

verifyTab:Button("🔑 Submit Key", function()
    submitKey()
end)

verifyTab:Label("─────────────────────────────")
verifyTab:Label("System Information:")
verifyTab:Label("Time (UTC): " .. CURRENT_TIME)
verifyTab:Label("User: " .. USERNAME)
verifyTab:Label("─────────────────────────────")
verifyTab:Label("How to use:")
verifyTab:Label("1. Copy your key from Discord")
verifyTab:Label("2. Click 'Auto-Paste & Fix Key'")
verifyTab:Label("3. Click 'Submit Key' to verify")
verifyTab:Label("─────────────────────────────")

verifyTab:Button("🌐 Copy Discord Invite", function()
    setclipboard("https://discord.gg/your-invite-here")
    if statusLabel then
        statusLabel:set("✅ Discord invite copied!")
        task.wait(2)
        statusLabel:set("Welcome to Crystal Scripts")
    end
end)

local keySystemStatus = verifyTab:Label("Checking system status...")

local testResponse = request({
    Url = "https://crystal-hub-bot.onrender.com/api/keys",
    Method = "GET"
})

if testResponse and testResponse.StatusCode == 200 then
    keySystemStatus:set("✅ System Online")
else
    keySystemStatus:set("❌ System Offline")
end

verifyTab:Label("─────────────────────────────")
log("INIT", "Key system initialization complete")

task.spawn(function()
    task.wait(1)
    autoPasteAndFix()
end)
"""

# Encrypt and save to JSON with better logging
def save_encrypted_script():
    try:
        log_message("ENCRYPT", "Starting script encryption...")
        
        f = Fernet(encryption_key)
        encrypted = f.encrypt(crystal_hub_script.encode())
        
        script_data = {
            "data": base64.b64encode(encrypted).decode()
        }
        
        with open("crystal_hub.json", "w") as f:
            json.dump(script_data, f)
            
        log_message("ENCRYPT", "✅ Script successfully encrypted and saved!")
        return True
    except Exception as e:
        log_message("ENCRYPT", "❌ Failed to encrypt script", e)
        return False

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
        log_message("LOADER", "🔄 Received loader request")
        
        with open("crystal_hub.json", "r") as f:
            script_data = json.load(f)
            log_message("LOADER", "📂 Successfully read crystal_hub.json")
            
        # Decrypt script
        f = Fernet(encryption_key)
        encrypted = base64.b64decode(script_data["data"])
        script = f.decrypt(encrypted).decode()
        log_message("LOADER", "🔓 Successfully decrypted script")
        
        return web.json_response({
            "success": True,
            "script": script
        })
    except FileNotFoundError:
        log_message("LOADER", "⚠️ Script file not found, attempting to recreate...")
        if save_encrypted_script():
            log_message("LOADER", "✅ Script file recreated successfully")
            return web.json_response({
                "success": True,
                "message": "Script regenerated, please try again"
            })
        else:
            log_message("LOADER", "❌ Failed to recreate script file")
            return web.json_response({
                "success": False,
                "message": "Failed to generate script"
            })
    except Exception as e:
        log_message("LOADER", "❌ Error in loader endpoint", e)
        return web.json_response({
            "success": False,
            "message": str(e)
        })

async def start_server():
    try:
        log_message("SERVER", "🚀 Starting server initialization...")
        
        # Add routes
        app.router.add_get('/api/discord/redirect', handle_callback)
        app.router.add_get('/api/keys', handle_keys)
        app.router.add_post('/api/activate', handle_activate)
        app.router.add_get('/api/script', handle_script)
        app.router.add_get('/api/loader', handle_loader)
        log_message("SERVER", "✅ Routes configured")
        
        # Create encrypted script
        if save_encrypted_script():
            log_message("SERVER", "✅ Initial script encryption successful")
        else:
            log_message("SERVER", "❌ Failed to create initial script")
            return
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
        await site.start()
        log_message("SERVER", "✅ Web server started successfully")
        
        # Start expiry checker
        asyncio.create_task(check_expired_keys())
        log_message("SERVER", "✅ Key expiry checker started")
        
    except Exception as e:
        log_message("SERVER", "❌ Failed to start server", e)
        raise e

@bot.event
async def on_ready():
    log_message("BOT", f"✅ Logged in as {bot.user}")
    try:
        await start_server()
        log_message("BOT", "✅ Server initialization complete")
    except Exception as e:
        log_message("BOT", "❌ Failed to start server", e)

# Premium control panel
class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 Get Script", style=discord.ButtonStyle.green)
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == BUYER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ You need the buyer role!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        if user_id not in hwid_data["users"]:
            # Generate new HWID-locked script
            hwid = hashlib.sha256(f"{platform.node()}{uuid.getnode()}".encode()).hexdigest()
            hwid_data["users"][user_id] = {"hwid": hwid, "resets": 0}
            await save_hwid_data()

        # Generate HWID-locked script
        script = generate_hwid_script(interaction.user.id, hwid_data["users"][user_id]["hwid"])
        
        file = discord.File(io.StringIO(script), filename="crystal_hub_premium.lua")
        await interaction.response.send_message("✨ Here's your HWID-locked script!", file=file, ephemeral=True)

    @discord.ui.button(label="🔄 Reset HWID", style=discord.ButtonStyle.blurple)
    async def reset_hwid(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if user_id not in hwid_data["users"]:
            await interaction.response.send_message("❌ You don't have a bound HWID!", ephemeral=True)
            return

        if hwid_data["users"][user_id]["resets"] >= 3:
            await interaction.response.send_message("❌ You've used all your HWID resets! Contact an admin.", ephemeral=True)
            return

        # Reset HWID
        hwid_data["users"][user_id]["hwid"] = None
        hwid_data["users"][user_id]["resets"] += 1
        await save_hwid_data()
        
        await interaction.response.send_message("✅ HWID reset! Get your new script with the Get Script button.", ephemeral=True)

# Admin commands
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def givepremium(ctx, user: discord.Member):
    """Give a user premium access"""
    try:
        buyer_role = ctx.guild.get_role(BUYER_ROLE_ID)
        await user.add_roles(buyer_role)
        
        embed = discord.Embed(
            title="✨ Premium Access Granted",
            description=f"Gave premium to {user.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        # DM user instructions
        dm_embed = discord.Embed(
            title="🎉 Welcome to Crystal Hub Premium!",
            description="Head to the control panel to get your HWID-locked script!",
            color=discord.Color.purple()
        )
        await user.send(embed=dm_embed)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def resetpremium(ctx, user: discord.Member):
    """Force reset a user's HWID"""
    user_id = str(user.id)
    if user_id in hwid_data["users"]:
        hwid_data["users"][user_id]["hwid"] = None
        hwid_data["users"][user_id]["resets"] = 0
        await save_hwid_data()
        
        embed = discord.Embed(
            title="🔄 HWID Reset",
            description=f"Reset HWID for {user.mention}",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ User has no HWID bound!")

# Function to generate HWID-locked script
def generate_hwid_script(user_id, hwid):
    return f"""
-- Crystal Hub Premium (HWID: {hwid[:8]}...)
local function getHWID()
    local hwid = game:GetService("RbxAnalyticsService"):GetClientId()
    return hwid
end

local function verifyHWID()
    local currentHWID = getHWID()
    if currentHWID ~= "{hwid}" then
        game.Players.LocalPlayer:Kick("⚠️ HWID Mismatch! Reset your HWID in the Discord.")
        return false
    end
    return true
end

if verifyHWID() then
    -- Your premium script here
    loadstring(game:HttpGet("https://raw.githubusercontent.com/jiohasdas/CRYSTAL-HUB-SCRIPT/refs/heads/main/BASKETBALL%20LEGENDS"))()
end
"""

# Control panel setup
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def setup(ctx):
    """Create the ultimate Crystal Hub control panel"""
    try:
        # Delete previous messages to start fresh
        await ctx.channel.purge(limit=100)
        
        # Main welcome banner
        welcome_embed = discord.Embed(
            title="🌟 Crystal Hub Premium",
            description="Welcome to the exclusive Crystal Hub control panel.\nYour premium experience starts here.",
            color=discord.Color.purple()
        )
        welcome_embed.set_thumbnail(url="https://your-crystal-logo-url.png")
        welcome_embed.add_field(
            name="🔒 Security",
            value="• HWID Protection\n• Anti-Tamper System\n• 24/7 Monitoring",
            inline=True
        )
        welcome_embed.add_field(
            name="✨ Features",
            value="• Instant Script Access\n• Auto-Updates\n• Priority Support",
            inline=True
        )
        await ctx.send(embed=welcome_embed)
        
        # Separator
        separator = discord.Embed(color=discord.Color.purple())
        separator.set_image(url="https://i.imgur.com/wvbwk6G.png")
        await ctx.send(embed=separator)
        
        # Status panel
        status_embed = discord.Embed(
            title="📊 System Status",
            color=discord.Color.green()
        )
        status_embed.add_field(
            name="🟢 Server Status",
            value="Operational",
            inline=True
        )
        status_embed.add_field(
            name="📈 Uptime",
            value="99.9%",
            inline=True
        )
        status_embed.add_field(
            name="👥 Active Users",
            value=f"{len(hwid_data['users'])}",
            inline=True
        )
        await ctx.send(embed=status_embed)
        
        # Control panel
        control_embed = discord.Embed(
            title="🎮 Control Panel",
            description="Access your premium features below",
            color=discord.Color.purple()
        )
        control_embed.add_field(
            name="🔑 Get Script",
            value="Get your HWID-locked premium script",
            inline=False
        )
        control_embed.add_field(
            name="🔄 Reset HWID",
            value="Reset your HWID (3 resets maximum)",
            inline=False
        )
        control_embed.add_field(
            name="❓ Need Help?",
            value="Contact our support team for assistance",
            inline=False
        )
        await ctx.send(embed=control_embed, view=ControlPanel())
        
        # Information panel
        info_embed = discord.Embed(
            title="ℹ️ Information",
            color=discord.Color.blue()
        )
        info_embed.add_field(
            name="📖 Commands",
            value="```\n"
                  "!getscript - Get your script\n"
                  "!resethwid - Reset your HWID\n"
                  "!support - Get help\n"
                  "```",
            inline=False
        )
        info_embed.add_field(
            name="🛡️ Admin Commands",
            value="```\n"
                  "!givepremium @user - Grant premium\n"
                  "!resetpremium @user - Force HWID reset\n"
                  "!blacklist @user - Blacklist user\n"
                  "```",
            inline=False
        )
        await ctx.send(embed=info_embed)
        
        # Support panel
        support_embed = discord.Embed(
            title="📞 Support",
            description="Need assistance? Our team is here to help!",
            color=discord.Color.green()
        )
        support_embed.add_field(
            name="🎫 Open Ticket",
            value="Click the button below to create a support ticket",
            inline=False
        )
        support_embed.add_field(
            name="📱 Contact",
            value="Discord: Your-Support-Tag\nEmail: support@crystalhub.com",
            inline=False
        )
        await ctx.send(embed=support_embed)
        
        # Footer
        footer_embed = discord.Embed(
            description="Crystal Hub Premium © 2024 - All rights reserved",
            color=discord.Color.purple()
        )
        await ctx.send(embed=footer_embed)
        
        # Log setup completion
        log_message("SETUP", f"✅ Control panel created by {ctx.author}")
        
    except Exception as e:
        log_message("SETUP", "❌ Failed to create control panel", e)
        await ctx.send(f"❌ Error: {str(e)}")

# Enhanced Control Panel with animations
class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(
        label="🔑 Get Script",
        style=discord.ButtonStyle.green,
        custom_id="get_script"
    )
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == BUYER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Access Denied",
                    description="You need the premium role to access this feature!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        # Loading animation
        loading_embed = discord.Embed(
            title="⚡ Generating Script",
            description="Please wait while we prepare your script...",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        user_id = str(interaction.user.id)
        if user_id not in hwid_data["users"]:
            hwid = hashlib.sha256(f"{platform.node()}{uuid.getnode()}".encode()).hexdigest()
            hwid_data["users"][user_id] = {"hwid": hwid, "resets": 0}
            await save_hwid_data()

        script = generate_hwid_script(interaction.user.id, hwid_data["users"][user_id]["hwid"])
        
        success_embed = discord.Embed(
            title="✅ Script Generated",
            description="Your HWID-locked premium script is ready!",
            color=discord.Color.green()
        )
        success_embed.add_field(
            name="HWID",
            value=f"```{hwid_data['users'][user_id]['hwid'][:16]}...```",
            inline=False
        )
        success_embed.add_field(
            name="Resets Available",
            value=f"```{3 - hwid_data['users'][user_id]['resets']}/3```",
            inline=False
        )
        
        file = discord.File(io.StringIO(script), filename="crystal_hub_premium.lua")
        await interaction.edit_original_response(embed=success_embed, attachments=[file])

    # ... rest of your control panel buttons ...

bot.run(os.getenv('DISCORD_TOKEN'))
