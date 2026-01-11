#!/usr/bin/env python3
"""
Test if gibberish sections are anagrams of multi-word phrases
This is the most likely encoding method given the structure
"""

from itertools import combinations
from collections import Counter

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

gaps = {
    "gap1": ("QAPBZDBKZEL", 11),
    "gap2": ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", 38),
    "gap3": ("RSPVJWQUL", 9),
    "gap4": ("ZOLRKCAYF", 9),
}

print("="*80)
print("MULTI-WORD ANAGRAM ANALYSIS")
print("="*80)

# Common words by length
word_list_by_length = {
    1: ["A", "I"],
    2: ["OF", "TO", "IN", "IS", "AT", "BY", "IT", "OR", "AN", "AS"],
    3: ["THE", "AND", "FOR", "ARE", "NOT", "YOU", "ALL", "CAN", "HAD", "HER", "WAS", "ONE", "OUR", "OUT", "HAD"],
    4: ["THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY", "BEEN", "WALL", "LIES", "MARK", "SHOW"],
    5: ["WOULD", "THERE", "WHICH", "THEIR", "ABOUT", "FIRST", "STONE", "UNDER", "ABOVE", "MARKS", "SHOWS", "HIDES"],
    6: ["GROUND", "SHADOW", "HIDDEN", "SEARCH", "BEFORE"],
    7: ["PASSAGE", "BENEATH", "THROUGH", "EASTERN"],
    8: ["TREASURE", "LOCATION"],
    9: ["DIRECTION", "LOCATIONS"],
    11: ["UNDERNEATH", "NORTHEASTERN"],
}

# Build lookup
all_words = []
for length, words in word_list_by_length.items():
    all_words.extend(words)

print("\nTesting each gap for multi-word anagrams:\n")

def check_anagram_multi(text, words, num_words=2):
    """Find if text is an anagram of num_words words from the list"""
    text_counter = Counter(text)

    results = []

    # For 2-word combinations
    if num_words == 2:
        for word1 in words:
            for word2 in words:
                if word1 == word2:
                    continue
                combined = word1 + word2
                if sorted(combined) == sorted(text):
                    results.append((word1, word2))

    # For 3-word combinations
    elif num_words == 3:
        for word1 in words:
            for word2 in words:
                for word3 in words:
                    if len(set([word1, word2, word3])) < 3:
                        continue
                    combined = word1 + word2 + word3
                    if sorted(combined) == sorted(text):
                        results.append((word1, word2, word3))

    return results

# Test each gap
print("="*80)
print("GAP 1: QAPBZDBKZEL (11 letters)")
print("="*80)

results1_2 = check_anagram_multi("QAPBZDBKZEL", all_words, num_words=2)
if results1_2:
    print(f"2-word anagrams found:")
    for combo in results1_2:
        print(f"  {combo[0]:12} + {combo[1]:12} = {combo[0]}{combo[1]}")
else:
    print("No 2-word anagrams found")

# Try 3-word
results1_3 = check_anagram_multi("QAPBZDBKZEL", all_words, num_words=3)
if results1_3:
    print(f"\n3-word anagrams found:")
    for combo in results1_3:
        print(f"  {combo}")
else:
    print("No 3-word anagrams found")

print("\n" + "="*80)
print("GAP 2: LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH (38 letters)")
print("="*80)

results2_2 = check_anagram_multi("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", all_words, num_words=2)
if results2_2:
    print(f"2-word anagrams found (showing first 10):")
    for combo in results2_2[:10]:
        print(f"  {combo[0]:12} + {combo[1]:12}")
    print(f"  ... and {len(results2_2) - 10} more combinations") if len(results2_2) > 10 else None
else:
    print("No 2-word anagrams found")

# Try 3-word for the large gap
results2_3 = check_anagram_multi("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", all_words, num_words=3)
if results2_3:
    print(f"\n3-word anagrams found (showing first 10):")
    for combo in results2_3[:10]:
        print(f"  {combo}")
    if len(results2_3) > 10:
        print(f"  ... and {len(results2_3) - 10} more combinations")
else:
    print("\nNo 3-word anagrams found")

print("\n" + "="*80)
print("GAP 3: RSPVJWQUL (9 letters)")
print("="*80)

results3_2 = check_anagram_multi("RSPVJWQUL", all_words, num_words=2)
if results3_2:
    print(f"2-word anagrams found:")
    for combo in results3_2:
        print(f"  {combo[0]:12} + {combo[1]:12}")
