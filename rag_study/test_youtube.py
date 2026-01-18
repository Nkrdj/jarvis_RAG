"""
Test script for YouTube video transcript extraction
This demonstrates how to add YouTube videos to your RAG knowledge base
"""
from simple_rag import SimpleRAG

def main():
    print("=" * 60)
    print("YouTube Video Integration Test for RAG")
    print("=" * 60)
    
    # Initialize RAG
    rag = SimpleRAG()
    
    # Example: Add a YouTube video
    print("\n📺 Testing YouTube Video Transcript Extraction\n")
    
    # You can use any YouTube video URL
    # Example URLs (you can replace with your own):
    test_urls = [
        # "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Example video
        # "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
    ]
    
    print("Enter a YouTube video URL to add to the knowledge base:")
    print("(or press Enter to skip)")
    url = input("URL: ").strip()
    
    if url:
        print(f"\n🔄 Processing: {url}")
        rag.load_youtube_video(url)
        print("✅ Video transcript added to knowledge base!\n")
        
        # Test querying the video content
        print("\n" + "=" * 60)
        print("Now you can ask questions about the video!")
        print("=" * 60)
        
        while True:
            query = input("\nYour question (or 'quit' to exit): ").strip()
            if query.lower() in ['quit', 'exit', '']:
                break
            
            # Retrieve relevant context
            results = rag.retrieve(query, top_k=3)
            
            print("\n📚 Retrieved Context:")
            context = ""
            for i, doc in enumerate(results, 1):
                print(f"\n{i}. (Score: {doc['score']:.4f})")
                print(f"   {doc['document'][:200]}...")
                context += doc['document'] + " "
            
            # Generate answer
            print("\n💡 Answer:")
            answer = rag.generate_response(query, context)
            print(answer)
    else:
        print("\nNo URL provided. Exiting...")
        print("\nTo use this feature, run the script again and enter a YouTube URL.")

if __name__ == "__main__":
    main()
