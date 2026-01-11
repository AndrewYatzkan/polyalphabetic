#!/usr/bin/env python3
"""
Test Gromark cipher hypothesis on K4
Gromark uses a lagged Fibonacci generator for the running key
"""

import itertools
from collections import defaultdict

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

PRIMERS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]
TARGETS = ["BERLINCLOCK", "NORTHEAST"]

def char_to_num(c):
    """Convert A-Z to 0-25"""
    return ord(c.upper()) - ord('A')

def num_to_char(n):
    """Convert 0-25 to A-Z"""
    return chr(n % 26 + ord('A'))

def gromark_decrypt_variant1(ciphertext, primer, m, n):
    """
    Gromark variant 1: Key[i] = (Key[i-m] + Key[i-n]) mod 26
    The key is purely generated from primer using Fibonacci
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]

    # Initialize key with primer
    key = [char_to_num(c) for c in primer]

    # Generate key values using lagged Fibonacci
    for i in range(len(key), len(ciphertext)):
        if i - m >= 0 and i - n >= 0:
            new_key_val = (key[i - m] + key[i - n]) % 26
            key.append(new_key_val)
        else:
            # Not enough history yet, skip or use different approach
            break

    # If key is shorter than ciphertext, we can't decrypt fully
    if len(key) < len(ciphertext):
        return None

    # Decrypt
    plaintext = []
    for i, cipher_num in enumerate(cipher_nums):
        plain_num = (cipher_num - key[i]) % 26
        plaintext.append(num_to_char(plain_num))

    return ''.join(plaintext)

def gromark_decrypt_variant2(ciphertext, primer, m, n):
    """
    Gromark variant 2: Key[i] = (Plaintext[i-m] + Plaintext[i-n]) mod 26
    The key is generated from plaintext itself (more like true autokey)
    This requires iterative decryption
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    plaintext = []
    key_history = [char_to_num(c) for c in primer]

    for i, cipher_num in enumerate(cipher_nums):
        # Determine current key value
        if i < len(key_history):
            key_val = key_history[i]
        else:
            # Generate from plaintext
            if i - m >= 0 and i - n >= 0:
                plain_m = char_to_num(plaintext[i - m])
                plain_n = char_to_num(plaintext[i - n])
                key_val = (plain_m + plain_n) % 26
            else:
                # Not enough plaintext yet
                break

        # Decrypt
        plain_num = (cipher_num - key_val) % 26
        plaintext.append(num_to_char(plain_num))
        key_history.append(key_val)

    if len(plaintext) < len(ciphertext):
        return None

    return ''.join(plaintext)

def gromark_decrypt_variant3(ciphertext, primer, m, n):
    """
    Gromark variant 3: Hybrid - start with primer, then use plaintext feedback
    Key[i] for i < len(primer) is from primer
    Key[i] for i >= len(primer) uses: Key[i] = (Plaintext[i-m] + Plaintext[i-n]) mod 26
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    plaintext = []
    primer_nums = [char_to_num(c) for c in primer]

    for i, cipher_num in enumerate(cipher_nums):
        # Determine current key value
        if i < len(primer_nums):
            key_val = primer_nums[i]
        else:
            # Generate from plaintext
            if i - m >= 0 and i - n >= 0:
                plain_m = char_to_num(plaintext[i - m])
                plain_n = char_to_num(plaintext[i - n])
                key_val = (plain_m + plain_n) % 26
            else:
                # Not enough plaintext yet, can't proceed
                return None

        # Decrypt
        plain_num = (cipher_num - key_val) % 26
        plaintext.append(num_to_char(plain_num))

    if len(plaintext) < len(ciphertext):
        return None

    return ''.join(plaintext)

def test_all_combinations():
    """Test all combinations of primers and lag pairs"""
    results = defaultdict(list)
    tested = 0
    found_targets = 0

    # Generate all lag pair combinations: m=1 to 5, n=2 to 7
    lag_pairs = []
    for m in range(1, 6):
        for n in range(2, 8):
            if m != n:  # Different lags
                lag_pairs.append((m, n))

    print(f"Testing {len(PRIMERS)} primers × {len(lag_pairs)} lag pairs × 3 variants")
    print(f"Total combinations: {len(PRIMERS) * len(lag_pairs) * 3}\n")
    print("=" * 80)

    for primer in PRIMERS:
        for m, n in lag_pairs:
            for variant_num, decrypt_func in [
                (1, gromark_decrypt_variant1),
                (2, gromark_decrypt_variant2),
                (3, gromark_decrypt_variant3)
            ]:
                tested += 1
                plaintext = decrypt_func(K4, primer, m, n)

                if plaintext:
                    # Check for target strings
                    found_any_target = False
                    for target in TARGETS:
                        if target in plaintext:
                            found_targets += 1
                            found_any_target = True
                            results[target].append({
                                'plaintext': plaintext,
                                'primer': primer,
                                'm': m,
                                'n': n,
                                'variant': variant_num
                            })
                            print(f"✓ MATCH FOUND!")
                            print(f"  Primer: {primer}, Variant: {variant_num}, m={m}, n={n}")
                            print(f"  Target: {target}")
                            print(f"  Plaintext: {plaintext}\n")

                    # Also save interesting results (ones that look like English)
                    if not found_any_target:
                        # Count vowels and common letters
                        vowel_count = sum(1 for c in plaintext if c in 'AEIOU')
                        vowel_ratio = vowel_count / len(plaintext)

                        if vowel_ratio > 0.25:  # More than 25% vowels is reasonable
                            results[f'vowel_ratio_{vowel_ratio:.2f}'].append({
                                'plaintext': plaintext,
                                'primer': primer,
                                'm': m,
                                'n': n,
                                'variant': variant_num
                            })

    print("=" * 80)
    print(f"\nTested: {tested} combinations")
    print(f"Found target strings: {found_targets}")

    if found_targets > 0:
        print("\nSUMMARY OF MATCHES:")
        for target in TARGETS:
            if target in results:
                print(f"\n{target}: {len(results[target])} match(es)")
                for match in results[target]:
                    print(f"  - Primer: {match['primer']}, Variant: {match['variant']}, m={match['m']}, n={match['n']}")
    else:
        print("\nNo target strings found in any decryption.")
        print("Showing top candidates with high vowel ratio (>0.30):")

        high_vowel = [k for k in results.keys() if k.startswith('vowel_ratio') and float(k.split('_')[2]) > 0.30]
        high_vowel.sort(reverse=True)

        for ratio_key in high_vowel[:10]:
            ratio = float(ratio_key.split('_')[2])
            results_list = results[ratio_key]
            if results_list:
                print(f"\nVowel ratio {ratio}:")
                for match in results_list[:3]:  # Show first 3 of each ratio
                    print(f"  Primer: {match['primer']}, Variant: {match['variant']}, m={match['m']}, n={match['n']}")
                    print(f"  {match['plaintext'][:80]}...")

if __name__ == "__main__":
    test_all_combinations()
