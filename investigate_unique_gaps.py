#!/usr/bin/env python3
"""
ANOMALY INVESTIGATION: Gap3 (RSPVJWQUL) and Gap4 (ZOLRKCAYF)
Investigation of 9 unique letters with 1 in 362 million probability
"""

import itertools
from collections import Counter
import math

# Gap data
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

print("=" * 80)
print("ANOMALY INVESTIGATION: Gap3 and Gap4 - Unique Letters Analysis")
print("=" * 80)

# ===== HYPOTHESIS 1: ANAGRAMS =====
print("\n[HYPOTHESIS 1] ANAGRAMS OF ENGLISH WORDS")
print("-" * 80)

# Common English word patterns
# Let's check if these could be anagrams of real words
def is_anagram(word1, word2):
    """Check if two words are anagrams"""
    return sorted(word1.lower()) == sorted(word2.lower())

# Load a word list (we'll try some common words)
common_words = [
    # 9-letter words
    "PLAYGROUP", "WAREHOUSE", "BLUEPRINT", "SCULPTURE", "ALGORITHM",
    "LANDSCAPE", "TRANSLATE", "VARIABLES", "FIREPLACE", "CLOUDLESS",
    "WRESTLING", "PINEAPPLE", "NIGHTMARE", "CHOCOLATE", "BUTTERFLY",
    "PARAGRAPH", "THEREFORE", "CELEBRATE", "CORPORATE", "DESPERATE",
    "BEAUTIFUL", "DIFFERENT", "EMERGENCY", "FURNITURE", "GUARANTEE",
    "HAZARDOUS", "IMPORTANT", "KNOWLEDGE", "MEANWHILE", "NECESSARY",
    "ORCHESTRA", "POLITICIAN", "QUESTIONS", "RECTANGLE", "SOMETHING",
    "TECHNICAL", "UNIVERSAL", "VOLUNTARY", "WATERMELON", "YESTERDAY",
    # 9-letter words that might match
    "SURPLUS", "SLURP", "LUPUS", "SPRAWL", "PULPS", "JURYS",
    "CORRUPT", "LOCKJAW", "CLAYWORK", "ROCKFALL", "CORALFLY",
    "QUALIFY", "SQUIRREL", "QUARTERS", "SPARKLED", "PLUCKING",
    "WASPLIKE", "PURSEFUL", "SPRAWLED", "SQUALLED", "PALSYING",
    "SPRAWLUP", "PULSWRAP", "SPURWALK", "VULPRASS", "JUKESLAP",
    # More 9-letter combinations
    "SPRUCELY", "SQUIRRELY", "SPRINKLE", "SPRAWLIER", "SPARKLING"
]

# Additional specialized words
specialized = [
    "ROCKFALL", "CORALFLY", "CLAYWORK", "QUARRELS", "QUALIFY",
    "LACKSPUR", "SULFURLY", "SPRAWLUP", "CORSAULT", "CORKSCREW",
    "OVERLAPS", "OVERLAID", "OVERLAST", "OVERLAWS", "OVERLAYS",
    "ZEALOTRY", "CARRYOFF", "FAVORABLE", "FLORALLY", "FORCIBLY"
]

gap3_anagrams = []
gap4_anagrams = []

all_words = common_words + specialized

for word in all_words:
    if len(word) == 9:
        if is_anagram(word, GAP3):
            gap3_anagrams.append(word)
        if is_anagram(word, GAP4):
            gap4_anagrams.append(word)

print(f"\nGap3 ({GAP3}) Anagrams Found: {gap3_anagrams if gap3_anagrams else 'NONE'}")
print(f"Gap4 ({GAP4}) Anagrams Found: {gap4_anagrams if gap4_anagrams else 'NONE'}")

# ===== HYPOTHESIS 2: MISSING LETTERS =====
print("\n[HYPOTHESIS 2] MISSING LETTERS FROM ALPHABET")
print("-" * 80)

