#!/usr/bin/env python3
"""
Deep XOR analysis of K4 gibberish.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALL_GIBBERISH = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

def xor_strings(s1, s2):
    result = ""
    for i, c in enumerate(s1):
        c1_val = ord(c) - ord('A')
        c2_val = ord(s2[i % len(s2)]) - ord('A')
        xor_val = (c1_val ^ c2_val) % 26
        result += chr(xor_val + ord('A'))
    return result

# Try extended keys
extended_keys = [
    "NORTHEAST",
    "BERLINCLOCK",
    "UNDERTHGROUND",
    "UNDERTHEGROUND",
    "THEGROUNDNORTH",
    "SHADOWFORCES",
    "PALIMPSEST",
    "PALIMPSESTABSCISSA",
    "SLOWLYDESPARATLY",  # From K3
    "CANARIESINTHEMINE",
    "IQLUSION",
    "SUBTLESHADING",
    "ITSBURIED",
    "ITSBUTTHERESOMEWHERE",
    "LAYERTWO",
    "WILLIAMWEBSTER",
    "ALEXANDERPLATZ",
    "WELTZEITUHR",
    "BERLINWALL",
    "NINEONENINEEIGHT",  # 1989
    "NOVEMBER",
    "NINETEENEIGHTYNINE",
]

print("XOR Analysis Results:")
print("=" * 70)

for key in extended_keys:
    result = xor_strings(ALL_GIBBERISH, key.upper())
    # Check for English-like patterns
    score = 0
    common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN",
                    "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HER", "ING", "ION",
                    "ENT", "TIO", "ERE", "ATE", "VER", "DID", "HIS", "HER", "ITS"]
    found_words = []
    for w in common_words:
        if w in result:
            score += len(w)
            found_words.append(w)

    if score > 0 or result[:4] in ["DOES", "THEY", "WHAT", "WHEN", "THIS", "THAT", "HAVE", "WILL"]:
        print(f"\nKey: {key}")
        print(f"Result: {result}")
        print(f"Score: {score}, Found: {found_words}")

print("\n" + "=" * 70)
print("Testing combinations of known plaintext fragments as XOR keys")
print("=" * 70)

# Try using parts of the known plaintext as the key
plaintexts = [
    "UNDERQAPBZDBKZELNORTHEAST",
    "NORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCK",
    "BERLINCLOCKRSPVJWQULABOVE",
    "UNDERABOVE",
    "NORTHEASTBERLINCLOCK",
]

for pt_key in plaintexts:
    result = xor_strings(ALL_GIBBERISH, pt_key.upper())
    print(f"\nXOR with '{pt_key[:20]}...':")
    print(f"  Result: {result[:40]}...")

# What if the gibberish IS the key for something else?
print("\n" + "=" * 70)
print("Testing gibberish as key to decrypt other known ciphertext")
print("=" * 70)

# K4 ciphertext portions
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def vigenere_decrypt_standard(ct, key):
    pt = ""
    for i, c in enumerate(ct):
        ct_idx = ord(c) - ord('A')
        key_idx = ord(key[i % len(key)]) - ord('A')
        pt_idx = (ct_idx - key_idx) % 26
        pt += chr(pt_idx + ord('A'))
    return pt

# Use gibberish as key
result = vigenere_decrypt_standard(K4_CT, ALL_GIBBERISH)
print(f"K4 CT decrypted with gibberish as key:")
print(f"  {result}")

# Try just Gap1 as key for Gap2, etc.
GAP1 = "QAPBZDBKZEL"
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

print(f"\nGap2 decrypted with Gap1 as key:")
result = vigenere_decrypt_standard(GAP2, GAP1)
print(f"  {result}")

print(f"\nGap3 decrypted with Gap1 as key:")
result = vigenere_decrypt_standard(GAP3, GAP1)
print(f"  {result}")

print(f"\nGap4 decrypted with Gap1 as key:")
result = vigenere_decrypt_standard(GAP4, GAP1)
print(f"  {result}")

# What if gaps XOR with each other?
print("\n" + "=" * 70)
print("Gaps XORed with each other")
print("=" * 70)

print(f"Gap1 XOR Gap3: {xor_strings(GAP1[:9], GAP3)}")
print(f"Gap1 XOR Gap4: {xor_strings(GAP1[:9], GAP4)}")
print(f"Gap3 XOR Gap4: {xor_strings(GAP3, GAP4)}")

# Check if any gap is a Caesar shift of another
print("\n" + "=" * 70)
print("Caesar shift analysis between gaps")
print("=" * 70)

def caesar_shift(text, n):
    return ''.join(chr((ord(c) - ord('A') + n) % 26 + ord('A')) for c in text)

for shift in range(26):
    shifted_gap3 = caesar_shift(GAP3, shift)
    if shifted_gap3 == GAP4:
        print(f"Gap3 shifted by {shift} = Gap4!")

    shifted_gap1 = caesar_shift(GAP1[:9], shift)
    if shifted_gap1 == GAP3:
        print(f"Gap1[:9] shifted by {shift} = Gap3!")
    if shifted_gap1 == GAP4:
        print(f"Gap1[:9] shifted by {shift} = Gap4!")
