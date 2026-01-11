import re
from collections import Counter

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

def analyze_text_quality(text):
    """Analyze text for English characteristics"""
    vowels = sum(1 for c in text if c in 'AEIOU')
    vowel_ratio = vowels / len(text) if text else 0
    
    # Common bigrams
    bigrams = {}
    for i in range(len(text)-1):
        bg = text[i:i+2]
        bigrams[bg] = bigrams.get(bg, 0) + 1
    
    common_bigrams = {'TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'OR', 'RE', 'AR', 'EN'}
    found_bigrams = sum(bigrams.get(bg, 0) for bg in common_bigrams)
    
    return vowel_ratio, found_bigrams, bigrams

def show_result(key, text):
    """Display result with analysis"""
    vowel_ratio, bigram_count, bigrams = analyze_text_quality(text)
    
    print(f"\nKey: {key}")
    print(f"  Vowel ratio: {vowel_ratio:.1%}")
    print(f"  Common bigrams found: {bigram_count}")
    print(f"  Text: {text}")
    
    # Look for partial English words
    words_4plus = [w for w in re.findall(r'[A-Z]{4,}', text)]
    if words_4plus:
        print(f"  Sequences 4+: {', '.join(set(words_4plus[:10]))}")
    
    return vowel_ratio

print("=" * 80)
print("COMPREHENSIVE VIGENERE ANALYSIS ON STEP49_TRANSPOSED")
print("=" * 80)

print(f"\nInput: {STEP49_TRANSPOSED}")
print(f"Length: {len(STEP49_TRANSPOSED)}")
print(f"\nKnown words in this text: ONLY (pos 28), USE (pos 85), SEE (pos 86)")

# Extended key list
keys_to_test = [
    # Original requested keys
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "NORTHEAST",
    
    # Derived keys from crib analysis
    "DAVM", "MSQ", "SQD",
    
    # Variations
    "DAVMMUSIC", "MUSICDAVM", "DAVIDMUSIC",
    "BERLINUNDERGRO", "UNDERGROUNDBERLIN",
    
    # Common K4-related keys
    "SHADOW", "SHADES", "LIGHT", "STONE", "STONE SKULL",
    "EMUFIND", "EMBEDED",
    
    # Compound keys
    "KRYPTOSBERG", "BERLINKEY", "MUSICBOX",
    
    # Short keys
    "MUSIC", "DAVID", "SCULPTURE", "COPPER",
    "SECRETMESSAGE", "HIDDEN", "LAYER",
]

results = []

for key in keys_to_test:
    try:
        decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key)
        vowel_ratio, bigram_count, bigrams = analyze_text_quality(decrypted)
        
        # Check for specific patterns
        has_only = "ONLY" in decrypted
        has_use = "USE" in decrypted
        has_see = "SEE" in decrypted
        has_berlin = "BERLIN" in decrypted
        has_clock = "CLOCK" in decrypted
        
        score = vowel_ratio + (bigram_count / len(decrypted)) * 0.1
        
        results.append({
            'key': key,
            'text': decrypted,
            'vowel_ratio': vowel_ratio,
            'bigrams': bigram_count,
            'score': score,
            'has_only': has_only,
            'has_use': has_use,
            'has_see': has_see,
            'has_berlin': has_berlin,
            'has_clock': has_clock,
        })
    except:
        pass

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)

print("\n" + "=" * 80)
print("TOP RESULTS BY READABILITY SCORE")
print("=" * 80)

for i, r in enumerate(results[:15]):
    marker = ""
    if r['has_berlin'] or r['has_clock']:
        marker = " *** CONTAINS BERLIN/CLOCK ***"
    elif r['has_only'] or r['has_use'] or r['has_see']:
        marker = " [Contains crib]"
    
    print(f"\n{i+1}. Key: {r['key']:20} | Score: {r['score']:.3f} | Vowels: {r['vowel_ratio']:.1%}{marker}")
    print(f"   {r['text'][:90]}")

print("\n" + "=" * 80)
print("BEST CANDIDATE - KEY WITH HIGHEST VOWEL RATIO")
print("=" * 80)

best = max(results, key=lambda x: x['vowel_ratio'])
show_result(best['key'], best['text'])

print("\n" + "=" * 80)
print("CHECKING: What if we apply REVERSE Vigenere (encryption)?")
print("=" * 80)

def vigenere_encrypt(plaintext, key):
    """Encrypt using Vigenere cipher"""
    plaintext = re.sub(r'[^A-Za-z]', '', plaintext).upper()
    key = re.sub(r'[^A-Za-z]', '', key).upper()
    
    ciphertext = []
    key_index = 0
    
    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            encrypted = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            ciphertext.append(encrypted)
            key_index += 1
    
    return ''.join(ciphertext)

# Try encrypting STEP49 with keys to see if we get known plaintexts
for key in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]:
    encrypted = vigenere_encrypt(STEP49_TRANSPOSED, key)
    # Check if this looks like K4 or has patterns
    print(f"\nEncrypting STEP49 with '{key}':")
    print(f"  Result: {encrypted}")

