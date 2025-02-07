import os
import discord
import asyncio
import yt_dlp as youtube_dl
from discord import app_commands
from discord.ext import commands


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)


ffmpeg_options = {
    'options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'before_options': '-headers "Referer: https://soundcloud.com" -protocol_whitelist file,http,https,tcp,tls,crypto'
}

@bot.event
async def on_ready():
    await bot.tree.sync()  
    print(f'✅ Logged in as {bot.user.name} ({bot.user.id})')

#  Music Control Buttons
class MusicControls(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.vc = vc

    @discord.ui.button(label="▶️ Play", style=discord.ButtonStyle.green)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc and self.vc.is_paused():
            self.vc.resume()
            await interaction.response.send_message("▶️ Resuming music!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No paused music to resume.", ephemeral=True)

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.gray)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc and self.vc.is_playing():
            self.vc.pause()
            await interaction.response.send_message("⏸ Music paused!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music playing to pause.", ephemeral=True)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            await interaction.response.send_message("⏹ Music stopped!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music playing to stop.", ephemeral=True)

# 🎵 Slash Command: Play Music (SoundCloud & YouTube)
@bot.tree.command(name="play", description="Plays a track from SoundCloud or YouTube")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("❌ You need to be in a voice channel to play music!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not vc or not vc.is_connected():
        vc = await voice_channel.connect()

    
    if "soundcloud.com" in url:
        ydl_opts = {'format': 'http_mp3_0_0'}  
    
    elif "youtube.com" in url or "youtu.be" in url:
        ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
    else:
        await interaction.followup.send("❌ Please provide a valid YouTube or SoundCloud URL.", ephemeral=True)
        return

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get("title", "Unknown Title")
            print(f"🔊 Extracted Audio URL: {audio_url}")
        except Exception as e:
            await interaction.followup.send(f"❌ Error extracting audio: {e}")
            print(f"Error: {e}")
            return

    try:
        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: print(f"Player error: {e}") if e else None)
        await interaction.followup.send(f"🎶 Now playing: {title}", view=MusicControls(vc))

        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(2)

    except Exception as e:
        await interaction.followup.send(f"❌ Error playing audio: {e}")
        print(f"❌ FFmpeg Error: {e}")

# 🔌 Slash Command: Disconnect
@bot.tree.command(name="disconnect", description="Disconnects the bot from the voice channel")
async def disconnect(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("👋 Disconnected from voice channel.")
    else:
        await interaction.response.send_message("❌ The bot is not in a voice channel.", ephemeral=True)

#  Run Bot
token = os.getenv('DISCORD_BOT_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ Token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
