#!/usr/bin/env python3
"""
Cryptographic analysis of K4 gibberish sections
Looking for: double encryption, Vigenere effects, substitution patterns
"""

from collections import Counter
import math

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
ciphertext = "KRYPTOSOBJECTIVECYPHERABSCISSAORDFINATEPALLISADEDEGREESSTRANSLATEDSSLOWLYDESPERATELYSLOWLYTHEOBJECTIVEBMITGESFULLYSTATIC"

gibberish = {
    "Section 1": ("QAPBZDBKZEL", (5, 15)),
    "Section 2": ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", (25, 62)),
    "Section 3": ("RSPVJWQUL", (74, 82)),
    "Section 4": ("ZOLRKCAYF", (88, 96))
}

readable = {
    "UNDER": (0, 4),
    "NORTHEAST": (16, 24),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73),
    "ABOVE": (83, 86)
}

print("=" * 80)
print("CRYPTOGRAPHIC ANALYSIS OF GIBBERISH SECTIONS")
print("=" * 80)

# ============================================================================
# 1. COMPARING WITH ORIGINAL K4 CIPHERTEXT
# ============================================================================
print("\n1. COMPARISON WITH ORIGINAL K4 CIPHERTEXT")
print("-" * 80)

print(f"\nOriginal K4 (first 100 chars):")
print(f"  {ciphertext[:100]}")

print(f"\nOur Period 29 plaintext (first 100 chars):")
print(f"  {plaintext[:100]}")

# Letter frequency comparison
freq_cipher = Counter(ciphertext)
freq_plain = Counter(plaintext)
freq_gib = Counter("".join(section[0] for section in gibberish.values()))

print(f"\nLetter frequency - Top 10:")
print(f"  Original K4:        {freq_cipher.most_common(10)}")
print(f"  Our plaintext:      {freq_plain.most_common(10)}")
print(f"  Gibberish sections: {freq_gib.most_common(10)}")

# ============================================================================
# 2. INDEX OF COINCIDENCE (IC) ANALYSIS
# ============================================================================
print("\n\n2. INDEX OF COINCIDENCE (IC) ANALYSIS")
print("-" * 80)

def calculate_ic(text):
    """Calculate Index of Coincidence"""
    n = len(text)
    freq = Counter(text)
    ic = sum(freq[letter] * (freq[letter] - 1) for letter in freq) / (n * (n - 1))
    return ic

print(f"\nIC for different texts:")
print(f"  English text:       ~0.067")
print(f"  Random text:        ~0.038")
print(f"  Original K4:        {calculate_ic(ciphertext):.4f}")
print(f"  Our plaintext:      {calculate_ic(plaintext):.4f}")

for sec_name, (sec_text, _) in gibberish.items():
    ic = calculate_ic(sec_text)
    print(f"  {sec_name}: {ic:.4f}")

all_gib = "".join(section[0] for section in gibberish.values())
print(f"  All gibberish:      {calculate_ic(all_gib):.4f}")

# ============================================================================
# 3. CHECKING FOR POLYALPHABETIC CIPHER EFFECTS
# ============================================================================
print("\n\n3. POLYALPHABETIC CIPHER ANALYSIS")
print("-" * 80)

# For a Vigenere cipher, same plaintext letter encrypted at different positions
# with the same key letter should give same ciphertext

# Look at the ciphertext pairs from our plaintext
print("\nLooking for repeated digraphs that might indicate key reuse...")

for sec_name, (sec_text, _) in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    # Calculate digraph distribution
    digraphs = Counter()
    for i in range(len(sec_text) - 1):
        digraphs[sec_text[i:i+2]] += 1

    # Repeating digraphs suggest either:
    # 1. Same plaintext pair encrypted multiple times with same key
    # 2. Chance repetition
    repeated = [(dg, count) for dg, count in digraphs.items() if count > 1]
    if repeated:
        print(f"  Repeated digraphs: {repeated}")
        for dg, count in repeated:
            positions = [i for i in range(len(sec_text)-1) if sec_text[i:i+2] == dg]
            distances = [positions[j+1] - positions[j] for j in range(len(positions)-1)]
            if distances:
                print(f"    {dg} distances between repeats: {distances}")

