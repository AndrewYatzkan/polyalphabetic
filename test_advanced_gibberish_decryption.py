#!/usr/bin/env python3
"""
Advanced testing for K4 gibberish sections.
Tests multiple cipher types and transformations.
"""

import sys
import re
from collections import Counter

# Load dictionary
WORDS = set()
try:
    with open('/home/user/polyalphabetic/OxfordEnglishWords.txt', 'r') as f:
        WORDS = set(word.strip().upper() for word in f.readlines() if word.strip())
except:
    print("Warning: Could not load word dictionary")

# Define alphabets
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def find_words_in_text(text, min_length=3):
    """Find English words in text"""
    words = []
    potential_words = re.findall(r'[A-Z]{3,}', text)
    for word in potential_words:
        if word in WORDS:
            words.append(word)
    return words

def vigenere_decrypt(ciphertext, key, alphabet):
    """Decrypt text using Vigenère cipher"""
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

def vigenere_encrypt(plaintext, key, alphabet):
    """Encrypt text using Vigenère cipher"""
    plaintext = plaintext.upper()
    key = key.upper()
    ciphertext = ""
    key_index = 0

    for char in plaintext:
        if char not in alphabet:
            ciphertext += char
            continue

        pt_pos = alphabet.index(char)
        key_char = key[key_index % len(key)]
        key_pos = alphabet.index(key_char)

        ct_pos = (pt_pos + key_pos) % len(alphabet)
        ciphertext += alphabet[ct_pos]
        key_index += 1

    return ciphertext

def beaufort_decrypt(ciphertext, key, alphabet):
    """Decrypt text using Beaufort cipher"""
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

        pt_pos = (key_pos - ct_pos) % len(alphabet)
        plaintext += alphabet[pt_pos]
        key_index += 1

    return plaintext

def autokey_decrypt(ciphertext, key, alphabet):
    """Decrypt text using Autokey cipher"""
    ciphertext = ciphertext.upper()
    key = key.upper()
    plaintext = ""
    key_index = 0

    for char in ciphertext:
        if char not in alphabet:
            continue

        ct_pos = alphabet.index(char)
        key_char = key[key_index % len(key)]
        key_pos = alphabet.index(key_char)

        pt_pos = (ct_pos - key_pos) % len(alphabet)
        pt_char = alphabet[pt_pos]
        plaintext += pt_char
        key_index += 1

        # In autokey, the plaintext feeds back into the key
        if key_index <= len(key):
            key += pt_char

    return plaintext

def homophonic_check(ciphertext, key):
    """Check for homophonic substitution patterns"""
    # Look for repeated letters that might decrypt to the same thing
    patterns = []
    for i in range(len(ciphertext) - 1):
        if ciphertext[i] == ciphertext[i+1]:
            patterns.append((i, ciphertext[i]))
    return patterns

def xor_decrypt(ciphertext, key):
    """Try XOR decryption"""
    ciphertext = ciphertext.upper()
    key = key.upper()
    result = ""

    # Convert to numbers
    ct_nums = [ord(c) - ord('A') for c in ciphertext]
    key_nums = [ord(c) - ord('A') for c in key]

    for i, ct_num in enumerate(ct_nums):
        key_num = key_nums[i % len(key_nums)]
        result_num = (ct_num ^ key_num) % 26
        result += chr(result_num + ord('A'))

    return result

def test_all_methods(ciphertext, key, section_name):
    """Test multiple decryption methods"""
    print(f"\n{'='*80}")
    print(f"KEY: {key:20} SECTION: {section_name}")
    print(f"{'='*80}")
    print(f"Ciphertext: {ciphertext}\n")

    methods = [
        ("Vigenère (STD)", lambda: vigenere_decrypt(ciphertext, key, STANDARD_ALPHA)),
        ("Vigenère (KRYPTOS)", lambda: vigenere_decrypt(ciphertext, key, KRYPTOS_ALPHA)),
        ("Beaufort (STD)", lambda: beaufort_decrypt(ciphertext, key, STANDARD_ALPHA)),
        ("Beaufort (KRYPTOS)", lambda: beaufort_decrypt(ciphertext, key, KRYPTOS_ALPHA)),
        ("XOR", lambda: xor_decrypt(ciphertext, key)),
    ]

    results_found = []

    for method_name, decrypt_func in methods:
        try:
            plaintext = decrypt_func()
            words = find_words_in_text(plaintext)

            if words:
                print(f"[{method_name:25}]")
                print(f"  Plaintext: {plaintext}")
                print(f"  Words: {', '.join(words)}")
                print()
                results_found.append({
                    'method': method_name,
                    'plaintext': plaintext,
                    'words': words
                })
        except Exception as e:
            pass

    if not results_found:
        print("No English words found with any method.\n")

    return results_found

