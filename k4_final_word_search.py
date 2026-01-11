#!/usr/bin/env python3
"""
K4 Final Word Search - Brute force unknown key positions to maximize readable words.
"""

# KRYPTOS alphabet
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# K4 ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Best known Period 29 key (with UNDER at 0, NORTHEAST at 16, BERLINCLOCK at 63, ABOVE at 83)
# Positions 0-4: DIJJQ (from UNDER)
# Positions 5-15: ELYOIECBAQK (from BERLINCLOCK)
# Positions 16-24: VAATCRDUM (from NORTHEAST)
# Positions 25-28: PABT (from ABOVE)
BASE_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# English words to search for (3+ letters)
WORDS = [
    # 3-letter words
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT",
    "DAY", "HAD", "HOT", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "ITS",
    "LET", "PUT", "SAY", "SHE", "TOO", "USE", "HIS", "END", "KEY", "SPY", "CIA", "KGB", "MAP", "DIG",
    # 4-letter words
    "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY", "BEEN", "CALL", "FIRST", "FIND",
    "WORD", "EACH", "LOOK", "ONLY", "COME", "MADE", "LONG", "THAN", "SITE", "BURY", "HIDE", "WALL",
    "EAST", "WEST", "TIME", "HERE", "MARK", "SPOT", "LAND", "SHOW", "LEFT", "GOLD", "OPEN", "DARK",
    # 5-letter words
    "THERE", "THEIR", "ABOUT", "WOULD", "COULD", "THESE", "OTHER", "WHERE", "AFTER", "CLOCK",
    "UNDER", "ABOVE", "NORTH", "SOUTH", "LAYER", "POINT", "PLACE", "STONE", "EARTH", "FIELD",
    "LIGHT", "NIGHT", "RIGHT", "BELOW", "WORLD", "HANDS", "HOURS", "WATCH", "GRAVE", "VAULT",
    # 6+ letter words
    "BERLIN", "SHADOW", "BURIED", "HIDDEN", "SECRET", "SLOWLY", "LOCATION", "TREASURE", "COORDINATES",
    "BETWEEN", "ABSENCE", "NUANCE", "LANGLEY", "MAGNETIC", "CHAMBER", "CANDLE", "DOORWAY",
    "NORTHEAST", "SOUTHEAST", "NORTHWEST", "SOUTHWEST", "PALIMPSEST", "ABSCISSA",
    "BERLINCLOCK", "DESPERATELY"
]

def kryptos_decrypt_char(ct_char, key_char):
    """Decrypt single character using KRYPTOS tableau."""
    if ct_char not in KRYPTOS or key_char not in KRYPTOS:
        return ct_char
    ct_idx = KRYPTOS.index(ct_char)
    key_idx = KRYPTOS.index(key_char)
    pt_idx = (ct_idx - key_idx) % 26
    return KRYPTOS[pt_idx]

def decrypt_with_key(ciphertext, key):
    """Decrypt ciphertext with repeating key."""
    plaintext = ""
    key_len = len(key)
    for i, c in enumerate(ciphertext):
        plaintext += kryptos_decrypt_char(c, key[i % key_len])
    return plaintext

def find_words(plaintext):
    """Find all English words in plaintext and return them with positions."""
    found = []
    pt_upper = plaintext.upper()
    for word in WORDS:
        pos = 0
        while True:
            idx = pt_upper.find(word, pos)
            if idx == -1:
                break
            found.append((word, idx))
            pos = idx + 1
    return sorted(found, key=lambda x: x[1])

def score_words(words):
    """Score based on word lengths."""
    return sum(len(w[0]) for w in words)

# Test base key
print("=== K4 FINAL WORD SEARCH ===\n")
print(f"Base Key: {BASE_KEY}")
pt = decrypt_with_key(K4, BASE_KEY)
print(f"Plaintext: {pt}")
words = find_words(pt)
print(f"Words found: {words}")
print(f"Score: {score_words(words)}\n")

# Brute force positions 25-28 (4 positions = 26^4 = 456976 combinations)
print("=== BRUTE FORCING POSITIONS 25-28 ===\n")

best_score = 0
best_keys = []
best_limit = 10

for i0 in range(26):
    for i1 in range(26):
        for i2 in range(26):
            for i3 in range(26):
                key = BASE_KEY[:25] + KRYPTOS[i0] + KRYPTOS[i1] + KRYPTOS[i2] + KRYPTOS[i3]
                pt = decrypt_with_key(K4, key)
                words = find_words(pt)
                score = score_words(words)

                if score > best_score:
                    best_score = score
                    best_keys = [(key, pt, words, score)]
                elif score == best_score and len(best_keys) < best_limit:
                    best_keys.append((key, pt, words, score))

print(f"Best score: {best_score}")
print(f"Number of keys with best score: {len(best_keys)}\n")

for i, (key, pt, words, score) in enumerate(best_keys[:10]):
    print(f"--- Result {i+1} ---")
    print(f"Key positions 25-28: {key[25:]}")
    print(f"Full Key: {key}")
    print(f"Plaintext: {pt}")
    print(f"Words: {words}")
    print(f"Score: {score}")
    print()

# Also try brute forcing positions 0-4 while keeping 25-28 fixed
print("=== BRUTE FORCING POSITIONS 0-4 ===\n")

best_score2 = 0
best_keys2 = []

for i0 in range(26):
    if i0 % 5 == 0:
        print(f"Progress: {i0}/26...")
    for i1 in range(26):
        for i2 in range(26):
            for i3 in range(26):
                for i4 in range(26):
                    key = KRYPTOS[i0] + KRYPTOS[i1] + KRYPTOS[i2] + KRYPTOS[i3] + KRYPTOS[i4] + BASE_KEY[5:]
                    pt = decrypt_with_key(K4, key)
                    words = find_words(pt)
                    score = score_words(words)

                    if score > best_score2:
                        best_score2 = score
                        best_keys2 = [(key, pt, words, score)]
                    elif score == best_score2 and len(best_keys2) < best_limit:
                        best_keys2.append((key, pt, words, score))

print(f"\nBest score: {best_score2}")
print(f"Number of keys with best score: {len(best_keys2)}\n")

for i, (key, pt, words, score) in enumerate(best_keys2[:10]):
    print(f"--- Result {i+1} ---")
    print(f"Key positions 0-4: {key[:5]}")
    print(f"Full Key: {key}")
    print(f"Plaintext: {pt}")
    print(f"Words: {words}")
    print(f"Score: {score}")
    print()
