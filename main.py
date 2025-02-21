import os
import discord
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands
from flask import Flask
import threading

# ------------------------- Flask Web Server ------------------------- #
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Discord Music Bot is Running on Google Cloud Run!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)), use_reloader=False)

# ------------------------ Discord Bot Setup ------------------------- #
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True  # Enables message reading

bot = commands.Bot(command_prefix='!', intents=intents)

# FFmpeg Options
ffmpeg_options = {
    'options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'before_options': '-headers "Referer: https://soundcloud.com" -protocol_whitelist file,http,https,tcp,tls,crypto'
}

# ------------------------- Bot Ready Event ------------------------- #
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} ({bot.user.id})')

    # Sync slash commands
    await bot.tree.sync()
    print("✅ Slash commands synced!")

# ------------------------- Music Controls UI ------------------------- #
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

# ------------------------- Play Music Command ------------------------- #
@bot.tree.command(name="play", description="Plays a track from a SoundCloud or YouTube URL")
async def play(interaction: discord.Interaction, url: str):
    if 'soundcloud.com' not in url and 'youtube.com' not in url and 'youtu.be' not in url:
        await interaction.response.send_message("❌ Please provide a valid SoundCloud or YouTube URL.", ephemeral=True)
        return

    # Ensure user is in a voice channel
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You need to be in a voice channel to play music!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    # Check if bot is already connected
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not vc or not vc.is_connected():
        vc = await voice_channel.connect()

    # Extract direct audio URL
    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            print(f"🔊 Extracted Audio URL: {audio_url}")
        except Exception as e:
            await interaction.response.send_message("❌ Error extracting audio.")
            print(f"Error: {e}")
            return

    # Play audio using FFmpeg
    try:
        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: print(f"Player error: {e}") if e else None)
        await interaction.response.send_message(f"🎶 Now playing: {info['title']}", view=MusicControls(vc))

        # Wait for song to finish before disconnecting
        while vc.is_playing():
            await asyncio.sleep(2)

    except Exception as e:
        await interaction.response.send_message(f"❌ Error playing audio: {e}")
        print(f"❌ FFmpeg Error: {e}")

# ------------------------- Disconnect Command ------------------------- #
@bot.tree.command(name="disconnect", description="Disconnects the bot from the voice channel")
async def disconnect(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("👋 Disconnected from voice channel.")
    else:
        await interaction.response.send_message("❌ The bot is not in a voice channel.", ephemeral=True)

# ------------------------- Run Flask and Discord Bot ------------------------- #
if __name__ == "__main__":
    # Start Flask in a separate thread to keep Cloud Run alive
    threading.Thread(target=run_flask, daemon=True).start()

    # Run Discord bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
