# 🚀 QUICK START - Get Your Industrial LLM Running NOW!

## ✅ I've Already Set Up Most of It For You!

The `.env` file is created and ready. You just need to add your API key!

---

## 🎯 Step 1: Choose Your LLM (Pick ONE)

### 🟢 OPTION A: Google Gemini (FREE) - **RECOMMENDED**

1. **Get your API key** (takes 30 seconds):
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key

2. **Open `.env` file** and replace this line:
   ```
   GOOGLE_API_KEY=your-google-api-key-here
   ```
   With your actual key:
   ```
   GOOGLE_API_KEY=AIzaSyDe3F...your-actual-key...
   ```

3. **Done!** Run `python simple_rag.py`

---

### 🔵 OPTION B: OpenAI (Fast & Cheap)

1. **Get your API key**:
   - Go to: https://platform.openai.com/api-keys
   - Sign up / Sign in
   - Click "Create new secret key"
   - Copy the key

2. **Edit `.env` file**:
   - Comment out (add #) to Google lines:
     ```
     # LLM_PROVIDER=google
     # GOOGLE_API_KEY=...
     ```
   - Uncomment OpenAI lines (remove #):
     ```
     LLM_PROVIDER=openai
     OPENAI_API_KEY=sk-proj-your-actual-key-here
     OPENAI_MODEL=gpt-4o-mini
     ```

3. **Done!** Run `python simple_rag.py`

---

### 🟣 OPTION C: Local Model (No API Key)

1. **Edit `.env` file**:
   - Comment out all other providers
   - Uncomment:
     ```
     LLM_PROVIDER=local
     ```

2. **Done!** Run `python simple_rag.py`

---

## 🎬 Step 2: Test with YouTube

After setting up your LLM, test it:

```bash
python simple_rag.py
```

Then paste this YouTube URL:
```
https://youtu.be/LxoG4R_E3UE
```

Wait for it to process, then ask:
```
What is this video about?
```

You should get a much better answer than before!

---

## 🐛 YouTube Fix Applied

I also fixed the YouTube API error you encountered. The video should now load correctly!

---

## 💡 Quick Tips

- **Google Gemini** = FREE, Great quality
- **OpenAI GPT-4o-mini** = $0.001/query, Excellent quality  
- **Local Model** = FREE, Lower quality

**I recommend starting with Google Gemini (FREE)!**

---

## ✨ Your .env File Location

The file is here:
```
C:\Users\Admin\Jarvis\rag_study\.env
```

Just open it in Notepad and add your API key!

---

**Need help?** See `LLM_SETUP_GUIDE.md` for detailed instructions.