ALPHABET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
gap3_letters = set(GAP3)
gap4_letters = set(GAP4)
combined = gap3_letters | gap4_letters

missing = ALPHABET - combined
print(f"\nGap3 letters: {sorted(gap3_letters)}")
print(f"Gap4 letters: {sorted(gap4_letters)}")
print(f"Combined (18 unique): {sorted(combined)}")
print(f"Missing from alphabet (8 letters): {sorted(missing)}")

# Check if missing letters spell anything
print(f"\nMissing letters as string: {''.join(sorted(missing))}")
missing_permutations = list(itertools.permutations(sorted(missing)))
print(f"Possible arrangements: {len(missing_permutations)} permutations")
print(f"First 10 arrangements: {[''.join(p) for p in missing_permutations[:10]]}")

# ===== HYPOTHESIS 3: COORDINATES FORMAT =====
print("\n[HYPOTHESIS 3] COORDINATE ENCODING (DDD°MM'SS\")")
print("-" * 80)

# Try to extract coordinate values
def letter_value(letter):
    """A=1, B=2, ..., Z=26"""
    return ord(letter.upper()) - ord('A') + 1

def letter_to_digit(letter):
    """A=0, B=1, ..., I=8, J=9"""
    val = ord(letter.upper()) - ord('A')
    return val % 10

print("\nGap3 as numeric sequence:")
print(f"  Letter values (A=1...Z=26): {[letter_value(c) for c in GAP3]}")
print(f"  As digits (A=0...J=9): {[letter_to_digit(c) for c in GAP3]}")
print(f"  Sum of values: {sum(letter_value(c) for c in GAP3)}")
print(f"  Average: {sum(letter_value(c) for c in GAP3) / len(GAP3):.2f}")

print("\nGap4 as numeric sequence:")
print(f"  Letter values (A=1...Z=26): {[letter_value(c) for c in GAP4]}")
print(f"  As digits (A=0...J=9): {[letter_to_digit(c) for c in GAP4]}")
print(f"  Sum of values: {sum(letter_value(c) for c in GAP4)}")
print(f"  Average: {sum(letter_value(c) for c in GAP4) / len(GAP4):.2f}")

# ===== HYPOTHESIS 4: LETTER VALUES PATTERN =====
print("\n[HYPOTHESIS 4] LETTER VALUE ANALYSIS")
print("-" * 80)

gap3_values = [letter_value(c) for c in GAP3]
gap4_values = [letter_value(c) for c in GAP4]

print(f"\nGap3 Values: {gap3_values}")
print(f"  R={gap3_values[0]}, S={gap3_values[1]}, P={gap3_values[2]}, V={gap3_values[3]}, "
      f"J={gap3_values[4]}, W={gap3_values[5]}, Q={gap3_values[6]}, U={gap3_values[7]}, L={gap3_values[8]}")

print(f"\nGap4 Values: {gap4_values}")
print(f"  Z={gap4_values[0]}, O={gap4_values[1]}, L={gap4_values[2]}, R={gap4_values[3]}, "
      f"K={gap4_values[4]}, C={gap4_values[5]}, A={gap4_values[6]}, Y={gap4_values[7]}, F={gap4_values[8]}")

# Check for patterns
print(f"\nGap3 differences: {[gap3_values[i+1] - gap3_values[i] for i in range(len(gap3_values)-1)]}")
print(f"Gap4 differences: {[gap4_values[i+1] - gap4_values[i] for i in range(len(gap4_values)-1)]}")

# Check for mathematical patterns
print(f"\nGap3 sum: {sum(gap3_values)} (average per letter: {sum(gap3_values)/9:.2f})")
print(f"Gap4 sum: {sum(gap4_values)} (average per letter: {sum(gap4_values)/9:.2f})")
print(f"Combined sum: {sum(gap3_values) + sum(gap4_values)}")

