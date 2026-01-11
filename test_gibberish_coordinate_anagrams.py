#!/usr/bin/env python3
"""
Deep analysis of gibberish sections as potential coordinate/data encodings.

Key observation: Gap4 (ZOLRKCAYF) can form:
- COROLLARY (9 chars, exact match!)
- ROCKFALL (8 of 9 chars)
- CLOCK (5 chars)
- CORAL (5 chars)

Could these gap sections encode:
1. Coordinates (latitude/longitude)
2. Dates/times
3. Multi-word anagrams
4. Compound words
"""

import itertools
from pathlib import Path

GAP1 = "QAPBZDBKZEL"      # 11 chars
GAP2B = "MPAPGKPVH"        # 9 chars
GAP3 = "RSPVJWQUL"         # 9 chars
GAP4 = "ZOLRKCAYF"         # 9 chars

def load_wordlist():
    """Load comprehensive English word list"""
    words = set()

    # Try to load system dictionary
    try:
        with open('/usr/share/dict/words', 'r') as f:
            words = {w.upper().strip() for w in f if len(w.strip()) >= 3 and w.strip().isalpha()}
    except:
        pass

    # Add known/relevant words
    extra_words = {
        "COROLLARY", "ROCKFALL", "CLOCK", "CORAL", "COAL", "FLACK", "FORK", "WOLF",
        "BERLINCLOCK", "COORDINATES", "LATITUDE", "LONGITUDE", "DEGREES", "MINUTES",
        "SECONDS", "NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST",
        "SOUTHEAST", "SOUTHWEST", "ABOVE", "BELOW", "UNDER", "OVER",
        "PRAYER", "PLAYED", "SPRAYED", "FORCED", "SCORES", "SURFACED",
        "SPARE", "SPEAR", "REAPS", "PAIRS", "VIALS", "RIALS", "SUPER", "PURSE",
        "PURPLE", "LURKED", "SULKED", "JUMPED", "WURST", "FIRST", "DRIFT",
        "SWIFT", "CRAFT", "DRAFT", "WRIST", "WORST", "TWIST", "QUEST", "QUEST",
        "SQUID", "LIQUID", "COPULA", "FOCUS", "LOCUS", "JUGGLER", "PUZZLE",
        "RAZZLE", "DAZZLE", "FIZZLE", "PUZZLE", "MUZZLE", "NUZZLE", "GUZZLE",
        "SQUALID", "PLAQUES", "OPAQUE", "GROTESQUE",
    }

    words.update(extra_words)
    return words

def find_anagrams_exact(text, wordlist):
    """Find exact anagrams"""
    text_sorted = ''.join(sorted(text.upper()))
    anagrams = []
    for word in wordlist:
        if len(word) == len(text.upper()) and ''.join(sorted(word)) == text_sorted:
            anagrams.append(word)
    return anagrams

def find_multi_word_anagrams(text, wordlist, max_words=3):
    """Find multi-word anagrams"""
    text_upper = text.upper()
    char_list = list(text_upper)

    results = []

    # Try combinations of 2 words
    if max_words >= 2:
        for len1 in range(1, len(text_upper) - 1):
            for word1 in wordlist:
                if len(word1) == len1:
                    # Check if word1 can be formed from text
                    remaining = char_list.copy()
                    can_form = True
                    for c in word1:
                        if c in remaining:
                            remaining.remove(c)
                        else:
                            can_form = False
                            break

                    if can_form:
                        # Try to form second word from remaining
                        remaining_text = ''.join(remaining)
                        for word2 in wordlist:
                            if ''.join(sorted(word2)) == ''.join(sorted(remaining_text)):
                                results.append((word1, word2))

    # Try combinations of 3 words
    if max_words >= 3:
        for len1 in range(1, len(text_upper) - 2):
            for len2 in range(1, len(text_upper) - len1 - 1):
                for word1 in [w for w in wordlist if len(w) == len1]:
                    remaining1 = char_list.copy()
                    can_form1 = True
                    for c in word1:
                        if c in remaining1:
                            remaining1.remove(c)
                        else:
                            can_form1 = False
                            break

                    if can_form1:
                        for word2 in [w for w in wordlist if len(w) == len2]:
                            remaining2 = remaining1.copy()
                            can_form2 = True
                            for c in word2:
                                if c in remaining2:
                                    remaining2.remove(c)
                                else:
                                    can_form2 = False
                                    break

                            if can_form2:
                                remaining_text = ''.join(remaining2)
                                for word3 in wordlist:
                                    if ''.join(sorted(word3)) == ''.join(sorted(remaining_text)):
                                        results.append((word1, word2, word3))

    return results

def find_substring_words(text, wordlist, min_length=3):
    """Find words that can be spelled using the characters (not necessarily all)"""
    text_upper = text.upper()
    words_possible = []

    for word in wordlist:
        can_form = all(c in text_upper for c in word)
        if can_form and len(word) >= min_length:
            words_possible.append(word)

    return words_possible

