# 🎬 YouTube RAG - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install (if not already done)
pip install youtube-transcript-api

# 2. Run interactive shell
python simple_rag.py

# 3. Paste a YouTube URL when prompted
# Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 4. Ask questions about the video!
```

---

## 📝 Common Tasks

### Add a YouTube Video
```python
from simple_rag import SimpleRAG
rag = SimpleRAG()
rag.load_youtube_video("https://www.youtube.com/watch?v=VIDEO_ID")
```

### Query Video Content
```python
results = rag.retrieve("What is discussed in the video?", top_k=3)
context = " ".join([doc['document'] for doc in results])
answer = rag.generate_response("What is discussed?", context)
print(answer)
```

### List All Documents
```python
print(f"Total documents: {len(rag.documents)}")
```

---

## 🎯 URL Formats Supported

✅ `https://www.youtube.com/watch?v=VIDEO_ID`  
✅ `https://youtu.be/VIDEO_ID`  
✅ `https://m.youtube.com/watch?v=VIDEO_ID`  
✅ `https://www.youtube.com/embed/VIDEO_ID`

---

## 💻 Command Line Options

| Command | Purpose |
|---------|---------|
| `python simple_rag.py` | Interactive shell (auto-detects YouTube URLs) |
| `python test_youtube.py` | YouTube-focused testing |
| `python demo_youtube.py` | Guided demonstration |

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "Could not retrieve transcript" | Video doesn't have transcripts enabled |
| "Could not extract video ID" | Check URL format |
| "Connection error" | Check internet connection |
| Module not found | Run `pip install youtube-transcript-api` |

---

## 📊 How It Works (Simple)

```
YouTube URL → Extract ID → Get Transcript → Chunk Text → 
Embed → Store in DB → Search → Retrieve → Generate Answer
```

---

## ⚡ Pro Tips

1. **Educational videos work best** - tutorials, lectures, talks
2. **Paste URLs directly** - the shell auto-detects them
3. **Combine with PDFs** - mix video + document sources
4. **Ask specific questions** - better specificity = better answers
5. **Check transcript availability** - some videos don't have them

---

## 🎓 Example Questions to Ask

After adding a tutorial video:
- "What are the main topics covered?"
- "How do I implement [specific feature]?"
- "What are the key takeaways?"
- "Can you summarize the video?"
- "What tools were mentioned?"

---

## 📁 File Structure

```
rag_study/
├── simple_rag.py          # Main RAG implementation (YouTube support!)
├── test_youtube.py        # YouTube testing script
├── demo_youtube.py        # Interactive demo
├── db.py                  # Database layer
├── requirements.txt       # Dependencies (includes youtube-transcript-api)
├── README.md             # Full documentation
├── YOUTUBE_SUPPORT.md    # Detailed YouTube guide
└── SUMMARY.md            # Implementation summary
```

---

## 🔑 Key Features at a Glance

| Feature | Status |
|---------|--------|
| PDF Support | ✅ |
| DOCX Support | ✅ |
| YouTube Videos | ✅ NEW! |
| Web Search Fallback | ✅ |
| Persistent Storage | ✅ |
| Auto URL Detection | ✅ |
| Multi-language | ✅ |
| Smart Chunking | ✅ |
| MCP Server | ✅ |

---

## 📚 Documentation

- **README.md** - Main project docs
- **YOUTUBE_SUPPORT.md** - Complete YouTube guide  
- **SUMMARY.md** - Implementation details
- **This file** - Quick reference

---

## 🎬 Video Processing Specs

- **Chunk Size**: ~500 characters
- **Overlap**: 50 characters
- **Storage**: SQLite database
- **Embedding Model**: all-MiniLM-L6-v2
- **LLM**: google/flan-t5-base

---

## 🌟 Next Steps After Adding Videos

1. ✅ Add your first YouTube video
2. ✅ Ask a question about it
3. ✅ Add a PDF/DOCX for comparison
4. ✅ Try multi-source queries
5. ✅ Explore MCP server integration

---

**Need Help?** See `YOUTUBE_SUPPORT.md` for full documentation.

**Quick Test:**
```bash
python test_youtube.py
# Enter: https://www.youtube.com/watch?v=dQw4w9WgXcQ
# Ask: "What is this video about?"
```

---

*Last Updated: 2026-01-18*  
*Version: 1.0*
