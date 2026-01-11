#!/usr/bin/env python3
"""
Test K4 with the known period 29 key discovered earlier: DIJJQELYOIECBAQKVAATCRDUMPABT
Try with and without inverse transposition
"""

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere with KRYPTOS alphabet"""
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

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

def cyclic_shift_inverse(text, step):
    """Inverse cyclic shift with multiplicative step"""
    n = len(text)
    result = [''] * n
    for i in range(n):
        source_idx = (i * step) % n
        result[i] = text[source_idx]
    return ''.join(result)

def main():
    k4_original = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    # Known key from earlier analysis (period 29)
    known_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"

    print("=" * 80)
    print("K4 DECRYPTION WITH KNOWN KEY (Period 29)")
    print("=" * 80)
    print(f"\nKey: {known_key}")
    print(f"Key Length: {len(known_key)}")

    # Test 1: Original K4 with known key
    print("\n" + "-" * 80)
    print("TEST 1: Original K4 with Known Key")
    print("-" * 80)
    plaintext1 = vigenere_decrypt(k4_original, known_key)
    print(f"\nPlaintext:\n{plaintext1}")
    check_words(plaintext1, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Test 2: Apply inverse transposition (step 2), then decrypt
    print("\n" + "-" * 80)
    print("TEST 2: Inverse Transposition (step 2) + Known Key")
    print("-" * 80)
    k4_transposed = cyclic_shift_inverse(k4_original, 2)
    print(f"Transposed K4: {k4_transposed}")
    plaintext2 = vigenere_decrypt(k4_transposed, known_key)
    print(f"\nPlaintext:\n{plaintext2}")
    check_words(plaintext2, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Test 3: Try different key positions with original K4
    print("\n" + "-" * 80)
    print("TEST 3: Original K4 with Rotated Key")
    print("-" * 80)
    for offset in range(min(5, len(known_key))):
        rotated_key = known_key[offset:] + known_key[:offset]
        plaintext = vigenere_decrypt(k4_original, rotated_key)
        print(f"\nKey offset {offset} ({rotated_key}):")
        print(f"Plaintext: {plaintext}")
        if "BERLINCLOCK" in plaintext or "NORTHEAST" in plaintext or "UNDER" in plaintext or "ABOVE" in plaintext:
            check_words(plaintext, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Test 4: Try inverse transposition with rotated keys
    print("\n" + "-" * 80)
    print("TEST 4: Inverse Transposition + Rotated Keys")
    print("-" * 80)
    k4_transposed = cyclic_shift_inverse(k4_original, 2)
    for offset in range(min(5, len(known_key))):
        rotated_key = known_key[offset:] + known_key[:offset]
        plaintext = vigenere_decrypt(k4_transposed, rotated_key)
        print(f"\nKey offset {offset} ({rotated_key}):")
        if "BERLINCLOCK" in plaintext or "NORTHEAST" in plaintext or "UNDER" in plaintext or "ABOVE" in plaintext:
            print(f"Plaintext: {plaintext}")
            check_words(plaintext, ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"])

    # Test 5: Try different multiplicative steps
    print("\n" + "-" * 80)
    print("TEST 5: Different Multiplicative Inverse Steps")
    print("-" * 80)
    # Try to find what step gives us the best result
    for step in range(1, 10):
        if step % 97 == 0:
            continue
        try:
            k4_t = cyclic_shift_inverse(k4_original, step)
            plaintext = vigenere_decrypt(k4_t, known_key)
            words_found = []
            for word in ["BERLINCLOCK", "NORTHEAST", "UNDER", "ABOVE"]:
                if word in plaintext:
                    words_found.append(word)
            if words_found:
                print(f"\nStep {step}: Found {words_found}")
                print(f"Plaintext: {plaintext}")
        except:
            pass

def check_words(plaintext, words):
    """Check which important words appear in plaintext"""
    found = []
    for word in words:
        if word in plaintext:
            pos = plaintext.index(word)
            print(f"  ✓ {word} at position {pos}")
            found.append(word)
        else:
            print(f"  ✗ {word} NOT found")
    return found

if __name__ == "__main__":
    main()
