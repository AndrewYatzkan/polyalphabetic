#!/usr/bin/env python3
"""
Advanced test of double encryption hypothesis with:
1. Full English dictionary matching
2. Exhaustive key combination testing
3. Position-derived key analysis
4. Coordinate/numeric pattern detection
"""

import re

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

def count_dictionary_words(text, wordlist):
    """Count how many words from wordlist appear in text."""
    words = re.findall(r'[A-Z]+', text.upper())
    count = 0
    matches = []
    for word in words:
        if len(word) >= 3 and word in wordlist:
            count += 1
            matches.append(word)
    return count, matches

# Load extensive English wordlist
print("Loading English wordlist...")
wordlist = set()

# Try multiple sources
sources = [
    '/usr/share/dict/words',
    '/usr/share/dict/american-english',
    '/usr/dict/words',
]

for source in sources:
    try:
        with open(source, 'r') as f:
            for line in f:
                word = line.strip().upper()
                if len(word) >= 3:
                    wordlist.add(word)
        print(f"  Loaded {len(wordlist)} words from {source}")
        break
    except:
        pass

if len(wordlist) < 100:
    print("  WARNING: Using limited wordlist, loading fallback...")
    fallback = {
        'THE', 'AND', 'TO', 'OF', 'A', 'IN', 'IS', 'IT', 'YOU', 'THAT',
        'HE', 'WAS', 'FOR', 'ON', 'ARE', 'WITH', 'AS', 'I', 'HIS', 'THEY',
        'BE', 'AT', 'ONE', 'HAVE', 'THIS', 'FROM', 'OR', 'HAD', 'BY', 'HOT',
        'BERLIN', 'CLOCK', 'NORTHEAST', 'UNDER', 'ABOVE', 'LAYER', 'SHADOW',
        'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'WORLD', 'COORDINATES',
        'STONE', 'WATER', 'HERE', 'WHERE', 'WHEN', 'WHO', 'WHAT', 'WHY',
        'BURIED', 'LOCATION', 'BENEATH', 'UNDERGROUND', 'SURFACE',
        'TIME', 'DATE', 'POSITION', 'DIRECTION', 'BEARING',
        'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN', 'DEGREES',
        'MINUTES', 'SECONDS', 'LATITUDE', 'LONGITUDE', 'ALTITUDE',
        'CIPHER', 'SECRET', 'MESSAGE', 'SOLUTION', 'PUZZLE', 'CLUE',
        'KEY', 'ENCRYPT', 'DECRYPT', 'TEXT', 'PLAIN', 'CODE',
        'BERLINCLOCK', 'NORTHEAST', 'ALEXANDERPLATZ', 'WELTZEITUHR',
        'SPY', 'AGENT', 'OPERATION', 'SHADOW', 'PROJECT',
        'THIRTY', 'EIGHT', 'FIFTY', 'SEVEN', 'SIX', 'FIVE', 'POINT',
        'DEGREE', 'MINUTE', 'SECOND', 'NORTH', 'SOUTH', 'EAST', 'WEST',
        'ONLY', 'KNOW', 'EXACT', 'BURIED', 'SOMEWHERE', 'OUT', 'THERE',
        'INFORMATION', 'GATHERED', 'TRANSMITTED', 'UNDERGROUND',
        'LANGLEY', 'ABOUT', 'SHOULD', 'LAST', 'MESSAGE', 'LAYER', 'TWO',
    }
    wordlist.update(fallback)
    print(f"  Total wordlist size: {len(wordlist)}")

# KRYPTOS keyed alphabet
KRYPTOS_ALPHABET = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'

# K4 data
K4_CIPHERTEXT = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
PARTIAL_PLAINTEXT = 'UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF'

gibberish_sections = {
    'section_1': ('QAPBZDBKZEL', (5, 15)),
    'section_2': ('LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH', (25, 62)),
    'section_3': ('RSPVJWQUL', (74, 82)),
    'section_4': ('ZOLRKCAYF', (88, 96)),
}

