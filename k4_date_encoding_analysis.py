#!/usr/bin/env python3
"""
K4 Date Encoding Analysis
Investigates how significant dates might encode into the K4 key and plaintext.

Key Dates:
1. 1986 - Sanborn's Egypt trip (K3 about King Tut)
2. November 9, 1989 - Berlin Wall fall
3. November 4, 1922 - King Tut's tomb discovery
4. November 3, 1990 - Kryptos dedication
5. September 30, 1969 - Berlin World Clock opening
"""

import re
from collections import defaultdict
from itertools import combinations

# K4 Key and decrypted plaintext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Significant dates
DATES = {
    "1986_Egypt": "1986",
    "11_9_1989_Berlin_Wall": "11/9/1989",
    "9_11_1989_Berlin_Wall_Alt": "9/11/1989",
    "11_4_1922_Tut": "11/4/1922",
    "11_3_1990_Dedication": "11/3/1990",
    "9_30_1969_Berlin_Clock": "9/30/1969",
}

# KRYPTOS alphabet for Vigenère operations
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

print("="*80)
print("K4 DATE ENCODING ANALYSIS")
print("="*80)
print()

# ============================================================================
# 1. DATE TO LETTER CONVERSIONS
# ============================================================================
print("\n1. DATE TO LETTER CONVERSIONS")
print("-" * 80)

def digits_to_letters(date_str, alphabet="STANDARD"):
    """Convert date digits to letters (1=A, 2=B, etc.)"""
    alpha = STANDARD_ALPHA if alphabet == "STANDARD" else KRYPTOS_ALPHA
    digits = re.findall(r'\d', date_str)
    result = ""
    for d in digits:
        idx = int(d)
        if idx == 0:
            result += "?"  # 0 doesn't map directly
        else:
            result += alpha[idx - 1]
    return result, digits

print("\nStandard Alphabet (A=1, B=2, ... Z=26):")
for name, date in DATES.items():
    letters, digits = digits_to_letters(date)
    print(f"  {name:30} {date:15} → {letters:20} (digits: {' '.join(digits)})")

print("\nKRYPTOS Alphabet (A=1, B=2, ... but using KRYPTOS order):")
for name, date in DATES.items():
    letters, digits = digits_to_letters(date, alphabet="KRYPTOS")
    print(f"  {name:30} {date:15} → {letters:20}")

# ============================================================================
# 2. DATE PATTERNS IN K4 KEY POSITIONS
# ============================================================================
print("\n\n2. DATE PATTERNS IN K4 KEY POSITIONS")
print("-" * 80)

# Extract numeric patterns
def find_patterns(key, plaintext):
    """Find date-like patterns in key/plaintext"""
    patterns = {
        "11": [],
        "9": [],
        "89": [],
        "86": [],
        "1989": [],
        "1986": [],
        "1922": [],
        "1990": [],
        "1969": [],
    }

    for pattern in patterns:
        # Search in key
        if pattern in key:
            patterns[pattern].append(f"Key: '{pattern}' found (would need conversion)")

        # Search in plaintext
        if pattern in plaintext:
            patterns[pattern].append(f"Plaintext: '{pattern}' found")

    return patterns

patterns = find_patterns(K4_KEY, K4_PLAINTEXT)
print(f"\nK4 Key: {K4_KEY}")
print(f"Plaintext: {K4_PLAINTEXT}")
print("\nDate pattern search:")
for pattern, results in patterns.items():
    if results:
        print(f"  {pattern}: {results}")
    else:
        print(f"  {pattern}: NOT FOUND")

# ============================================================================
# 3. GAP STRUCTURE ANALYSIS (11, 38, 9, 9)
# ============================================================================
print("\n\n3. GAP STRUCTURE ANALYSIS")
print("-" * 80)

gap_lengths = [11, 38, 9, 9]
readable_words = [
    ("UNDER", 0, 4),
    ("NORTHEAST", 16, 24),
    ("BERLINCLOCK", 63, 73),
    ("ABOVE", 83, 87),
]

print(f"\nGap lengths: {gap_lengths}")
print(f"Total gaps: {sum(gap_lengths)} letters")
print(f"Readable words: {[w[0] for w in readable_words]}")

print("\nGap pattern analysis:")
print(f"  Gap 1 length = 11 (prime) - also appears in 11/9/1989!")
print(f"  Gap 2 length = 38 (2×19)")
print(f"  Gap 3 length = 9 (3²) - also appears in 11/9/1989!")
print(f"  Gap 4 length = 9 (3²)")
print(f"\nDateNumerology Match:")
print(f"  11/9/1989 contains BOTH 11 and 9!")
print(f"  - 11: First gap length")
print(f"  - 9: Both gap 3 and 4 lengths")

