"""Check current key and test it"""
from pathlib import Path
from openai import OpenAI

env_file = Path(__file__).parent.parent / '.env'

print("="*70)
print("OpenAI API Key Checker")
print("="*70)

# Read current key from .env
with open(env_file, 'r', encoding='utf-8') as f:
    content = f.read()
    for line in content.split('\n'):
        if line.strip().startswith('OPENAI_API_KEY') and not line.strip().startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                current_key = parts[1].strip().strip('"').strip("'")
                print(f"\nCurrent key in .env file:")
                print(f"  Length: {len(current_key)}")
                print(f"  Starts with: {current_key[:25]}...")
                print(f"  Ends with: ...{current_key[-15:]}")
                
                # Test it
                print(f"\nTesting current key...")
                try:
                    client = OpenAI(api_key=current_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Say 'Working'"}],
                        max_tokens=10
                    )
                    print("[SUCCESS] Current key is VALID and working!")
                    print(f"Response: {response.choices[0].message.content}")
                    break
                except Exception as e:
                    error_str = str(e)
                    if "401" in error_str or "invalid" in error_str.lower():
                        print("[FAIL] Current key is INVALID")
                        print("\nThe key in your .env file is not working.")
                        print("Please verify:")
                        print("  1. The key in .env matches the one that works elsewhere")
                        print("  2. The key is complete (not truncated)")
                        print("  3. There are no extra spaces or characters")
                        print("\nTo update the key:")
                        print("  1. Open the .env file")
                        print("  2. Replace the value after OPENAI_API_KEY=")
                        print("  3. Format: OPENAI_API_KEY=sk-proj-... (no quotes, no spaces)")
                        print("  4. Save the file")
                        print("  5. Run this test again")
                    else:
                        print(f"[ERROR] {error_str[:200]}")
                    break

print("\n" + "="*70)

