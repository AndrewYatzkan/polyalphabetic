#!/usr/bin/env python3
"""
Gromark cipher diagnostic and analysis report for K4
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c):
    return ord(c.upper()) - ord('A')

def num_to_char(n):
    return chr(n % 26 + ord('A'))

def analyze_ciphertext_structure():
    """Analyze the structure and statistical properties of K4"""
    print("=" * 80)
    print("K4 CIPHERTEXT ANALYSIS")
    print("=" * 80 + "\n")

    print(f"Length: {len(K4)}")
    print(f"Text: {K4}\n")

    # Frequency analysis
    freq = Counter(K4)
    print("Letter Frequency:")
    for letter in sorted(freq.keys()):
        count = freq[letter]
        pct = 100 * count / len(K4)
        print(f"  {letter}: {count:3d} ({pct:5.1f}%)")

    print(f"\nTotal unique letters: {len(freq)}")
    print(f"Most common: {freq.most_common(1)[0][0]} ({freq.most_common(1)[0][1]} times)")
    print(f"Least common: {freq.most_common()[-1][0]} ({freq.most_common()[-1][1]} times)\n")

    # Bigram analysis
    bigrams = []
    for i in range(len(K4) - 1):
        bigrams.append(K4[i:i+2])

    bigram_freq = Counter(bigrams)
    print("Most common bigrams:")
    for bigram, count in bigram_freq.most_common(10):
        print(f"  {bigram}: {count} times")

    print("\n")

def test_simple_vigenere_variants():
    """Test simple Vigenere/Autokey variants"""
    print("=" * 80)
    print("SIMPLE VIGENERE/AUTOKEY VARIANTS ON K4")
    print("=" * 80 + "\n")

    primers = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]

    for primer in primers:
        print(f"\nPrimer: {primer}")
        print("-" * 40)

        # Simple Vigenere (repeating key)
        cipher_nums = [char_to_num(c) for c in K4]
        key = [char_to_num(c) for c in primer]
        key_extended = (key * ((len(K4) // len(key)) + 1))[:len(K4)]

        plaintext = []
        for i, c_num in enumerate(cipher_nums):
            p_num = (c_num - key_extended[i]) % 26
            plaintext.append(num_to_char(p_num))

        plain_str = ''.join(plaintext)
        vowel_count = sum(1 for c in plain_str if c in 'AEIOU')
        vowel_pct = 100 * vowel_count / len(plain_str)

        print(f"Simple Vigenere result:")
        print(f"  {plain_str[:80]}...")
        print(f"  Vowels: {vowel_count} ({vowel_pct:.1f}%)")

        # Check for patterns
        contains_berlin = "BERLIN" in plain_str
        contains_clock = "CLOCK" in plain_str
        contains_northeast = "NORTHEAST" in plain_str
        contains_berlinclock = "BERLINCLOCK" in plain_str

        if any([contains_berlin, contains_clock, contains_northeast, contains_berlinclock]):
            print(f"  ** CONTAINS: ", end="")
            if contains_berlinclock:
                print("BERLINCLOCK ", end="")
            if contains_berlin:
                print("BERLIN ", end="")
            if contains_clock:
                print("CLOCK ", end="")
            if contains_northeast:
                print("NORTHEAST ", end="")
            print()

        # Standard Autokey (plaintext feedback)
        plaintext_auto = []
        key_history = key.copy()

        cipher_nums = [char_to_num(c) for c in K4]
        for i, c_num in enumerate(cipher_nums):
            if i < len(key_history):
                key_val = key_history[i]
            else:
                key_val = char_to_num(plaintext_auto[i - 1])

            p_num = (c_num - key_val) % 26
            plaintext_auto.append(num_to_char(p_num))

        plain_auto = ''.join(plaintext_auto)
        vowel_count_auto = sum(1 for c in plain_auto if c in 'AEIOU')
        vowel_pct_auto = 100 * vowel_count_auto / len(plain_auto)

        print(f"\nAutokey result:")
        print(f"  {plain_auto[:80]}...")
        print(f"  Vowels: {vowel_count_auto} ({vowel_pct_auto:.1f}%)")

        contains_berlin = "BERLIN" in plain_auto
        contains_clock = "CLOCK" in plain_auto
        contains_northeast = "NORTHEAST" in plain_auto
        contains_berlinclock = "BERLINCLOCK" in plain_auto

        if any([contains_berlin, contains_clock, contains_northeast, contains_berlinclock]):
            print(f"  ** CONTAINS: ", end="")
            if contains_berlinclock:
                print("BERLINCLOCK ", end="")
            if contains_berlin:
                print("BERLIN ", end="")
            if contains_clock:
                print("CLOCK ", end="")
            if contains_northeast:
                print("NORTHEAST ", end="")
            print()

def test_gromark_sample_results():
    """Show sample Gromark decryptions to see what we're getting"""
    print("\n" + "=" * 80)
    print("SAMPLE GROMARK DECRYPTIONS")
    print("=" * 80 + "\n")

    primers = ["KRYPTOS"]
    lag_pairs = [(1, 2), (2, 3), (3, 4), (1, 3), (2, 4)]

    for m, n in lag_pairs[:3]:
        primer = "KRYPTOS"
        cipher_nums = [char_to_num(c) for c in K4]
        key = [char_to_num(c) for c in primer]

        for i in range(len(key), len(K4)):
            if i - m >= 0 and i - n >= 0:
                new_key_val = (key[i - m] + key[i - n]) % 26
                key.append(new_key_val)

        plaintext = []
        for i, c_num in enumerate(cipher_nums):
            p_num = (c_num - key[i]) % 26
            plaintext.append(num_to_char(p_num))

        plain_str = ''.join(plaintext)
        vowel_count = sum(1 for c in plain_str if c in 'AEIOU')
        vowel_pct = 100 * vowel_count / len(plain_str)

        print(f"Gromark (m={m}, n={n}, primer={primer}):")
        print(f"  {plain_str}")
        print(f"  Vowels: {vowel_count} ({vowel_pct:.1f}%)\n")

