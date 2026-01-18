"""
Quick Setup Script for Industrial LLM
======================================
This script helps you quickly set up your industrial-standard LLM.
"""

import os
import sys

def create_env_file():
    """Create .env file with user's API key"""
    print("="*70)
    print("  INDUSTRIAL-STANDARD LLM SETUP")
    print("="*70)
    print("\nThis script will help you set up your RAG system with a professional LLM.")
    print("\n📌 Recommended Options:")
    print("  1. Google Gemini (FREE)")
    print("  2. OpenAI GPT-4o-mini (Cheap & Fast)")
    print("  3. Anthropic Claude (Best Quality)")
    print("  4. Local model (No API key needed)")
    
    print("\n" + "-"*70)
    choice = input("\nEnter your choice (1-4): ").strip()
    
    env_content = ""
    
    if choice == "1":
        print("\n✅ Great choice! Google Gemini has a generous FREE tier.")
        print("\n📝 To get your API key:")
        print("   1. Go to: https://makersuite.google.com/app/apikey")
        print("   2. Sign in with your Google account")
        print("   3. Click 'Create API Key'")
        print("   4. Copy the key")
        
        api_key = input("\n🔑 Paste your Google API key here: ").strip()
        
        env_content = f"""# Google Gemini Configuration
LLM_PROVIDER=google
GOOGLE_API_KEY={api_key}
GOOGLE_MODEL=gemini-2.0-flash-exp
"""
        
    elif choice == "2":
        print("\n✅ Excellent! OpenAI GPT-4o-mini offers great quality at low cost.")
        print("\n📝 To get your API key:")
        print("   1. Go to: https://platform.openai.com/api-keys")
        print("   2. Sign in or create an account")
        print("   3. Click 'Create new secret key'")
        print("   4. Copy the key")
        
        api_key = input("\n🔑 Paste your OpenAI API key here: ").strip()
        
        env_content = f"""# OpenAI Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY={api_key}
OPENAI_MODEL=gpt-4o-mini
"""
        
    elif choice == "3":
        print("\n✅ Perfect! Claude provides the highest quality responses.")
        print("\n📝 To get your API key:")
        print("   1. Go to: https://console.anthropic.com/")
        print("   2. Sign in or create an account")
        print("   3. Go to API Keys section")
        print("   4. Create a new key")
        
        api_key = input("\n🔑 Paste your Anthropic API key here: ").strip()
        
        env_content = f"""# Anthropic Claude Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY={api_key}
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
"""
        
    elif choice == "4":
        print("\n✅ Using local model - no API key required!")
        print("   Note: Quality will be lower than API-based models.")
        
        env_content = """# Local Model Configuration
LLM_PROVIDER=local
# No API key needed!
"""
        
    else:
        print("\n❌ Invalid choice! Using local model as default.")
        env_content = "LLM_PROVIDER=local\n"
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file!")
    print("\n" + "="*70)
    print("  SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python simple_rag.py")
    print("  2. Paste a YouTube URL or ask questions")
    print("  3. Enjoy professional-quality AI responses!")
    print("\n💡 Tip: See LLM_SETUP_GUIDE.md for detailed documentation")


if __name__ == "__main__":
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
