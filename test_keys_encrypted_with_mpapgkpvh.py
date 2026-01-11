#!/usr/bin/env python3
"""
Test if the actual extracted keys are themselves encrypted with MPAPGKPVH
or another candidate key.

Theory: The sequence is:
1. Original message encrypted with MPAPGKPVH → Intermediate
2. Intermediate encrypted with Gap keys → Final gibberish
3. Final gibberish encrypted with Period 29 → K4 ciphertext

If we can decrypt the Gap keys with MPAPGKPVH, we might find:
- Original message structure
- Key derivation method
- Pattern recognition
"""

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def vigenere_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    """Decrypt with Vigenère"""
    ciphertext = ciphertext.upper()
    key = key.upper()
    plaintext = ""
    key_index = 0

    for char in ciphertext:
        if char not in alphabet:
            plaintext += char
            continue

        ct_pos = alphabet.index(char)
        key_char = key[key_index % len(key)]
        key_pos = alphabet.index(key_char)

        pt_pos = (ct_pos - key_pos) % len(alphabet)
        plaintext += alphabet[pt_pos]
        key_index += 1

    return plaintext

# The actual extracted keys from gap sections
actual_keys = {
    'Gap1': 'YXZFIRKRTKA',
    'Gap2A': 'FKVVLJHJNYNCUCYJLTNARNNJDERW',
    'Gap2B': 'MIOILQYYK',
    'Gap3': 'FOOPQBDPR',
    'Gap4': 'IGPDUICCM',
}

# Keys to try
candidate_keys = [
    "MPAPGKPVH",
    "HVPKGPAPM",
    "AEPLZ",
    "ZLPEA",
]

def main():
    print("\n" + "="*80)
    print("TEST: Are the actual gap keys encrypted with MPAPGKPVH?")
    print("="*80)
    print("\nDecrypting the actual extracted keys with candidate keys...\n")

    for key_name, actual_key in actual_keys.items():
        print(f"{key_name} (actual: {actual_key})")

        for candidate in candidate_keys:
            decrypted = vigenere_decrypt(actual_key, candidate)
            print(f"  {candidate:15}: {decrypted}")

        print()

    # Also try reverse
    print("\n" + "="*80)
    print("Also trying reversed keys...")
    print("="*80 + "\n")

    for key_name, actual_key in actual_keys.items():
        print(f"{key_name} (actual: {actual_key})")

        for candidate in candidate_keys:
            reversed_candidate = candidate[::-1]
            decrypted = vigenere_decrypt(actual_key, reversed_candidate)
            print(f"  {reversed_candidate:15}: {decrypted}")

        print()

    # Analyze if any results contain English words
    print("\n" + "="*80)
    print("Checking results for English word patterns...")
    print("="*80 + "\n")

    # Load dictionary
    WORDS = set()
    try:
        with open('/home/user/polyalphabetic/OxfordEnglishWords.txt', 'r') as f:
            WORDS = set(word.strip().upper() for word in f.readlines())
    except:
        print("Could not load dictionary")
        return

    import re

    for key_name, actual_key in actual_keys.items():
        for candidate in candidate_keys:
            decrypted = vigenere_decrypt(actual_key, candidate)
            words = [w for w in re.findall(r'[A-Z]{3,}', decrypted) if w in WORDS]

            if words:
                print(f"{key_name} + {candidate}: {words}")

            reversed_candidate = candidate[::-1]
            decrypted_rev = vigenere_decrypt(actual_key, reversed_candidate)
            words_rev = [w for w in re.findall(r'[A-Z]{3,}', decrypted_rev) if w in WORDS]

            if words_rev:
                print(f"{key_name} + {reversed_candidate}: {words_rev}")

    print("\nNo strong English word patterns found.")

    # Different hypothesis: what if the gap keys XOR with MPAPGKPVH yield something?
    print("\n" + "="*80)
    print("XOR ANALYSIS: Gap Keys XOR MPAPGKPVH")
    print("="*80 + "\n")

    mpapgkpvh = "MPAPGKPVH"

    for key_name, actual_key in actual_keys.items():
        print(f"{key_name}:")
        print(f"  Actual key: {actual_key}")

        # Take the portion of actual_key that matches mpapgkpvh length
        portion = actual_key[:len(mpapgkpvh)]

        xor_result = ""
        for i in range(min(len(portion), len(mpapgkpvh))):
            c1_pos = ord(portion[i]) - ord('A')
            c2_pos = ord(mpapgkpvh[i]) - ord('A')
            xor_pos = c1_pos ^ c2_pos
            xor_result += chr(xor_pos + ord('A'))

        print(f"  Gap key XOR MPAPGKPVH: {xor_result}")

        # Also try addition mod 26
        add_result = ""
        for i in range(min(len(portion), len(mpapgkpvh))):
            c1_pos = ord(portion[i]) - ord('A')
            c2_pos = ord(mpapgkpvh[i]) - ord('A')
            add_pos = (c1_pos + c2_pos) % 26
            add_result += chr(add_pos + ord('A'))

        print(f"  Gap key + MPAPGKPVH:   {add_result}")

        # And subtraction
        sub_result = ""
        for i in range(min(len(portion), len(mpapgkpvh))):
            c1_pos = ord(portion[i]) - ord('A')
            c2_pos = ord(mpapgkpvh[i]) - ord('A')
            sub_pos = (c1_pos - c2_pos) % 26
            sub_result += chr(sub_pos + ord('A'))

        print(f"  Gap key - MPAPGKPVH:   {sub_result}")
        print()

if __name__ == '__main__':
    main()
