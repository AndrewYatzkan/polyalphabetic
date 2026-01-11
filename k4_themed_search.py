#!/usr/bin/env python3
"""
K4 Themed Search - Based on Sanborn's hints:
1. BERLINCLOCK = World Clock at Alexanderplatz
2. 1986 Egypt trip (K3 = King Tut discovery)
3. 1989 Berlin Wall fall
4. NORTHEAST in plaintext
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def decrypt(ct, key):
    pt = ""
    for i, c in enumerate(ct):
        if c not in KRYPTOS:
            pt += c
            continue
        ct_idx = KRYPTOS.index(c)
        key_idx = KRYPTOS.index(key[i % len(key)])
        pt_idx = (ct_idx - key_idx) % 26
        pt += KRYPTOS[pt_idx]
    return pt

# Base key from confirmed cribs
# Positions 5-15: ELYOIECBAQK (from BERLINCLOCK at 63)
# Positions 16-24: VAATCRDUM (from NORTHEAST at 16)
BASE_KEY = "?????ELYOIECBAQKVAATCRDUM????"

def try_words(start_word, end_word):
    """Try a combination of start and end words."""
    key = list(BASE_KEY)

    # Fill positions 0-4 from start_word
    if len(start_word) >= 5:
        for i in range(5):
            ct_char = K4[i]
            pt_char = start_word[i]
            ct_idx = KRYPTOS.index(ct_char)
            pt_idx = KRYPTOS.index(pt_char)
            key_char = KRYPTOS[(ct_idx - pt_idx) % 26]
            key[i] = key_char

    # Fill positions 25-28 from end_word at position 83
    # Position 83 mod 29 = 25, so positions 83-87 use key positions 25-28,0
    if len(end_word) >= 5:
        for i in range(4):  # First 4 chars of end word use positions 25-28
            pos = 83 + i
            ct_char = K4[pos]
            pt_char = end_word[i]
            ct_idx = KRYPTOS.index(ct_char)
            pt_idx = KRYPTOS.index(pt_char)
            key_char = KRYPTOS[(ct_idx - pt_idx) % 26]
            key[25 + i] = key_char

    key_str = ''.join(key)
    if '?' in key_str:
        key_str = key_str.replace('?', 'K')  # Default fill

    pt = decrypt(K4, key_str)
    return key_str, pt

# Themed word combinations to try
themes = {
    "Berlin Wall": [
        ("WALLS", "ABOVE"), ("WALLS", "BELOW"), ("FALLS", "ABOVE"),
        ("AFTER", "ABOVE"), ("SINCE", "ABOVE"), ("WHEN ", "ABOVE"),  # Need 5 chars
    ],
    "Directions": [
        ("UNDER", "ABOVE"), ("BELOW", "ABOVE"), ("NORTH", "SOUTH"),
        ("ABOVE", "BELOW"), ("ALONG", "ABOVE"), ("GOING", "ABOVE"),
    ],
    "Egypt/Tomb": [
        ("UNDER", "SANDS"), ("BELOW", "SANDS"), ("TOMB ", "ABOVE"),
        ("WALLS", "SANDS"), ("STONE", "ABOVE"), ("STONE", "BELOW"),
    ],
    "Clock theme": [
        ("CLOCK", "HANDS"), ("WATCH", "HANDS"), ("HOURS", "HANDS"),
        ("AFTER", "HOURS"), ("TIMED", "ABOVE"),
    ],
    "Treasure hunt": [
        ("LAYER", "ABOVE"), ("BELOW", "LAYER"), ("DEPTH", "ABOVE"),
        ("FINDS", "ABOVE"), ("SEEKS", "ABOVE"), ("WHERE", "ABOVE"),
    ],
    "Instructions": [
        ("START", "ABOVE"), ("STAND", "ABOVE"), ("POINT", "ABOVE"),
        ("THERE", "ABOVE"), ("FROM ", "ABOVE"),
    ],
}

print("="*70)
print("K4 THEMED WORD SEARCH")
print("="*70)

all_results = []
for theme, pairs in themes.items():
    print(f"\n{theme}:")
    for start, end in pairs:
        start = start.strip().upper()
        end = end.strip().upper()
        if len(start) < 5 or len(end) < 5:
            continue

        key, pt = try_words(start, end)

        # Score based on English-like patterns
        score = 0
        # Check for THE, AND, FOR, etc.
        common = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN",
                  "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HER", "NEW", "OLD",
                  "SEE", "NOW", "WAY", "DAY", "MAN", "ITS", "SAY", "SHE", "TWO",
                  "HOW", "OUR", "HIM", "HAS", "HER", "ITS", "LET", "MAY", "WHO"]
        for w in common:
            count = pt.count(w)
            score += count * len(w)

        if start in pt[:10]:
            score += 20
        if end in pt[80:]:
            score += 20
        if "NORTHEAST" in pt:
            score += 50
        if "BERLINCLOCK" in pt:
            score += 50

        all_results.append((theme, start, end, key, pt, score))
        print(f"  {start}/{end}: {pt[:25]}...{pt[60:]}  (score:{score})")

# Sort all results
all_results.sort(key=lambda x: -x[5])

print("\n" + "="*70)
print("TOP 10 RESULTS")
print("="*70)
for i, (theme, start, end, key, pt, score) in enumerate(all_results[:10]):
    print(f"\n{i+1}. {start}/{end} ({theme}) - Score: {score}")
    print(f"   Key: {key}")
    print(f"   PT:  {pt}")

# Now let's try to understand the gibberish by looking for patterns
print("\n" + "="*70)
print("ANALYZING BEST RESULT'S GIBBERISH")
print("="*70)

best = all_results[0]
pt = best[4]
print(f"Best plaintext: {pt}")
print(f"\nSegments:")
print(f"  0-4:   {pt[0:5]} (start word)")
print(f"  5-15:  {pt[5:16]} (Gap1 - 11 chars)")
print(f"  16-24: {pt[16:25]} (NORTHEAST)")
print(f"  25-62: {pt[25:63]} (Gap2 - 38 chars)")
print(f"  63-73: {pt[63:74]} (BERLINCLOCK)")
print(f"  74-82: {pt[74:83]} (Gap3 - 9 chars)")
print(f"  83-87: {pt[83:88]} (end word)")
print(f"  88-96: {pt[88:97]} (Gap4 - 9 chars)")

# What if the gaps spell something when combined?
combined_gaps = pt[5:16] + pt[25:63] + pt[74:83] + pt[88:97]
print(f"\nCombined gaps (67 chars): {combined_gaps}")

# Try reversing
print(f"Reversed: {combined_gaps[::-1]}")

# Try every other letter
print(f"Every 2nd: {combined_gaps[::2]}")
print(f"Every 3rd: {combined_gaps[::3]}")
