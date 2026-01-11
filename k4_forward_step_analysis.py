#!/usr/bin/env python3
"""
Analyze what happens if we apply forward step 49 transposition to K4
and try to decrypt with period 29
"""

def forward_step_transposition(text, step):
    """Forward transposition: result[(i+step)%n] = text[i]"""
    n = len(text)
    result = [''] * n
    for i in range(n):
        result[(i + step) % n] = text[i]
    return ''.join(result)

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

def get_key_letter(ct, pt):
    """Get key letter from ciphertext and plaintext"""
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    ct_idx = kryptos_alpha.index(ct)
    pt_idx = kryptos_alpha.index(pt)
    key_idx = (ct_idx - pt_idx) % 26
    return kryptos_alpha[key_idx]

def extract_key_from_text(ciphertext, constraints, period):
    """Extract key from known plaintext constraints"""
    key = ['?'] * period

    for pos, pt_text in constraints:
        for j, pt_char in enumerate(pt_text):
            if pos + j >= len(ciphertext):
                break
            ct_char = ciphertext[pos + j]
            key_pos = (pos + j) % period
            key_char = get_key_letter(ct_char, pt_char)
            if key[key_pos] == '?':
                key[key_pos] = key_char
            elif key[key_pos] != key_char:
                print(f"  Conflict at key pos {key_pos}: {key[key_pos]} vs {key_char}")

    return key

def main():
    k4_original = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    known_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    period = 29

    print("=" * 80)
    print("FORWARD STEP 49 TRANSPOSITION ANALYSIS")
    print("=" * 80)

    # Original K4 plaintext (for reference)
    print("\nKNOWN PLAINTEXT (with correct key):")
    plaintext_correct = vigenere_decrypt(k4_original, known_key)
    print(plaintext_correct)
    print("\nKey words found:")
    print(f"  UNDER at 0: {plaintext_correct[0:5]}")
    print(f"  NORTHEAST at 16: {plaintext_correct[16:25]}")
    print(f"  BERLINCLOCK at 63: {plaintext_correct[63:74]}")
    print(f"  ABOVE at 83: {plaintext_correct[83:88]}")

    # Test 1: Apply forward step 49
    print("\n" + "=" * 80)
    print("TEST 1: Forward Step 49 on K4 ciphertext")
    print("=" * 80)

    k4_forward = forward_step_transposition(k4_original, 49)
    print(f"Transposed K4: {k4_forward}")

    # Try to extract key from the transposed version
    constraints = [(63, "BERLINCLOCK"), (16, "NORTHEAST")]
    key_extracted = extract_key_from_text(k4_forward, constraints, period)
    print(f"\nExtracted key: {''.join(key_extracted)}")

    # Decrypt with extracted key
    key_str = ''.join(['A' if c == '?' else c for c in key_extracted])
    plaintext_forward = vigenere_decrypt(k4_forward, key_str)
    print(f"Decrypted plaintext: {plaintext_forward}")

    # Test 2: Try to find what step would transform K4 to produce the known plaintext
    print("\n" + "=" * 80)
    print("TEST 2: Reverse Engineering - What step was used?")
    print("=" * 80)

    # If we know the plaintext, we can compute what the ciphertext should be
    # and figure out what transposition step was applied
    print("Analyzing if plaintext was transposed BEFORE encryption...")

    # Hypothesis: plaintext was transposed with step 49, THEN encrypted
    plaintext_known = plaintext_correct
    print(f"Known plaintext: {plaintext_known}")

    # Apply step 49 to the known plaintext
    plaintext_transposed = forward_step_transposition(plaintext_known, 49)
    print(f"\nPlaintext after step 49: {plaintext_transposed}")

    # Now encrypt this with the key to see if we get K4
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

    def vigenere_encrypt(plaintext, key):
        ciphertext = []
        for i, pt_char in enumerate(plaintext):
            key_pos = i % len(key)
            key_char = key[key_pos]
            pt_idx = kryptos_alpha.index(pt_char)
            key_idx = kryptos_alpha.index(key_char)
            ct_idx = (pt_idx + key_idx) % 26
            ciphertext.append(kryptos_alpha[ct_idx])
        return ''.join(ciphertext)

    ciphertext_computed = vigenere_encrypt(plaintext_transposed, known_key)
    print(f"Ciphertext computed from transposed plaintext: {ciphertext_computed}")
    print(f"Actual K4: {k4_original}")
    print(f"Match: {ciphertext_computed == k4_original}")

    # Test 3: Try the inverse - what if plaintext was transposed with INVERSE of 49?
    print("\n" + "=" * 80)
    print("TEST 3: Inverse Transposition on Known Plaintext")
    print("=" * 80)

    # Inverse of step 49 mod 97
    # 49 * x ≡ 1 (mod 97), so x = 2
    plaintext_inverse = forward_step_transposition(plaintext_known, -49 % 97)
    print(f"Plaintext after inverse step 49: {plaintext_inverse}")

    ciphertext_inverse = vigenere_encrypt(plaintext_inverse, known_key)
    print(f"Ciphertext from inverse transposed plaintext: {ciphertext_inverse}")
    print(f"Actual K4: {k4_original}")
    print(f"Match: {ciphertext_inverse == k4_original}")

    # Test 4: Try different transposition steps
    print("\n" + "=" * 80)
    print("TEST 4: Testing All Possible Transposition Steps")
    print("=" * 80)

    for step in [2, 49, 95, 96]:  # 2 is inverse of 49, 95 is -2, 96 is -1
        plaintext_t = forward_step_transposition(plaintext_known, step)
        ciphertext_t = vigenere_encrypt(plaintext_t, known_key)
        match = ciphertext_t == k4_original
        print(f"Step {step:3d}: {'MATCH!' if match else 'no match'}")
        if match:
            print(f"  -> Found: step {step} reproduces K4!")

if __name__ == "__main__":
    main()
