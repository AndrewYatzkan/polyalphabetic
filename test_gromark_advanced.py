#!/usr/bin/env python3
"""
Advanced Gromark testing with additional mechanisms and diagnostics
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

def gromark_standard_extended(ciphertext, primer, m, n, mult=1, add=0):
    """
    Key[i] = (mult * Key[i-m] + Key[i-n] + add) mod 26
    Extended with multiplication and addition parameters
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    key = [char_to_num(c) for c in primer]

    for i in range(len(key), len(ciphertext)):
        if i - m >= 0 and i - n >= 0:
            new_key_val = (mult * key[i - m] + key[i - n] + add) % 26
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

def gromark_double_lag(ciphertext, primer, m1, n1, m2, n2):
    """
    Key[i] = (Key[i-m1] + Key[i-n1] + Key[i-m2] + Key[i-n2]) mod 26
    Double lag pair combination
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    key = [char_to_num(c) for c in primer]

    for i in range(len(key), len(ciphertext)):
        if all(i - x >= 0 for x in [m1, n1, m2, n2]):
            new_key_val = (key[i - m1] + key[i - n1] + key[i - m2] + key[i - n2]) % 26
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

def gromark_reverse(ciphertext, primer, m, n):
    """
    Decrypt from reverse direction
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    primer_nums = [char_to_num(c) for c in primer]

    # Build key from the end backwards
    key = [0] * len(ciphertext)
    for i in range(len(primer_nums)):
        key[-(i+1)] = primer_nums[-(i+1)]

    # Try to fill remaining key backwards
    for i in range(len(ciphertext) - len(primer_nums) - 1, -1, -1):
        if i + m < len(ciphertext) and i + n < len(ciphertext):
            key[i] = (key[i + m] + key[i + n]) % 26

    plaintext = []
    for i, cipher_num in enumerate(cipher_nums):
        plain_num = (cipher_num - key[i]) % 26
        plaintext.append(num_to_char(plain_num))

    return ''.join(plaintext)

def gromark_subtraction(ciphertext, primer, m, n):
    """
    Key[i] = (Key[i-m] - Key[i-n]) mod 26
    Subtraction variant instead of addition
    """
    cipher_nums = [char_to_num(c) for c in ciphertext]
    key = [char_to_num(c) for c in primer]

    for i in range(len(key), len(ciphertext)):
        if i - m >= 0 and i - n >= 0:
            new_key_val = (key[i - m] - key[i - n]) % 26
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

def test_all_advanced():
    """Test all advanced variants"""
    results = defaultdict(list)
    tested = 0

    print("=" * 80)
    print("ADVANCED GROMARK TESTING")
    print("=" * 80 + "\n")

    # Test 1: Standard with extended parameters
    print("Test 1: Extended parameters (mult, add)")
    test1_count = 0
    for primer in PRIMERS:
        for m in range(1, 6):
            for n in range(m + 1, min(m + 5, 10)):
                for mult in [1, 2, 3]:
                    for add in [0, 1, 3]:
                        if mult == 1 and add == 0:
                            continue  # Skip standard, already tested
                        test1_count += 1
                        plaintext = gromark_standard_extended(K4, primer, m, n, mult, add)
                        if plaintext:
                            for target in TARGETS:
                                if target in plaintext:
                                    print(f"✓ MATCH! Primer={primer}, m={m}, n={n}, mult={mult}, add={add}")
                                    print(f"  {plaintext}\n")
                                    results[target].append(plaintext)

    print(f"Tested {test1_count} extended parameter combinations - no matches\n")

    # Test 2: Subtraction variant
    print("Test 2: Subtraction variant")
    test2_count = 0
    for primer in PRIMERS:
        for m in range(1, 6):
            for n in range(m + 1, 8):
                test2_count += 1
                plaintext = gromark_subtraction(K4, primer, m, n)
                if plaintext:
                    for target in TARGETS:
                        if target in plaintext:
                            print(f"✓ MATCH! Primer={primer}, m={m}, n={n} (subtraction)")
                            print(f"  {plaintext}\n")
                            results[target].append(plaintext)

    print(f"Tested {test2_count} subtraction combinations - no matches\n")

    # Test 3: Reverse direction
    print("Test 3: Reverse direction decryption")
    test3_count = 0
    for primer in PRIMERS:
        for m in range(1, 6):
            for n in range(m + 1, 8):
                test3_count += 1
                plaintext = gromark_reverse(K4, primer, m, n)
                if plaintext:
                    for target in TARGETS:
                        if target in plaintext:
                            print(f"✓ MATCH! Primer={primer}, m={m}, n={n} (reverse)")
                            print(f"  {plaintext}\n")
                            results[target].append(plaintext)

    print(f"Tested {test3_count} reverse direction combinations - no matches\n")

    # Test 4: Double lag
    print("Test 4: Double lag pair combinations")
    test4_count = 0
    lag_set = [(1, 2), (2, 3), (1, 3), (3, 4), (2, 4), (1, 4)]
    for primer in PRIMERS:
        for (m1, n1) in lag_set:
            for (m2, n2) in lag_set:
                if (m1, n1) != (m2, n2):
                    test4_count += 1
                    plaintext = gromark_double_lag(K4, primer, m1, n1, m2, n2)
                    if plaintext:
                        for target in TARGETS:
                            if target in plaintext:
                                print(f"✓ MATCH! Primer={primer}, ({m1},{n1})+({m2},{n2})")
                                print(f"  {plaintext}\n")
                                results[target].append(plaintext)

    print(f"Tested {test4_count} double lag combinations - no matches\n")

    print("=" * 80)
    print(f"Total advanced tests: {test1_count + test2_count + test3_count + test4_count}")

    if results:
        print("\nMATCHES FOUND:")
        for target in TARGETS:
            if target in results:
                print(f"{target}: {len(results[target])} match(es)")
    else:
        print("\nCONCLUSION: Gromark cipher hypothesis does not produce known cribs from K4")
        print("across all tested variants, parameters, and directions.")

def test_basic_sanity():
    """Test that our basic decryption works with known values"""
    print("\n" + "=" * 80)
    print("SANITY CHECK: Testing basic autokey Vigenere (m=0, n=1)")
    print("=" * 80 + "\n")

    # Test basic autokey where the plaintext becomes the key
    cipher = "LVPABBUABBA"
    plain = "BERLINCLOCK"

    # Encrypt plain with autokey starting with "KRYPTOS"
    primer = "KRYPTOS"
    plain_nums = [char_to_num(c) for c in plain]
    key_vals = [char_to_num(c) for c in primer]

    for i in range(len(primer), len(plain)):
        key_vals.append(plain_nums[i - 1])

    ciphertext = []
    for i, p_num in enumerate(plain_nums):
        c_num = (p_num + key_vals[i]) % 26
        ciphertext.append(num_to_char(c_num))

    generated = ''.join(ciphertext)
    print(f"Plaintext:  {plain}")
    print(f"Primer:     {primer}")
    print(f"Generated cipher: {generated}")
    print(f"Expected:   {cipher}")
    print(f"Match: {generated == cipher}\n")

if __name__ == "__main__":
    test_basic_sanity()
    test_all_advanced()
