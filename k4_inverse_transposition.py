#!/usr/bin/env python3
"""
K4 Inverse Transposition Analysis
Apply inverse step 49 transposition, then Vigenere decryption with period 29
"""

def inverse_transposition_step2(k4_text):
    """
    Apply inverse transposition using step 2 (inverse of 49 mod 97)
    result[i] = K4[(i × 2) % 97]

    With 97 characters, step 2 is the cyclic shift inverse
    """
    n = len(k4_text)
    result = [''] * n

    for i in range(n):
        source_idx = (i * 2) % n
        result[i] = k4_text[source_idx]

    return ''.join(result)

def vigenere_decrypt_with_period(ciphertext, period):
    """
    Decrypt with a given period, extracting key from BERLINCLOCK and NORTHEAST positions
    """
    # K4 known plaintext: BERLINCLOCK at position 63, NORTHEAST at position 16
    # We need to determine what the key should be

    # Using KRYPTOS alphabet
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

    def get_key_letter(ct, pt):
        """Get key letter from ciphertext and plaintext"""
        ct_idx = kryptos_alpha.index(ct)
        pt_idx = kryptos_alpha.index(pt)
        key_idx = (ct_idx - pt_idx) % 26
        return kryptos_alpha[key_idx]

    # Extract key from known cribs
    key = ['?'] * period

    # BERLINCLOCK at position 63
    berlinclock = "BERLINCLOCK"
    berlinclock_ct_start = 63
    for j, pt_char in enumerate(berlinclock):
        pos = berlinclock_ct_start + j
        ct_char = ciphertext[pos]
        key_pos = pos % period
        key_char = get_key_letter(ct_char, pt_char)
        if key[key_pos] == '?':
            key[key_pos] = key_char
        elif key[key_pos] != key_char:
            print(f"WARNING: Key conflict at position {key_pos}: {key[key_pos]} vs {key_char}")

    # NORTHEAST at position 16
    northeast = "NORTHEAST"
    northeast_ct_start = 16
    for j, pt_char in enumerate(northeast):
        pos = northeast_ct_start + j
        if pos < len(ciphertext):
            ct_char = ciphertext[pos]
            key_pos = pos % period
            key_char = get_key_letter(ct_char, pt_char)
            if key[key_pos] == '?':
                key[key_pos] = key_char
            elif key[key_pos] != key_char:
                print(f"WARNING: Key conflict at position {key_pos}: {key[key_pos]} vs {key_char}")

    # Print key
    key_str = ''.join(key)
    print(f"\nExtracted key (period {period}): {key_str}")
    print(f"Known positions filled: {26 - key_str.count('?')}/{period}")

    # Try to fill remaining positions (if any) with 'A' for testing
    if '?' in key:
        key = [c if c != '?' else 'A' for c in key]
        print(f"Filling unknowns with 'A': {key_str}")

    key_str = ''.join(key)

    # Decrypt the entire text
    plaintext = []
    for i, ct_char in enumerate(ciphertext):
        key_pos = i % period
        key_char = key_str[key_pos]
        ct_idx = kryptos_alpha.index(ct_char)
        key_idx = kryptos_alpha.index(key_char)
        pt_idx = (ct_idx - key_idx) % 26
        plaintext.append(kryptos_alpha[pt_idx])

    return ''.join(plaintext)

def analyze_inverse_transposition():
    """Main analysis"""

    # Original K4 ciphertext
    k4_original = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    print("=" * 80)
    print("K4 INVERSE TRANSPOSITION ANALYSIS")
    print("=" * 80)
    print(f"\nOriginal K4 ({len(k4_original)} chars):")
    print(k4_original)

    # Step 1: Apply inverse transposition (step 2)
    print("\n" + "=" * 80)
    print("STEP 1: Apply Inverse Transposition (step 2, inverse of 49 mod 97)")
    print("=" * 80)

    k4_transposed = inverse_transposition_step2(k4_original)
    print(f"\nAfter inverse transposition ({len(k4_transposed)} chars):")
    print(k4_transposed)

    # Show positions of key words if they appear
    if "BERLINCLOCK" in k4_transposed:
        pos = k4_transposed.index("BERLINCLOCK")
        print(f"\nFOUND: BERLINCLOCK at position {pos}!")
    else:
        print(f"\nNOT FOUND: BERLINCLOCK in transposed text")

    if "NORTHEAST" in k4_transposed:
        pos = k4_transposed.index("NORTHEAST")
        print(f"FOUND: NORTHEAST at position {pos}!")
    else:
        print(f"NOT FOUND: NORTHEAST in transposed text")

    # Step 2: Try Vigenere decryption with period 29
    print("\n" + "=" * 80)
    print("STEP 2: Decrypt with Vigenere (Period 29)")
    print("=" * 80)

    plaintext = vigenere_decrypt_with_period(k4_transposed, 29)
    print(f"\nDecrypted plaintext ({len(plaintext)} chars):")
    print(plaintext)

    # Search for meaningful words
    print("\n" + "=" * 80)
    print("PLAINTEXT ANALYSIS")
    print("=" * 80)

    important_words = ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE", "CLOCK", "BERLIN", "LAYER"]
    for word in important_words:
        if word in plaintext:
            pos = plaintext.index(word)
            print(f"✓ FOUND: {word} at position {pos}")
        else:
            print(f"✗ NOT FOUND: {word}")

    # Try with original K4 for comparison
    print("\n" + "=" * 80)
    print("COMPARISON: Direct Vigenere on Original K4")
    print("=" * 80)

    plaintext_original = vigenere_decrypt_with_period(k4_original, 29)
    print(f"\nDecrypted plaintext ({len(plaintext_original)} chars):")
    print(plaintext_original)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nDoes inverse transposition improve results? Let me check both versions...")

    if "BERLINCLOCK" in plaintext:
        print("✓ Inverse transposition: BERLINCLOCK found in plaintext")
    else:
        print("✗ Inverse transposition: BERLINCLOCK NOT in plaintext")

    if "BERLINCLOCK" in plaintext_original:
        print("✓ Original K4: BERLINCLOCK found in plaintext")
    else:
        print("✗ Original K4: BERLINCLOCK NOT in plaintext")

if __name__ == "__main__":
    analyze_inverse_transposition()
