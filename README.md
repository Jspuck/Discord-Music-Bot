# 🎵 Discord Music Bot (YouTube & SoundCloud)

A **Discord Music Bot** that plays audio from **YouTube and SoundCloud** in your voice channel! 🚀

---

## **✨ Features**
- ✅ **Plays music from YouTube & SoundCloud**
- ✅ **Slash commands** (`/play`, `/pause`, `/stop`, `/queue`, `/skip`, `/disconnect`)
- ✅ **Interactive music controls** (Pause, Resume, Stop, Skip)
- ✅ **Queue system** for multiple songs
- ✅ **Reacts to voice channel join/leave events**

---

## **📌 Installation**
### **1️⃣ Clone the Repository**
```
git clone https://github.com/Jspuck/YourRepoName.git
cd YourRepoName
```

### **2️⃣ Install Dependencies**
```
pip install -r requirements.txt
```

### **3️⃣ Setup Your `.env` File**
Create a **.env** file and add your bot token:
```
DISCORD_BOT_TOKEN=your-bot-token-here
```

### **4️⃣ Run the Bot**
```
python Discord_Music_Bot.py
```

---

## **🎮 Commands**
| Command       | Description                              |
|--------------|----------------------------------|
| `/play [URL]` | Plays a song from YouTube/SoundCloud |
| `/pause` | Pauses the current song |
| `/resume` | Resumes a paused song |
| `/stop` | Stops the music |
| `/skip` | Skips to the next song in queue |
| `/queue` | Displays the current queue |
| `/disconnect` | Disconnects the bot from voice |

---

## **🛠 Deployment**
To deploy this bot so it’s always online, consider:
- **Railway.app** 🚀
- **Replit**
- **VPS (DigitalOcean, AWS, Linode)**

---

## **💡 Troubleshooting**
❌ **Bot joins but doesn’t play music?**
- Make sure **FFmpeg** is installed and in your system PATH.
- Run `ffmpeg -version` to check.

❌ **Bot crashes with `TOKEN Not Found`?**
- Ensure your `.env` file is correctly set up.

❌ **Permissions Error?**
- Make sure the bot has `Connect` and `Speak` permissions in the voice channel.

---

## **📝 Credits**
Created by **Jarett Spuck** 👨‍💻

💡 **Contributions & Issues**: Open a GitHub issue if you find a bug or want to contribute!

---

🎵 **Enjoy your music!** 🎶

