#!/usr/bin/env python3
"""
CRITICAL TEST: What if the plaintext contains EASTNORTHEAST as one
continuous 13-character string? This gives us a 13-char crib instead of 9.

The Smithsonian discovery showed "EAST NORTHEAST" fragments. If this is
one continuous word EASTNORTHEAST (a compass direction), it's a much
stronger constraint.

With BERLINCLOCK at position 63 (confirmed), test EASTNORTHEAST at every
possible position. For period 29, check which placements:
1. Don't conflict with BERLINCLOCK's key positions
2. Produce readable English at other positions
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c):
    return KRYPTOS.index(c)

def k_chr(i):
    return KRYPTOS[i % 26]

def derive_key(ct_char, pt_char):
    return k_chr(k_idx(ct_char) - k_idx(pt_char))

def decrypt_char(ct_char, key_char):
    return k_chr(k_idx(ct_char) - k_idx(key_char))

CRIB1 = "BERLINCLOCK"
CRIB1_POS = 63
CRIB2 = "EASTNORTHEAST"

print("=" * 80)
print("EASTNORTHEAST CRIB TEST")
print("=" * 80)
print(f"K4: {K4} ({len(K4)} chars)")
print(f"BERLINCLOCK fixed at position {CRIB1_POS}")
print(f"Testing EASTNORTHEAST at all valid positions")
print()

# First derive key positions from BERLINCLOCK@63
bc_key = {}
for i, pt_char in enumerate(CRIB1):
    ct_pos = CRIB1_POS + i
    key_pos = ct_pos % 29
    key_char = derive_key(K4[ct_pos], pt_char)
    bc_key[key_pos] = key_char

print(f"BERLINCLOCK@63 constrains key positions: {sorted(bc_key.keys())}")
print(f"  Key values: {dict(sorted(bc_key.items()))}")
print()

# Test EASTNORTHEAST at every position
results = []
for ent_pos in range(len(K4) - len(CRIB2) + 1):
    # Derive key positions from EASTNORTHEAST
    ent_key = {}
    conflict = False

    for i, pt_char in enumerate(CRIB2):
        ct_pos = ent_pos + i
        if ct_pos >= len(K4):
            conflict = True
            break
        key_pos = ct_pos % 29
        key_char = derive_key(K4[ct_pos], pt_char)

        # Check conflict with BERLINCLOCK key
        if key_pos in bc_key and bc_key[key_pos] != key_char:
            conflict = True
            break
        # Check internal conflict
        if key_pos in ent_key and ent_key[key_pos] != key_char:
            conflict = True
            break
        ent_key[key_pos] = key_char

    if conflict:
        continue

    # Merge keys
    full_key = {**bc_key, **ent_key}
    known_key_count = len(full_key)

    # Build partial key string
    key_str = ['?'] * 29
    for pos, char in full_key.items():
        key_str[pos] = char
    key_display = ''.join(key_str)
    unknown_count = key_display.count('?')

    # Decrypt what we can
    pt = []
    for i in range(len(K4)):
        kpos = i % 29
        if kpos in full_key:
            pt.append(decrypt_char(K4[i], full_key[kpos]))
        else:
            pt.append('.')
    pt_str = ''.join(pt)

    # Count known chars
    known_chars = sum(1 for c in pt_str if c != '.')

    # Score: count English words in plaintext
    WORDS = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN",
             "HER", "WAS", "ONE", "OUR", "OUT", "HIS", "HAS", "DAY", "HOW",
             "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "DID", "ITS",
             "LET", "SAY", "SHE", "TOO", "USE", "END", "KEY", "SET", "TRY",
             "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY",
             "BEEN", "CALL", "FIND", "EACH", "LOOK", "ONLY", "COME", "MADE",
             "LONG", "THAN", "SITE", "WALL", "EAST", "WEST", "TIME", "HERE",
             "MARK", "SPOT", "LAND", "SHOW", "LEFT", "OPEN", "DARK",
             "THERE", "THEIR", "ABOUT", "WOULD", "COULD", "THESE", "OTHER",
             "WHERE", "AFTER", "CLOCK", "UNDER", "ABOVE", "NORTH", "SOUTH",
             "LAYER", "POINT", "PLACE", "STONE", "EARTH", "FIELD", "LIGHT",
             "NIGHT", "RIGHT", "BELOW", "WORLD", "HANDS", "HOURS", "WATCH",
             "BERLIN", "SHADOW", "BURIED", "HIDDEN", "SECRET", "SLOWLY",
             "NORTHEAST", "SOUTHEAST", "BERLINCLOCK", "EASTNORTHEAST",
             "BEARING", "DEGREE", "COMPASS", "DIRECTION", "TOWARD",
             "BETWEEN", "THROUGH", "BENEATH"]

    # Only count words NOT part of our cribs
    found_words = []
    for w in WORDS:
        if w in pt_str:
            wpos = pt_str.index(w)
            # Skip if it's part of our placed cribs
            in_crib = False
            if wpos >= ent_pos and wpos + len(w) <= ent_pos + len(CRIB2):
                in_crib = True
            if wpos >= CRIB1_POS and wpos + len(w) <= CRIB1_POS + len(CRIB1):
                in_crib = True
            if not in_crib:
                found_words.append((w, wpos))

    score = sum(len(w[0])**2 for w in found_words)

    results.append({
        'ent_pos': ent_pos,
        'key': key_display,
        'unknown': unknown_count,
        'pt': pt_str,
        'known_chars': known_chars,
        'words': found_words,
        'score': score
    })

# Sort by score then by known chars
results.sort(key=lambda x: (-x['score'], -x['known_chars']))

print(f"Valid EASTNORTHEAST positions (no key conflict): {len(results)}")
print()

# Show all results
print("=" * 80)
print("ALL VALID PLACEMENTS (sorted by extra-word score)")
print("=" * 80)
for r in results:
    print(f"\nEASTNORTHEAST @ position {r['ent_pos']}:")
    print(f"  Key ({29-r['unknown']}/29 known): {r['key']}")
    print(f"  PT ({r['known_chars']}/97 known):  {r['pt']}")
    if r['words']:
        print(f"  Extra words: {r['words']}")
        print(f"  Score: {r['score']}")
    else:
        print(f"  No extra words found (score: 0)")

# Deep analysis of top results
print("\n" + "=" * 80)
print("DEEP ANALYSIS OF TOP RESULTS")
print("=" * 80)

for r in results[:5]:
    ent_pos = r['ent_pos']
    print(f"\n--- EASTNORTHEAST @ position {ent_pos} ---")
    print(f"Key: {r['key']}")

    # For unknown key positions, brute force 5-letter words at those positions
    unknown_positions = [i for i in range(29) if r['key'][i] == '?']
    print(f"Unknown key positions: {unknown_positions}")
    print(f"Unknown count: {len(unknown_positions)}")

    if len(unknown_positions) <= 5:
        print(f"\nBrute-forcing {26**len(unknown_positions)} key combinations...")

        # Build the base key
        base_key = list(r['key'])

        best_score = 0
        best_pt = ""
        best_key = ""

        # For up to 5 unknowns, we can try dictionary words
        # Map unknown CT positions to find what they decrypt to
        unknown_ct_positions = []
        for i in range(97):
            if i % 29 in unknown_positions:
                unknown_ct_positions.append(i)

        print(f"CT positions using unknown key slots: {unknown_ct_positions}")

        # Quick check: try filling unknown with common letters
        from itertools import product

        # For efficiency, only test if <= 4 unknowns (26^4 = 456,976)
        if len(unknown_positions) <= 4:
            count = 0
            for combo in product(range(26), repeat=len(unknown_positions)):
                test_key = list(base_key)
                for idx, kval in zip(unknown_positions, combo):
                    test_key[idx] = KRYPTOS[kval]

                # Decrypt
                pt = []
                for i in range(97):
                    kpos = i % 29
                    pt.append(decrypt_char(K4[i], test_key[kpos]))
                pt_str = ''.join(pt)

                # Quick score: check for common English patterns
                extra_words = []
                for w in ["THE", "AND", "FOR", "NOT", "YOU", "ALL", "HIS", "HER",
                          "WAS", "ONE", "OUR", "OUT", "HAS", "ITS", "NOW", "WAY",
                          "THAT", "WITH", "HAVE", "THIS", "WILL", "FROM", "THEY",
                          "BEEN", "FIND", "EACH", "ONLY", "COME", "MADE", "LONG",
                          "UNDER", "ABOVE", "WHERE", "THERE", "THEIR", "ABOUT",
                          "CLOCK", "NORTH", "SOUTH", "BELOW", "WORLD", "POINT",
                          "LIGHT", "NIGHT", "EARTH", "FIELD", "STONE", "PLACE",
                          "BERLIN", "HIDDEN", "SECRET", "BURIED", "SHADOW",
                          "BETWEEN", "THROUGH", "BENEATH", "BEARING", "DEGREE",
                          "COMPASS", "TOWARD", "SLOWLY", "DESPERATELY"]:
                    if w in pt_str:
                        wpos = pt_str.index(w)
                        # Skip if part of cribs
                        in_crib = False
                        if wpos >= ent_pos and wpos + len(w) <= ent_pos + len(CRIB2):
                            in_crib = True
                        if wpos >= CRIB1_POS and wpos + len(w) <= CRIB1_POS + len(CRIB1):
                            in_crib = True
                        if not in_crib:
                            extra_words.append((w, wpos))

                sc = sum(len(w[0])**2 for w in extra_words)
                if sc > best_score:
                    best_score = sc
                    best_pt = pt_str
                    best_key = ''.join(test_key)
                    print(f"  NEW BEST (score={sc}): key={''.join(test_key)}")
                    print(f"    PT: {pt_str}")
                    print(f"    Words: {extra_words}")

                count += 1
                if count % 100000 == 0:
                    print(f"  ... tested {count}/{26**len(unknown_positions)}")

            print(f"  Brute force complete. Best score: {best_score}")
            if best_score > 0:
                print(f"  Best key: {best_key}")
                print(f"  Best PT:  {best_pt}")
        else:
            print(f"  Too many unknowns ({len(unknown_positions)}) for brute force")

# Special test: EASTNORTHEAST at position 21 (0-indexed)
# This would put EAST at 21-24, NORTHEAST at 25-33
print("\n" + "=" * 80)
print("SPECIAL: EASTNORTHEAST @ position 21")
print("=" * 80)
if 21 in [r['ent_pos'] for r in results]:
    r21 = [r for r in results if r['ent_pos'] == 21][0]
    print(f"Key: {r21['key']}")
    print(f"PT:  {r21['pt']}")
    print(f"Unknown positions: {[i for i in range(29) if r21['key'][i] == '?']}")

    # With EASTNORTHEAST@21 and BERLINCLOCK@63:
    # Key positions covered by EASTNORTHEAST: 21,22,23,24,25,26,27,28,0,1,2,3,4
    # Key positions covered by BERLINCLOCK: 5,6,7,8,9,10,11,12,13,14,15
    # Unknown: 16,17,18,19,20
    # That's only 5 unknowns!

    print("\nWith only 5 unknown key positions (16-20), the plaintext is 82/97 known!")
    print("Positions using key slots 16-20:")
    for kp in range(16, 21):
        positions = [i for i in range(97) if i % 29 == kp]
        ct_chars = [K4[i] for i in positions]
        pt_chars = [r21['pt'][i] for i in positions]
        print(f"  Key pos {kp}: CT positions {positions}, CT chars {''.join(ct_chars)}, current PT {''.join(pt_chars)}")

# Compare with original NORTHEAST@16 assumption
print("\n" + "=" * 80)
print("COMPARISON: NORTHEAST@16 vs EASTNORTHEAST@21")
print("=" * 80)
print("\nOriginal (NORTHEAST@16):")
print("  Key: DIJJQELYOIECBAQKVAATCRDUMPABT (9 unknown positions: 0-4, 25-28)")
print("  PT:  UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF")

if 21 in [r['ent_pos'] for r in results]:
    r21 = [r for r in results if r['ent_pos'] == 21][0]
    print(f"\nNew (EASTNORTHEAST@21):")
    print(f"  Key: {r21['key']} (5 unknown positions: 16-20)")
    print(f"  PT:  {r21['pt']}")
    print(f"\nNew approach knows {29-r21['unknown']}/29 key positions vs 20/29 for original")
    print(f"New approach knows {r21['known_chars']}/97 plaintext chars vs ~68/97 for original")
