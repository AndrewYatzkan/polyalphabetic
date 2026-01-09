#!/usr/bin/env python3
"""
K4 Key Derivation - Derive the full key from known plaintext positions

If K4 is a simple Vigenère with the KRYPTOS alphabet, we can derive
the key from the known BERLINCLOCK positions.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known plaintext at positions 63-73
KNOWN_PT = "BERLINCLOCK"
KNOWN_CT = K4[63:74]  # "NYPVTTMZFPK"

print("=" * 70)
print("K4 KEY DERIVATION FROM KNOWN PLAINTEXT")
print("=" * 70)

print(f"\nKnown ciphertext (pos 63-73): {KNOWN_CT}")
print(f"Known plaintext:              {KNOWN_PT}")

# Derive key values for each alphabet
for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("Standard", STANDARD_ALPHA)]:
    print(f"\n{'='*70}")
    print(f"Using {alpha_name} alphabet: {alpha}")
    print("="*70)

    # Calculate key character for each known position
    key_chars = {}
    print("\nDeriving key positions:")
    for i, (ct_char, pt_char) in enumerate(zip(KNOWN_CT, KNOWN_PT)):
        pos = 63 + i
        ct_pos = alpha.index(ct_char)
        pt_pos = alpha.index(pt_char)
        key_val = (ct_pos - pt_pos) % len(alpha)
        key_char = alpha[key_val]
        key_chars[pos] = key_char
        print(f"  Position {pos}: CT={ct_char}({ct_pos}) - PT={pt_char}({pt_pos}) = Key[{pos % 11}] = {key_char}")

    # Try different key periods
    for period in range(7, 15):
        print(f"\n--- Testing period {period} ---")

        # Reconstruct key
        key = ['?'] * period
        for pos, key_char in key_chars.items():
            key_pos = pos % period
            if key[key_pos] == '?':
                key[key_pos] = key_char
            elif key[key_pos] != key_char:
                # Conflict - this period doesn't work
                print(f"  Conflict at key position {key_pos}: existing={key[key_pos]}, new={key_char}")
                break
        else:
            key_str = ''.join(key)
            unknowns = key_str.count('?')
            print(f"  Reconstructed key: {key_str} ({unknowns} unknowns)")

            if unknowns == 0:
                # Full key - decrypt!
                plaintext = ''
                for i, c in enumerate(K4):
                    ct_pos = alpha.index(c)
                    key_pos = alpha.index(key[i % period])
                    pt_pos = (ct_pos - key_pos) % len(alpha)
                    plaintext += alpha[pt_pos]

                print(f"  DECRYPTED: {plaintext}")

                # Check if BERLINCLOCK is at position 63
                if plaintext[63:74] == "BERLINCLOCK":
                    print(f"  *** BERLINCLOCK VERIFIED AT POSITION 63! ***")

                # Check for NORTHEAST
                if "NORTHEAST" in plaintext:
                    print(f"  *** FOUND NORTHEAST! ***")

                # Count English words
                common_words = ['THE', 'AND', 'FOR', 'YOU', 'WAS', 'ARE', 'BUT', 'NOT', 'ALL',
                               'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'ITS',
                               'THEY', 'THIS', 'FROM', 'HAVE', 'BEEN', 'WERE', 'SAID', 'EACH',
                               'WHICH', 'THEIR', 'TIME', 'WILL', 'WOULD', 'THERE', 'COULD',
                               'NORTH', 'SOUTH', 'EAST', 'WEST', 'SECRET', 'HIDDEN', 'BURIED']
                word_count = sum(1 for w in common_words if w in plaintext)
                print(f"  Common words found: {word_count}")

            elif unknowns <= 3:
                # Try brute forcing remaining positions
                unknown_positions = [i for i, c in enumerate(key) if c == '?']
                print(f"  Brute forcing {unknowns} positions: {unknown_positions}")

                best_score = 0
                best_key = None
                best_pt = None

                for combo in itertools.product(alpha[:10], repeat=unknowns):
                    test_key = list(key)
                    for i, pos in enumerate(unknown_positions):
                        test_key[pos] = combo[i]
                    test_key_str = ''.join(test_key)

                    # Decrypt
                    plaintext = ''
                    for i, c in enumerate(K4):
                        ct_pos = alpha.index(c)
                        key_pos = alpha.index(test_key[i % period])
                        pt_pos = (ct_pos - key_pos) % len(alpha)
                        plaintext += alpha[pt_pos]

                    # Score
                    score = 0
                    if plaintext[63:74] == "BERLINCLOCK":
                        score += 10
                    if "NORTHEAST" in plaintext:
                        score += 20

                    common_words = ['THE', 'AND', 'YOU', 'WAS', 'FOR', 'ARE', 'BUT', 'NOT']
                    score += sum(1 for w in common_words if w in plaintext)

                    if score > best_score:
                        best_score = score
                        best_key = test_key_str
                        best_pt = plaintext

                if best_score > 10:
                    print(f"  Best key: {best_key} (score: {best_score})")
                    print(f"  Best plaintext: {best_pt}")

import itertools

# Special focus on period 11 since the known segment is 11 chars
print("\n" + "="*70)
print("SPECIAL ANALYSIS: PERIOD 11")
print("="*70)

# For period 11, positions 63-73 give us the complete key
# Position 63 mod 11 = 8, position 73 mod 11 = 7
# So we get key positions 8,9,10,0,1,2,3,4,5,6,7 = all 11 positions!

# Let me calculate this properly
mask_from_kryptos = []
for ct_char, pt_char in zip(KNOWN_CT, KNOWN_PT):
    ct_pos = KRYPTOS_ALPHA.index(ct_char)
    pt_pos = KRYPTOS_ALPHA.index(pt_char)
    key_val = (ct_pos - pt_pos) % len(KRYPTOS_ALPHA)
    mask_from_kryptos.append(KRYPTOS_ALPHA[key_val])

print(f"\nMask from known positions: {''.join(mask_from_kryptos)}")

# Rearrange to get key in order (positions 8,9,10,0,1,2,3,4,5,6,7)
# mask[0] = key[8], mask[1] = key[9], ..., mask[3] = key[0], ...
key_11 = ['?'] * 11
for i, m in enumerate(mask_from_kryptos):
    key_pos = (63 + i) % 11
    key_11[key_pos] = m

print(f"Reconstructed 11-char key: {''.join(key_11)}")

# Decrypt with this key
print("\nDecrypting K4 with derived key...")
key_str = ''.join(key_11)
plaintext = ''
for i, c in enumerate(K4):
    ct_pos = KRYPTOS_ALPHA.index(c)
    key_pos = KRYPTOS_ALPHA.index(key_str[i % 11])
    pt_pos = (ct_pos - key_pos) % len(KRYPTOS_ALPHA)
    plaintext += KRYPTOS_ALPHA[pt_pos]

print(f"\nKey: {key_str}")
print(f"Plaintext: {plaintext}")
print(f"\nVerification:")
print(f"  Position 63-73: {plaintext[63:74]} (expected: BERLINCLOCK)")
print(f"  NORTHEAST present: {'NORTHEAST' in plaintext}")

# Break into possible words
print(f"\nPossible word boundaries analysis:")
text = plaintext
# Look for common patterns
import re
for word in ['THE', 'AND', 'FOR', 'WAS', 'ARE', 'BUT', 'NOT', 'ALL', 'CAN',
             'WITH', 'THAT', 'THIS', 'FROM', 'HAVE', 'BEEN', 'NORTH', 'EAST',
             'SOUTH', 'WEST', 'CLOCK', 'BERLIN', 'TIME', 'LOCATION', 'BURIED']:
    if word in text:
        pos = text.find(word)
        print(f"  Found '{word}' at position {pos}")
