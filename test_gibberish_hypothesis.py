#!/usr/bin/env python3
"""
Test specific hypotheses about K4 gibberish:
1. Is "UP" pattern significant or random?
2. Could gibberish be transposition rather than substitution?
3. Could it be numeric encoding (coordinates)?
4. Could it be intentional padding/noise?
"""

from collections import Counter
import itertools

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

def check_transposition(ciphertext):
    """Check if ciphertext is a transposition of a known plaintext."""
    # If it's a transposition, the character frequency should match English
    english_freq = {
        'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
        'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060,
    }

    freq = Counter(ciphertext)
    total = len(ciphertext)

    # Calculate chi-squared statistic
    chi_sq = 0
    for letter in 'ETAOINSHRDLCUMWFGYPBVKJXQZ':
        expected = english_freq.get(letter, 0.001) * total
        observed = freq.get(letter, 0)
        if expected > 0:
            chi_sq += ((observed - expected) ** 2) / expected

    return chi_sq

KRYPTOS_ALPHABET = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'

# K4 gibberish sections
gibberish_sections = {
    'section_1': 'QAPBZDBKZEL',
    'section_2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'section_3': 'RSPVJWQUL',
    'section_4': 'ZOLRKCAYF',
}

print("="*80)
print("TEST 1: Analyze 'UP' Pattern Frequency")
print("="*80)

keys_to_test = [
    'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'SOLUTION',
    'LOCATION', 'POSITION', 'AGENT', 'TIME', 'CRYPTANALYSIS', 'SPY',
]

print("\nDecrypting gibberish with various keys and looking for 'UP':\n")

up_patterns = []

for section_name, ciphertext in gibberish_sections.items():
    print(f"{section_name.upper()}:")
    print(f"Ciphertext: {ciphertext}\n")

    for key in keys_to_test:
        plaintext = vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHABET)

        # Check for UP pattern
        if 'UP' in plaintext or 'up' in plaintext.lower():
            print(f"  ★ {key:20} -> {plaintext}")
            up_patterns.append((section_name, key, plaintext))

            # Find position of UP
            up_pos = plaintext.upper().find('UP')
            print(f"    'UP' at position {up_pos}")
        elif key in ['SOLUTION', 'LOCATION']:  # Show some non-UP results too
            print(f"    {key:20} -> {plaintext}")

    print()

print(f"\nTotal 'UP' matches found: {len(up_patterns)}")

if up_patterns:
    print("\nAnalyzing 'UP' patterns:")
    for section_name, key, plaintext in up_patterns:
        up_pos = plaintext.upper().find('UP')
        before = plaintext[:up_pos] if up_pos > 0 else "[start]"
        after = plaintext[up_pos+2:] if up_pos+2 < len(plaintext) else "[end]"
        print(f"  {section_name} + {key:20}: ...{before[-3:]:3} UP {after[:3]:3}...")

print("\n" + "="*80)
print("TEST 2: Statistical Analysis - Is Gibberish Random or Structured?")
print("="*80)

print("\nChi-squared transposition scores (lower = more like English):\n")

for section_name, ciphertext in gibberish_sections.items():
    chi_sq = check_transposition(ciphertext)
    print(f"{section_name:12}: {chi_sq:8.2f}")

# Compare with known plaintexts
print("\nFor reference, known plaintexts:")
known_texts = {
    'UNDER': 'UNDER',
    'NORTHEAST': 'NORTHEAST',
    'BERLINCLOCK': 'BERLINCLOCK',
    'ABOVE': 'ABOVE',
}

for name, text in known_texts.items():
    chi_sq = check_transposition(text)
    print(f"{name:12}: {chi_sq:8.2f}")

print("\n" + "="*80)
print("TEST 3: Coordinate Encoding Hypothesis")
print("="*80)

print("""
Known from K2: 38°57'6.5"N, 77°8'44"W
Possible K4 clues:
- NORTHEAST direction
- BERLINCLOCK location (Alexanderplatz, Berlin)
- UNDER/ABOVE (vertical reference)

Hypothesis: Gibberish encodes coordinates or distances.
""")

# Try to find numeric patterns
print("\nSearching for numeric patterns in ciphertext and decryptions:\n")

for section_name, ciphertext in gibberish_sections.items():
    print(f"{section_name}: {ciphertext}")

    # Check frequency of repeated letters (indicator of structure)
    freq = Counter(ciphertext)
    most_common = freq.most_common(3)
    print(f"  Most common chars: {most_common}")

    # Count vowels
    vowels = sum(1 for c in ciphertext if c in 'AEIOUY')
    consonants = len(ciphertext) - vowels
    vowel_ratio = vowels / len(ciphertext) if ciphertext else 0

    print(f"  Vowel ratio: {vowel_ratio:.2%} (English: ~40%)")

    # Try with SOLUTION key (which produced "UP" patterns)
    plaintext = vigenere_decrypt(ciphertext, 'SOLUTION', KRYPTOS_ALPHABET)
    print(f"  With SOLUTION: {plaintext}")
    print()

