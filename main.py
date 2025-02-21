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

# ------------------------- Play Music Command ------------------------- #
@bot.command(name="play", help="Plays a track from YouTube or SoundCloud URL")
async def play(ctx, url: str):
    if not url.startswith(("https://www.youtube.com", "https://youtu.be", "https://soundcloud.com")):
        await ctx.send("❌ Please provide a valid SoundCloud or YouTube URL.")
        return

    # Ensure user is in a voice channel
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to be in a voice channel to play music!")
        return

    voice_channel = ctx.author.voice.channel

    # Check if bot is already connected
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
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
            await ctx.send("❌ Error extracting audio.")
            print(f"Error: {e}")
            return

    # Play audio using FFmpeg
    try:
        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))
        await ctx.send(f"🎶 Now playing: {info['title']}")

        # Wait for song to finish before disconnecting
        while vc.is_playing():
            await asyncio.sleep(2)

    except Exception as e:
        await ctx.send(f"❌ Error playing audio: {e}")
        print(f"❌ FFmpeg Error: {e}")

# ------------------------- Disconnect Command ------------------------- #
@bot.command(name="disconnect", help="Disconnects the bot from the voice channel")
async def disconnect(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_connected():
        await vc.disconnect()
        await ctx.send("👋 Disconnected from voice channel.")
    else:
        await ctx.send("❌ The bot is not in a voice channel.")

# ------------------------- Run Flask and Discord Bot ------------------------- #
if __name__ == "__main__":
    # Start Flask in a separate thread to keep Cloud Run alive
    threading.Thread(target=run_flask, daemon=True).start()

    # Run Discord bot
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