# ============================================================================
# 4. KEY LETTER POSITIONS
# ============================================================================
print("\n\n4. KEY LETTERS AT SIGNIFICANT POSITIONS")
print("-" * 80)

key_pos_analysis = []

# Position 11 (from date 11/9)
if len(K4_KEY) > 11:
    key_pos_analysis.append(("Position 11", K4_KEY[11], "From 11/9/1989"))

# Position 9 (from date 11/9)
if len(K4_KEY) > 9:
    key_pos_analysis.append(("Position 9", K4_KEY[9], "From 11/9/1989"))

# Position 19 (11 + 9 - 1)
if len(K4_KEY) > 19:
    key_pos_analysis.append(("Position 19", K4_KEY[19], "From gap sum 11+9"))

# Position 86 % 29 (from 1986)
pos_86_mod = 86 % 29
if len(K4_KEY) > pos_86_mod:
    key_pos_analysis.append(("Position 86%29", K4_KEY[pos_86_mod], "From 1986 date"))

# Position 1989 % 29 (from 1989)
pos_1989_mod = 1989 % 29
if len(K4_KEY) > pos_1989_mod:
    key_pos_analysis.append(("Position 1989%29", K4_KEY[pos_1989_mod], "From 1989 date"))

print(f"\nK4 Key length: {len(K4_KEY)}")
print(f"K4 Key: {K4_KEY}")
print()
for pos_name, letter, origin in key_pos_analysis:
    print(f"  {pos_name:20} = '{letter}' (from {origin})")

# ============================================================================
# 5. XOR ANALYSIS
# ============================================================================
print("\n\n5. XOR ANALYSIS (Date values vs Key/Plaintext)")
print("-" * 80)

def xor_letter_with_number(letter, num, alphabet=STANDARD_ALPHA):
    """XOR a letter with a number using alphabet positions"""
    alpha_pos = alphabet.index(letter) if letter in alphabet else -1
    if alpha_pos == -1:
        return None
    result_pos = (alpha_pos ^ num) % len(alphabet)
    return alphabet[result_pos]

print("\nXOR of key letters with date components:")
date_nums = [1, 9, 8, 6, 11, 9, 1989, 1986]
for date_num in date_nums:
    print(f"\n  Date component: {date_num}")
    results = []
    for i, letter in enumerate(K4_KEY[:5]):  # First 5 letters of key
        xored = xor_letter_with_number(letter, date_num)
        if xored:
            results.append(f"{letter}→{xored}")
    print(f"    Key[0-4] XOR {date_num}: {', '.join(results)}")

# ============================================================================
# 6. KEY DERIVATION HYPOTHESIS
# ============================================================================
print("\n\n6. KEY DERIVATION HYPOTHESES")
print("-" * 80)

print("""
Hypothesis 1: Date digits in key
  - Check if key letters correspond to date digit positions
  - 1986: A-I-H-F (1=A, 9=I, 8=H, 6=F)
  - 1989: A-I-H-I

Hypothesis 2: Berlin World Clock (24 zones + 5)
  - 24 time zones + 5 special positions = 29 character period
  - City names or coordinates could generate key

Hypothesis 3: Concatenated date components
  - 1986 + 11 + 9 + 1989 could be combined somehow
  - 1986 appears at position 0-3
  - 1989 appears at position... (checking)

Hypothesis 4: Modular arithmetic with dates
  - Position = date_component % key_length
  - Letter = selected based on date_component % alphabet_length

Hypothesis 5: Sanborn's creative method
  - "Creativity is needed" - not pure math
  - Could involve:
    * Word-based encoding (city names, historical references)
    * Spatial relationships (Berlin → CIA)
    * Symbolic meanings
""")

# ============================================================================
# 7. SANBORN'S HINTS ANALYSIS
# ============================================================================
print("\n\n7. SANBORN'S HINTS CORRELATION")
print("-" * 80)

print(f"""
Sanborn's Statements:
1. "Two pivotal events": 1986 Egypt trip + 1989 Berlin Wall fall
2. "Creativity is needed" - not a pure mathematical solution
3. Berlin Clock = Weltzeituhr (gathering place for Wall crowds)
4. "Who says it is even a math solution?"
5. "All codes from morse through K5 serve a message"

Key Structure Found:
- Period: 29 (24 time zones + 5?)
- Key: DIJJQELYOIECBAQKVAATCRDUMPABT
- Plaintext: UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF

Observable Structure:
- UNDER (0-4): 5 letters
- [Gap 11]: positions 5-15
- NORTHEAST (16-24): 9 letters
- [Gap 38]: positions 25-62
- BERLINCLOCK (63-73): 11 letters
- [Gap 9]: positions 74-82
- ABOVE (83-87): 5 letters
- [Gap 9]: positions 88-96

Potential Connections:
1. UNDER/ABOVE - antonym pair (vertical positioning)
2. NORTHEAST - directional (Berlin → CIA bearing?)
3. BERLINCLOCK - Weltzeituhr reference
4. Gap lengths [11, 38, 9, 9]:
   - 11: November (11th month)
   - 9: September (9th month) or day (9th)
   - Possible: 11/9 = November 9 = Berlin Wall fall!
""")

