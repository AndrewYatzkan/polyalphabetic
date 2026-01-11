#!/usr/bin/env python3
"""
K4 Quick Word Search - Fast targeted search.
"""

# KRYPTOS alphabet
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known Period 29 key
BASE_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

WORDS = set([
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT",
    "DAY", "HAD", "HOT", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "ITS",
    "LET", "PUT", "SAY", "SHE", "TOO", "USE", "HIS", "END", "KEY", "SPY", "CIA", "KGB", "MAP", "DIG",
    "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY", "BEEN", "CALL", "FIND",
    "WORD", "EACH", "LOOK", "ONLY", "COME", "MADE", "LONG", "THAN", "SITE", "BURY", "HIDE", "WALL",
    "EAST", "WEST", "TIME", "HERE", "MARK", "SPOT", "LAND", "SHOW", "LEFT", "GOLD", "OPEN", "DARK",
    "THERE", "THEIR", "ABOUT", "WOULD", "COULD", "THESE", "OTHER", "WHERE", "AFTER", "CLOCK",
    "UNDER", "ABOVE", "NORTH", "SOUTH", "LAYER", "POINT", "PLACE", "STONE", "EARTH", "FIELD",
    "LIGHT", "NIGHT", "RIGHT", "BELOW", "WORLD", "HANDS", "HOURS", "WATCH", "GRAVE", "VAULT",
    "BERLIN", "SHADOW", "BURIED", "HIDDEN", "SECRET", "SLOWLY", "LOCATION", "TREASURE",
    "BETWEEN", "ABSENCE", "NUANCE", "LANGLEY", "MAGNETIC", "CHAMBER", "CANDLE", "DOORWAY",
    "NORTHEAST", "SOUTHEAST", "NORTHWEST", "SOUTHWEST", "PALIMPSEST", "ABSCISSA",
    "BERLINCLOCK", "DESPERATELY"
])

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

def find_words(pt):
    found = []
    for length in range(3, min(15, len(pt)+1)):
        for i in range(len(pt) - length + 1):
            substr = pt[i:i+length]
            if substr in WORDS:
                found.append((substr, i))
    return found

def score(words):
    return sum(len(w[0])**2 for w in words)  # Square length to favor longer words

# Test base key
print("=== BASE KEY TEST ===")
pt = decrypt(K4, BASE_KEY)
print(f"Key: {BASE_KEY}")
print(f"PT:  {pt}")
words = find_words(pt)
print(f"Words: {words}")
print(f"Score: {score(words)}\n")

# Try meaningful starting words
START_WORDS = ["UNDER", "LAYER", "CLOCK", "EARTH", "LIGHT", "NIGHT", "FIELD", "STONE",
               "PLACE", "GRAVE", "VAULT", "WATCH", "HANDS", "HOURS", "POINT", "WORLD",
               "THERE", "WHERE", "ABOUT", "AFTER", "THEIR", "THESE", "COULD", "WOULD",
               "BELOW", "ABOVE", "NORTH", "SOUTH", "SHADOW", "HIDDEN", "BURIED", "SECRET"]

print("=== TESTING STARTING WORDS ===")
results = []
for word in START_WORDS:
    # Derive key positions 0-len(word)-1 from this word at position 0
    derived = ""
    for i, c in enumerate(word):
        if i >= len(K4):
            break
        ct_char = K4[i]
        pt_char = c
        ct_idx = KRYPTOS.index(ct_char)
        pt_idx = KRYPTOS.index(pt_char)
        key_idx = (ct_idx - pt_idx) % 26
        derived += KRYPTOS[key_idx]

    # Build key with derived start + base key middle + base key end
    word_len = len(word)
    if word_len <= 5:
        key = derived + BASE_KEY[word_len:]
    else:
        key = derived + BASE_KEY[word_len:]

    pt = decrypt(K4, key)
    words_found = find_words(pt)
    s = score(words_found)
    results.append((word, key, pt, words_found, s))

# Sort by score
results.sort(key=lambda x: -x[4])

print("Top 15 results:\n")
for i, (start_word, key, pt, words_found, s) in enumerate(results[:15]):
    print(f"{i+1}. Start: {start_word}")
    print(f"   Key: {key}")
    print(f"   PT:  {pt}")
    print(f"   Words: {words_found}")
    print(f"   Score: {s}")
    print()

# Now try ending words at position 83
print("=== TESTING ENDING WORDS AT POSITION 83 ===")
END_WORDS = ["ABOVE", "BELOW", "UNDER", "LIGHT", "NIGHT", "RIGHT", "SIGHT", "FIGHT",
             "HANDS", "LANDS", "SANDS", "BANDS"]

end_results = []
for word in END_WORDS:
    if len(word) > 97 - 83:
        word = word[:97-83]

    # Derive key positions (83 mod 29) to (83+len-1 mod 29)
    key_list = list(BASE_KEY)
    for i, c in enumerate(word):
        pos = 83 + i
        if pos >= len(K4):
            break
        ct_char = K4[pos]
        pt_char = c
        ct_idx = KRYPTOS.index(ct_char)
        pt_idx = KRYPTOS.index(pt_char)
        key_idx = (ct_idx - pt_idx) % 26
        key_pos = pos % 29
        key_list[key_pos] = KRYPTOS[key_idx]

    key = "".join(key_list)
    pt = decrypt(K4, key)
    words_found = find_words(pt)
    s = score(words_found)
    end_results.append((word, key, pt, words_found, s))

end_results.sort(key=lambda x: -x[4])

print("Top 10 ending results:\n")
for i, (end_word, key, pt, words_found, s) in enumerate(end_results[:10]):
    print(f"{i+1}. End: {end_word}")
    print(f"   Key: {key}")
    print(f"   PT:  {pt}")
    print(f"   Words: {words_found}")
    print(f"   Score: {s}")
    print()
