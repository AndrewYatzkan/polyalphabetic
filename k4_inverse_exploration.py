#!/usr/bin/env python3
"""
K4 Inverse Transposition - Explore Different Approaches
"""

import sys
from collections import Counter

def forward_step_transposition(text, step):
    """
    Forward transposition: result[i] = text[(i + step) % n]
    Used in the forward step 49 approach
    """
    n = len(text)
    result = [''] * n
    for i in range(n):
        result[(i + step) % n] = text[i]
    return ''.join(result)

def inverse_step_transposition(text, step):
    """
    Inverse of forward step transposition
    If forward does: result[(i+step)%n] = text[i]
    Then inverse does: result[i] = text[(i-step)%n]
    """
    n = len(text)
    result = [''] * n
    for i in range(n):
        source_idx = (i - step) % n
        result[i] = text[source_idx]
    return ''.join(result)

def cyclic_shift_inverse(text, step):
    """
    Inverse of cyclic shift with multiplicative step
    result[i] = text[(i * inv_step) % n]
    where inv_step is the multiplicative inverse of step mod n
    """
    n = len(text)
    result = [''] * n
    for i in range(n):
        source_idx = (i * step) % n
        result[i] = text[source_idx]
    return ''.join(result)

def vigenere_decrypt_with_key(ciphertext, key):
    """
    Decrypt with a specific key string (fills unknown positions with 'A')
    """
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

    # Replace unknown positions with 'A'
    if isinstance(key, list):
        key = ['A' if c == '?' else c for c in key]
        key = ''.join(key)
    else:
        key = key.replace('?', 'A')

    plaintext = []
    for i, ct_char in enumerate(ciphertext):
        if ct_char not in kryptos_alpha:
            plaintext.append(ct_char)
            continue

        key_pos = i % len(key)
        key_char = key[key_pos]
        ct_idx = kryptos_alpha.index(ct_char)
        key_idx = kryptos_alpha.index(key_char)
        pt_idx = (ct_idx - key_idx) % 26
        plaintext.append(kryptos_alpha[pt_idx])

    return ''.join(plaintext)

def get_key_letter(ct, pt, kryptos_alpha):
    """Get key letter from ciphertext and plaintext"""
    ct_idx = kryptos_alpha.index(ct)
    pt_idx = kryptos_alpha.index(pt)
    key_idx = (ct_idx - pt_idx) % 26
    return kryptos_alpha[key_idx]

def extract_key_from_text(ciphertext, constraints, period):
    """
    Extract key from known plaintext constraints
    constraints: list of (position, plaintext_string) tuples
    """
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    key = ['?'] * period

    for pos, pt_text in constraints:
        for j, pt_char in enumerate(pt_text):
            if pos + j >= len(ciphertext):
                break
            ct_char = ciphertext[pos + j]
            if ct_char not in kryptos_alpha:
                continue
            key_pos = (pos + j) % period
            key_char = get_key_letter(ct_char, pt_char, kryptos_alpha)
            if key[key_pos] == '?':
                key[key_pos] = key_char

    return key

def test_inverse_methods():
    """Test different inverse transposition approaches"""

    k4_original = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    print("=" * 80)
    print("K4 INVERSE TRANSPOSITION - MULTIPLE APPROACHES")
    print("=" * 80)

    # Known constraints
    constraints = [(63, "BERLINCLOCK"), (16, "NORTHEAST")]
    period = 29

    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

    # Approach 1: Inverse cyclic shift (step 2)
    print("\n" + "-" * 80)
    print("APPROACH 1: Inverse Cyclic Shift (step 2, multiplicative inverse of 49)")
    print("-" * 80)
    transposed1 = cyclic_shift_inverse(k4_original, 2)
    print(f"Transposed: {transposed1}")
    key1 = extract_key_from_text(transposed1, constraints, period)
    plaintext1 = vigenere_decrypt_with_key(transposed1, ''.join(key1))
    print(f"Plaintext: {plaintext1}")
    print(f"Key: {''.join(key1)}")
    check_words(plaintext1, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Approach 2: Inverse additive step (-49 mod 97)
    print("\n" + "-" * 80)
    print("APPROACH 2: Inverse Additive Step (-49 mod 97)")
    print("-" * 80)
    transposed2 = inverse_step_transposition(k4_original, 49)
    print(f"Transposed: {transposed2}")
    key2 = extract_key_from_text(transposed2, constraints, period)
    plaintext2 = vigenere_decrypt_with_key(transposed2, ''.join(key2))
    print(f"Plaintext: {plaintext2}")
    print(f"Key: {''.join(key2)}")
    check_words(plaintext2, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Approach 3: Forward step (comparison)
    print("\n" + "-" * 80)
    print("APPROACH 3: Forward Step 49 (for comparison)")
    print("-" * 80)
    transposed3 = forward_step_transposition(k4_original, 49)
    print(f"Transposed: {transposed3}")
    key3 = extract_key_from_text(transposed3, constraints, period)
    plaintext3 = vigenere_decrypt_with_key(transposed3, ''.join(key3))
    print(f"Plaintext: {plaintext3}")
    print(f"Key: {''.join(key3)}")
    check_words(plaintext3, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Approach 4: Original K4 (no transposition)
    print("\n" + "-" * 80)
    print("APPROACH 4: Original K4 (No Transposition)")
    print("-" * 80)
    key4 = extract_key_from_text(k4_original, constraints, period)
    plaintext4 = vigenere_decrypt_with_key(k4_original, ''.join(key4))
    print(f"Plaintext: {plaintext4}")
    print(f"Key: {''.join(key4)}")
    check_words(plaintext4, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Approach 5: Try double transposition (forward then inverse)
    print("\n" + "-" * 80)
    print("APPROACH 5: Double Transposition (forward 49 + inverse 49)")
    print("-" * 80)
    transposed5 = forward_step_transposition(k4_original, 49)
    transposed5 = inverse_step_transposition(transposed5, 49)
    print(f"Transposed: {transposed5}")
    key5 = extract_key_from_text(transposed5, constraints, period)
    plaintext5 = vigenere_decrypt_with_key(transposed5, ''.join(key5))
    print(f"Plaintext: {plaintext5}")
    print(f"Key: {''.join(key5)}")
    check_words(plaintext5, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Approach 6: Try multiplicative inverse both ways
    print("\n" + "-" * 80)
    print("APPROACH 6: Double Multiplicative (step 2 + step 49)")
    print("-" * 80)
    transposed6 = cyclic_shift_inverse(k4_original, 2)
    transposed6 = cyclic_shift_inverse(transposed6, 49)
    print(f"Transposed: {transposed6}")
    key6 = extract_key_from_text(transposed6, constraints, period)
    plaintext6 = vigenere_decrypt_with_key(transposed6, ''.join(key6))
    print(f"Plaintext: {plaintext6}")
    print(f"Key: {''.join(key6)}")
    check_words(plaintext6, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

def check_words(plaintext, words):
    """Check which important words appear in plaintext"""
    for word in words:
        if word in plaintext:
            pos = plaintext.index(word)
            print(f"  ✓ {word} at position {pos}")
        else:
            print(f"  ✗ {word} NOT found")

if __name__ == "__main__":
    test_inverse_methods()
