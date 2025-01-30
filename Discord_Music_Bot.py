import os
import discord
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands

# Set up the discord client with appropriate intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True  # Required for message commands

bot = commands.Bot(command_prefix='?', intents=intents)

# Define FFmpeg options for audio playback
ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Explicit FFmpeg path
ffmpeg_options = {
    'executable': ffmpeg_path,
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

# Event listener for when the bot is online
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command to play music from a SoundCloud link
@bot.command(name='play', help='Plays a song from SoundCloud')
async def play(ctx, url: str):
    if 'soundcloud.com' not in url:
        await ctx.send("Please provide a valid SoundCloud URL.")
        return

    if not ctx.author.voice:
        await ctx.send("You need to be connected to a voice channel.")
        return

    voice_channel = ctx.author.voice.channel

    # Check if bot is already in a voice channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['url']
            title = info.get('title', 'Unknown Title')

        vc.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options),
                after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'🎵 Now playing: **{title}**')

        while vc.is_playing():
            await asyncio.sleep(1)

        await vc.disconnect()  # Disconnect after the song is done

    except Exception as e:
        await ctx.send(f"⚠️ Error: {str(e)}")
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

# Use the token from the environment variable
token = os.getenv('DISCORD_BOT_TOKEN')
if token:
    bot.run(token)
else:
    print("Token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
