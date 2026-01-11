import re
from collections import Counter

# The ciphertext and transposition result
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

# Keys to test
KEYS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "NORTHEAST"]

# Common English words dictionary (for highlighting)
COMMON_WORDS = {
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
    'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'OWN', 'SAY', 'SHE', 'TOO', 'TWO',
    'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'TOO', 'USE',
    'BERLIN', 'CLOCK', 'KRYPTOS', 'ONLY', 'SEE', 'NORTHEAST', 'ABSCISSA',
    'PALIMPSEST', 'KEY', 'DECRYPT', 'TEXT', 'WORDS', 'FOUND', 'SOLUTION',
    'MYSTERIOUS', 'MESSAGE', 'CIPHER', 'CODE', 'WORK', 'THROUGH', 'FIND',
    'BELOW', 'ABOVE', 'LAYER', 'STONE', 'GARDEN', 'COPPER', 'SCULPTURE'
}

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere cipher"""
    # Remove non-letters and convert to uppercase
    ciphertext = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    key = re.sub(r'[^A-Za-z]', '', key).upper()
    
    plaintext = []
    key_index = 0
    
    for char in ciphertext:
        if char.isalpha():
            # Get the shift value from the key
            shift = ord(key[key_index % len(key)]) - ord('A')
            # Decrypt: shift backwards
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext.append(decrypted)
            key_index += 1
        else:
            plaintext.append(char)
    
    return ''.join(plaintext)

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
        else:
            ciphertext.append(char)
    
    return ''.join(ciphertext)

def find_words_in_text(text):
    """Find common English words in the text"""
    words = re.findall(r'[A-Z]{2,}', text)
    found = []
    for word in words:
        if word in COMMON_WORDS or len(word) >= 5:
            found.append(word)
    return found

def highlight_words(text):
    """Highlight common words in text"""
    result = text
    for word in COMMON_WORDS:
        if len(word) >= 3:
            pattern = r'\b' + word + r'\b'
            # This is a simple approach - just mark found words
            if word in text:
                result = result.replace(word, f"[{word}]")
    return result

def apply_step49_transposition_reverse(text):
    """Reverse the step 49 transposition"""
    # This would need the actual transposition mapping
    # For now, just return the text as is
    return text

def check_for_phrases(text):
    """Check for important phrases"""
    phrases = [
        'BERLINCLOCK',
        'BERLIN CLOCK',
        'CLOCK',
        'BERLIN',
        'KRYPTOS',
        'PALIMPSEST',
        'ABSCISSA',
        'NORTHEAST',
    ]
    
    found = []
    text_no_space = text.replace(' ', '')
    for phrase in phrases:
        phrase_no_space = phrase.replace(' ', '')
        if phrase_no_space in text_no_space:
            found.append(phrase)
    
    return found

print("=" * 80)
print("VIGENERE DECRYPTION - DIRECTION 1: Transposed Text")
print("=" * 80)
print(f"\nStarting with Step 49 transposed result:")
print(f"{STEP49_TRANSPOSED}\n")

results_dir1 = {}

for key in KEYS:
    print(f"\n{'='*80}")
    print(f"Key: {key}")
    print(f"{'='*80}")
    
    decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key)
    results_dir1[key] = decrypted
    
    print(f"Decrypted: {decrypted}")
    
    # Find words
    words = find_words_in_text(decrypted)
    if words:
        print(f"Found words: {', '.join(set(words))}")
    
    # Check for phrases
    phrases = check_for_phrases(decrypted)
    if phrases:
        print(f"FOUND PHRASES: {', '.join(phrases)}")
    
    # Show text with highlighting
    highlighted = decrypted
    for word in COMMON_WORDS:
        if len(word) >= 3 and word in decrypted:
            highlighted = highlighted.replace(word, f"[{word}]")
    
    print(f"Highlighted: {highlighted}")

print("\n\n" + "=" * 80)
print("VIGENERE DECRYPTION - DIRECTION 2: Original K4 Ciphertext")
print("=" * 80)
print(f"\nStarting with K4 ciphertext:")
print(f"{K4_CIPHER}\n")

results_dir2 = {}

for key in KEYS:
    print(f"\n{'='*80}")
    print(f"Key: {key}")
    print(f"{'='*80}")
    
    decrypted = vigenere_decrypt(K4_CIPHER, key)
    results_dir2[key] = decrypted
    
    print(f"Decrypted: {decrypted}")
    
    # Find words
    words = find_words_in_text(decrypted)
    if words:
        print(f"Found words: {', '.join(set(words))}")
    
    # Check for phrases
    phrases = check_for_phrases(decrypted)
    if phrases:
        print(f"FOUND PHRASES: {', '.join(phrases)}")
    
    # Show text with highlighting
    highlighted = decrypted
    for word in COMMON_WORDS:
        if len(word) >= 3 and word in decrypted:
            highlighted = highlighted.replace(word, f"[{word}]")
    
    print(f"Highlighted: {highlighted}")

print("\n\n" + "=" * 80)
print("SUMMARY - MOST PROMISING RESULTS")
print("=" * 80)

print("\nDirection 1 (Transposed -> Vigenere Decrypt):")
for key, text in results_dir1.items():
    words = find_words_in_text(text)
    phrases = check_for_phrases(text)
    if words or phrases:
        print(f"\n{key}: Found {len(words)} words, {len(phrases)} phrases")
        if phrases:
            print(f"  Phrases: {phrases}")
        if words:
            print(f"  Words: {words}")

print("\n\nDirection 2 (K4 Cipher -> Vigenere Decrypt):")
for key, text in results_dir2.items():
    words = find_words_in_text(text)
    phrases = check_for_phrases(text)
    if words or phrases:
        print(f"\n{key}: Found {len(words)} words, {len(phrases)} phrases")
        if phrases:
            print(f"  Phrases: {phrases}")
        if words:
            print(f"  Words: {words}")

