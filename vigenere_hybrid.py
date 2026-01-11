import re

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

# Key fragments discovered
KEY_FRAGMENTS = {
    "DAVM": "From ONLY at position 28",
    "MSQ": "From USE at position 85",
    "SQD": "From SEE at position 86",
}

# Extended keys based on fragments
EXTENDED_KEYS = [
    "DAVM",
    "DAVMDAVM",
    "DAVMONLY",
    "MSQ",
    "MSQMSQ",
    "MSQUSE",
    "SQD",
    "SQDSQD",
    "SQDSEE",
    "DAVMMSQ",
    "MSQSQD",
    "DAVMMSQSQD",
    "CLOCKDAVM",
    "CLOCKMSQ",
    "CLOCKSQD",
    "DAVMCLOCK",
    "MSQCLOCK",
    "SQDCLOCK",
]

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
        else:
            plaintext.append(char)
    
    return ''.join(plaintext)

def count_vowels(text):
    """Count vowel ratio"""
    vowels = sum(1 for c in text if c in 'AEIOU')
    return vowels / len(text) if text else 0

def find_english_words(text, min_len=3):
    """Extract potential English words"""
    words = re.findall(r'[A-Z]{' + str(min_len) + r',}', text)
    return list(set(words))

def assess_readability(text):
    """Score text readability"""
    vowel_ratio = count_vowels(text)
    # Check for common digraphs
    digraphs = sum(1 for i in range(len(text)-1) if text[i:i+2] in 
                   ['TH', 'HE', 'AN', 'IN', 'ER', 'RE', 'ED', 'OR', 'AR', 'EN', 'ND', 'TO', 'AT'])
    
    return vowel_ratio * 0.5 + (digraphs / len(text)) * 0.5 if text else 0

print("=" * 80)
print("HYBRID VIGENERE APPROACH - Testing Fragment-based Keys")
print("=" * 80)

results = []

print("\n1. Testing on STEP49 TRANSPOSED text:\n")
for key in EXTENDED_KEYS:
    decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key)
    vowel_ratio = count_vowels(decrypted)
    readability = assess_readability(decrypted)
    
    results.append({
        'key': key,
        'text': decrypted,
        'vowel_ratio': vowel_ratio,
        'readability': readability,
        'source': 'transposed'
    })

# Sort by readability
results_transposed = sorted([r for r in results if r['source'] == 'transposed'], 
                            key=lambda x: x['readability'], reverse=True)

print("Top 5 by readability score:\n")
for i, r in enumerate(results_transposed[:5]):
    print(f"{i+1}. Key: {r['key']:20} | Vowels: {r['vowel_ratio']:.2%} | Score: {r['readability']:.3f}")
    print(f"   Text: {r['text'][:70]}...")
    
    # Check for patterns
    if "ONLY" in r['text']:
        print(f"   *** CONTAINS ONLY ***")
    if "USE" in r['text']:
        print(f"   *** CONTAINS USE ***")
    if "SEE" in r['text']:
        print(f"   *** CONTAINS SEE ***")
    if "BERLIN" in r['text']:
        print(f"   *** CONTAINS BERLIN ***")
    if "CLOCK" in r['text']:
        print(f"   *** CONTAINS CLOCK ***")
    print()

print("\n" + "=" * 80)
print("2. Testing on K4 CIPHER text:\n")

results_cipher = []
for key in EXTENDED_KEYS:
    decrypted = vigenere_decrypt(K4_CIPHER, key)
    vowel_ratio = count_vowels(decrypted)
    readability = assess_readability(decrypted)
    
    results_cipher.append({
        'key': key,
        'text': decrypted,
        'vowel_ratio': vowel_ratio,
        'readability': readability
    })

results_cipher_sorted = sorted(results_cipher, key=lambda x: x['readability'], reverse=True)

print("Top 5 by readability score:\n")
for i, r in enumerate(results_cipher_sorted[:5]):
    print(f"{i+1}. Key: {r['key']:20} | Vowels: {r['vowel_ratio']:.2%} | Score: {r['readability']:.3f}")
    print(f"   Text: {r['text'][:70]}...")
    
    # Check for patterns
    if "ONLY" in r['text']:
        print(f"   *** CONTAINS ONLY ***")
    if "USE" in r['text']:
        print(f"   *** CONTAINS USE ***")
    if "SEE" in r['text']:
        print(f"   *** CONTAINS SEE ***")
    if "BERLIN" in r['text']:
        print(f"   *** CONTAINS BERLIN ***")
    if "CLOCK" in r['text']:
        print(f"   *** CONTAINS CLOCK ***")
    print()

# Additional analysis: What if CLOCK key is correct for cipher, then we apply transposition?
print("\n" + "=" * 80)
print("3. REVERSE COMBINED: K4 + CLOCK key, then check for transposition patterns\n")

decrypted_k4_clock = vigenere_decrypt(K4_CIPHER, "CLOCK")
print(f"K4 decrypted with CLOCK:")
print(f"{decrypted_k4_clock}\n")

vowel_ratio = count_vowels(decrypted_k4_clock)
print(f"Vowel ratio: {vowel_ratio:.2%}")
print(f"Length: {len(decrypted_k4_clock)}")

# Look for patterns
for pattern in ["ONLY", "USE", "SEE", "BERLIN", "CLOCK", "THE", "AND"]:
    if pattern in decrypted_k4_clock:
        pos = decrypted_k4_clock.find(pattern)
        print(f"Found '{pattern}' at position {pos}")

# Try other possible combinations
print("\n" + "=" * 80)
print("4. COMBINED KEYS: Testing if step49 was encrypted with compound key\n")

compound_keys = [
    "CLOCKBERLIN",
    "CLOCKPALIMPSEST",
    "CLOCKABSCISSA",
    "BERLINPALIMPSEST",
    "BERLINABSCISSA",
    "CLOCKNORTHEAST",
]

for key in compound_keys:
    decrypted_t = vigenere_decrypt(STEP49_TRANSPOSED, key)
    decrypted_k4 = vigenere_decrypt(K4_CIPHER, key)
    
    vowel_t = count_vowels(decrypted_t)
    vowel_k4 = count_vowels(decrypted_k4)
    
    if vowel_t > 0.35 or vowel_k4 > 0.35:
        print(f"\nKey: {key}")
        print(f"  Transposed (vowels {vowel_t:.2%}): {decrypted_t[:60]}...")
        print(f"  K4 Cipher (vowels {vowel_k4:.2%}): {decrypted_k4[:60]}...")