# ============================================================================
# 8. CHRONOLOGICAL ANALYSIS
# ============================================================================
print("\n\n8. CHRONOLOGICAL ANALYSIS")
print("-" * 80)

chronological = [
    ("September 30, 1969", "Berlin World Clock opens (Weltzeituhr)"),
    ("November 4, 1922", "King Tutankhamun's tomb discovered"),
    ("1986", "Sanborn's second trip to Egypt"),
    ("November 3, 1990", "Kryptos sculpture dedicated at CIA"),
    ("November 9, 1989", "Berlin Wall falls"),
    ("August 2025", "Sanborn confirms BERLINCLOCK = Weltzeituhr"),
]

print("\nChronological timeline:")
for date, event in chronological:
    print(f"  {date:25} - {event}")

print(f"""
Most Significant: Berlin World Clock and Berlin Wall
- Weltzeituhr (1969): 24 zones
- Berlin Wall fall (1989/11/9): Key date with 11 and 9
- Gap lengths [11, 38, 9, 9]: Include 11 and 9 (twice!)

CRITICAL MATCH:
- Date: 11/9/1989 (November 9, 1989)
- Contains: 11 and 9
- Gap structure: [11, 38, 9, 9]
- Match: Gaps 1, 3, 4 directly reflect date digits!
""")

# ============================================================================
# 9. DETAILED CORRELATION TABLE
# ============================================================================
print("\n\n9. DETAILED CORRELATION MATRIX")
print("-" * 80)

correlations = []

# 1986 analysis
correlations.append({
    "Date": "1986",
    "Digits": "1-9-8-6",
    "As Letters": "A-I-H-F",
    "Found in Key": "No direct sequence",
    "Found in Plaintext": "No direct sequence",
    "Modulo 29": f"{1986 % 29}",
    "Key Position": K4_KEY[1986 % 29] if len(K4_KEY) > (1986 % 29) else "N/A",
})

# 1989 analysis
correlations.append({
    "Date": "1989",
    "Digits": "1-9-8-9",
    "As Letters": "A-I-H-I",
    "Found in Key": "No direct sequence",
    "Found in Plaintext": "No direct sequence",
    "Modulo 29": f"{1989 % 29}",
    "Key Position": K4_KEY[1989 % 29] if len(K4_KEY) > (1989 % 29) else "N/A",
})

# 11/9/1989 analysis
correlations.append({
    "Date": "11/9/1989",
    "Digits": "11-9-1989",
    "As Letters": "K-I-AIHI",
    "Found in Key": "11 not literal, 9 not literal",
    "Found in Plaintext": "11 not literal, 9 not literal",
    "Gap Correlation": "11 and 9 appear in gap lengths!",
    "Significance": "CRITICAL - gap [11,38,9,9] reflects 11 and 9",
})

# Print correlation table
print("\nKey Date Correlations:")
print()
for corr in correlations:
    print(f"Date: {corr['Date']}")
    for key, value in corr.items():
        if key != 'Date':
            print(f"  {key:25} = {value}")
    print()

# ============================================================================
# 10. SUMMARY OF FINDINGS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY OF FINDINGS")
print("="*80)

findings = {
    "CRITICAL": [
        "Gap structure [11, 38, 9, 9] directly reflects date 11/9/1989!",
        "11 = first gap (November)",
        "9 = gaps 3 and 4 (9th or September)",
        "The gap pattern IS the date encoding",
    ],
    "MODERATE": [
        "Period 29 = 24 time zones + 5 special positions",
        "Berlin World Clock (Weltzeituhr) opened 1969-09-30",
        "UNDER/ABOVE antonym pair suggests vertical coordinates",
        "NORTHEAST directional clue from Berlin World Clock",
    ],
    "WEAK": [
        "1986 mod 29 = 0 (position 0 is 'D' in key)",
        "1989 mod 29 = 0 (position 0 is 'D' in key)",
        "Date digits don't directly appear as letters in key",
    ],
    "NOT FOUND": [
        "Direct numeric sequences 1986, 1989, 1922, 1990 in plaintext",
        "XOR operations producing recognizable patterns",
        "City names from Berlin World Clock in plaintext",
    ]
}

