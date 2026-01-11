#!/usr/bin/env python3
"""
Test MPAPGKPVH and related keys as secondary Vigenère keys for K4 gibberish sections.
Tests both standard and KRYPTOS alphabets.
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
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # KRYPTOS + remaining letters (no J, no W duplicated)

def find_words_in_text(text, min_length=3):
    """Find English words in text"""
    words = []
    # Split on non-letters
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

def analyze_decryption(ciphertext, key, alphabet, alphabet_name="Standard"):
    """Decrypt and analyze results"""
    plaintext = vigenere_decrypt(ciphertext, key, alphabet)
    words = find_words_in_text(plaintext)

    # Calculate characteristics
    total_potential = len(re.findall(r'[A-Z]', plaintext))
    word_chars = sum(len(w) for w in words)
    coverage = word_chars / total_potential if total_potential > 0 else 0

    return {
        'plaintext': plaintext,
        'words': words,
        'word_count': len(words),
        'coverage': coverage,
        'alphabet': alphabet_name
    }

def test_key_on_section(ciphertext, key, section_name):
    """Test a key on a ciphertext section with both alphabets"""
    print(f"\n{'='*80}")
    print(f"KEY: {key} | SECTION: {section_name}")
    print(f"{'='*80}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Key length: {len(key)} characters\n")

    results = []

    # Test with standard alphabet
    result_std = analyze_decryption(ciphertext, key, STANDARD_ALPHA, "Standard")
    results.append(result_std)

    # Test with KRYPTOS alphabet
    result_kryptos = analyze_decryption(ciphertext, key, KRYPTOS_ALPHA, "KRYPTOS")
    results.append(result_kryptos)

    # Display results
    for result in results:
        print(f"\n[{result['alphabet']} Alphabet]")
        print(f"Plaintext:  {result['plaintext']}")
        if result['words']:
            print(f"Words found: {', '.join(result['words'])}")
            print(f"Word count: {result['word_count']}, Coverage: {result['coverage']:.1%}")
        else:
            print("No English words found")

    return results

def main():
    print("\n" + "="*80)
    print("TESTING SECONDARY VIGENÈRE KEYS FOR K4 GIBBERISH SECTIONS")
    print("="*80)

    # K4 gibberish sections from the Period 29 solution
    gap1 = "QAPBZDBKZEL"  # 11 chars (positions 5-15)
    gap2_part1 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"  # 38 chars (positions 25-62)
    gap2_subset = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ"  # 29 chars
    gap3 = "RSPVJWQUL"  # 9 chars (positions 74-82)
    gap4 = "ZOLRKCAYF"  # 9 chars (positions 88-96)

    # Keys to test
    keys_to_test = [
        ("MPAPGKPVH", "From Section 3 of gibberish"),
        ("HVPKGPAPM", "MPAPGKPVH reversed"),
        ("AEPLZ", "From 6×6 diagonal"),
        ("ZLPEA", "AEPLZ reversed"),
        ("M", "Single M"),
        ("P", "Single P"),
        ("A", "Single A"),
    ]

    print(f"\nGibberish sections to test:")
    print(f"  Gap1 (11 chars):     {gap1}")
    print(f"  Gap2 (29 chars):     {gap2_subset}")
    print(f"  Gap2 full (38 chars):{gap2_part1}")
    print(f"  Gap3 (9 chars):      {gap3}")
    print(f"  Gap4 (9 chars):      {gap4}")
    print(f"\nKeys to test ({len(keys_to_test)} keys):")
    for key, desc in keys_to_test:
        print(f"  {key:15} - {desc}")

    # Track all findings
    all_results = {}

    # Test each key on each section
    sections = [
        (gap1, "Gap1 (11 chars)"),
        (gap2_subset, "Gap2 (29 chars)"),
        (gap2_part1, "Gap2 Full (38 chars)"),
        (gap3, "Gap3 (9 chars)"),
        (gap4, "Gap4 (9 chars)"),
    ]

    for ciphertext, section_name in sections:
        all_results[section_name] = {}
        for key, key_desc in keys_to_test:
            results = test_key_on_section(ciphertext, key, section_name)
            all_results[section_name][key] = {
                'std': results[0],
                'kryptos': results[1],
                'description': key_desc
            }

    # Summary report
    print(f"\n\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}\n")

    # Find all meaningful results
    meaningful_finds = []
    for section_name, section_results in all_results.items():
        for key, results_pair in section_results.items():
            std_words = results_pair['std']['words']
            kryptos_words = results_pair['kryptos']['words']

            if std_words or kryptos_words:
                meaningful_finds.append({
                    'section': section_name,
                    'key': key,
                    'std_words': std_words,
                    'kryptos_words': kryptos_words,
                    'std_coverage': results_pair['std']['coverage'],
                    'kryptos_coverage': results_pair['kryptos']['coverage']
                })

    if meaningful_finds:
        print(f"Found {len(meaningful_finds)} potential matches:\n")
        for find in meaningful_finds:
            print(f"Section: {find['section']:20} | Key: {find['key']:15}")
            if find['std_words']:
                print(f"  [STD]    Words: {', '.join(find['std_words'])}")
            if find['kryptos_words']:
                print(f"  [KRYPTOS] Words: {', '.join(find['kryptos_words'])}")
            print()
    else:
        print("No English words found with any key-section combination.")

    # Additional analysis - look for patterns
    print(f"\n{'='*80}")
    print("PATTERN ANALYSIS")
    print(f"{'='*80}\n")

    # Check for repeated substrings in gibberish
    print("Analyzing gibberish structure:")
    for ciphertext, section_name in sections:
        print(f"\n{section_name}: {ciphertext}")

        # Look for digraph/trigraph patterns
        digraphs = Counter()
        trigraphs = Counter()
        for i in range(len(ciphertext) - 1):
            digraphs[ciphertext[i:i+2]] += 1
        for i in range(len(ciphertext) - 2):
            trigraphs[ciphertext[i:i+3]] += 1

        if digraphs:
            top_digraphs = digraphs.most_common(3)
            print(f"  Top digraphs: {top_digraphs}")
        if trigraphs:
            top_trigraphs = trigraphs.most_common(3)
            print(f"  Top trigraphs: {top_trigraphs}")

if __name__ == '__main__':
    main()