# ===== HYPOTHESIS 5: MODULAR ARITHMETIC =====
print("\n[HYPOTHESIS 5] MODULAR ARITHMETIC PATTERNS")
print("-" * 80)

print(f"\nGap3 mod 10: {[letter_value(c) % 10 for c in GAP3]}")
print(f"Gap4 mod 10: {[letter_value(c) % 10 for c in GAP4]}")

print(f"\nGap3 mod 9: {[letter_value(c) % 9 for c in GAP3]}")
print(f"Gap4 mod 9: {[letter_value(c) % 9 for c in GAP4]}")

# ===== HYPOTHESIS 6: POSITION ANALYSIS =====
print("\n[HYPOTHESIS 6] POSITION IN K4 PLAINTEXT")
print("-" * 80)

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print(f"\nK4 Plaintext length: {len(K4_PLAINTEXT)}")
print(f"Gap3 position: 74-82 (RSPVJWQUL)")
print(f"Gap4 position: 88-96 (ZOLRKCAYF)")
print(f"Gap between them: {88-82-1} characters (ABOVE)")

# Check what's around them
print(f"\nContext:")
print(f"  Before Gap3: ...{K4_PLAINTEXT[70:74]}")
print(f"  Gap3: {K4_PLAINTEXT[74:83]}")
print(f"  After Gap3: {K4_PLAINTEXT[83:88]}...")
print(f"  Gap4: {K4_PLAINTEXT[88:97]}")

# ===== HYPOTHESIS 7: PROBABILITY VERIFICATION =====
print("\n[HYPOTHESIS 7] PROBABILITY CALCULATION")
print("-" * 80)

# Probability of 9 completely unique letters from 26
# First letter: 26 choices (26/26 unique)
# Second letter: 25 choices (25/26 unique)
# ... and so on
# Probability = (26×25×24×23×22×21×20×19×18) / 26^9

prob_numerator = 1
for i in range(9):
    prob_numerator *= (26 - i)

prob_denominator = 26 ** 9
probability = prob_numerator / prob_denominator
odds = 1 / probability

print(f"\nProbability of 9 random letters being all unique:")
print(f"  P = (26×25×24×23×22×21×20×19×18) / 26^9")
print(f"  P = {prob_numerator:,} / {prob_denominator:,}")
print(f"  P = {probability:.10f}")
print(f"  Odds: 1 in {odds:,.0f}")

print(f"\nEntropy (Shannon):")
gap3_entropy = -sum((Counter(GAP3)[c] / 9) * math.log2((Counter(GAP3)[c] / 9)) 
                     for c in set(GAP3))
gap4_entropy = -sum((Counter(GAP4)[c] / 9) * math.log2((Counter(GAP4)[c] / 9)) 
                     for c in set(GAP4))
print(f"  Gap3 entropy: {gap3_entropy:.4f} (perfect = log2(9) = {math.log2(9):.4f})")
print(f"  Gap4 entropy: {gap4_entropy:.4f} (perfect = log2(9) = {math.log2(9):.4f})")

# ===== HYPOTHESIS 8: RELATIONSHIP TO EACH OTHER =====
print("\n[HYPOTHESIS 8] RELATIONSHIP ANALYSIS")
print("-" * 80)

print(f"\nGap3: {GAP3}")
print(f"Gap4: {GAP4}")
print(f"Gap3 reversed: {GAP3[::-1]}")
print(f"Gap4 reversed: {GAP4[::-1]}")

# Check if one is key to decrypt the other
print(f"\nCharacter overlap: {len(gap3_letters & gap4_letters)} shared letters")
print(f"Shared letters: {sorted(gap3_letters & gap4_letters)}")

# XOR-like operations
print(f"\nAs ASCII codes:")
print(f"  Gap3: {[ord(c) for c in GAP3]}")
print(f"  Gap4: {[ord(c) for c in GAP4]}")

print("\n" + "=" * 80)
print("END OF INVESTIGATION")
print("=" * 80)
