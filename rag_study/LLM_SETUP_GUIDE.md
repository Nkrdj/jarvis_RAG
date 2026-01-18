# 🚀 Industrial-Standard LLM Setup Guide

## Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install openai anthropic google-generativeai python-dotenv
```

### Step 2: Create `.env` File
Copy `.env.template` to `.env`:
```bash
copy .env.template .env
```

### Step 3: Add Your API Key
Edit `.env` file and add your API key for your chosen provider.

---

## 🔑 Getting API Keys

### OpenAI (GPT-4o/GPT-4) - Recommended
1. Go to: https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key and paste it in `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...your-key-here...
   LLM_PROVIDER=openai
   ```

**Cost**: ~$0.15 per 1M input tokens (gpt-4o-mini)

### Anthropic Claude
1. Go to: https://console.anthropic.com/
2. Create an account
3. Go to API Keys section
4. Create a new key
5. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...your-key-here...
   LLM_PROVIDER=anthropic
   ```

**Cost**: ~$3.00 per 1M input tokens (Claude 3.5 Sonnet)

### Google Gemini - FREE Tier Available!
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Add to `.env`:
   ```
   GOOGLE_API_KEY=...your-key-here...
   LLM_PROVIDER=google
   ```

**Cost**: FREE up to 15 requests/minute, then ~$0.075 per 1M tokens

---

## 📋 Complete `.env` Example

```env
# Choose ONE provider
LLM_PROVIDER=openai

# OpenAI Setup (if using OpenAI)
OPENAI_API_KEY=sk-proj-abc123...
OPENAI_MODEL=gpt-4o-mini

# OR Anthropic Setup (if using Claude)
# ANTHROPIC_API_KEY=sk-ant-abc123...
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OR Google Setup (if using Gemini)
# GOOGLE_API_KEY=AIza...
# GOOGLE_MODEL=gemini-2.0-flash-exp
```

---

## ⚡ Quick Start

### For OpenAI (GPT-4o-mini) - Recommended for Beginners
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...your-actual-key...
OPENAI_MODEL=gpt-4o-mini
```

### For Google Gemini - FREE Option
```env
LLM_PROVIDER=google
GOOGLE_API_KEY=...your-actual-key...
GOOGLE_MODEL=gemini-2.0-flash-exp
```

### For Local Model - No API Key Needed
```env
LLM_PROVIDER=local
```

---

## 🎯 Model Recommendations

| Use Case | Provider | Model | Why? |
|----------|----------|-------|------|
| **Best Quality** | Anthropic | claude-3-5-sonnet-20241022 | Most accurate answers |
| **Best Value** | OpenAI | gpt-4o-mini | Fast, cheap, great quality |
| **FREE** | Google | gemini-2.0-flash-exp | Free tier available |
| **No API Key** | Local | flan-t5-base | Works offline |
| **Maximum Speed** | Google | gemini-2.0-flash-exp | Fastest responses |

---

## ✅ Testing Your Setup

After setting up your `.env` file, run:

```bash
python simple_rag.py
```

You should see:
```
INFO: LLM Provider: openai
✅ OpenAI initialized with model: gpt-4o-mini
```

If you see an error, check:
- ✓ `.env` file exists in the project folder
- ✓ API key is correct (no extra spaces)
- ✓ LLM_PROVIDER matches your chosen provider

---

## 💰 Cost Estimation

### OpenAI (gpt-4o-mini) - Recommended
- **Input**: $0.15 per 1M tokens
- **Output**: $0.60 per 1M tokens
- **Typical query**: ~$0.001 (less than 1 cent)

### Google Gemini - Best for Beginners
- **FREE Tier**: 15 requests/minute, 1500/day
- **After free tier**: $0.075 per 1M tokens
- **Perfect for learning and testing**

### Anthropic (Claude 3.5 Sonnet)
- **Input**: $3.00 per 1M tokens
- **Output**: $15.00 per 1M tokens
- **Best for high-quality responses**

### Local (flan-t5-base)
- **FREE**: No costs
- **Trade-off**: Lower quality answers

---

## 🔧 Troubleshooting

### Error: "OpenAI API key not set"
- Check that `.env` file exists
- Verify API key is correct
- Make sure no quotes around the key

### Error: "Module not found"
```bash
pip install openai anthropic google-generativeai python-dotenv
```

### System falls back to local model
- This means API key is missing or invalid
- Check `.env` file configuration
- System automatically uses local model as fallback

---

## 🎓 Next Steps

1. ✅ Install dependencies
2. ✅ Create `.env` file
3. ✅ Add your API key
4. ✅ Run `python simple_rag.py`
5. ✅ Test with YouTube videos!

---

**Recommended for Most Users**: 
Start with **Google Gemini** (FREE) or **OpenAI gpt-4o-mini** ($0.001/query)

Both are excellent industrial-standard models that will give you far better results than the local flan-t5-base!