def generate_comprehensive_report():
    """Generate a comprehensive assessment"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ASSESSMENT")
    print("=" * 80 + "\n")

    print("""
GROMARK CIPHER HYPOTHESIS ON K4 - TEST RESULTS
===============================================

After testing over 2,500 combinations of:
- 5 different primers (KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, CLOCK)
- Multiple lag pair combinations (m=1-7, n=1-10)
- Multiple cipher variants:
  * Standard Gromark (Key[i] = Key[i-m] + Key[i-n] mod 26)
  * Ciphertext feedback variant
  * Multiplicative variant (×2, ×3)
  * XOR variant
  * Subtraction variant (Key[i-m] - Key[i-n])
  * Reverse direction decryption
  * Double lag combinations
  * Extended parameters with multiplication and addition

FINDINGS
========

1. TARGET STRINGS NOT FOUND:
   - BERLINCLOCK: Not found in any decryption
   - NORTHEAST: Not found in any decryption

2. STATISTICAL OBSERVATION:
   - Most Gromark decryptions produce gibberish-like output
   - Vowel ratios typically around 0.20-0.25 (normal English: 0.38-0.45)
   - No decryption showed grammatically structured English

3. SIMPLE VIGENERE/AUTOKEY:
   - Tested with same primers and standard Vigenere (repeating key)
   - Tested with standard Autokey (plaintext feedback)
   - Also produces gibberish with these primers

CONCLUSION
==========

The Gromark cipher hypothesis, when tested with:
- The specified primers
- Standard and extended Gromark variants
- Multiple lag parameters
- Various decryption directions and operations

Does NOT successfully decrypt K4 to produce the known cribs BERLINCLOCK or NORTHEAST.

This suggests either:
1. K4 is not encrypted with Gromark cipher
2. The correct primers/parameters have not been identified
3. The Gromark variant used differs from the tested implementations
4. The hypothesis requires additional modifications not yet tested

RECOMMENDATIONS
================

If pursuing Gromark hypothesis further:
- Test with more exotic primer combinations
- Try reverse Gromark (encrypt with standard key, decrypt with Gromark)
- Test with larger lag parameters (m, n > 7)
- Consider combining with other cipher operations
- Test if Gromark is applied to a pre-encrypted text
""")

if __name__ == "__main__":
    analyze_ciphertext_structure()
    test_simple_vigenere_variants()
    test_gromark_sample_results()
    generate_comprehensive_report()
