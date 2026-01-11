#!/usr/bin/env python3
"""
Expanded Gromark cipher testing with more variants and approaches
"""

import itertools
from collections import defaultdict

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

PRIMERS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]
TARGETS = ["BERLINCLOCK", "NORTHEAST"]

def char_to_num(c):
    return ord(c.upper()) - ord('A')

def num_to_char(n):
    return chr(n % 26 + ord('A'))

def gromark_ciphertext_feedback(ciphertext, primer, m, n):
    """
    Key[i] = (Ciphertext[i-m] + Ciphertext[i-n]) mod 26
    Using ciphertext feedback instead of plaintext
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    plaintext = []
    primer_nums = [char_to_num(c) for c in primer]

    for i, cipher_num in enumerate(cipher_nums):
        if i < len(primer_nums):
            key_val = primer_nums[i]
        else:
            # Generate from ciphertext
            if i - m >= 0 and i - n >= 0:
                cipher_m = cipher_nums[i - m]
                cipher_n = cipher_nums[i - n]
                key_val = (cipher_m + cipher_n) % 26
            else:
                return None

        plain_num = (cipher_num - key_val) % 26
        plaintext.append(num_to_char(plain_num))

    return ''.join(plaintext)

def gromark_multiplicative(ciphertext, primer, m, n, mult=2):
    """
    Key[i] = (mult * Key[i-m] + Key[i-n]) mod 26
    Multiplicative variant
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    key = [char_to_num(c) for c in primer]
    primer_nums = [char_to_num(c) for c in primer]

    for i in range(len(key), len(ciphertext)):
        if i - m >= 0 and i - n >= 0:
            new_key_val = (mult * key[i - m] + key[i - n]) % 26
            key.append(new_key_val)
        else:
            break

    if len(key) < len(ciphertext):
        return None

    plaintext = []
    for i, cipher_num in enumerate(cipher_nums):
        plain_num = (cipher_num - key[i]) % 26
        plaintext.append(num_to_char(plain_num))

    return ''.join(plaintext)

def gromark_xor_style(ciphertext, primer, m, n):
    """
    Key[i] = (Key[i-m] XOR Key[i-n]) mod 26
    XOR variant
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    key = [char_to_num(c) for c in primer]
    primer_nums = [char_to_num(c) for c in primer]

    for i in range(len(key), len(ciphertext)):
        if i - m >= 0 and i - n >= 0:
            new_key_val = (key[i - m] ^ key[i - n]) % 26
            key.append(new_key_val)
        else:
            break

    if len(key) < len(ciphertext):
        return None

    plaintext = []
    for i, cipher_num in enumerate(cipher_nums):
        plain_num = (cipher_num - key[i]) % 26
        plaintext.append(num_to_char(plain_num))

    return ''.join(plaintext)

def gromark_encryption_test(plaintext_str, primer, m, n):
    """
    Test forward encryption to validate decryption logic
    Gromark encryption with key feedback from plaintext
    """
    plain_nums = [char_to_num(c) for c in plaintext_str]
    primer_nums = [char_to_num(c) for c in primer]
    ciphertext = []
    key_history = primer_nums.copy()

    for i, plain_num in enumerate(plain_nums):
        if i < len(primer_nums):
            key_val = primer_nums[i]
        else:
            if i - m >= 0 and i - n >= 0:
                plain_m = plain_nums[i - m]
                plain_n = plain_nums[i - n]
                key_val = (plain_m + plain_n) % 26
            else:
                break

        cipher_num = (plain_num + key_val) % 26
        ciphertext.append(num_to_char(cipher_num))
        key_history.append(key_val)

    return ''.join(ciphertext)

def test_forward_validation():
    """Test that encryption/decryption are working correctly"""
    print("=" * 80)
    print("FORWARD VALIDATION TEST")
    print("=" * 80)

    test_plain = "BERLINCLOCK"
    primers_test = ["KRYPTOS"]
    lags_test = [(1, 2), (2, 3), (3, 4)]

    for primer in primers_test:
        for m, n in lags_test:
            ciphertext_gen = gromark_encryption_test(test_plain, primer, m, n)
            if ciphertext_gen:
                print(f"\nPrimer: {primer}, m={m}, n={n}")
                print(f"  Original plaintext:  {test_plain}")
                print(f"  Generated ciphertext: {ciphertext_gen}")

def test_expanded_combinations():
    """Test with expanded parameters"""
    results = defaultdict(list)
    tested = 0

    # More aggressive lag exploration
    lag_pairs = []
    for m in range(1, 8):
        for n in range(1, 10):
            if m != n:
                lag_pairs.append((m, n))

    lag_pairs = list(set(lag_pairs))  # Remove duplicates

    variants = [
        ('Ciphertext Feedback', gromark_ciphertext_feedback),
        ('Multiplicative (×2)', lambda c, p, m, n: gromark_multiplicative(c, p, m, n, 2)),
        ('Multiplicative (×3)', lambda c, p, m, n: gromark_multiplicative(c, p, m, n, 3)),
        ('XOR Variant', gromark_xor_style),
    ]

    print("\n" + "=" * 80)
    print("EXPANDED GROMARK VARIANTS TEST")
    print(f"Testing {len(PRIMERS)} primers × {len(lag_pairs)} lag pairs × {len(variants)} variants")
    print(f"Total combinations: {len(PRIMERS) * len(lag_pairs) * len(variants)}")
    print("=" * 80 + "\n")

    for primer in PRIMERS:
        for m, n in lag_pairs:
            for variant_name, decrypt_func in variants:
                tested += 1
                try:
                    plaintext = decrypt_func(K4, primer, m, n)

                    if plaintext and len(plaintext) == len(K4):
                        # Check for target strings
                        for target in TARGETS:
                            if target in plaintext:
                                print(f"✓ MATCH FOUND!")
                                print(f"  Variant: {variant_name}")
                                print(f"  Primer: {primer}, m={m}, n={n}")
                                print(f"  Target: {target}")
                                print(f"  Plaintext: {plaintext}\n")
                                results[target].append({
                                    'plaintext': plaintext,
                                    'primer': primer,
                                    'm': m,
                                    'n': n,
                                    'variant': variant_name
                                })

                        # Save high vowel ratio results
                        vowel_count = sum(1 for c in plaintext if c in 'AEIOU')
                        vowel_ratio = vowel_count / len(plaintext)

                        if vowel_ratio > 0.32:
                            results[f'vowel_{vowel_ratio:.3f}'].append({
                                'plaintext': plaintext,
                                'primer': primer,
                                'm': m,
                                'n': n,
                                'variant': variant_name
                            })
                except:
                    pass

    print("=" * 80)
    print(f"Tested: {tested} combinations")

    # Report any matches
    targets_found = sum(1 for k in results.keys() if k in TARGETS)
    print(f"Found target strings: {targets_found}")

    if targets_found > 0:
        print("\nMATCHES FOUND:")
        for target in TARGETS:
            if target in results:
                print(f"\n{target}: {len(results[target])} match(es)")
    else:
        print("\nNo target strings found. Showing candidates with highest vowel ratio:")
        vowel_keys = sorted([k for k in results.keys() if k.startswith('vowel_')], reverse=True)[:15]
        for vowel_key in vowel_keys:
            ratio = float(vowel_key.split('_')[1])
            print(f"\nVowel ratio {ratio:.3f}:")
            for match in results[vowel_key][:2]:
                print(f"  [{match['variant']}] Primer: {match['primer']}, m={match['m']}, n={match['n']}")
                print(f"    {match['plaintext'][:70]}...")

if __name__ == "__main__":
    test_forward_validation()
    test_expanded_combinations()
