#!/usr/bin/env python3
"""
Focused testing on TRANSPOSITIONS and ANAGRAMS for gibberish sections.

Key findings from previous research:
- Gap3 (RSPVJWQUL): 9 unique characters
- Gap4 (ZOLRKCAYF): 9 unique characters
- These sections might be pure transpositions/anagrams

This script tests:
1. Anagram reconstruction
2. Columnar transposition with various key widths
3. Rail fence transposition variants
4. Simple permutations
5. XOR-based masking
6. Substitution cipher patterns
"""

import itertools
from collections import Counter
from pathlib import Path

# All gibberish sections from K4
GIBBERISH_FULL = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

# Individual gaps
GAP1 = "QAPBZDBKZEL"      # 11 chars
GAP2A = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ"  # 29 chars
GAP2B = "MPAPGKPVH"        # 9 chars
GAP3 = "RSPVJWQUL"         # 9 chars, all unique
GAP4 = "ZOLRKCAYF"         # 9 chars, all unique

# Load word list
def load_wordlist():
    """Load English word list"""
    words = set()
    try:
        with open('/usr/share/dict/words', 'r') as f:
            words = {w.upper().strip() for w in f if len(w.strip()) >= 3}
    except:
        # Fallback to common words
        words = {
            "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
            "WAS", "ONE", "OUR", "OUT", "NOW", "NEW", "HAD", "HIS", "HOW", "ITS",
            "MAY", "SAY", "SHE", "TOO", "USE", "WHO", "BOY", "DID", "GET", "GOT",
            "LET", "PUT", "SAY", "WAY", "WHO", "BERLIN", "CLOCK", "NORTH", "EAST",
            "COORDINATES", "NORTHEAST", "ABOVE", "UNDER", "BELOW", "INSIDE", "OUTSIDE",
            "LATITUDE", "LONGITUDE", "DEGREE", "MINUTE", "SECOND",
            "SURPLUS", "SLURP", "LUPUS", "COROLLARY", "ROCKFALL",
            "PRAYER", "PLAYED", "SPRAYED", "SURFACED", "FORCED", "SCORES",
            "WRIST", "WORST", "TWIST", "SWIFT", "CLIFF", "CRAFT", "DRAFT",
            "FOUND", "SOUND", "ROUND", "GROUND", "POUND", "MOUND", "BOUND",
        }
    return words

def find_anagrams(text, wordlist):
    """Find all anagrams of text in wordlist"""
    text_sorted = ''.join(sorted(text.upper()))
    anagrams = []
    for word in wordlist:
        if len(word) == len(text) and ''.join(sorted(word)) == text_sorted:
            anagrams.append(word)
    return anagrams

def columnar_transposition_decrypt(ciphertext, key_width):
    """Try decrypting with columnar transposition (naive approach)"""
    ct = ciphertext.upper()
    n = len(ct)

    if n % key_width != 0:
        return []  # Can't evenly divide

    num_rows = n // key_width

    # Try all permutations of column order (expensive but needed)
    results = []

    # For efficiency, only try a few key orders
    # Try: reading left-to-right, then try various reversals
    key_orders = [
        list(range(key_width)),  # Normal order
        list(range(key_width))[::-1],  # Reverse order
    ]

    # Try shifted orders (simulating different key values)
    for shift in range(min(key_width, 5)):
        order = [(i + shift) % key_width for i in range(key_width)]
        key_orders.append(order)

    for order in key_orders:
        plaintext = ""
        for row in range(num_rows):
            for col in order:
                idx = col * num_rows + row
                if idx < n:
                    plaintext += ct[idx]

        results.append(plaintext)

    return results

