#!/usr/bin/env python3
"""
Test ALL NORTHEAST positions (0-88) against ALL periods (20-50).
For each (position, period) pair:
  - Check compatibility of BERLINCLOCK@63 and NORTHEAST@N constraints
  - Derive forced key positions
  - Decrypt what we can
  - Score by English word count
Report top 10 results.
"""

import sys
from collections import defaultdict

# ─── Constants ────────────────────────────────────────────────────────────────

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
assert len(KRYPTOS_ALPHA) == 26, f"Expected 26, got {len(KRYPTOS_ALPHA)}"

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
assert len(K4_CIPHER) == 97, f"Expected 97, got {len(K4_CIPHER)}"

# Known cribs
BERLINCLOCK_PLAIN = "BERLINCLOCK"   # confirmed at ciphertext position 63
BERLINCLOCK_POS   = 63

NORTHEAST_PLAIN   = "NORTHEAST"     # position is what we're testing
NORTHEAST_LEN     = len(NORTHEAST_PLAIN)  # 9

# Sanborn also mentioned NORTHEAST could start at various positions.
# Valid range: 0 through len(K4_CIPHER)-len(NORTHEAST_PLAIN) = 88
MAX_NE_POS = len(K4_CIPHER) - NORTHEAST_LEN  # 88

# ─── Alphabet helpers ─────────────────────────────────────────────────────────

ALPHA_INDEX = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}

def vigenere_decrypt_char(cipher_char, key_char):
    """Decrypt one character using Kryptos-alphabet Vigenère."""
    c = ALPHA_INDEX[cipher_char]
    k = ALPHA_INDEX[key_char]
    p = (c - k) % 26
    return KRYPTOS_ALPHA[p]

def vigenere_encrypt_char(plain_char, key_char):
    """Encrypt one character using Kryptos-alphabet Vigenère."""
    p = ALPHA_INDEX[plain_char]
    k = ALPHA_INDEX[key_char]
    c = (p + k) % 26
    return KRYPTOS_ALPHA[c]

def derive_key_char(cipher_char, plain_char):
    """Given cipher and plain, derive the key character."""
    c = ALPHA_INDEX[cipher_char]
    p = ALPHA_INDEX[plain_char]
    k = (c - p) % 26
    return KRYPTOS_ALPHA[k]

# ─── Load word list ────────────────────────────────────────────────────────────

WORD_SET = set()
DICT_PATH = "/home/user/polyalphabetic/OxfordEnglishWords.txt"
try:
    with open(DICT_PATH) as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 3:
                # Only keep words using letters in KRYPTOS_ALPHA (standard A-Z minus J)
                if all(c in ALPHA_INDEX for c in w):
                    WORD_SET.add(w)
    print(f"Loaded {len(WORD_SET):,} words from dictionary.")
except FileNotFoundError:
    # Fallback minimal set
    print("Dictionary not found, using minimal fallback.")
    for w in ["THE","AND","THAT","HAVE","FOR","NOT","WITH","YOU","THIS","BUT",
              "HIS","FROM","THEY","SAY","HER","SHE","WILL","ONE","ALL","WOULD",
              "THERE","THEIR","WHAT","OUT","ABOUT","WHO","GET","WHICH","WHEN","MAKE",
              "CAN","LIKE","TIME","JUST","HIM","KNOW","TAKE","PEOPLE","INTO","YEAR",
              "YOUR","GOOD","SOME","COULD","THEM","SEE","OTHER","THAN","THEN","NOW",
              "LOOK","ONLY","COME","ITS","OVER","THINK","ALSO","BACK","AFTER","USE",
              "TWO","HOW","OUR","WORK","FIRST","WELL","WAY","EVEN","NEW","WANT",
              "BECAUSE","ANY","THESE","GIVE","DAY","MOST","NORTH","EAST","SOUTH","WEST",
              "NORTHEAST","BERLIN","CLOCK","SHADOW","LAYER","UNDERGROUND","BETWEEN",
              "BELOW","ABOVE","NIGHT","LIGHT","DARK","HIDDEN","SECRET","MESSAGE",
              "POSITION","DEGREES","LATITUDE","LONGITUDE","COORDINATE","LOCATION",
              "INVISIBLE","DIGITAL","SHADOWS","PERHAPS","ALREADY","SOMEWHAT","SLOWLY",
              "DIGETAL","INTERPRE","SHADOW","FORCES",
              "WHO","KNOWS","WHAT","LIES","BEEN","TOLD","FIND","MINE","AREA","WEST",
              "EAST","NORTH","SOUTH","ABOVE","BELOW","NEAR","FAR","LONG","DEEP",
              "LAYER","POINT","PLACE","SPACE","MOVE","TURN","LEFT","RIGHT","SIDE",
              "GROUND","FEET","INCH","MILE","YARD","METER","FOOT","ACRE","LAND",
              "SITE","MARK","LINE","ROAD","PATH","GATE","DOOR","WALL","ROOM","HALL",
              "THEY","SAID","WHEN","TOLD","THIS","FROM","WITH","HAVE","BEEN","WILL",
              "ONLY","INTO","SOME","LIKE","KNOW","JUST","COME","MAKE","TAKE","GIVE"]:
        WORD_SET.add(w)

