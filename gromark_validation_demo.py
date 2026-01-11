#!/usr/bin/env python3
"""
Gromark cipher validation demonstration
Shows step-by-step encryption and decryption
"""

def char_to_num(c):
    return ord(c.upper()) - ord('A')

def num_to_char(n):
    return chr(n % 26 + ord('A'))

def gromark_encrypt(plaintext, primer, m, n):
    """Encrypt with Gromark - generate key from plaintext"""
    plain_nums = [char_to_num(c) for c in plaintext]
    primer_nums = [char_to_num(c) for c in primer]
    
    # Key starts as primer, then plaintext feedback + Fibonacci
    key_sequence = primer_nums.copy()
    ciphertext = []
    
    print(f"Encryption: {plaintext}")
    print(f"Primer: {primer} (length {len(primer)})")
    print(f"Parameters: m={m}, n={n}")
    print(f"Formula: Key[i] = (Key[i-{m}] + Key[i-{n}]) mod 26\n")
    
    for i in range(len(plaintext)):
        # Get current key value
        if i < len(key_sequence):
            key_val = key_sequence[i]
        else:
            # Generate from previous key values using Fibonacci
            key_val = (key_sequence[i - m] + key_sequence[i - n]) % 26
            key_sequence.append(key_val)
        
        # Encrypt
        cipher_num = (plain_nums[i] + key_val) % 26
        ciphertext.append(num_to_char(cipher_num))
        
        key_char = num_to_char(key_val)
        plain_char = plaintext[i]
        cipher_char = num_to_char(cipher_num)
        
        if i < 15:  # Show first 15 steps
            print(f"i={i:2d}: Plain={plain_char} + Key={key_char} = Cipher={cipher_char} (key_val={key_val})")
    
    result = ''.join(ciphertext)
    print(f"\nCiphertext: {result}\n")
    return result, key_sequence

def gromark_decrypt(ciphertext, primer, m, n):
    """Decrypt with Gromark - key generated from plaintext"""
    cipher_nums = [char_to_num(c) for c in ciphertext]
    primer_nums = [char_to_num(c) for c in primer]
    
    plaintext = []
    key_sequence = primer_nums.copy()
    
    print(f"Decryption: {ciphertext}")
    print(f"Primer: {primer} (length {len(primer)})")
    print(f"Parameters: m={m}, n={n}")
    print(f"Formula: Key[i] = (Key[i-{m}] + Key[i-{n}]) mod 26\n")
    
    for i in range(len(ciphertext)):
        # Get current key value
        if i < len(key_sequence):
            key_val = key_sequence[i]
        else:
            # Generate from previous key values using Fibonacci
            key_val = (key_sequence[i - m] + key_sequence[i - n]) % 26
            key_sequence.append(key_val)
        
        # Decrypt
        plain_num = (cipher_nums[i] - key_val) % 26
        plaintext.append(num_to_char(plain_num))
        
        # Extend key_sequence with new plaintext for next iteration
        key_sequence.append(plain_num)
        
        key_char = num_to_char(key_val)
        cipher_char = ciphertext[i]
        plain_char = num_to_char(plain_num)
        
        if i < 15:  # Show first 15 steps
            print(f"i={i:2d}: Cipher={cipher_char} - Key={key_char} = Plain={plain_char} (key_val={key_val})")
    
    result = ''.join(plaintext)
    print(f"\nPlaintext: {result}\n")
    return result

if __name__ == "__main__":
    print("=" * 80)
    print("GROMARK CIPHER VALIDATION DEMONSTRATION")
    print("=" * 80 + "\n")
    
    # Test encryption and decryption round-trip
    plaintext = "BERLINCLOCK"
    primer = "KRYPTOS"
    m, n = 1, 2
    
    print("TEST 1: Encrypt 'BERLINCLOCK' with Gromark\n")
    ciphertext, key_seq = gromark_encrypt(plaintext, primer, m, n)
    
    print("TEST 2: Decrypt the result (should get 'BERLINCLOCK' back)\n")
    recovered = gromark_decrypt(ciphertext, primer, m, n)
    
    print("=" * 80)
    print("VALIDATION RESULT")
    print("=" * 80)
    if recovered == plaintext:
        print(f"✓ SUCCESS: Encryption/Decryption round-trip works correctly")
        print(f"  Original:  {plaintext}")
        print(f"  Recovered: {recovered}")
    else:
        print(f"✗ FAILURE: Round-trip did not recover original")
        print(f"  Original:  {plaintext}")
        print(f"  Recovered: {recovered}")
    
    print("\nNOTE: The decryption logic extends key_sequence with plaintext values")
    print("during decryption, implementing 'plaintext feedback' variant of Gromark.")