def rail_fence_decrypt(ciphertext, num_rails):
    """Decrypt rail fence cipher"""
    ct = ciphertext.upper()
    n = len(ct)

    # Calculate positions for each rail
    if num_rails == 1:
        return ct

    fence = [[] for _ in range(num_rails)]
    rail = 0
    direction = 1

    # Count characters per rail
    for i in range(n):
        fence[rail].append(None)
        if num_rails > 1:
            rail += direction
            if rail == 0 or rail == num_rails - 1:
                direction *= -1

    # Fill in the ciphertext
    idx = 0
    for r in range(num_rails):
        for i in range(len(fence[r])):
            fence[r][i] = ct[idx]
            idx += 1

    # Read off the plaintext
    plaintext = ""
    rail = 0
    direction = 1
    for i in range(n):
        plaintext += fence[rail][0] if fence[rail] else ""
        if fence[rail]:
            fence[rail] = fence[rail][1:]
        if num_rails > 1:
            rail += direction
            if rail == 0 or rail == num_rails - 1:
                direction *= -1

    return plaintext

def xor_patterns(ciphertext):
    """Test XOR with various patterns"""
    ct = ciphertext.upper()
    results = []

    # Try XOR with simple patterns
    patterns = [
        "KRYPTOS",
        "PALIMPSEST",
        "ABSCISSA",
        "BERLIN",
        "CLOCK",
        "12345678",
        "AAAAAA",
        "ZYXWVU",
    ]

    for pattern in patterns:
        plaintext = ""
        for i, c in enumerate(ct):
            if c.isalpha():
                p_char = pattern[i % len(pattern)]
                if p_char.isalpha():
                    shift = ord(p_char.upper()) - ord('A')
                    plaintext += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
                else:
                    shift = int(p_char)
                    plaintext += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            else:
                plaintext += c

        results.append((pattern, plaintext))

    return results

def test_gap3_anagrams():
    """Test anagrams for Gap3 (all unique characters)"""
    print("\n" + "="*70)
    print("GAP3 ANAGRAM ANALYSIS")
    print("="*70)
    print(f"Gap3: {GAP3} (9 unique characters)")

    wordlist = load_wordlist()
    anagrams = find_anagrams(GAP3, wordlist)

    if anagrams:
        print(f"Found {len(anagrams)} anagrams:")
        for word in sorted(anagrams):
            print(f"  - {word}")
    else:
        print("No standard English word anagrams found")

    # Try permutations manually for some patterns
    print("\nLooking for partial word matches:")
    gap3_chars = list(GAP3)

    # Try to find words using 5-7 of the characters
    test_words = ["WRIST", "WORST", "TWIST", "SWIFT", "CRAFT", "DRIFT", "SPURT",
                  "COULD", "WOULD", "SHOULD", "PRAYER", "PLAYED", "PRAYED"]

    for word in test_words:
        if all(c in gap3_chars for c in word):
            print(f"  Possible: {word} (uses {len(word)} of {len(gap3_chars)} chars)")

def test_gap4_anagrams():
    """Test anagrams for Gap4 (all unique characters)"""
    print("\n" + "="*70)
    print("GAP4 ANAGRAM ANALYSIS")
    print("="*70)
    print(f"Gap4: {GAP4} (9 unique characters)")

    wordlist = load_wordlist()
    anagrams = find_anagrams(GAP4, wordlist)

    if anagrams:
        print(f"Found {len(anagrams)} anagrams:")
        for word in sorted(anagrams):
            print(f"  - {word}")
    else:
        print("No standard English word anagrams found")

    # Try permutations manually
    print("\nLooking for partial word matches:")
    gap4_chars = list(GAP4)

    test_words = ["CLOCK", "CORAL", "COAL", "FOLD", "FLOW", "COROLLARY", "ROCKFALL",
                  "FLACK", "FORCE", "FORK", "WOLF"]

    for word in test_words:
        if all(c in gap4_chars for c in word):
            print(f"  Possible: {word} (uses {len(word)} of {len(gap4_chars)} chars)")