# ─── Score plaintext ──────────────────────────────────────────────────────────

def score_plaintext(plaintext, min_word_len=3):
    """
    Count overlapping occurrences of dictionary words in the plaintext.
    Use a substring search so we don't need explicit word boundaries
    (since K4 has no spaces).
    Returns (score, list_of_found_words).
    """
    found = []
    text = "".join(c if c in ALPHA_INDEX else "?" for c in plaintext)
    # Only score non-'?' characters
    solid = "".join(c for c in text if c != "?")

    # Check all substrings of length 3+
    for length in range(3, min(15, len(text) + 1)):
        for start in range(len(text) - length + 1):
            substr = text[start:start+length]
            if "?" not in substr and substr in WORD_SET:
                found.append((start, substr))

    # Deduplicate: keep longest non-overlapping set (greedy by length then position)
    found.sort(key=lambda x: (-len(x[1]), x[0]))
    used_positions = set()
    kept = []
    for start, word in found:
        positions = set(range(start, start + len(word)))
        if not positions & used_positions:
            used_positions |= positions
            kept.append((start, word))

    score = sum(len(w) ** 2 for _, w in kept)  # longer words score quadratically
    return score, [w for _, w in kept]

# ─── Main analysis ─────────────────────────────────────────────────────────────

def analyze(ne_pos, period):
    """
    Given NORTHEAST at ne_pos and a Vigenère period, attempt to derive
    the partial key from both cribs and decrypt what we can.
    Returns (score, words_found, key_slots, plaintext) or None if conflict.
    """
    # key_slots[i] = known key character at period position i
    # i ranges 0..period-1
    key_slots = [None] * period

    # --- Derive key slots from BERLINCLOCK at pos 63 ---
    bc_pos = BERLINCLOCK_POS
    bc_plain = "BERLINCLOCK"
    for offset, pc in enumerate(bc_plain):
        cipher_idx = bc_pos + offset
        key_slot   = cipher_idx % period
        cc = K4_CIPHER[cipher_idx]
        kc = derive_key_char(cc, pc)
        if key_slots[key_slot] is None:
            key_slots[key_slot] = kc
        elif key_slots[key_slot] != kc:
            return None  # conflict from BERLINCLOCK alone (shouldn't happen for valid key)

    # --- Derive key slots from NORTHEAST at ne_pos ---
    ne_plain = NORTHEAST_PLAIN
    for offset, pc in enumerate(ne_plain):
        cipher_idx = ne_pos + offset
        key_slot   = cipher_idx % period
        cc = K4_CIPHER[cipher_idx]
        kc = derive_key_char(cc, pc)
        if key_slots[key_slot] is None:
            key_slots[key_slot] = kc
        elif key_slots[key_slot] != kc:
            return None  # conflict between the two cribs

    # --- Decrypt all positions where key_slot is known ---
    plaintext = []
    for i, cc in enumerate(K4_CIPHER):
        ks = i % period
        if key_slots[ks] is not None:
            pc = vigenere_decrypt_char(cc, key_slots[ks])
            plaintext.append(pc)
        else:
            plaintext.append("?")

    # Score it
    score, words = score_plaintext(plaintext)

    # Count known positions
    known_count = sum(1 for c in plaintext if c != "?")

    return score, words, key_slots, "".join(plaintext), known_count