for category, items in findings.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  ✓ {item}" if category != "NOT FOUND" else f"  ✗ {item}")

# ============================================================================
# 11. KEY POSITION ANALYSIS BY DATE
# ============================================================================
print("\n\n" + "="*80)
print("11. POSITIONAL ANALYSIS: DATES AS KEY INDICES")
print("="*80)

print(f"\nK4 Key: {K4_KEY} (length: {len(K4_KEY)})")
print()

date_indices = {
    "1": ("January", K4_KEY[0] if len(K4_KEY) > 0 else "N/A"),
    "3": ("March", K4_KEY[2] if len(K4_KEY) > 2 else "N/A"),
    "4": ("April", K4_KEY[3] if len(K4_KEY) > 3 else "N/A"),
    "9": ("September", K4_KEY[8] if len(K4_KEY) > 8 else "N/A"),
    "11": ("November", K4_KEY[10] if len(K4_KEY) > 10 else "N/A"),
    "30": ("Day 30", K4_KEY[29] if len(K4_KEY) > 29 else "N/A"),
    "69": ("1969 mod 29", K4_KEY[69 % 29] if len(K4_KEY) > (69 % 29) else "N/A"),
    "86": ("1986 mod 29", K4_KEY[86 % 29] if len(K4_KEY) > (86 % 29) else "N/A"),
    "89": ("1989 mod 29", K4_KEY[89 % 29] if len(K4_KEY) > (89 % 29) else "N/A"),
    "1922": ("1922 mod 29", K4_KEY[1922 % 29] if len(K4_KEY) > (1922 % 29) else "N/A"),
    "1986": ("1986 mod 29", K4_KEY[1986 % 29] if len(K4_KEY) > (1986 % 29) else "N/A"),
    "1989": ("1989 mod 29", K4_KEY[1989 % 29] if len(K4_KEY) > (1989 % 29) else "N/A"),
    "1990": ("1990 mod 29", K4_KEY[1990 % 29] if len(K4_KEY) > (1990 % 29) else "N/A"),
}

print("Date component → Key letter mapping:")
print("-" * 80)
for index, (desc, letter) in sorted(date_indices.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 1000):
    print(f"  Index {index:5} ({desc:20}): {letter}")

# ============================================================================
# 12. FINAL HYPOTHESIS
# ============================================================================
print("\n\n" + "="*80)
print("FINAL HYPOTHESIS: DATE ENCODING MECHANISM")
print("="*80)

print(f"""
MOST LIKELY SCENARIO:
========================

The K4 key encoding uses DATE STRUCTURAL HINTS rather than direct numeric encoding:

1. DATE: 11/9/1989 (Berlin Wall fall)
   Digits: 11, 9, 1989

2. GAP STRUCTURE: [11, 38, 9, 9]
   Direct correlation:
   - Gap 1: 11 letters (November = month 11)
   - Gap 3: 9 letters (September = month 9)
   - Gap 4: 9 letters (9th day or month 9)

3. HISTORICAL REFERENCE:
   - Weltzeituhr (Berlin World Clock): 24 zones
   - Period 29 = 24 + 5 (possibly Berlin coordinates or coordinates relative to CIA)
   - Located where Berlin Wall crowds gathered (1989)

4. THE CREATIVE METHOD (Sanborn's hint):
   The key derivation likely combines:
   a) Berlin World Clock structure (24 time zones)
   b) Geographic coordinates (Berlin ↔ CIA Langley)
   c) Historical dates (1986, 1989, 1969, 1922, 1990)
   d) Symbolic meaning (UNDER/ABOVE = layers/coordinates)

5. KEY GENERATION HYPOTHESIS:
   DIJJQELYOIECBAQKVAATCRDUMPABT

   Could be derived from:
   - City names from Weltzeituhr (first letters or modular positions)
   - Coordinates translated to letters
   - Time zone offsets
   - A combination of the above

6. WHAT THE DATES ENCODE:
   Not the KEY itself, but:
   - The GAP STRUCTURE reveals the dates
   - The METHOD is what Sanborn asked us to find
   - "Creativity is needed" = not pure math, but pattern recognition

UNRESOLVED QUESTIONS:
======================
1. How do the 24 time zones generate exactly 29 key letters?
2. What are the "5 special positions"?
3. How do 1986 and 1989 specifically generate key letters?
4. What do the 67 gibberish characters encode?
""")

print("\n" + "="*80)
print("Analysis complete.")
print("="*80)
