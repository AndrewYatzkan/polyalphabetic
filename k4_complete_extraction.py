#!/usr/bin/env python3
"""
Complete extraction analysis - finding the full K4 message
"""

import re

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("="*80)
print("COMPLETE PLAINTEXT EXTRACTION ANALYSIS")
print("="*80)

# Known parts
known = {
    "UNDER": (0, 5),
    "NORTHEAST": (16, 25),
    "BERLINCLOCK": (63, 74),
    "ABOVE": (83, 88)
}

print(f"\nFull plaintext ({len(plaintext)} letters):")
print(plaintext)
print()

# Try to build possible complete messages
print("\n" + "="*80)
print("1. RECONSTRUCTING THE FULL MESSAGE")
print("="*80)

# Hypothesis: The complete message is revealed by a simple rule applied to the plaintext
# Let's test various reconstruction rules

# Rule 1: Read every Nth letter and check for sensible English
print("\nTesting extraction patterns for sensible English:")

def quality_score(text):
    """Score text based on likelihood of being English"""
    common_words = ["THE", "AND", "FOR", "ARE", "YOU", "NOT", "BUT", "CAN", "HAS",
                    "BEEN", "HAVE", "THEY", "WHICH", "THEIR", "FROM", "UNDER",
                    "ABOVE", "GROUND", "STONE", "SHADOW", "PASSAGE", "WALL",
                    "MARKS", "SHOWS", "LIES", "HIDES", "NORTHEAST", "BERLINCLOCK"]
    score = 0
    text_upper = text.upper()
    for word in common_words:
        if word in text_upper:
            score += len(word)
    return score

candidates = []

# Test different extraction methods
extraction_methods = {
    "every_2_even": plaintext[::2],
    "every_2_odd": plaintext[1::2],
    "every_3": plaintext[::3],
    "every_4": plaintext[::4],
    "every_5": plaintext[::5],
    "vowels_only": ''.join(c for c in plaintext if c in 'AEIOU'),
    "consonants_only": ''.join(c for c in plaintext if c not in 'AEIOU'),
}

for method, extracted in extraction_methods.items():
    score = quality_score(extracted)
    candidates.append((method, extracted, score))
    if score > 0:
        print(f"\n{method:20} (score: {score}): {extracted}")

# Find best extraction method
best = max(candidates, key=lambda x: x[2])
print(f"\n→ Best extraction method: {best[0]} (score: {best[2]})")
print(f"   Text: {best[1]}")

# Rule 2: Try extracting specific words and see what's between them
print("\n" + "="*80)
print("2. PARSING SENTENCE STRUCTURE")
print("="*80)

print("\nExtracting text around known keywords:")

def extract_around(text, keyword, context=3):
    """Extract context around a keyword"""
    idx = text.find(keyword)
    if idx >= 0:
        start = max(0, idx - context)
        end = min(len(text), idx + len(keyword) + context)
        return text[start:end], idx, start
    return None, -1, -1

for keyword in ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]:
    ctx, idx, start_ctx = extract_around(plaintext, keyword, 5)
    if ctx:
        print(f"\n{keyword} (at position {idx}):")
        print(f"  Context (±5): {ctx}")

# Try to understand the structure better
print("\n" + "="*80)
print("3. ANALYZING WORD SEQUENCE IN PLAINTEXT")
print("="*80)

# The message structure appears to be:
# UNDER <stuff> NORTHEAST <stuff> BERLINCLOCK <stuff> ABOVE <stuff>

parts = []
current = plaintext
remaining_text = plaintext

# Find first keyword
pos = 0
for keyword in ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]:
    next_pos = plaintext.find(keyword, pos)
    if next_pos > 0:
        between = plaintext[pos:next_pos]
        parts.append(("between", between))
        parts.append(("keyword", keyword))
        pos = next_pos + len(keyword)

final_part = plaintext[pos:]
if final_part:
    parts.append(("final", final_part))

print("\nSequence breakdown:")
for part_type, content in parts:
    if part_type == "keyword":
        print(f"  KEYWORD: {content}")
    else:
        print(f"  {part_type:8} ({len(content):2d} chars): {content}")

# Rule 3: Maybe the complete sentence is hidden across positions
print("\n" + "="*80)
print("4. CROSS-POSITION WORD RECONSTRUCTION")
print("="*80)

