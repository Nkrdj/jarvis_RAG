# YouTube Video Support for RAG System

## 📺 Overview
Your RAG (Retrieval-Augmented Generation) system now supports processing YouTube videos! This feature extracts transcripts from YouTube videos and adds them to your knowledge base, allowing you to ask questions about video content.

## ✨ Features
- **Automatic Transcript Extraction**: Fetches video transcripts using YouTube's official API
- **Smart Chunking**: Intelligently breaks down transcript into manageable chunks for better retrieval
- **Multiple URL Formats**: Supports various YouTube URL formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://m.youtube.com/watch?v=VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
- **Persistent Storage**: Transcripts are saved to the database for future queries

## 🚀 Usage

### Method 1: Using the Test Script (Recommended for Testing)
```bash
python test_youtube.py
```

Then enter a YouTube URL when prompted, and start asking questions about the video content!

### Method 2: Programmatic Usage
```python
from simple_rag import SimpleRAG

# Initialize RAG
rag = SimpleRAG()

# Add a YouTube video
video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
rag.load_youtube_video(video_url)

# Query the video content
results = rag.retrieve("What is this video about?", top_k=3)

# Generate answer
context = " ".join([doc['document'] for doc in results])
answer = rag.generate_response("What is this video about?", context)
print(answer)
```

### Method 3: Add to Interactive RAG Shell
You can modify `simple_rag.py`'s main() function to add a command for YouTube videos:

```python
# In the main loop, add:
if user_query.lower().startswith('yt:'):
    # Extract URL from command: "yt: https://youtube.com/..."
    url = user_query[3:].strip()
    rag.load_youtube_video(url)
    print("✅ Video added to knowledge base!")
    continue
```

## 📝 Example Workflow

1. **Add a YouTube video**:
   ```python
   rag.load_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
   ```

2. **Ask questions**:
   - "What are the main topics discussed in this video?"
   - "Can you summarize the key points?"
   - "What did the speaker say about [specific topic]?"

## 🔧 How It Works

1. **URL Parsing**: Extracts the video ID from various YouTube URL formats
2. **Transcript Fetching**: Uses `YouTubeTranscriptApi` to download the video's transcript
3. **Text Chunking**: Splits the transcript into ~500 character chunks with 50-character overlap
4. **Embedding**: Each chunk is converted to a vector embedding
5. **Storage**: Chunks and embeddings are saved to the SQLite database
6. **Retrieval**: When you ask questions, the system finds the most relevant chunks
7. **Generation**: Uses the context from retrieved chunks to generate answers

## ⚠️ Important Notes

- **Transcripts Required**: The video must have transcripts available (auto-generated or manual)
- **Language Support**: Works best with English videos, but supports any language with available transcripts
- **Network Required**: Needs an internet connection to fetch transcripts
- **Rate Limiting**: YouTube may rate-limit excessive requests

## 🐛 Troubleshooting

### "Could not retrieve transcript"
- The video might not have transcripts enabled
- Check if the video is private or age-restricted
- Verify the URL is correct

### "Could not extract video ID"
- Make sure you're using a valid YouTube URL format
- Try copying the URL directly from your browser's address bar

## 💡 Tips for Best Results

1. **Use Educational Content**: Technical tutorials, lectures, and educational videos work best
2. **Check Transcript Quality**: Auto-generated transcripts may have errors
3. **Ask Specific Questions**: The more specific your question, the better the answer
4. **Combine Sources**: Mix YouTube content with PDFs and DOCX files for comprehensive knowledge

## 🎯 Example Use Cases

- **Learn from Tutorials**: Add programming tutorials and ask specific implementation questions
- **Research**: Process conference talks and research presentations
- **Study**: Add lecture videos and quiz yourself
- **Content Analysis**: Analyze multiple videos on the same topic

## 📚 Dependencies

- `youtube-transcript-api`: For fetching YouTube transcripts
- All existing RAG dependencies (transformers, sentence-transformers, etc.)

Already installed via `requirements.txt`!

---

**Happy Learning! 🎓**
