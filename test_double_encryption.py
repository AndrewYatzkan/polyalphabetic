#!/usr/bin/env python3
"""
Test if K4 uses double encryption (Vigenere applied twice).
Hypothesis: The gibberish sections are encrypted with a secondary key.
"""

def vigenere_decrypt(ciphertext, key, keyed_alphabet=None):
    """Decrypt Vigenère cipher."""
    if keyed_alphabet is None:
        keyed_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    plaintext = []
    key = key.upper()
    ciphertext = ciphertext.upper()

    key_idx = 0
    for char in ciphertext:
        if char not in keyed_alphabet:
            plaintext.append(char)
            continue

        ct_pos = keyed_alphabet.index(char)
        key_char = key[key_idx % len(key)]
        key_pos = keyed_alphabet.index(key_char)

        pt_pos = (ct_pos - key_pos) % len(keyed_alphabet)
        plaintext.append(keyed_alphabet[pt_pos])

        key_idx += 1

    return ''.join(plaintext)

def vigenere_encrypt(plaintext, key, keyed_alphabet=None):
    """Encrypt with Vigenère cipher."""
    if keyed_alphabet is None:
        keyed_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    ciphertext = []
    key = key.upper()
    plaintext = plaintext.upper()

    key_idx = 0
    for char in plaintext:
        if char not in keyed_alphabet:
            ciphertext.append(char)
            continue

        pt_pos = keyed_alphabet.index(char)
        key_char = key[key_idx % len(key)]
        key_pos = keyed_alphabet.index(key_char)

        ct_pos = (pt_pos + key_pos) % len(keyed_alphabet)
        ciphertext.append(keyed_alphabet[ct_pos])

        key_idx += 1

    return ''.join(ciphertext)

def is_english_word(word, wordlist):
    """Check if word is in English wordlist."""
    return word.upper() in wordlist

def score_text(text, wordlist):
    """Score text based on English word frequency."""
    words = text.split()
    score = 0
    for word in words:
        # Remove non-alphabetic characters
        clean_word = ''.join(c for c in word if c.isalpha()).upper()
        if clean_word in wordlist:
            score += 1
    return score

# Load English wordlist
print("Loading English wordlist...")
wordlist = set()
try:
    with open('/usr/share/dict/words', 'r') as f:
        wordlist = {line.strip().upper() for line in f}
except:
    # Fallback wordlist
    wordlist = {
        'THE', 'AND', 'TO', 'OF', 'A', 'IN', 'IS', 'IT', 'YOU', 'THAT',
        'HE', 'WAS', 'FOR', 'ON', 'ARE', 'WITH', 'AS', 'I', 'HIS', 'THEY',
        'BE', 'AT', 'ONE', 'HAVE', 'THIS', 'FROM', 'OR', 'HAD', 'BY', 'HOT',
        'BERLIN', 'CLOCK', 'NORTHEAST', 'UNDER', 'ABOVE', 'LAYER', 'SHADOW',
        'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'WORLD', 'COORDINATES',
        'STONE', 'WATER', 'HERE', 'WHERE', 'WHEN', 'WHO', 'WHAT', 'WHY',
        'BURIED', 'LOCATION', 'BENEATH', 'UNDERGROUND', 'SURFACE',
        'TIME', 'DATE', 'POSITION', 'DIRECTION', 'BEARING',
        'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN',
    }

# KRYPTOS keyed alphabet (from K1-K3)
KRYPTOS_ALPHABET = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'

# K4 data
K4_CIPHERTEXT = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'

# Partial plaintext from Period 29 key
PARTIAL_PLAINTEXT = 'UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF'

# Gibberish sections (the "double encryption" candidates)
gibberish_sections = {
    'section_1': {
        'text': 'QAPBZDBKZEL',
        'position': (5, 15),
        'description': 'Between UNDER and NORTHEAST'
    },
    'section_2': {
        'text': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
        'position': (25, 62),
        'description': 'Between NORTHEAST and BERLINCLOCK'
    },
    'section_3': {
        'text': 'RSPVJWQUL',
        'position': (74, 82),
        'description': 'Between BERLINCLOCK and ABOVE'
    },
    'section_4': {
        'text': 'ZOLRKCAYF',
        'position': (88, 96),
        'description': 'After ABOVE'
    }
}

# Secondary keys to try
secondary_keys = [
    'KRYPTOS',
    'PALIMPSEST',
    'ABSCISSA',
    'BERLIN',
    'CLOCK',
    'SHADOW',
    'LAYER',
    'WELTZEITUHR',
    'ALEXANDERPLATZ',
    'CIPHER',
    'SECRET',
    'MESSAGE',
    'SOLUTION',
    'BERLINCLOCK',
    'NORTHEAST',
    'COORDINATES',
    'LOCATION',
    'UNDERGROUND',
]

print("\n" + "="*80)
print("TEST 1: Attempt Vigenère Decryption on Gibberish Sections")
print("="*80)

for section_name, section_data in gibberish_sections.items():
    ciphertext = section_data['text']
    description = section_data['description']

    print(f"\n{section_name.upper()}: {description}")
    print(f"Ciphertext: {ciphertext}")
    print("-" * 60)

    best_score = 0
    best_results = []

    for key in secondary_keys:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)
        score = score_text(plaintext, wordlist)

        if score > 0:
            print(f"Key: {key:20} -> {plaintext} (score: {score})")
            if score >= best_score:
                best_score = score
                best_results.append((key, plaintext, score))

