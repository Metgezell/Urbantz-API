#!/usr/bin/env python3
"""
Simple test to find working Claude model
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ANTHROPIC_API_KEY not set")
    exit(1)

print(f"✅ API Key found: {api_key[:15]}...")

# Initialize Anthropic client
client = Anthropic(api_key=api_key)

# List of models to try
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-2.1",
    "claude-2",
    "claude-instant-1.2"
]

print("\n🔍 Testing which model works...\n")

for model in models_to_try:
    try:
        print(f"Testing {model}...", end=" ")
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Zeg 'API werkt!' in het Nederlands"}
            ]
        )
        response_text = message.content[0].text
        print(f"✅ WERKT!")
        print(f"   Response: {response_text}\n")
        print(f"\n🎉 SUCCESS! Gebruik model: {model}\n")
        break
    except Exception as e:
        error_msg = str(e)
        if "not_found_error" in error_msg:
            print(f"❌ Model niet gevonden")
        else:
            print(f"❌ Error: {error_msg[:50]}...")