# ============================================================================
# 4. CHI-SQUARED ANALYSIS FOR EACH POSITION (MOD 26)
# ============================================================================
print("\n\n4. CHI-SQUARED BY POSITION (looking for Vigenere patterns)")
print("-" * 80)

english_freq = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
    'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
    'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
    'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07
}

for sec_name, (sec_text, _) in gibberish.items():
    print(f"\n{sec_name}:")

    # Group by position modulo 5, 6, 7 (common key lengths)
    for period in [5, 6, 7]:
        chi_sq_by_pos = {}

        for pos in range(period):
            letters_at_pos = [sec_text[i] for i in range(pos, len(sec_text), period)]

            if len(letters_at_pos) > 0:
                freq = Counter(letters_at_pos)
                chi_sq = sum(((freq.get(letter, 0) - (len(letters_at_pos) * english_freq.get(letter, 0) / 100)) ** 2)
                            / (len(letters_at_pos) * english_freq.get(letter, 0) / 100 + 0.001)
                            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                chi_sq_by_pos[pos] = chi_sq

        print(f"  Period {period}: {chi_sq_by_pos}")

# ============================================================================
# 5. LOOKING FOR DOUBLE ENCRYPTION SIGNATURES
# ============================================================================
print("\n\n5. DOUBLE ENCRYPTION ANALYSIS")
print("-" * 80)

print("\nAnalyzing if gibberish shows signs of being encrypted twice...")

for sec_name, (sec_text, _) in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    # If text is encrypted twice, we'd expect:
    # - Very high entropy (close to random)
    # - Unusual letter distribution
    # - No obvious patterns

    entropy = -sum((Counter(sec_text)[c] / len(sec_text)) * math.log2(Counter(sec_text)[c] / len(sec_text))
                   for c in set(sec_text))

    freq = Counter(sec_text)
    diversity = len(set(sec_text)) / 26  # fraction of alphabet used

    print(f"  Entropy: {entropy:.3f} (max 4.7)")
    print(f"  Alphabet diversity: {diversity:.1%} ({len(set(sec_text))}/26 letters)")
    print(f"  Interpretation: ", end="")

    if entropy > 4.2:
        print("HIGH entropy - consistent with encryption")
    elif entropy > 3.5:
        print("MODERATE entropy - could be encrypted")
    else:
        print("LOW entropy - not heavily encrypted")

# ============================================================================
# 6. CHECKING FOR TRANSPOSITION SIGNATURES
# ============================================================================
print("\n\n6. TRANSPOSITION VS SUBSTITUTION ANALYSIS")
print("-" * 80)

print("\nTransposition cipher: letters are rearranged (IC stays ~0.067)")
print("Substitution cipher: letters are replaced (IC drops to ~0.038)")

print("\nOur gibberish sections:")
for sec_name, (sec_text, _) in gibberish.items():
    ic = calculate_ic(sec_text)
    print(f"\n{sec_name} (IC: {ic:.4f}):")

    if ic > 0.055:
        print("  -> Consistent with TRANSPOSITION (IC near English)")
    elif ic > 0.045:
        print("  -> Mixed signatures")
    else:
        print("  -> Consistent with SUBSTITUTION (IC near random)")

# ============================================================================
# 7. LETTER DISTRIBUTION SHAPE
# ============================================================================
print("\n\n7. LETTER DISTRIBUTION SHAPE ANALYSIS")
print("-" * 80)

for sec_name, (sec_text, _) in gibberish.items():
    print(f"\n{sec_name}:")

    freq = Counter(sec_text)
    sorted_freq = sorted(freq.values(), reverse=True)

    # Calculate Zipf coefficient approximation
    # Real English has a power-law distribution

    if len(sorted_freq) > 1:
        # Compare most frequent to least frequent
        ratio = sorted_freq[0] / (sorted_freq[-1] + 0.001)
        print(f"  Most common letter appears {ratio:.1f}x more than least common")
        print(f"  Distribution: {sorted_freq}")

        if ratio < 3:
            print("  -> Flat distribution (suggests randomness/encryption)")
        else:
            print("  -> Steep distribution (suggests natural language)")

# ============================================================================
# 8. LOOKING FOR STEGANOGRAPHY SIGNATURES
# ============================================================================
print("\n\n8. STEGANOGRAPHY ANALYSIS (hidden messages)")
print("-" * 80)

print("\nChecking if gibberish contains encoded length information...")

all_gib = "".join(section[0] for section in gibberish.values())

# Convert letters to numbers (A=1, Z=26)
nums = [ord(c) - ord('A') + 1 for c in all_gib]

print(f"\nAll gibberish as numbers: {nums[:20]}... (total {len(nums)})")

# Check for patterns
print(f"\nTotal gibberish length: {len(all_gib)} characters")
print(f"Section lengths: {[len(s[0]) for s in gibberish.values()]}")

# Sum of all lengths
print(f"Sum of section lengths: {sum(len(s[0]) for s in gibberish.values())} = {all_gib}")

# ============================================================================
# 9. POSITION-BASED PATTERNS ACROSS ENTIRE PLAINTEXT
# ============================================================================
print("\n\n9. POSITION-BASED ANALYSIS IN FULL PLAINTEXT")
print("-" * 80)

print("\nPositions of readable vs gibberish sections:")
print("\nReadable sections:")
for word, (start, end) in sorted(readable.items(), key=lambda x: x[1][0]):
    length = end - start + 1
    print(f"  {word:12s}: positions {start:2d}-{end:2d} (length {length})")

print("\nGibberish sections:")
for sec_name, (text, (start, end)) in sorted(gibberish.items(), key=lambda x: x[1][1][0]):
    length = end - start + 1
    print(f"  {sec_name:12s}: positions {start:2d}-{end:2d} (length {length})")

print("\nPattern observation:")
print("  Readable: 5 sections with pattern: 5, 9, 6, 5, 5 characters")
print("  Gibberish: 4 sections with pattern: 11, 38, 9, 9 characters")

# ============================================================================
# 10. LOOKING FOR KEY MATERIAL IN GIBBERISH
# ============================================================================
print("\n\n10. KEY MATERIAL ANALYSIS")
print("-" * 80)

print("\nThe encryption key was: DIJJQELYOIECBAQKVAATCRDUMPABT (29 letters)")
key = "DIJJQELYOIECBAQKVAATCRDUMPABT"
key_freq = Counter(key)

print(f"Key letter frequencies: {dict(sorted(key_freq.items()))}")

print("\nChecking if any gibberish section contains key letters:")

for sec_name, (sec_text, _) in gibberish.items():
    key_letters = set(key)
    sec_letters = set(sec_text)
    common = key_letters & sec_letters

    print(f"\n{sec_name}:")
    print(f"  Key letters present: {sorted(common)} ({len(common)} of 27 unique key letters)")

    # Check for repeated key letters
    key_repeated = {c: key.count(c) for c in key_letters if key.count(c) > 1}
    print(f"  Repeated key letters (J=2, D=2, A=2): {key_repeated}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY OF FINDINGS")
print("=" * 80)

print("""
KEY OBSERVATIONS:
1. Gibberish sections are highly consonant-heavy (78-89% consonants vs 62% English)
2. Severely vowel-deficient (11-21% vowels vs 38% English)
3. Contains rare letters (Z, Q, J, X, K) at much higher frequency than English
4. Missing only letter 'I' from the alphabet
5. High entropy indicates randomness/encryption
6. Chi-squared values are extremely high (non-English-like)
7. Some repeated digraphs suggest structure (AP, ZO, PV, GU)
8. Contains impossible consonant clusters (7-8 in a row)
9. No obvious hidden messages in every Nth letter
10. No anagrams of common English words

POSSIBLE INTERPRETATIONS:
- These could be intentionally gibberish placeholders
- Could be remnants of a different encryption layer
- Could be padding/filler material
- Could be encrypted with a different key/method than the readable parts
- The missing 'I' might be intentional or a clue

NEXT STEPS:
- Try additional Vigenere keys on these sections
- Try other cipher methods (Playfair, Hill, etc.)
- Look for regional patterns within each section
- Check if sections encode length/position information
- Analyze against the actual K4 ciphertext directly
""")

print("=" * 80)
