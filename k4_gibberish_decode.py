#!/usr/bin/env python3
"""
Attempt to decode K4 gibberish sections.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Best plaintext with UNDER/ABOVE
PT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Gibberish sections
GAP1 = "QAPBZDBKZEL"      # 11 chars, positions 5-15
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"  # 38 chars, positions 25-62
GAP3 = "RSPVJWQUL"        # 9 chars, positions 74-82
GAP4 = "ZOLRKCAYF"        # 9 chars, positions 88-96

ALL_GIBBERISH = GAP1 + GAP2 + GAP3 + GAP4
print(f"Total gibberish: {len(ALL_GIBBERISH)} chars")
print(f"Combined: {ALL_GIBBERISH}")

# 1. Letter to number analysis
print("\n1. LETTER TO NUMBER ANALYSIS")
def letter_to_num_a1(c):
    return ord(c) - ord('A') + 1

def letter_to_num_a0(c):
    return ord(c) - ord('A')

nums_a1 = [letter_to_num_a1(c) for c in ALL_GIBBERISH]
nums_a0 = [letter_to_num_a0(c) for c in ALL_GIBBERISH]

print(f"A=1 encoding: {nums_a1}")
print(f"A=0 encoding: {nums_a0}")

# Look for coordinate patterns
print("\n2. COORDINATE SEARCH (CIA: 38.9517, -77.1467)")

# Check pairs for 38, 95, 17, 77, 14, 67
target_pairs = [(3, 8), (9, 5), (1, 7), (7, 7), (1, 4), (6, 7)]
for i in range(len(nums_a1) - 1):
    pair = (nums_a1[i] % 10, nums_a1[i+1] % 10)
    if pair in target_pairs:
        print(f"  Found {pair[0]}{pair[1]} at position {i}: {ALL_GIBBERISH[i:i+2]}")

# 3. Try different Vigenere keys on gibberish
print("\n3. SECONDARY VIGENERE ON GIBBERISH")
def vigenere_decrypt(ct, key, alphabet=KRYPTOS):
    pt = ""
    for i, c in enumerate(ct):
        if c not in alphabet:
            pt += c
            continue
        ct_idx = alphabet.index(c)
        key_idx = alphabet.index(key[i % len(key)])
        pt_idx = (ct_idx - key_idx) % 26
        pt += alphabet[pt_idx]
    return pt

# Try keys related to Kryptos themes
test_keys = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
    "WELTZEIT", "SANBORN", "LANGLEY", "SECRET", "SHADOW",
    "LAYER", "UNDER", "ABOVE", "NORTHEAST", "BURIED",
    "TUTANKHAMUN", "CARTER", "EGYPT", "TREASURE"
]

for key in test_keys:
    result = vigenere_decrypt(ALL_GIBBERISH, key)
    # Check for English patterns
    english_score = 0
    common = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
              "CAN", "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HER",
              "ING", "ION", "ENT", "TIO", "ERE", "HER", "ATE", "VER"]
    for w in common:
        if w in result:
            english_score += 1
    if english_score > 0:
        print(f"  Key '{key}': {result[:30]}... (score: {english_score})")

# 4. Check for German words
print("\n4. GERMAN WORD CHECK")
german_words = ["DER", "DIE", "DAS", "UND", "IST", "VON", "MIT", "AUF",
                "ZUM", "ZUR", "BEI", "NACH", "DURCH", "UBER", "UNTER",
                "VOR", "HINTER", "NEBEN", "ZWISCHEN", "GEGEN", "OHNE",
                "MAUER", "WAND", "UHR", "ZEIT", "TURM", "PLATZ",
                "STRASSE", "STADT", "STEIN", "WASSER", "FEUER", "LUFT"]
for word in german_words:
    if word in ALL_GIBBERISH:
        print(f"  Found: {word}")
    if word in PT:
        print(f"  Found in full PT: {word}")

# 5. XOR/Masking analysis
print("\n5. XOR ANALYSIS")
# What if gibberish = plaintext XOR mask?
# Try XORing with simple patterns
def xor_strings(s1, s2):
    result = ""
    for i, c in enumerate(s1):
        c1_val = ord(c) - ord('A')
        c2_val = ord(s2[i % len(s2)]) - ord('A')
        xor_val = (c1_val ^ c2_val) % 26
        result += chr(xor_val + ord('A'))
    return result

xor_keys = ["A", "K", "KRYPTOS", "BERLIN", "NORTHEAST"]
for key in xor_keys:
    result = xor_strings(ALL_GIBBERISH, key)
    print(f"  XOR with '{key}': {result[:40]}...")

# 6. Atbash-like transformations
print("\n6. ATBASH TRANSFORMATION")
def atbash(text):
    result = ""
    for c in text:
        if c in KRYPTOS:
            idx = KRYPTOS.index(c)
            result += KRYPTOS[25 - idx]
        else:
            result += c
    return result

print(f"  Atbash: {atbash(ALL_GIBBERISH)}")

# 7. Position-based analysis
print("\n7. POSITION-BASED PATTERNS")
print("Gap positions in plaintext and their significance:")
print(f"  Gap1 (pos 5-15):  Between UNDER and NORTHEAST - 11 chars")
print(f"  Gap2 (pos 25-62): Between NORTHEAST and BERLINCLOCK - 38 chars")
print(f"  Gap3 (pos 74-82): Between BERLINCLOCK and ABOVE - 9 chars")
print(f"  Gap4 (pos 88-96): After ABOVE - 9 chars")
print("")
print("Gap lengths: 11, 38, 9, 9")
print("  11 = prime")
print("  38 = 2 × 19")
print("  9 = 3²")
print("  Sum = 67 (prime)")
print("")
print("What if gaps encode: GROUND/THE/SURFACE/XYZABCDEF?")

# 8. Try filling gaps with common phrases
print("\n8. POTENTIAL GAP FILLINGS")
# The pattern UNDER___NORTHEAST___BERLINCLOCK___ABOVE___ suggests:
# "UNDER THE GROUND NORTHEAST OF THE BERLINCLOCK AND ABOVE THE SURFACE..."
# But that doesn't fit the letter counts

gap1_len = 11  # Could be "THE GROUND " (10 chars) + 1
gap2_len = 38  # Longer phrase
gap3_len = 9   # "THE " + 5 more
gap4_len = 9   # Could be coordinates or ending

print(f"Gap1 ({gap1_len} chars): Could be 'THE GROUND' (10) + padding")
print(f"Gap2 ({gap2_len} chars): Long phrase, possibly location description")
print(f"Gap3 ({gap3_len} chars): Could be 'THE EARTH' (9) or 'LIES DEEP' (8)")
print(f"Gap4 ({gap4_len} chars): Ending phrase")

# 9. Final combined analysis
print("\n9. STRUCTURE HYPOTHESIS")
print("Most likely plaintext structure:")
print("  UNDER [11 char phrase] NORTHEAST [38 char phrase] BERLINCLOCK [9 chars] ABOVE [9 chars]")
print("")
print("Possible complete messages:")
print("  'UNDER THE GROUND NORTHEAST OF THE BERLINCLOCK LIES ABOVE THE EARTH' - doesn't fit exactly")
print("  'UNDER LIES BURIED NORTHEAST FROM THE BERLINCLOCK AND ABOVE GROUND IT' - doesn't fit")