def test_columnar_transposition():
    """Test columnar transposition on all gaps"""
    print("\n" + "="*70)
    print("COLUMNAR TRANSPOSITION ANALYSIS")
    print("="*70)

    gaps = [
        ("Gap1", GAP1),
        ("Gap2A", GAP2A),
        ("Gap2B", GAP2B),
        ("Gap3", GAP3),
        ("Gap4", GAP4),
    ]

    wordlist = load_wordlist()

    for gap_name, gap_text in gaps:
        print(f"\n{gap_name}: {gap_text}")
        length = len(gap_text)
        print(f"Length: {length} (factors: {[i for i in range(2, length) if length % i == 0]})")

        # Try columnar transposition with all factors
        factors = [i for i in range(2, min(length, 15)) if length % i == 0]

        found_any = False
        for width in factors:
            results = columnar_transposition_decrypt(gap_text, width)
            for plaintext in results:
                # Check for words
                word_count = sum(1 for word in plaintext.split() if word in wordlist)
                if word_count > 0:
                    print(f"  Width {width}: Found {word_count} words: {plaintext}")
                    found_any = True

        if not found_any:
            print(f"  No word patterns found with columnar transposition")

def test_rail_fence():
    """Test rail fence transposition"""
    print("\n" + "="*70)
    print("RAIL FENCE TRANSPOSITION ANALYSIS")
    print("="*70)

    gaps = [
        ("Gap3", GAP3),
        ("Gap4", GAP4),
    ]

    wordlist = load_wordlist()

    for gap_name, gap_text in gaps:
        print(f"\n{gap_name}: {gap_text}")

        for num_rails in range(2, min(len(gap_text), 8)):
            plaintext = rail_fence_decrypt(gap_text, num_rails)
            word_count = sum(1 for word in plaintext.split() if word in wordlist)

            if word_count > 0 or any(word in plaintext for word in ["THE", "AND", "FOR"]):
                print(f"  {num_rails} rails: {plaintext}")

def test_xor():
    """Test XOR masking"""
    print("\n" + "="*70)
    print("XOR MASKING ANALYSIS")
    print("="*70)

    gaps = [
        ("Gap3", GAP3),
        ("Gap4", GAP4),
    ]

    for gap_name, gap_text in gaps:
        print(f"\n{gap_name}: {gap_text}")

        results = xor_patterns(gap_text)
        for pattern, plaintext in results:
            vowels = sum(1 for c in plaintext if c in "AEIOU")
            if vowels > len(plaintext) * 0.2:  # Good vowel ratio
                print(f"  XOR {pattern:15s}: {plaintext}")

def test_simple_substitution():
    """Test if gibberish is simple substitution"""
    print("\n" + "="*70)
    print("SIMPLE SUBSTITUTION DETECTION")
    print("="*70)

    gaps = [
        ("Gap3", GAP3),
        ("Gap4", GAP4),
    ]

    for gap_name, gap_text in gaps:
        print(f"\n{gap_name}: {gap_text}")

        # Check digraph patterns
        digraphs = {}
        for i in range(len(gap_text) - 1):
            dg = gap_text[i:i+2]
            digraphs[dg] = digraphs.get(dg, 0) + 1

        print(f"  Digraphs: {digraphs}")
        print(f"  Unique digraphs: {len(digraphs)}")

        # Check letter frequency
        freq = Counter(gap_text)
        print(f"  Letter frequency: {sorted(freq.items(), key=lambda x: x[1], reverse=True)}")

        # High entropy suggests strong encryption, not simple substitution
        entropy = sum(-(p/len(gap_text) * 2.33 * (p/len(gap_text))) for p in freq.values())
        print(f"  Entropy: {entropy:.2f}")

def main():
    print("TRANSPOSITION AND ANAGRAM ANALYSIS OF K4 GIBBERISH")
    print("="*70)

    test_gap3_anagrams()
    test_gap4_anagrams()
    test_columnar_transposition()
    test_rail_fence()
    test_xor()
    test_simple_substitution()

if __name__ == "__main__":
    main()
