#!/usr/bin/env python3
"""
Test hypothesis: The gibberish is a secondary encryption.
If MPAPGKPVH encrypted something to create the gibberish,
what was the original plaintext?

The flow would be:
Original plaintext → [encrypt with MPAPGKPVH] → Intermediate gibberish
Intermediate gibberish → [encrypt with Period 29 key] → K4 ciphertext gibberish

We're seeing the final ciphertext gibberish. If we decrypt with Period 29 key,
we get the "plaintext" (which is the intermediate gibberish).
If we decrypt THAT with MPAPGKPVH, we should get meaningful text.
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

def analyze_text_quality(text):
    """Analyze how English-like a text is"""
    words = find_words_in_text(text)
    total_letters = len(re.findall(r'[A-Z]', text))
    word_chars = sum(len(w) for w in words)
    coverage = word_chars / total_letters if total_letters > 0 else 0

    return {
        'words': words,
        'word_count': len(words),
        'coverage': coverage,
        'text': text
    }

def main():
    print("\n" + "="*80)
    print("TESTING SECONDARY ENCRYPTION HYPOTHESIS")
    print("="*80)
    print("\nHypothesis: Gibberish = Secondary encryption with MPAPGKPVH")
    print("           + Primary encryption with Period 29 key\n")

    # The "gibberish" plaintext from Period 29 decryption
    gap1_plaintext = "QAPBZDBKZEL"
    gap2_plaintext = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
    gap3_plaintext = "RSPVJWQUL"
    gap4_plaintext = "ZOLRKCAYF"

    # Keys to test
    keys = [
        "MPAPGKPVH",
        "HVPKGPAPM",
        "AEPLZ",
        "ZLPEA",
    ]

    sections = [
        (gap1_plaintext, "Gap1"),
        (gap2_plaintext, "Gap2"),
        (gap3_plaintext, "Gap3"),
        (gap4_plaintext, "Gap4"),
    ]

    print("Testing hypothesis: decrypt 'gibberish' with secondary keys\n")

    all_results = []

    for plaintext_from_period29, section_name in sections:
        print(f"\n{'='*80}")
        print(f"SECTION: {section_name}")
        print(f"Period 29 decryption result: {plaintext_from_period29}")
        print(f"{'='*80}")

        for key in keys:
            # Try decrypting this with the potential secondary key
            # This would give us the "pre-secondary-encryption" plaintext
            result_std = vigenere_decrypt(plaintext_from_period29, key, STANDARD_ALPHA)
            result_kryptos = vigenere_decrypt(plaintext_from_period29, key, KRYPTOS_ALPHA)

            words_std = find_words_in_text(result_std)
            words_kryptos = find_words_in_text(result_kryptos)

            if words_std or words_kryptos:
                print(f"\n  KEY: {key}")
                if words_std:
                    print(f"    [STD]     {result_std}")
                    print(f"    [STD]     Words: {', '.join(words_std)}")
                    all_results.append({
                        'section': section_name,
                        'key': key,
                        'alphabet': 'STD',
                        'result': result_std,
                        'words': words_std
                    })
                if words_kryptos:
                    print(f"    [KRYPTOS] {result_kryptos}")
                    print(f"    [KRYPTOS] Words: {', '.join(words_kryptos)}")
                    all_results.append({
                        'section': section_name,
                        'key': key,
                        'alphabet': 'KRYPTOS',
                        'result': result_kryptos,
                        'words': words_kryptos
                    })

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    if all_results:
        print(f"Found {len(all_results)} results with English words:\n")
        for r in all_results:
            print(f"  {r['section']:10} | Key: {r['key']:15} | Alphabet: {r['alphabet']:10} | Words: {', '.join(r['words'])}")
    else:
        print("No English words found.\n")

    # Now test the reverse: ENCRYPT known words with these keys
    # to see if we get the gibberish
    print(f"\n{'='*80}")
    print("REVERSE TEST: Can we ENCRYPT English words to get the gibberish?")
    print(f"{'='*80}\n")

    # Try some common words that might appear
    common_words = [
        "WATER",
        "STONE",
        "EARTH",
        "PLACE",
        "POINT",
        "NORTH",
        "SOUTH",
        "EAST",
        "WEST",
        "COORDINATES",
        "LOCATION",
        "LATITUDE",
        "LONGITUDE",
        "DEGREES",
        "MINUTES",
        "SECONDS",
        "PYRAMID",
        "SPHINX",
        "TOMB",
        "CHAMBER",
        "PASSAGE",
    ]

    print(f"Testing if encrypting words with {len(keys)} keys produces the gibberish...\n")

    for section_plaintext, section_name in sections:
        print(f"\n{section_name}: {section_plaintext} ({len(section_plaintext)} chars)")

        # Try to find what word + key would create this section
        for word in common_words:
            if len(word) == len(section_plaintext):
                for key in keys:
                    encrypted = vigenere_encrypt(word, key, STANDARD_ALPHA)
                    if encrypted == section_plaintext:
                        print(f"  MATCH! {word} + key {key} (STD) = {section_plaintext}")

                    encrypted_kryptos = vigenere_encrypt(word, key, KRYPTOS_ALPHA)
                    if encrypted_kryptos == section_plaintext:
                        print(f"  MATCH! {word} + key {key} (KRYPTOS) = {section_plaintext}")

    # Also test: what's the INDEX OF COINCIDENCE of the gibberish?
    print(f"\n{'='*80}")
    print("STATISTICS ON GIBBERISH SECTIONS")
    print(f"{'='*80}\n")

    for plaintext_from_period29, section_name in sections:
        # Calculate IC
        freq = Counter(plaintext_from_period29)
        ic = 0
        n = len(plaintext_from_period29)

        for letter, count in freq.items():
            ic += count * (count - 1) / (n * (n - 1))

        print(f"{section_name:10} | Length: {n:2} | IC: {ic:.4f} | Unique: {len(freq)}")

    print("\nReference: English ~0.067, Random ~0.038")

if __name__ == '__main__':
    main()