def main():
    results = []

    total = (MAX_NE_POS + 1) * (50 - 20 + 1)
    done  = 0

    print(f"Testing {MAX_NE_POS + 1} NE positions × 31 periods = {total} combinations...")
    print()

    for ne_pos in range(0, MAX_NE_POS + 1):
        for period in range(20, 51):
            done += 1
            if done % 500 == 0:
                sys.stdout.write(f"\r  Progress: {done}/{total} ({100*done/total:.1f}%)")
                sys.stdout.flush()

            result = analyze(ne_pos, period)
            if result is None:
                continue  # incompatible

            score, words, key_slots, plaintext, known_count = result

            # Only record if there's at least some score or known positions
            if known_count > 0:
                results.append((score, ne_pos, period, key_slots, plaintext, words, known_count))

    print(f"\r  Done: {done}/{total} combinations tested.          ")
    print()

    # Sort by score descending
    results.sort(key=lambda x: -x[0])

    print("=" * 100)
    print("TOP 20 RESULTS (by English word score)")
    print("=" * 100)

    shown = 0
    prev_key_sig = None

    for rank, (score, ne_pos, period, key_slots, plaintext, words, known_count) in enumerate(results[:50]):
        if shown >= 20:
            break

        # Build key string (? for unknown)
        key_str = "".join(k if k else "?" for k in key_slots)

        # Build a short signature to avoid showing trivially duplicate results
        key_sig = (ne_pos, period)

        shown += 1
        print(f"\nRank #{shown}")
        print(f"  Period:          {period}")
        print(f"  NORTHEAST pos:   {ne_pos}")
        print(f"  Score:           {score}")
        print(f"  Known positions: {known_count}/{len(K4_CIPHER)}")
        print(f"  Key ({period} chars):  {key_str}")

        # Show BERLINCLOCK overlap slots
        bc_slots = sorted(set((63 + i) % period for i in range(11)))
        ne_slots = sorted(set((ne_pos + i) % period for i in range(9)))
        overlap  = sorted(set(bc_slots) & set(ne_slots))
        print(f"  BERLINCLOCK uses key slots: {bc_slots}")
        print(f"  NORTHEAST uses key slots:   {ne_slots}")
        print(f"  Overlap slots:              {overlap}")

        # Print decrypted text with positional markers
        print(f"  Decrypted (? = unknown key slot):")
        # Show in rows of 10
        ct_chunks = [K4_CIPHER[i:i+10] for i in range(0, len(K4_CIPHER), 10)]
        pt_chunks = [plaintext[i:i+10] for i in range(0, len(plaintext), 10)]
        for row_i, (ct_chunk, pt_chunk) in enumerate(zip(ct_chunks, pt_chunks)):
            pos = row_i * 10
            print(f"    [{pos:2d}-{pos+len(ct_chunk)-1:2d}] CT: {ct_chunk}  PT: {pt_chunk}")

        if words:
            print(f"  English words found: {', '.join(sorted(set(words)))}")
        else:
            print(f"  English words found: (none)")

        print()

    # Also show best results for each period
    print("=" * 100)
    print("BEST RESULT PER PERIOD (period 20 to 50)")
    print("=" * 100)

    best_per_period = {}
    for score, ne_pos, period, key_slots, plaintext, words, known_count in results:
        if period not in best_per_period:
            best_per_period[period] = (score, ne_pos, period, key_slots, plaintext, words, known_count)

    for period in range(20, 51):
        if period not in best_per_period:
            print(f"  Period {period:2d}: No compatible result found")
            continue
        score, ne_pos, _, key_slots, plaintext, words, known_count = best_per_period[period]
        key_str = "".join(k if k else "?" for k in key_slots)
        print(f"  Period {period:2d}: NE_pos={ne_pos:2d}  score={score:4d}  known={known_count:2d}  "
              f"key={key_str}  words={words}")

    # Summary stats
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    compat_count = len(results)
    print(f"  Total combinations tested:   {total}")
    print(f"  Compatible combinations:     {compat_count}")
    print(f"  Incompatible (conflict):     {total - compat_count}")

    # Show all NE positions that conflict with period 29
    print()
    print("  Conflict analysis for period=29:")
    for ne_pos in range(0, MAX_NE_POS + 1):
        r = analyze(ne_pos, 29)
        if r is None:
            print(f"    NE_pos={ne_pos:2d}: CONFLICT with BERLINCLOCK@63 under period 29")

    # Show NE positions that give highest scores under period 29
    print()
    print("  Top NORTHEAST positions under period 29:")
    p29_results = [(score, ne_pos, words, plaintext, key_slots, known_count)
                   for score, ne_pos, period, key_slots, plaintext, words, known_count in results
                   if period == 29]
    p29_results.sort(key=lambda x: -x[0])
    for score, ne_pos, words, plaintext, key_slots, known_count in p29_results[:10]:
        key_str = "".join(k if k else "?" for k in key_slots)
        print(f"    NE_pos={ne_pos:2d}  score={score:4d}  known={known_count:2d}  words={words}")
        print(f"      key={key_str}")
        print(f"      pt ={plaintext}")

if __name__ == "__main__":
    main()
