#!/usr/bin/env python3
"""
K4 Analytical Analysis - Pattern-based approaches, no brute force.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEY_29 = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Best plaintext so far
PT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("=" * 60)
print("K4 ANALYTICAL ANALYSIS")
print("=" * 60)

# 1. Analyze the KEY pattern
print("\n1. KEY PATTERN ANALYSIS")
print(f"Key: {KEY_29}")
print(f"Length: {len(KEY_29)}")

# Check for patterns in the key
key_positions = {}
for i, c in enumerate(KEY_29):
    if c not in key_positions:
        key_positions[c] = []
    key_positions[c].append(i)

print("\nKey letter positions:")
for c in sorted(key_positions.keys()):
    positions = key_positions[c]
    if len(positions) > 1:
        diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        print(f"  {c}: positions {positions}, diffs: {diffs}")

# 2. Analyze gibberish sections
print("\n2. GIBBERISH SECTION ANALYSIS")
gibberish_sections = [
    ("Gap1", PT[5:16], 5, 16),      # 11 chars
    ("Gap2", PT[25:63], 25, 63),    # 38 chars
    ("Gap3", PT[74:83], 74, 83),    # 9 chars
    ("Gap4", PT[88:97], 88, 97),    # 9 chars
]

for name, text, start, end in gibberish_sections:
    print(f"\n{name} (pos {start}-{end-1}, len {len(text)}): {text}")

    # Frequency analysis
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])
    print(f"  Frequencies: {sorted_freq[:5]}")

    # Check for repeated bigrams/trigrams
    bigrams = {}
    for i in range(len(text) - 1):
        bg = text[i:i+2]
        bigrams[bg] = bigrams.get(bg, 0) + 1
    repeated_bigrams = [(k,v) for k,v in bigrams.items() if v > 1]
    if repeated_bigrams:
        print(f"  Repeated bigrams: {repeated_bigrams}")

# 3. Gap lengths analysis
print("\n3. GAP LENGTH PATTERN")
gap_lengths = [11, 38, 9, 9]
print(f"Gap lengths: {gap_lengths}")
print(f"Sum: {sum(gap_lengths)} (total gibberish)")
print(f"Factors of 11: 1, 11")
print(f"Factors of 38: 1, 2, 19, 38")
print(f"Factors of 9: 1, 3, 9")
print(f"Note: 11 + 38 + 9 + 9 = 67, and 67 is PRIME")

# 4. Position modulo analysis
print("\n4. POSITION MODULO ANALYSIS (mod 29)")
print("Key positions for each section:")
sections = [
    ("UNDER", 0, 5),
    ("Gap1", 5, 16),
    ("NORTHEAST", 16, 25),
    ("Gap2", 25, 63),
    ("BERLINCLOCK", 63, 74),
    ("Gap3", 74, 83),
    ("ABOVE", 83, 88),
    ("Gap4", 88, 97),
]

for name, start, end in sections:
    key_positions_used = [(i, i % 29, KEY_29[i % 29]) for i in range(start, end)]
    key_chars = ''.join([x[2] for x in key_positions_used])
    print(f"  {name:12} pos {start:2}-{end-1:2}: key positions {[x[1] for x in key_positions_used]}")
    print(f"               key chars: {key_chars}")

# 5. Look for words hiding in gibberish via different readings
print("\n5. ALTERNATIVE READINGS OF GIBBERISH")
full_gibberish = PT[5:16] + PT[25:63] + PT[74:83] + PT[88:97]
print(f"Combined gibberish ({len(full_gibberish)} chars): {full_gibberish}")

# Try reading every 2nd, 3rd letter
for step in [2, 3, 5, 7]:
    extracted = full_gibberish[::step]
    print(f"  Every {step}th letter: {extracted}")

# 6. Check if gibberish could be coordinates
print("\n6. COORDINATE CHECK")
# CIA coordinates: 38.9517° N, 77.1467° W
# Berlin World Clock: 52.5200° N, 13.4050° E

def letters_to_numbers(text):
    """Convert A=1, B=2, ..., Z=26"""
    return [ord(c) - ord('A') + 1 for c in text if c.isalpha()]

gap1_nums = letters_to_numbers(PT[5:16])
print(f"Gap1 as numbers (A=1): {gap1_nums}")
print(f"  As pairs: {[(gap1_nums[i], gap1_nums[i+1]) for i in range(0, len(gap1_nums)-1, 2)]}")

# 7. German word check
print("\n7. GERMAN WORD CHECK")
german_words = ["UNTER", "UBER", "NORD", "SUD", "OST", "WEST", "UHR", "ZEIT", "MAUER", "WAND",
                "STEIN", "GEHEIM", "VERSTECKT", "TURM", "PLATZ", "STRASSE"]
for word in german_words:
    if word in PT:
        print(f"  Found: {word} at position {PT.index(word)}")
    # Also check in full ciphertext
    if word in K4_CT:
        print(f"  Found in CT: {word} at position {K4_CT.index(word)}")

# 8. Key derivation hypothesis
print("\n8. KEY DERIVATION FROM KNOWN WORDS")
print("Known key segments derived from cribs:")
print("  BERLINCLOCK at pos 63 → key[5:16] = ELYOIECBAQK")
print("  NORTHEAST at pos 16 → key[16:25] = VAATCRDUM")
print("  UNDER at pos 0 → key[0:5] = DIJJQ")
print("  ABOVE at pos 83 → key[25:29] = PABT")

# Verify key derivation
def derive_key_char(ct_char, pt_char):
    ct_idx = KRYPTOS.index(ct_char)
    pt_idx = KRYPTOS.index(pt_char)
    key_idx = (ct_idx - pt_idx) % 26
    return KRYPTOS[key_idx]

print("\nVerifying DIJJQ from UNDER:")
for i, (ct, pt) in enumerate(zip(K4_CT[0:5], "UNDER")):
    key = derive_key_char(ct, pt)
    print(f"  pos {i}: CT={ct} PT={pt} → key={key}")

# 9. What words could the key spell?
print("\n9. KEY AS POTENTIAL WORDS")
print(f"Full key: {KEY_29}")
# Look for English words in key
key_words = ["DI", "ELY", "OIE", "BAQ", "VAA", "CRD", "PAB"]
print("Possible word fragments in key: DI, ELY (name?), BAQ, VAA, CRD, PAB")

# 10. Sanborn's other hints
print("\n10. SANBORN'S HINTS ANALYSIS")
print("Known hints:")
print("  - BERLINCLOCK = Weltzeituhr (World Clock)")
print("  - 1986 Egypt trip significant")
print("  - 1989 Berlin Wall fall significant")
print("  - NORTHEAST appears in plaintext")
print("")
print("Egypt connection: Pyramids? Hieroglyphics? Tutankhamun (K3 reference)?")
print("Berlin Wall connection: Nov 9, 1989 = 11/9/89 or 9/11/89")
