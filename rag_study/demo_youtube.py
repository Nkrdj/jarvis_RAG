"""
Quick Demo: YouTube Video RAG Integration
==========================================

This script demonstrates the YouTube video support in 3 different ways.
"""

from simple_rag import SimpleRAG
import sys

def demo_1_basic():
    """Demo 1: Basic YouTube video loading"""
    print("\n" + "="*60)
    print("DEMO 1: Basic YouTube Video Loading")
    print("="*60)
    
    rag = SimpleRAG()
    
    # Example: A short educational video
    # Replace with any YouTube URL you want to test
    print("\n📥 Loading a YouTube video...")
    print("(You can replace this URL with any video)")
    
    example_url = input("\nPaste a YouTube URL (or press Enter for manual test): ").strip()
    
    if example_url:
        rag.load_youtube_video(example_url)
        
        print("\n✅ Video loaded successfully!")
        print(f"   Total documents in knowledge base: {len(rag.documents)}")
        
        return rag
    else:
        print("\nSkipping Demo 1...")
        return rag

def demo_2_querying(rag):
    """Demo 2: Query the video content"""
    print("\n" + "="*60)
    print("DEMO 2: Querying Video Content")
    print("="*60)
    
    if len(rag.documents) == 0:
        print("\nNo documents in knowledge base. Please add a video first.")
        return
    
    print("\n💭 Let's ask some questions about the content...")
    
    sample_questions = [
        "What is the main topic of this video?",
        "Can you summarize the key points?",
        "What are the important concepts discussed?"
    ]
    
    print("\nSuggested questions:")
    for i, q in enumerate(sample_questions, 1):
        print(f"  {i}. {q}")
    
    question = input("\nYour question (or press Enter to skip): ").strip()
    
    if question:
        print(f"\n🔍 Searching for: {question}")
        
        # Retrieve relevant chunks
        results = rag.retrieve(question, top_k=3)
        
        print("\n📚 Retrieved chunks:")
        context = ""
        for i, doc in enumerate(results, 1):
            score = doc['score']
            snippet = doc['document'][:150]
            print(f"\n  Chunk {i} (Relevance: {score:.4f}):")
            print(f"  {snippet}...")
            context += doc['document'] + " "
        
        # Generate answer
        print("\n💡 Generated Answer:")
        print("-" * 60)
        answer = rag.generate_response(question, context)
        print(answer)
        print("-" * 60)

def demo_3_multiple_sources():
    """Demo 3: Combining YouTube with other sources"""
    print("\n" + "="*60)
    print("DEMO 3: Multi-Source Knowledge Base")
    print("="*60)
    
    print("\n🎯 The power of RAG: Combine YouTube videos with PDFs and DOCX!")
    print("\nYou can add:")
    print("  • YouTube educational videos")
    print("  • PDF research papers")
    print("  • DOCX lecture notes")
    print("  • Custom text chunks")
    
    print("\nAll sources are searchable together, creating a comprehensive")
    print("knowledge base that can answer complex questions!")

def main():
    print("="*60)
    print("🎬 YouTube RAG Integration - Interactive Demo")
    print("="*60)
    
    print("\nThis demo shows how to use YouTube videos in your RAG system.")
    print("You can add video transcripts and ask questions about them!")
    
    # Run demos
    rag = demo_1_basic()
    demo_2_querying(rag)
    demo_3_multiple_sources()
    
    print("\n" + "="*60)
    print("✨ Demo Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Try 'python simple_rag.py' for the interactive shell")
    print("  2. Try 'python test_youtube.py' for focused YouTube testing")
    print("  3. Read YOUTUBE_SUPPORT.md for full documentation")
    print("\nHappy learning! 🚀")

if __name__ == "__main__":
    main()