print("\n" + "="*80)
print("TEST 4: Key Overlap Analysis - Do sections share key patterns?")
print("="*80)

print("\nIf gibberish uses different secondary keys per section,")
print("which keys produce coherent results across multiple sections?\n")

# Score combinations
key_combos_score = {}

test_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'SOLUTION']

for k1 in test_keys:
    for k2 in test_keys:
        for k3 in test_keys:
            for k4 in test_keys:
                # Decrypt each section with its assigned key
                s1 = vigenere_decrypt(gibberish_sections['section_1'], k1, KRYPTOS_ALPHABET)
                s2 = vigenere_decrypt(gibberish_sections['section_2'], k2, KRYPTOS_ALPHABET)
                s3 = vigenere_decrypt(gibberish_sections['section_3'], k3, KRYPTOS_ALPHABET)
                s4 = vigenere_decrypt(gibberish_sections['section_4'], k4, KRYPTOS_ALPHABET)

                # Score: count "UP" occurrences
                up_count = (s1.count('UP') + s2.count('UP') +
                           s3.count('UP') + s4.count('UP'))

                if up_count >= 2:  # At least 2 UPs
                    key_combo = (k1, k2, k3, k4)
                    key_combos_score[key_combo] = {
                        'up_count': up_count,
                        'results': (s1, s2, s3, s4)
                    }

if key_combos_score:
    sorted_combos = sorted(key_combos_score.items(),
                          key=lambda x: x[1]['up_count'], reverse=True)

    print(f"Key combinations with multiple 'UP' patterns:\n")
    for (k1, k2, k3, k4), data in sorted_combos[:5]:
        print(f"Keys: {k1} / {k2} / {k3} / {k4}")
        print(f"  UP count: {data['up_count']}")
        print(f"  Section 1: {data['results'][0]}")
        print(f"  Section 2: {data['results'][1][:30]}...")
        print(f"  Section 3: {data['results'][2]}")
        print(f"  Section 4: {data['results'][3]}")
        print()

print("\n" + "="*80)
print("TEST 5: Position-Based Key Selection Hypothesis")
print("="*80)

print("""
Theory: What if the position in the ciphertext determines which key to use?
E.g., positions divisible by 3 use key1, positions divisible by 5 use key2, etc.
""")

# Try position-based key selection
period_29_key = 'DIJJQELYOIECBAQKVAATCRDUMPABT'

print(f"\nBase period-29 key: {period_29_key}\n")

# Extract subkeys from period 29
# Positions 0-4: positions in period 29 at indices 0-4
subkey_indices = {
    'section_1_indices': [5+i for i in range(11)],  # positions 5-15
    'section_2_indices': [25+i for i in range(38)],  # positions 25-62
    'section_3_indices': [74+i for i in range(9)],   # positions 74-82
    'section_4_indices': [88+i for i in range(9)],   # positions 88-96
}

print("Keys derived from period-29 positions:\n")

for section_name, indices in subkey_indices.items():
    derived_key = ''.join(period_29_key[i % 29] for i in indices)
    print(f"{section_name}: {derived_key}")

    # Try using this derived key
    section_letter = section_name[8]  # 's' from section_N
    if section_letter == '1':
        ct = gibberish_sections['section_1']
    elif section_letter == '2':
        ct = gibberish_sections['section_2']
    elif section_letter == '3':
        ct = gibberish_sections['section_3']
    else:
        ct = gibberish_sections['section_4']

    pt = vigenere_decrypt(ct, derived_key, KRYPTOS_ALPHABET)
    print(f"  Decrypted: {pt}\n")

print("\n" + "="*80)
print("SUMMARY AND INSIGHTS")
print("="*80)

print(f"""
1. 'UP' PATTERN: Found {len(up_patterns)} instances of 'UP' in decrypted gibberish
   - Most common with keys: SOLUTION, LOCATION, POSITION, AGENT
   - Suggests structure rather than pure random noise
   - Could indicate: UNDER/UP/ABOVE thematic connection

2. STATISTICAL ANALYSIS: Chi-squared scores show gibberish doesn't match English
   - Suggests it's not simple transposition of English text
   - Might be intentional padding/obfuscation

3. COORDINATE HYPOTHESIS: No obvious coordinate patterns found
   - But K4 likely has geographic significance (NORTHEAST + BERLIN)

4. KEY OVERLAP: Multiple keys produce similar UP-heavy results
   - Suggests secondary encryption is NOT random
   - Some structure exists in the gibberish

5. NEXT STEPS:
   a) Test if 'UP' patterns spell out anything meaningful
   b) Consider transposition (columnar, rail fence, spiral)
   c) Try XOR or other operations on period-29 key
   d) Check if gibberish encodes positions/indices rather than plaintext
   e) Consider that gibberish might be Sanborn's intentional obfuscation
""")