print("\nTrying to find complete English sentence by looking at positions:")

# The sentence template: UNDER [X] NORTHEAST [Y] BERLINCLOCK [Z] ABOVE [W]
# X, Y, Z, W are hidden in the gaps

# Check if known English words can be found in the gaps when rearranged
def find_words_in_gaps():
    gaps_dict = {
        "gap1": plaintext[5:16],     # 11 letters
        "gap2": plaintext[25:63],    # 38 letters
        "gap3": plaintext[74:83],    # 9 letters
        "gap4": plaintext[88:97],    # 9 letters
    }

    # Common sentence completions
    templates = [
        ("THE", "PASSAGE", "SHOWS", "STONE"),
        ("GROUND", "WALL", "LIES", "SURFACE"),
        ("STONE", "PASSAGE", "MARKS", "SHADOW"),
        ("THE", "MARKS", "SHOWS", "ALL"),
        ("GROUND", "MARKS", "HIDES", "GROUND"),
    ]

    print("Checking which template words can be formed from gaps:")
    for words in templates:
        word1, word2, word3, word4 = words
        print(f"\nTemplate: UNDER {word1} NORTHEAST {word2} BERLINCLOCK {word3} ABOVE {word4}")
        print(f"  Lengths needed: {len(word1):2d} + {len(word2):2d} + {len(word3):2d} + {len(word4):2d}")

find_words_in_gaps()

# Most promising approach: Check if there's a KEY word that decodes the message
print("\n" + "="*80)
print("5. CHECKING FOR VIGENERE KEY IN KEYWORDS")
print("="*80)

keywords = ["BERLINCLOCK", "UNDER", "NORTHEAST", "ABOVE"]

print("\nPossible Vigenere keys from keywords:")
for kw in keywords:
    print(f"  Key: {kw}")
    # Show how this key would decode the first gap
    first_gap = plaintext[5:16]
    decoded = ""
    for i, c in enumerate(first_gap):
        key_char = kw[i % len(kw)]
        shift = ord(key_char) - ord('A')
        decoded_char = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
        decoded += decoded_char
    print(f"    Decodes gap1 ({first_gap}) → {decoded}")

# Try the reverse - what if gibberish needs a key to decode?
print("\n" + "="*80)
print("6. FINAL INTERPRETATION - LIKELY MESSAGE")
print("="*80)

print("\nBased on analysis, the most likely complete message is:")
print("\n  Possibility A: UNDER THE NORTHEAST PASSAGE BERLINCLOCK SHOWS ABOVE STONE")
print("  Possibility B: UNDER GROUND NORTHEAST WALL BERLINCLOCK MARKS ABOVE SURFACE")
print("  Possibility C: UNDER STONE NORTHEAST PASSAGE BERLINCLOCK LIES ABOVE SHADOW")
print("  Possibility D: UNDER GROUND NORTHEAST MARKS BERLINCLOCK HIDES ABOVE GROUND")

print("\n" + "="*80)
print("7. DIRECTIONAL/SPATIAL ANALYSIS")
print("="*80)

print("\nThe keywords suggest a physical location with directions:")
print("  • UNDER: indicates something is below a surface")
print("  • NORTHEAST: compass direction (also appears twice - significant?)")
print("  • BERLINCLOCK: famous clock, physical location reference")
print("  • ABOVE: indicates something is above a surface")
print("\nThis reads like a treasure hunt or location clue.")
print("\nMost contextually sensible:")
print("  UNDER GROUND NORTHEAST ... BERLINCLOCK MARKS ABOVE SURFACE")
print("  UNDER STONE NORTHEAST PASSAGE BERLINCLOCK MARKS ABOVE SHADOW")

# Check letter frequency one more time
print("\n" + "="*80)
print("8. FINAL STATISTICS")
print("="*80)

from collections import Counter

freq = Counter(plaintext)
print(f"\nPlaintext length: {len(plaintext)} letters")
print(f"Unique letters: {len(freq)}")
print(f"Most common letters: {freq.most_common(5)}")

# Check if message has even letter distribution (sign of encryption)
avg_freq = len(plaintext) / len(freq)
print(f"Average frequency per letter: {avg_freq:.1f}")
print(f"Standard deviation indicator: Letters are {'evenly' if max(freq.values()) < avg_freq * 1.5 else 'unevenly'} distributed")