def analyze_letter_patterns(text):
    """Analyze letter patterns that might indicate coordinates or data"""
    print(f"  Letter analysis of {text}:")

    # Check if it looks like coordinates (numbers encoded as letters)
    # Coordinates often have patterns like: 38°55'06.0"N 77°02'56.1"W
    # Could be encoded as letter pairs

    pairs = [text[i:i+2] for i in range(0, len(text), 2)]
    print(f"    As pairs: {' '.join(pairs)}")

    # Try interpreting as position-based encoding
    # A=0, B=1, ..., Z=25
    values = [ord(c) - ord('A') for c in text]
    print(f"    As numbers (A=0): {values}")
    print(f"    Mod 10: {[v % 10 for v in values]}")

    # Check for patterns
    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
    print(f"    Differences: {diffs}")

def test_gap_analysis():
    """Comprehensive gap analysis"""
    print("="*70)
    print("COMPREHENSIVE GIBBERISH GAP ANALYSIS")
    print("="*70)

    gaps = [
        ("GAP1", GAP1),
        ("GAP2B", GAP2B),
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    wordlist = load_wordlist()

    for name, gap_text in gaps:
        print(f"\n{name}: {gap_text} ({len(gap_text)} chars, {len(set(gap_text))} unique)")

        # Exact anagrams
        exact_anagrams = find_anagrams_exact(gap_text, wordlist)
        if exact_anagrams:
            print(f"  EXACT ANAGRAMS: {exact_anagrams}")
        else:
            print(f"  No exact anagrams found")

        # Multi-word anagrams
        multi_anagrams = find_multi_word_anagrams(gap_text, wordlist, max_words=2)
        if multi_anagrams:
            print(f"  MULTI-WORD ANAGRAMS (2 words):")
            for pair in multi_anagrams[:10]:  # Limit output
                print(f"    {pair[0]} + {pair[1]}")

        # Substring words
        substring_words = find_substring_words(gap_text, wordlist, min_length=4)
        if substring_words:
            print(f"  POSSIBLE SUBSTRING WORDS (5+ chars):")
            for word in sorted(substring_words)[:10]:
                print(f"    {word}")

        # Pattern analysis
        analyze_letter_patterns(gap_text)

def special_focus_gap4():
    """Special analysis for Gap4 since it has interesting patterns"""
    print("\n" + "="*70)
    print("SPECIAL ANALYSIS: GAP4 (ZOLRKCAYF)")
    print("="*70)

    print("\nObservation: Gap4 uses exactly these characters:")
    print(f"  Z O L R K C A Y F")

    print("\nWords that can be formed:")
    # COROLLARY is interesting because it's 9 letters and uses Z, O, L, R, K, C, A, Y, F
    # Let's check if letters match
    gap4_chars = set("ZOLRKCAYF")
    corollary_chars = set("COROLLARY")

    print(f"\n  COROLLARY needs: {sorted(corollary_chars)}")
    print(f"  Gap4 has:       {sorted(gap4_chars)}")
    print(f"  Match: {gap4_chars == corollary_chars}")

    if gap4_chars == corollary_chars:
        print("\n  *** CRITICAL: Gap4 is an ANAGRAM OF 'COROLLARY'! ***")
        print("\n  Possible orderings of COROLLARY using Gap4 letter sequence:")

        # Generate a few permutations
        from itertools import permutations
        gap4_perms = set([''.join(p) for p in permutations(GAP4)])

        if 'COROLLARY' in gap4_perms:
            print("  - COROLLARY found in permutations!")

        # Check distances
        print("\n  Letter position mapping:")
        for i, c in enumerate(GAP4):
            for j, target in enumerate("COROLLARY"):
                if c == target:
                    print(f"    Gap4[{i}] = {c} could be Corollary[{j}]")

def test_coordinate_encoding():
    """Test if gaps encode coordinates"""
    print("\n" + "="*70)
    print("COORDINATE ENCODING HYPOTHESIS")
    print("="*70)

    # Known coordinates for Kryptos (in DC, USA)
    # Approximate: 38°55'06.0"N 77°02'56.1"W
    # Could be encoded various ways

    print("\nKryptos location (DC):")
    print("  Latitude: 38°55'06.0\"N = 38.918333°N")
    print("  Longitude: 77°02'56.1\"W = -77.048917°W")

    # Try to find these numbers in gaps
    gaps = [GAP1, GAP2B, GAP3, GAP4]
    gap_names = ["GAP1", "GAP2B", "GAP3", "GAP4"]

    for name, gap in zip(gap_names, gaps):
        print(f"\n  {name}: {gap}")

        # Convert to numbers (A=0, B=1, ..., Z=25)
        nums = [ord(c) - ord('A') for c in gap]
        print(f"    As numbers (0-25): {nums}")

        # Try mod 10
        nums_mod10 = [n % 10 for n in nums]
        print(f"    Mod 10: {nums_mod10}")

        # Try to find coordinate-like patterns
        concat = ''.join(str(n % 10) for n in nums)
        if "38" in concat or "55" in concat or "06" in concat:
            print(f"    *** FOUND POSSIBLE COORDINATE PATTERN ***")

def main():
    test_gap_analysis()
    special_focus_gap4()
    test_coordinate_encoding()

if __name__ == "__main__":
    main()