else:
    print("No 2-word anagrams found")

results3_3 = check_anagram_multi("RSPVJWQUL", all_words, num_words=3)
if results3_3:
    print(f"\n3-word anagrams found:")
    for combo in results3_3:
        print(f"  {combo}")
else:
    print("No 3-word anagrams found")

print("\n" + "="*80)
print("GAP 4: ZOLRKCAYF (9 letters)")
print("="*80)

results4_2 = check_anagram_multi("ZOLRKCAYF", all_words, num_words=2)
if results4_2:
    print(f"2-word anagrams found:")
    for combo in results4_2:
        print(f"  {combo[0]:12} + {combo[1]:12}")
else:
    print("No 2-word anagrams found")

results4_3 = check_anagram_multi("ZOLRKCAYF", all_words, num_words=3)
if results4_3:
    print(f"\n3-word anagrams found:")
    for combo in results4_3:
        print(f"  {combo}")
else:
    print("No 3-word anagrams found")

# Try a focused approach - what words CAN be extracted from gap 2?
print("\n" + "="*80)
print("FOCUSED APPROACH: What words fit the context?")
print("="*80)

gap2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
gap2_counter = Counter(gap2)

thematic_words = [
    ("NORTHEAST", 9),
    ("PASSAGE", 7),
    ("WALL", 4),
    ("MARKS", 5),
    ("BENEATH", 7),
    ("STONE", 5),
    ("SHADOW", 6),
    ("LOCATION", 8),
    ("QUEST", 5),
    ("TREASURE", 8),
]

print(f"\nCan the following thematic words be formed from Gap 2?")
print("(Gap 2: LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH)\n")

for word, length in thematic_words:
    word_counter = Counter(word)
    can_form = all(gap2_counter[c] >= word_counter[c] for c in word_counter)
    status = "✓ YES" if can_form else "✗ NO"
    print(f"  {word:15} ({length:2d} letters): {status}")

# Check the COMPLETE SENTENCE possibility
print("\n" + "="*80)
print("HYPOTHESIS TEST: Can gaps combine to form the sentence?")
print("="*80)

print("\nIf the sentence is:")
print("  UNDER THE NORTHEAST PASSAGE BERLINCLOCK SHOWS ABOVE STONE")
print("\nRequired word lengths:")
print("  Gap 1 (11 letters):  THE = 3 letters (need 8 more)")
print("  Gap 2 (38 letters):  PASSAGE = 7 letters (need 31 more)")
print("  Gap 3 (9 letters):   SHOWS = 5 letters (need 4 more)")
print("  Gap 4 (9 letters):   STONE = 5 letters (need 4 more)")

# Try to see if single clear anagrams work
print("\n" + "="*80)
print("TESTING SENTENCE COMPONENTS AS ANAGRAMS")
print("="*80)

test_combos = [
    ("Gap1", "QAPBZDBKZEL", ["THE", "GROUND", "STONE", "SHADOW"]),
    ("Gap2", "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", ["PASSAGE", "WALL", "MARKS", "BENEATH"]),
    ("Gap3", "RSPVJWQUL", ["SHOWS", "MARKS", "LIES", "HIDES"]),
    ("Gap4", "ZOLRKCAYF", ["STONE", "SHADOW", "GROUND", "SURFACE"]),
]

for gap_name, gap_text, candidate_words in test_combos:
    gap_sorted = sorted(gap_text)
    print(f"\n{gap_name} ({len(gap_text)} letters): {gap_text}")
    print(f"  Testing if any word is an anagram:")
    found_any = False
    for word in candidate_words:
        if sorted(word) == gap_sorted:
            print(f"    ✓ MATCH: {word}")
            found_any = True
        else:
            missing = sum(1 for c in word if gap_text.count(c) < word.count(c))
            extra = sum(1 for c in gap_text if gap_text.count(c) > word.count(c))
            if missing <= 2:
                print(f"    ~ CLOSE: {word} (need {missing} more letters, have {len(gap_text)-len(word)} extra)")
    if not found_any:
        print(f"    No anagrams found")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("\nIf gibberish is pure anagrams, the exact words may not be in our word list.")
print("The missing words are likely specialized/archaic English, proper nouns,")
print("or use a different encoding method altogether.")
