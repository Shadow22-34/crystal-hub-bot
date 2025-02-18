from typing import Optional
import aiohttp
import asyncio
from . import bot, hwid_data, script_database, save_scripts
from .obfuscation import CrystalObfuscator

class AutoIntegration:
    def __init__(self, bot):
        self.bot = bot
        self.update_lock = asyncio.Lock()
        self.script_cache = {}
        
    async def fetch_latest_version(self, game: str) -> str:
        """Fetch latest script version from repository"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CRYSTAL_API}/scripts/{game}/version") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["version"]
        return "1.0.0"
    
    async def integrate_whitelist(self, script: str, user_id: str) -> str:
        """Integrate whitelist into script"""
        whitelist_code = f"""
local _G._CRYSTAL_RUNTIME = {{
    user_id = "{user_id}",
    hwid = "{hwid_data['users'][user_id]['hwid']}",
    premium = true,
    expires = "{hwid_data['users'][user_id].get('expiry', 'never')}",
    version = "{await self.fetch_latest_version(game)}"
}}

-- Whitelist verification
if not _G._CRYSTAL_RUNTIME.hwid then
    error("Crystal Hub: Invalid HWID")
end
"""
        return whitelist_code + "\n" + script
    
    async def update_script(self, game: str, new_script: str) -> bool:
        """Update game script with new version"""
        async with self.update_lock:
            try:
                # Obfuscate new script
                obfuscator = CrystalObfuscator()
                protected_script = obfuscator.obfuscate(new_script, {
                    "game": game,
                    "version": await self.fetch_latest_version(game)
                })
                
                # Store in database
                script_database["games"][game] = {
                    "script": protected_script,
                    "updated_at": datetime.datetime.now().isoformat(),
                    "version": await self.fetch_latest_version(game)
                }
                
                # Clear cache
                if game in self.script_cache:
                    del self.script_cache[game]
                
                return True
            except Exception as e:
                print(f"Script update failed: {e}")
                return False 