print("\n" + "="*80)
print("TEST 2: Try Double Encryption Recovery - Different Key per Section")
print("="*80)

# Maybe different keys for different sections?
print("\nTrying all key combinations for sections...")

key_pair_results = []

for key1 in secondary_keys[:5]:  # Limit combinations for performance
    for key2 in secondary_keys[:5]:
        for key3 in secondary_keys[:5]:
            for key4 in secondary_keys[:5]:
                decrypted = []
                decrypted.append(vigenere_decrypt(gibberish_sections['section_1']['text'], key1, KRYPTOS_ALPHABET))
                decrypted.append(vigenere_decrypt(gibberish_sections['section_2']['text'], key2, KRYPTOS_ALPHABET))
                decrypted.append(vigenere_decrypt(gibberish_sections['section_3']['text'], key3, KRYPTOS_ALPHABET))
                decrypted.append(vigenere_decrypt(gibberish_sections['section_4']['text'], key4, KRYPTOS_ALPHABET))

                full_text = ''.join(decrypted)
                score = score_text(full_text, wordlist)

                if score > 1:
                    key_pair_results.append({
                        'keys': (key1, key2, key3, key4),
                        'score': score,
                        'text': full_text
                    })

if key_pair_results:
    key_pair_results.sort(key=lambda x: x['score'], reverse=True)
    print(f"\nTop 5 results from key combination search:")
    for i, result in enumerate(key_pair_results[:5]):
        print(f"\n{i+1}. Score: {result['score']}")
        print(f"   Keys: {result['keys']}")
        print(f"   Text: {result['text']}")
else:
    print("No strong results from key combination search")

print("\n" + "="*80)
print("TEST 3: Position-Specific Analysis")
print("="*80)

# What if only certain positions in the ciphertext have second encryption?
# Let's check if the plaintext has patterns

plaintext = PARTIAL_PLAINTEXT
ciphertext = K4_CIPHERTEXT

print("\nAnalyzing position-by-position alignment:")
print("Pos | CT  | PT  | (PT in wordlist)")
print("-" * 40)

readable_words = ['UNDER', 'NORTHEAST', 'BERLINCLOCK', 'ABOVE']

for i, (ct_char, pt_char) in enumerate(zip(ciphertext, plaintext)):
    # Check if this position is part of a readable word
    in_word = False
    word_info = ""

    pos = 0
    for word in readable_words:
        if i >= pos and i < pos + len(word):
            in_word = True
            word_info = f"in {word} at offset {i-pos}"
            break
        pos += len(word) + 1

    if i < 20 or in_word:  # Show first 20 and all readable positions
        print(f"{i:3} | {ct_char} | {pt_char} | {word_info}")

print("\n" + "="*80)
print("TEST 4: Try Period-Adjusted Keys (Position-Specific)")
print("="*80)

# Extract period 29 key from BERLINCLOCK
period_29_key = 'DIJJQELYOIECBAQKVAATCRDUMPABT'

print(f"\nPeriod 29 key: {period_29_key}")
print("\nKey distribution for positions 5-15 (section 1):")

section_1_positions = range(5, 16)
for pos in section_1_positions:
    key_char = period_29_key[pos % len(period_29_key)]
    ct_char = K4_CIPHERTEXT[pos]
    pt_char = PARTIAL_PLAINTEXT[pos]
    print(f"  Pos {pos}: key={key_char} ct={ct_char} pt={pt_char}")

print("\nKey distribution for positions 25-62 (section 2):")
for pos in range(25, 63, 4):  # Sample every 4th position
    key_char = period_29_key[pos % len(period_29_key)]
    ct_char = K4_CIPHERTEXT[pos]
    pt_char = PARTIAL_PLAINTEXT[pos]
    print(f"  Pos {pos}: key={key_char} ct={ct_char} pt={pt_char}")

print("\n" + "="*80)
print("TEST 5: Check if Gibberish Decrypts to Known Sequences")
print("="*80)

# What if the gibberish encodes coordinates, dates, or other patterns?
print("\nSearching for numeric patterns and common sequences in decrypted text...")

numeric_patterns = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'ZERO']
directional_patterns = ['NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN']
temporal_patterns = ['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'TIME', 'DATE']

found_patterns = []

for section_name, section_data in gibberish_sections.items():
    ciphertext = section_data['text']
    for key in secondary_keys:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)

        for pattern_set, pattern_type in [
            (numeric_patterns, 'numeric'),
            (directional_patterns, 'directional'),
            (temporal_patterns, 'temporal')
        ]:
            for pattern in pattern_set:
                if pattern in plaintext:
                    found_patterns.append({
                        'section': section_name,
                        'key': key,
                        'pattern_type': pattern_type,
                        'pattern': pattern,
                        'plaintext': plaintext
                    })
                    print(f"\n{section_name} + {key}: Found {pattern_type} pattern '{pattern}'")
                    print(f"  Full: {plaintext}")

if not found_patterns:
    print("\nNo obvious numeric/directional/temporal patterns found in gibberish")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("""
Test Results:
1. Single-key Vigenère decryption on gibberish sections
2. Multi-key combination search
3. Position-specific key analysis
4. Pattern matching in decrypted text

Hypothesis Status: Testing whether K4 uses double encryption...
""")