def main():
    print("\n" + "="*80)
    print("ADVANCED GIBBERISH DECRYPTION TEST")
    print("="*80)

    # K4 gibberish sections
    sections = [
        ("QAPBZDBKZEL", "Gap1 (11 chars)"),
        ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZ", "Gap2 (29 chars)"),
        ("RSPVJWQUL", "Gap3 (9 chars)"),
        ("ZOLRKCAYF", "Gap4 (9 chars)"),
    ]

    # Keys to test
    keys = [
        "MPAPGKPVH",
        "HVPKGPAPM",
        "AEPLZ",
        "ZLPEA",
    ]

    print(f"\nTesting {len(keys)} keys against {len(sections)} gibberish sections")
    print(f"Methods: Vigenère (STD/KRYPTOS), Beaufort (STD/KRYPTOS), XOR\n")

    all_found = []

    for ciphertext, section_name in sections:
        for key in keys:
            results = test_all_methods(ciphertext, key, section_name)
            if results:
                all_found.extend(results)

    # Summary
    print(f"\n{'='*80}")
    print("FINDINGS SUMMARY")
    print(f"{'='*80}\n")

    if all_found:
        print(f"Found {len(all_found)} promising decryptions:\n")
        for find in all_found:
            print(f"  Method: {find['method']}")
            print(f"  Words: {find['words']}")
            print(f"  Text: {find['plaintext']}\n")
    else:
        print("No English words found with any key-section-method combination.\n")

    # Analyze gibberish structure more deeply
    print(f"\n{'='*80}")
    print("DEEP PATTERN ANALYSIS")
    print(f"{'='*80}\n")

    for ciphertext, section_name in sections:
        print(f"\n{section_name}: {ciphertext}")

        # Character frequency
        freq = Counter(ciphertext)
        print(f"  Length: {len(ciphertext)}")
        print(f"  Unique chars: {len(freq)}")
        print(f"  Top 5 chars: {freq.most_common(5)}")

        # Check for sequential alphabet patterns
        sequential = []
        for i in range(len(ciphertext) - 1):
            c1 = ciphertext[i]
            c2 = ciphertext[i+1]
            pos1 = ord(c1) - ord('A')
            pos2 = ord(c2) - ord('A')
            diff = (pos2 - pos1) % 26
            if diff == 1:
                sequential.append((c1, c2))

        if sequential:
            print(f"  Sequential pairs (N→N+1): {sequential}")

        # Look for repeated bigrams
        bigrams = Counter()
        for i in range(len(ciphertext) - 1):
            bigrams[ciphertext[i:i+2]] += 1

        repeated_bigrams = [b for b, count in bigrams.items() if count > 1]
        if repeated_bigrams:
            print(f"  Repeated bigrams: {repeated_bigrams}")

    # Test if gibberish could be plaintext from Period 29 key with different key
    print(f"\n{'='*80}")
    print("HYPOTHESIS: Are these sections the result of specific transpositions?")
    print(f"{'='*80}\n")

    # K4 period 29 key for reference
    k4_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    k4_plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
    k4_ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    # Extract the gibberish from the plaintext and see what the corresponding ciphertext is
    plaintext_gap1 = k4_plaintext[5:16]  # QAPBZDBKZEL
    ciphertext_gap1 = k4_ciphertext[5:16]

    print(f"Plaintext Gap1: {plaintext_gap1}")
    print(f"Ciphertext Gap1: {ciphertext_gap1}")

    # Extract key used for this section
    extracted_key = ""
    for i in range(len(plaintext_gap1)):
        pt_char = plaintext_gap1[i]
        ct_char = ciphertext_gap1[i]
        pt_pos = STANDARD_ALPHA.index(pt_char)
        ct_pos = STANDARD_ALPHA.index(ct_char)
        key_pos = (ct_pos - pt_pos) % 26
        extracted_key += STANDARD_ALPHA[key_pos]

    print(f"Extracted key for Gap1: {extracted_key}")
    print()

    plaintext_gap2 = k4_plaintext[25:63]  # LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH
    ciphertext_gap2 = k4_ciphertext[25:63]

    print(f"Plaintext Gap2: {plaintext_gap2}")
    print(f"Ciphertext Gap2: {ciphertext_gap2}")

    # Extract key used for Gap2
    extracted_key2 = ""
    for i in range(len(plaintext_gap2)):
        pt_char = plaintext_gap2[i]
        ct_char = ciphertext_gap2[i]
        pt_pos = STANDARD_ALPHA.index(pt_char)
        ct_pos = STANDARD_ALPHA.index(ct_char)
        key_pos = (ct_pos - pt_pos) % 26
        extracted_key2 += STANDARD_ALPHA[key_pos]

    print(f"Extracted key for Gap2: {extracted_key2}")

if __name__ == '__main__':
    main()
