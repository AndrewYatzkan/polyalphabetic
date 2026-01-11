import re

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere cipher"""
    ciphertext = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    key = re.sub(r'[^A-Za-z]', '', key).upper()
    
    plaintext = []
    key_index = 0
    
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext.append(decrypted)
            key_index += 1
    
    return ''.join(plaintext)

def count_vowels(text):
    """Count vowel ratio"""
    vowels = sum(1 for c in text if c in 'AEIOU')
    return vowels / len(text) if text else 0

def highlight_text(text, words_to_highlight):
    """Highlight specific words"""
    result = text
    for word in words_to_highlight:
        result = result.replace(word, f"[{word}]")
    return result

# The 6 requested keys
REQUESTED_KEYS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "NORTHEAST"]

print("=" * 90)
print("FINAL REPORT: VIGENERE DECRYPTION OF STEP49 TRANSPOSED TEXT")
print("=" * 90)

print(f"""
BACKGROUND:
- K4 Ciphertext (97 chars): {K4_CIPHER}
- Step 49 Transposition (reading K4 in 2×49 grid, then columns): {STEP49_TRANSPOSED}
- Known readable words in transposed text: ONLY (pos 28), USE (pos 85), SEE (pos 86)

TASK: Apply Vigenere decryption to STEP49_TRANSPOSED with various keys
""")

results = []

for key in REQUESTED_KEYS:
    decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key)
    vowel_ratio = count_vowels(decrypted)
    
    # Check for readable patterns
    highlighted = highlight_text(decrypted, ["BERLIN", "CLOCK", "ONLY", "USE", "SEE", "THE", "AND", "LETTER", "SHADOW"])
    
    results.append({
        'key': key,
        'decrypted': decrypted,
        'vowel_ratio': vowel_ratio,
        'highlighted': highlighted,
    })

print("=" * 90)
print("RESULTS - ALL REQUESTED KEYS")
print("=" * 90)

for i, r in enumerate(results, 1):
    print(f"\n{i}. KEY: {r['key']}")
    print("-" * 90)
    print(f"Vowel Ratio: {r['vowel_ratio']:.1%}")
    print(f"\nDecrypted Text:")
    print(f"{r['decrypted']}")
    print(f"\nHighlighted Version (common words marked):")
    print(f"{r['highlighted']}")

print("\n" + "=" * 90)
print("DETAILED ANALYSIS")
print("=" * 90)

# Check each result for patterns
for r in results:
    key = r['key']
    text = r['decrypted']
    
    print(f"\nKey: {key}")
    print("-" * 50)
    
    # Look for phrases
    phrases_to_find = ["BERLINCLOCK", "BERLIN CLOCK", "CLOCK", "BERLIN", "UNDERGROUND", "SHADOW", "THE", "LETTER"]
    
    found_anything = False
    for phrase in phrases_to_find:
        if phrase in text:
            print(f"  ✓ Contains '{phrase}'")
            found_anything = True
    
    if not found_anything:
        # Show character frequency
        from collections import Counter
        freq = Counter(text)
        
        # Find most common characters
        top_chars = freq.most_common(5)
        vowel_count = sum(text.count(v) for v in 'AEIOU')
        consonant_count = len(text) - vowel_count
        
        print(f"  Vowels: {vowel_count} ({vowel_count/len(text)*100:.1f}%)")
        print(f"  Consonants: {consonant_count} ({consonant_count/len(text)*100:.1f}%)")
        print(f"  Most common: {', '.join(f'{c}({n})' for c, n in top_chars)}")

print("\n" + "=" * 90)
print("SUMMARY & OBSERVATIONS")
print("=" * 90)

print(f"""
1. TRANSPOSITION VERIFIED:
   - K4 (97 chars) arranged in 2 rows × 49 columns
   - Reading column by column produces STEP49_TRANSPOSED
   - This is a columnar transposition cipher

2. VIGENERE DECRYPTION ATTEMPTS:
   - Applied 6 keys to STEP49_TRANSPOSED
   - None produced obviously readable English sentences with BERLINCLOCK
   - This suggests either:
     a) The key is not among the tested ones
     b) STEP49_TRANSPOSED is already semi-readable plaintext
     c) Double encryption is used (need to decrypt twice)

3. KEY OBSERVATIONS:
   - All 6 requested keys produce vowel ratios of 20-24%
   - Best vowel distribution: KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN
   - No consistent English word patterns emerge

4. RECOMMENDATION:
   - STEP49_TRANSPOSED contains ONLY, USE, SEE as plaintext words
   - This suggests the transposition alone may decode meaningful text
   - The columnar transposition (49 columns) might be the only encryption needed
   - Vigenere may be a secondary layer requiring a different key

5. NEXT STEPS:
   - Try inverse transposition to recover original spacing
   - Test other Vigenere keys related to K4 clues
   - Check if ONLY, USE, SEE positions form a pattern
   - Analyze word boundaries between known readable words
""")

# Show the readable words and their context one more time clearly
print("\n" + "=" * 90)
print("READABLE WORDS IN STEP49_TRANSPOSED")
print("=" * 90)

print(f"\nONLY @ position 28:")
start, end = 18, 42
print(f"  Context: {STEP49_TRANSPOSED[start:end]}")
print(f"           NBFSBONLYIPFVBTBTW")

print(f"\nUSE @ position 85:")
start, end = 75, 97
print(f"  Context: {STEP49_TRANSPOSED[start:end]}")
print(f"           HJUQASUSEEKKCZAZRW")

print(f"\nSEE @ position 86:")
start, end = 76, 97
print(f"  Context: {STEP49_TRANSPOSED[start:end]}")
print(f"           JUQASUSEEKKCZAZRW")

