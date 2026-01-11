#!/usr/bin/env python3
"""
K4 Starting Word Search

Try many different 5-letter starting words at position 0.
For each:
1. Derive the key needed to produce that word
2. Check if BERLINCLOCK still appears at position 63
3. Check for additional English words in the result
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# The known key constraints from BERLINCLOCK at position 63
# Position 63-73 gives us key positions (63 mod 29) to (73 mod 29) = 5 to 15
BERLINCLOCK_KEY = {
    5: 'E', 6: 'L', 7: 'Y', 8: 'O', 9: 'I', 10: 'E',
    11: 'C', 12: 'B', 13: 'A', 14: 'Q', 15: 'K'
}

# NORTHEAST at position 16 gives us key positions (16 mod 29) to (24 mod 29) = 16 to 24
NORTHEAST_KEY = {
    16: 'V', 17: 'A', 18: 'A', 19: 'T', 20: 'C',
    21: 'R', 22: 'D', 23: 'U', 24: 'M'
}

def derive_key_char(ct_char, pt_char, alpha=KRYPTOS_ALPHA):
    """Derive key character: key = ct - pt mod 26"""
    ct_pos = alpha.index(ct_char)
    pt_pos = alpha.index(pt_char)
    key_val = (ct_pos - pt_pos) % len(alpha)
    return alpha[key_val]

def decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Decrypt: pt = ct - key mod 26"""
    ct_pos = alpha.index(ct_char)
    key_pos = alpha.index(key_char)
    pt_pos = (ct_pos - key_pos) % len(alpha)
    return alpha[pt_pos]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt full ciphertext with key"""
    return ''.join(decrypt_char(c, key[i % len(key)], alpha) for i, c in enumerate(ct))

# Extended English word list for checking
ENGLISH_WORDS = set([
    # 3-letter words
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE',
    'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'NOW', 'HIM', 'HOW', 'MAN', 'NEW', 'WAY', 'DAY',
    'TWO', 'USE', 'SET', 'END', 'SEE', 'SAY', 'SHE', 'OWN', 'OLD', 'WHO', 'WHY', 'TRY',
    # 4-letter words
    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN', 'CALL',
    'FIND', 'MANY', 'THEN', 'ALSO', 'INTO', 'JUST', 'OVER', 'SUCH', 'THAN', 'THEM',
    'WELL', 'WERE', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'MADE', 'EACH', 'ONLY',
    'KNOW', 'TAKE', 'YEAR', 'WORK', 'LAST', 'HERE', 'PART', 'SAID', 'BACK', 'MAKE',
    'LOOK', 'EVEN', 'MOST', 'LIKE', 'WHAT', 'MUST', 'LONG', 'EAST', 'WEST', 'NEAR',
    'LEFT', 'SIDE', 'HIGH', 'TURN', 'HEAD', 'HAND', 'FEET', 'DOOR', 'DOWN', 'UPON',
    'ROOM', 'AREA', 'SITE', 'BURY', 'DEEP', 'HIDE', 'TRUE', 'NEXT', 'WALL', 'STEP',
    # 5-letter words
    'ABOUT', 'AFTER', 'AGAIN', 'BELOW', 'BIRTH', 'BLOCK', 'BREAD', 'BREAK', 'BRING',
    'BUILD', 'CLOCK', 'CLOSE', 'COULD', 'DEPTH', 'EARTH', 'FIELD', 'FIRST', 'FOUND',
    'GIVEN', 'GOING', 'GREAT', 'GROUP', 'HEART', 'HOUSE', 'KNOWN', 'LARGE', 'LAYER',
    'LEARN', 'LEVEL', 'LIGHT', 'LOCAL', 'MAYBE', 'MONEY', 'NIGHT', 'NORTH', 'OTHER',
    'PEACE', 'PLACE', 'POINT', 'POWER', 'PRESS', 'QUITE', 'RIGHT', 'SHALL', 'SINCE',
    'SMALL', 'SOUND', 'SOUTH', 'SPEAK', 'SPENT', 'STAND', 'START', 'STATE', 'STILL',
    'STORY', 'STUDY', 'TAKEN', 'TERMS', 'THEIR', 'THERE', 'THESE', 'THING', 'THINK',
    'THREE', 'TODAY', 'TRUTH', 'UNTIL', 'USING', 'VALUE', 'VOICE', 'WATCH', 'WATER',
    'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE', 'WORLD', 'WOULD', 'WRITE', 'YEARS',
    'YOUNG', 'UNDER', 'ABOVE', 'CROSS', 'GRAVE', 'STONE', 'METER', 'STEPS', 'MILES',
    'SIGHT', 'ENTRY', 'ANGLE', 'POINT', 'EXACT', 'COVER', 'CLOAK', 'CRYPT', 'VAULT',
    # 6-letter words
    'BURIED', 'HIDDEN', 'SECRET', 'LOCATE', 'CENTER', 'CORNER', 'INSIDE', 'GROUND',
    'METERS', 'STAIRS', 'BEHIND', 'BESIDE', 'ACROSS', 'AROUND', 'TOWARD', 'WITHIN',
    'BEFORE', 'DURING', 'TWENTY', 'THIRTY', 'ELEVEN', 'TWELVE', 'DEGREE', 'MINUTE',
    'SECOND', 'SHADOW', 'LOCATE', 'DEEPER', 'HIGHER', 'SEARCH', 'FOLLOW', 'DIRECT',
    # 7+ letter words
    'BETWEEN', 'THROUGH', 'BECAUSE', 'HOWEVER', 'ANOTHER', 'AGAINST', 'ALREADY',
    'FURTHER', 'WITHOUT', 'BENEATH', 'EXACTLY', 'FIFTEEN', 'SIXTEEN', 'SEVENTY',
    'HUNDRED', 'DEGREES', 'MINUTES', 'SECONDS', 'HEADING', 'BEARING', 'COMPASS',
    'LOCATION', 'POSITION', 'DIRECTLY', 'DIRECTLY', 'TREASURE', 'ENTRANCE',
    # Direction/navigation words
    'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
    # Berlin related
    'BERLIN', 'BERLINCLOCK', 'CLOCK', 'WALL', 'GATE',
])

STARTING_WORDS = [
    'ABOUT', 'AFTER', 'AGAIN', 'BELOW', 'BIRTH', 'BLOCK', 'BREAD', 'BREAK', 'BRING',
    'BUILD', 'CLOCK', 'CLOSE', 'COULD', 'DEPTH', 'EARTH', 'FIELD', 'FIRST', 'FOUND',
    'GIVEN', 'GOING', 'GREAT', 'GROUP', 'HEART', 'HOUSE', 'KNOWN', 'LARGE', 'LAYER',
    'LEARN', 'LEVEL', 'LIGHT', 'LOCAL', 'MAYBE', 'MONEY', 'NIGHT', 'NORTH', 'OTHER',
    'PEACE', 'PLACE', 'POINT', 'POWER', 'PRESS', 'QUITE', 'RIGHT', 'SHALL', 'SINCE',
    'SMALL', 'SOUND', 'SOUTH', 'SPEAK', 'SPENT', 'STAND', 'START', 'STATE', 'STILL',
    'STORY', 'STUDY', 'TAKEN', 'TERMS', 'THEIR', 'THERE', 'THESE', 'THING', 'THINK',
    'THREE', 'TODAY', 'TRUTH', 'UNTIL', 'USING', 'VALUE', 'VOICE', 'WATCH', 'WATER',
    'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE', 'WORLD', 'WOULD', 'WRITE', 'YEARS',
    'YOUNG', 'UNDER', 'ABOVE', 'CROSS', 'GRAVE', 'STONE', 'METER', 'STEPS', 'MILES',
    'SIGHT', 'ENTRY', 'ANGLE', 'EXACT', 'COVER', 'CLOAK', 'CRYPT', 'VAULT', 'SPACE',
    'FINAL', 'INNER', 'OUTER', 'LOWER', 'UPPER', 'DIGIT', 'HANDS', 'HOURS', 'FORTH',
    'HENCE', 'THENCE', 'BELOW', 'TOWER', 'EIGHT', 'SEVEN', 'SIXTY', 'FIFTY', 'FORTY',
]

def find_words(text, min_len=3):
    """Find English words in text"""
    found = []
    for word in ENGLISH_WORDS:
        if len(word) >= min_len and word in text:
            pos = text.find(word)
            found.append((word, pos))
    # Remove substrings (e.g., if BERLINCLOCK found, don't also report BERLIN and CLOCK)
    filtered = []
    for word, pos in sorted(found, key=lambda x: -len(x[0])):  # Longest first
        overlaps = False
        for fword, fpos in filtered:
            if pos >= fpos and pos < fpos + len(fword):
                overlaps = True
                break
            if fpos >= pos and fpos < pos + len(word):
                overlaps = True
                break
        if not overlaps:
            filtered.append((word, pos))
    return sorted(filtered, key=lambda x: x[1])

def test_starting_word(word, period=29):
    """Test a starting word and return results"""
    # Build key with fixed positions from BERLINCLOCK (5-15) and NORTHEAST (16-24)
    key = ['?'] * period

    # Fill in from BERLINCLOCK at position 63
    for pos, char in BERLINCLOCK_KEY.items():
        key[pos] = char

    # Fill in from NORTHEAST at position 16
    for pos, char in NORTHEAST_KEY.items():
        key[pos] = char

    # Derive key for starting word at positions 0-4
    for i, pt_char in enumerate(word):
        ct_char = K4[i]
        key_char = derive_key_char(ct_char, pt_char)
        key[i] = key_char

    # Positions 25-28: derived from ABOVE at position 83 in original
    # Position 83 mod 29 = 25, so positions 25-28
    # But we might want to try without this constraint too

    # Decrypt with partial key (using 'K' for unknowns)
    test_key = ''.join(c if c != '?' else 'K' for c in key)
    plaintext = vigenere_decrypt(K4, test_key)

    # Check BERLINCLOCK at position 63
    has_berlinclock = plaintext[63:74] == 'BERLINCLOCK'

    # Check NORTHEAST at position 16
    has_northeast = plaintext[16:25] == 'NORTHEAST'

    # Find words
    words_found = find_words(plaintext, min_len=3)

    return {
        'word': word,
        'key': test_key,
        'plaintext': plaintext,
        'has_berlinclock': has_berlinclock,
        'has_northeast': has_northeast,
        'words_found': words_found,
        'word_count': len(words_found),
        'unknown_positions': [i for i, c in enumerate(key) if c == '?']
    }

print("="*80)
print("K4 STARTING WORD SEARCH")
print("="*80)
print(f"Testing {len(STARTING_WORDS)} starting words at position 0")
print(f"Period: 29")
print()

# Test all starting words
results = []
for word in STARTING_WORDS:
    if len(word) == 5:  # Only test 5-letter words
        result = test_starting_word(word)
        results.append(result)

# Sort by number of words found
results.sort(key=lambda x: (-x['word_count'], -int(x['has_berlinclock']), -int(x['has_northeast'])))

# Show top results
print("="*80)
print("TOP RESULTS (sorted by word count)")
print("="*80)

for i, r in enumerate(results[:30]):  # Show top 30
    print(f"\n--- {i+1}. Starting word: {r['word']} ---")
    print(f"Has BERLINCLOCK at 63: {r['has_berlinclock']}")
    print(f"Has NORTHEAST at 16:   {r['has_northeast']}")
    print(f"Words found ({r['word_count']}): {r['words_found']}")
    print(f"Plaintext: {r['plaintext']}")

# Focus on results that have both cribs
print("\n" + "="*80)
print("RESULTS WITH BOTH CRIBS (BERLINCLOCK and NORTHEAST)")
print("="*80)

both_cribs = [r for r in results if r['has_berlinclock'] and r['has_northeast']]
print(f"\n{len(both_cribs)} results have both cribs:")

for r in both_cribs:
    print(f"\n=== {r['word']} ===")
    print(f"Key: {r['key']}")
    print(f"Plaintext: {r['plaintext']}")
    print(f"Words found: {r['words_found']}")

    # Show structure
    print(f"\nStructure:")
    pt = r['plaintext']
    print(f"  0-4:   {pt[0:5]}")
    print(f"  5-15:  {pt[5:16]}")
    print(f" 16-24:  {pt[16:25]}")
    print(f" 25-62:  {pt[25:63]}")
    print(f" 63-73:  {pt[63:74]}")
    print(f" 74-96:  {pt[74:97]}")
