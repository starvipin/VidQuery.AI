---
title: VidQuery AI
emoji: 🎥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# VidQuery AI
Ye ek AI-powered application hai jo YouTube videos se data nikal kar answers deti hai.

## Deployment note: YouTube transcript  fetching

Ye app pehle `youtube-transcript-api` se transcript fetch karta hai. Agar cloud server par YouTube block kare, app ek free fallback try karta hai: YouTube watch page se caption track metadata nikal kar timed captions fetch karna.

Free deployment me expected behavior:

1. Public captions/subtitles enabled videos par link direct work kar sakta hai.
2. Agar YouTube Hugging Face/Render/Railway ki IP ko block kar de, fallback bhi fail ho sakta hai.
3. Pehle process ho chuke videos database cache se chalenge, isliye same video dobara YouTube ko hit nahi karega.

Optional proxy support bhi available hai, lekin app chalane ke liye required nahi:

```env
YOUTUBE_HTTP_PROXY=http://username:password@proxy-host:port
YOUTUBE_HTTPS_PROXY=http://username:password@proxy-host:port
```

Note: Official YouTube Data API public videos ke captions ko freely return nahi karti. Isliye sirf YouTube API key add karne se transcript fetch problem solve nahi hoti.

## Free public sharing without paid proxy

Paid proxy ke bina sabse reliable free setup ye hai ki app tumhare laptop/PC par run ho aur public URL Cloudflare Tunnel se mile. Isme YouTube request tumhare local internet se jayegi, Hugging Face/Render ki blocked IP se nahi.

Windows:

1. Cloudflared install karein: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Project folder me command run karein:

```powershell
.\scripts\start_public_local.ps1
```

3. Terminal me jo `https://*.trycloudflare.com` URL aaye, users ko wahi link share karein.

Note: PC/laptop aur terminal window on rehna zaroori hai. Window band karte hi public URL stop ho jayega.
 
# How to use this RAG AI Teaching assistant on your own data 
## Step 1 - Collect your videos
Move all your video files to the videos folder

## Step 2 - Convert to mp3
Convert all the video files to mp3 by ruunning video_to_mp3

## Step 3 - Convert mp3 to json file 
Convert all the mp3 files to json by ruunning mp3_to_json

## Step 4 - Convert the json files to Vectors
Use the file preprocess_json to convert the json files to a dataframe with Embeddings and save it as a joblib pickle

## Step 5 - Prompt generation and feeding to LLM

Read the joblib file and load it into the memory. Then create a relevant prompt as per the user query and feed it to the LLM