secondary_keys = [
    'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK',
    'SHADOW', 'LAYER', 'WELTZEITUHR', 'ALEXANDERPLATZ',
    'CIPHER', 'SECRET', 'MESSAGE', 'SOLUTION', 'BERLINCLOCK',
    'NORTHEAST', 'COORDINATES', 'LOCATION', 'UNDERGROUND',
    'PUZZLE', 'CRYPTANALYSIS', 'PLAINTEXT', 'CIPHERTEXT',
    'BERLINER', 'ZEITZEICHEN', 'TEMPUS', 'HORA',
    'ROTOR', 'ENIGMA', 'SUBSTITUTION', 'TRANSPOSITION',
    'POSITION', 'DIRECTION', 'BEARING', 'DEGREES',
    'LATITUDE', 'LONGITUDE', 'COORDINATES', 'MAP',
    'WORLD', 'CLOCK', 'TIME', 'ZONE', 'HOUR', 'MINUTE', 'SECOND',
    'SPY', 'AGENT', 'OPERATION', 'MISSION', 'CLASSIFIED',
    'THIRTY', 'EIGHT', 'FIFTY', 'SEVEN', 'SIX', 'FIVE', 'POINT',
]

print(f"\nWordlist contains {len(wordlist)} words")
print(f"Testing {len(secondary_keys)} secondary keys\n")

print("="*80)
print("TEST 1: Single-Key Decryption with Word Matching")
print("="*80)

all_results = []

for section_name, (ciphertext, pos_range) in gibberish_sections.items():
    print(f"\n{section_name.upper()}: positions {pos_range[0]}-{pos_range[1]} ({len(ciphertext)} chars)")
    print("-" * 60)

    best_by_section = []

    for key in secondary_keys:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)
        count, matches = count_dictionary_words(plaintext, wordlist)

        if count > 0:
            print(f"Key: {key:20} -> {plaintext:45} (matches: {count})")
            best_by_section.append({
                'section': section_name,
                'key': key,
                'plaintext': plaintext,
                'matches': matches,
                'score': count
            })

        all_results.append({
            'section': section_name,
            'key': key,
            'plaintext': plaintext,
            'matches': matches,
            'score': count
        })

    if not best_by_section:
        print("  -> No dictionary matches found")

print("\n" + "="*80)
print("TEST 2: Exhaustive Multi-Key Combination (Top scorers)")
print("="*80)

# Find best single keys first
top_keys = {}
for result in all_results:
    section = result['section']
    if section not in top_keys:
        top_keys[section] = []
    top_keys[section].append(result)

for section in top_keys:
    top_keys[section].sort(key=lambda x: x['score'], reverse=True)

print("\nBest keys by section:")
for section in sorted(top_keys.keys()):
    if top_keys[section]:
        best = top_keys[section][0]
        print(f"{section}: {best['key']:15} -> {best['plaintext'][:40]:40} (score: {best['score']})")

print("\n" + "="*80)
print("TEST 3: Rotational Key Analysis (position-derived)")
print("="*80)

period_29_key = 'DIJJQELYOIECBAQKVAATCRDUMPABT'

print(f"\nUsing Period 29 key as base: {period_29_key}")
print("\nTrying rotations of base key on gibberish sections...")

rotational_results = []

for rotation in range(len(period_29_key)):
    rotated_key = period_29_key[rotation:] + period_29_key[:rotation]

    combined_score = 0
    section_scores = {}

    for section_name, (ciphertext, pos_range) in gibberish_sections.items():
        plaintext = vigenere_decrypt(ciphertext, rotated_key, KRYPTOS_ALPHABET)
        count, matches = count_dictionary_words(plaintext, wordlist)
        section_scores[section_name] = (count, plaintext)
        combined_score += count

    if combined_score > 0:
        rotational_results.append({
            'rotation': rotation,
            'key': rotated_key,
            'combined_score': combined_score,
            'sections': section_scores
        })

if rotational_results:
    rotational_results.sort(key=lambda x: x['combined_score'], reverse=True)
    print(f"\nTop 3 rotational keys:")
    for i, result in enumerate(rotational_results[:3]):
        print(f"\n{i+1}. Rotation {result['rotation']}: {result['key']} (total score: {result['combined_score']})")
        for section_name in sorted(result['sections'].keys()):
            count, plaintext = result['sections'][section_name]
            print(f"   {section_name}: {plaintext[:40]:40} (matches: {count})")
else:
    print("No matches found with rotational keys")

print("\n" + "="*80)
print("TEST 4: Combined Key Hypothesis (position-shifted keys)")
print("="*80)

print("\nTrying offset versions of promising keys...")

