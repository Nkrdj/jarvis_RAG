#!/usr/bin/env python3
"""
Integration Test for YouTube RAG Feature
=========================================

This script tests all aspects of the YouTube integration to ensure
everything is working correctly.
"""

import sys
import os

def test_imports():
    """Test 1: Check if all required modules can be imported"""
    print("\n" + "="*60)
    print("TEST 1: Checking Imports")
    print("="*60)
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ youtube_transcript_api imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import youtube_transcript_api: {e}")
        return False
    
    try:
        from simple_rag import SimpleRAG
        print("✅ SimpleRAG imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SimpleRAG: {e}")
        return False
    
    try:
        import re
        print("✅ re module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import re: {e}")
        return False
    
    return True

def test_method_exists():
    """Test 2: Check if load_youtube_video method exists"""
    print("\n" + "="*60)
    print("TEST 2: Checking Method Existence")
    print("="*60)
    
    try:
        from simple_rag import SimpleRAG
        rag = SimpleRAG()
        
        if hasattr(rag, 'load_youtube_video'):
            print("✅ load_youtube_video method exists")
            
            # Check if it's callable
            if callable(getattr(rag, 'load_youtube_video')):
                print("✅ load_youtube_video is callable")
            else:
                print("❌ load_youtube_video is not callable")
                return False
        else:
            print("❌ load_youtube_video method NOT found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during method check: {e}")
        return False

def test_url_detection():
    """Test 3: Test URL pattern detection"""
    print("\n" + "="*60)
    print("TEST 3: URL Pattern Detection")
    print("="*60)
    
    import re
    
    youtube_patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
        r'youtube\.com'
    ]
    
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://youtu.be/dQw4w9WgXcQ", True),
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", True),
        ("https://www.google.com", False),
        ("What is RAG?", False),
    ]
    
    all_passed = True
    for url, should_match in test_urls:
        is_youtube = any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
        
        if is_youtube == should_match:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} '{url[:50]}...' - Expected: {should_match}, Got: {is_youtube}")
    
    return all_passed

def test_video_id_extraction():
    """Test 4: Test video ID extraction"""
    print("\n" + "="*60)
    print("TEST 4: Video ID Extraction")
    print("="*60)
    
    import re
    
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=abc123&t=10s", "abc123"),
    ]
    
    all_passed = True
    for url, expected_id in test_cases:
        video_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        
        if video_id == expected_id:
            print(f"✅ Extracted '{video_id}' from {url[:40]}...")
        else:
            print(f"❌ Expected '{expected_id}', got '{video_id}' from {url[:40]}...")
            all_passed = False
    
    return all_passed

def test_files_exist():
    """Test 5: Check if all documentation files exist"""
    print("\n" + "="*60)
    print("TEST 5: Documentation Files")
    print("="*60)
    
    required_files = [
        "simple_rag.py",
        "test_youtube.py",
        "demo_youtube.py",
        "README.md",
        "YOUTUBE_SUPPORT.md",
        "SUMMARY.md",
        "QUICK_REFERENCE.md",
        "requirements.txt",
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} NOT found")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Test 6: Check if youtube-transcript-api is in requirements.txt"""
    print("\n" + "="*60)
    print("TEST 6: Requirements.txt")
    print("="*60)
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        if "youtube-transcript-api" in content:
            print("✅ youtube-transcript-api found in requirements.txt")
            return True
        else:
            print("❌ youtube-transcript-api NOT found in requirements.txt")
            return False
    except FileNotFoundError:
        print("❌ requirements.txt file not found")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" " * 15 + "YOUTUBE RAG INTEGRATION TEST SUITE")
    print("="*70)
    print("\nRunning comprehensive tests to verify YouTube integration...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Method Existence", test_method_exists),
        ("URL Detection", test_url_detection),
        ("Video ID Extraction", test_video_id_extraction),
        ("Documentation Files", test_files_exist),
        ("Requirements", test_requirements),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" " * 25 + "TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("-"*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! YouTube integration is working perfectly!")
        print("\n✨ You're ready to use YouTube videos in your RAG system!")
        print("\nNext steps:")
        print("  1. Run: python simple_rag.py")
        print("  2. Paste a YouTube URL")
        print("  3. Start asking questions!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  - Run: pip install -r requirements.txt")
        print("  - Check that all files are present")
        print("  - Verify simple_rag.py has the load_youtube_video method")
    
    print("\n" + "="*70)
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