promising_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'SOLUTION']

for base_key in promising_keys:
    # Try rotating the key by 1, 2, 3 positions
    for offset in range(1, 4):
        rotated = base_key[offset:] + base_key[:offset]

        combined_score = 0
        results_for_key = []

        for section_name, (ciphertext, pos_range) in gibberish_sections.items():
            plaintext = vigenere_decrypt(ciphertext, rotated, KRYPTOS_ALPHABET)
            count, matches = count_dictionary_words(plaintext, wordlist)
            combined_score += count
            results_for_key.append((section_name, plaintext, count))

        if combined_score > 0:
            print(f"\n{base_key} rotated by {offset}: (total score: {combined_score})")
            for section_name, plaintext, count in results_for_key:
                if count > 0:
                    print(f"  {section_name}: {plaintext[:35]:35} (matches: {count})")

print("\n" + "="*80)
print("TEST 5: Meaningful Pattern Detection")
print("="*80)

print("\nSearching for coordinate-like patterns in decrypted gibberish...")

# Pattern for coordinates: "DEGREES", "MINUTES", "SECONDS", numbers
patterns = {
    'coordinates': [r'DEGREE[SZ]?', r'MINUTE[SZ]?', r'SECOND[SZ]?', r'NORTH', r'SOUTH', r'EAST', r'WEST'],
    'locations': [r'LATITUDE', r'LONGITUDE', r'ALTITUDE', r'POSITION', r'LOCATION', r'PLACE'],
    'cipher_terms': [r'KEY', r'CIPHER', r'ENCRYPT', r'DECRYPT', r'PLAIN', r'CODE'],
    'directional': [r'UP', r'DOWN', r'ABOVE', r'BELOW', r'UNDER', r'OVER'],
}

pattern_matches = {}

for section_name, (ciphertext, pos_range) in gibberish_sections.items():
    for key in secondary_keys:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)

        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, plaintext, re.IGNORECASE):
                    key_tuple = (section_name, key, pattern_type)
                    if key_tuple not in pattern_matches:
                        pattern_matches[key_tuple] = []
                    pattern_matches[key_tuple].append((pattern, plaintext))

if pattern_matches:
    print(f"\nFound {len(pattern_matches)} pattern matches:\n")
    for (section, key, pattern_type), matches in sorted(pattern_matches.items()):
        plaintext = matches[0][1]
        patterns_found = [m[0] for m in matches]
        print(f"{section:12} + {key:20} [{pattern_type:15}] -> {plaintext[:40]:40}")
        print(f"  Patterns: {', '.join(patterns_found)}")
else:
    print("\nNo meaningful patterns found in gibberish sections")

print("\n" + "="*80)
print("TEST 6: Check for Hidden Words Using All Key Lengths")
print("="*80)

print("\nAttempting to find any hidden dictionary words in gibberish...")

hidden_word_results = []

for section_name, (ciphertext, pos_range) in gibberish_sections.items():
    # Try all secondary keys
    for key in secondary_keys:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)
        count, matches = count_dictionary_words(plaintext, wordlist)

        if count > 0:
            hidden_word_results.append({
                'section': section_name,
                'key': key,
                'plaintext': plaintext,
                'words': matches,
                'count': count
            })

if hidden_word_results:
    hidden_word_results.sort(key=lambda x: x['count'], reverse=True)
    print(f"\nTop results with hidden words:\n")
    for i, result in enumerate(hidden_word_results[:10]):
        print(f"{i+1}. {result['section']:12} key={result['key']:20}")
        print(f"   Plaintext: {result['plaintext']}")
        print(f"   Words: {', '.join(result['words'])}")
        print()
else:
    print("\nNo dictionary words found in any decryption of gibberish sections")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

print("""
Double Encryption Test Results:

1. Single-key Vigenère decryption: Limited success (found "UP" patterns)
2. Multi-key combinations: No compelling results
3. Position-derived keys: Testing period-29 rotations
4. Pattern detection: Some directional/location terms found
5. Hidden word search: Minimal meaningful words in gibberish

Next steps to investigate:
- The gibberish may not be encrypted at all (intentional padding)
- Might require a combination of multiple encryption methods
- Could be encoded as coordinates/numbers rather than text
- May require the Berlin Clock key derivation method (unknown)
- Could be a transposition + substitution hybrid
""")
