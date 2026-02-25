#!/usr/bin/env python3
"""
Test progressive/shifting key hypotheses on K4.

K4 ciphertext: OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ
Known cribs: BERLINCLOCK at position 63, NORTHEAST at position 16

The hypothesis: the standard Vigenere key SHIFTS by some function f(i) at each position,
so that:
    key_effective[i] = base_key[i % P] + f(i)  (mod 26)

We test multiple progression functions and check if both cribs can be satisfied simultaneously.
"""

import sys
from collections import defaultdict

# ==============================================================================
# Constants
# ==============================================================================

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
assert len(CT) == 97

KALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
assert len(KALPHA) == 26

# Build lookup tables for the KRYPTOS alphabet
CHAR_TO_NUM = {ch: i for i, ch in enumerate(KALPHA)}
NUM_TO_CHAR = {i: ch for i, ch in enumerate(KALPHA)}

# Cribs
CRIB_BERLIN = ("BERLINCLOCK", 63)
CRIB_NORTHEAST = ("NORTHEAST", 16)

# Dictionary
DICT_PATH = "OxfordEnglishWords.txt"

# ==============================================================================
# Helper Functions
# ==============================================================================

def load_dictionary(min_len=3):
    """Load English words from dictionary, filtered by minimum length."""
    words = set()
    try:
        with open(DICT_PATH, 'r') as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= min_len:
                    words.add(w)
    except FileNotFoundError:
        print(f"WARNING: Dictionary file {DICT_PATH} not found. Using built-in word list.")
        # Fallback minimal list
        words = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                 "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "HAD",
                 "HAS", "HIS", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE",
                 "WAY", "WHO", "BOY", "DID", "GET", "HIM", "LET", "SAY",
                 "SHE", "TOO", "USE", "THAT", "WITH", "HAVE", "THIS",
                 "WILL", "YOUR", "FROM", "THEY", "BEEN", "CALL", "COME",
                 "EACH", "MAKE", "LIKE", "LONG", "LOOK", "MANY", "SOME",
                 "TIME", "VERY", "WHEN", "WORD", "SAID", "WHAT", "WERE",
                 "BERLIN", "CLOCK", "NORTH", "EAST", "NORTHEAST", "SOUTH",
                 "WEST", "BETWEEN", "SUBTLE", "SHADING", "ABSENCE", "LIGHT",
                 "SLOWLY", "DESPARATLY", "UNDERGROUND", "LAYER", "SHADOW",
                 "SECRET", "HIDDEN", "CIPHER", "CODE", "ENCRYPTED",
                 "COORDINATE", "LATITUDE", "LONGITUDE", "DEGREE", "MINUTES",
                 "SECONDS", "LOCATION", "POSITION", "BURIED", "TREASURE",
                 "EARTH", "STONE", "COPPER", "METAL", "PLATE"}
    return words


def k_encrypt(plain_num, key_num):
    """Encrypt: ciphertext = (plaintext + key) mod 26 in KRYPTOS alphabet."""
    return (plain_num + key_num) % 26


def k_decrypt(cipher_num, key_num):
    """Decrypt: plaintext = (ciphertext - key) mod 26 in KRYPTOS alphabet."""
    return (cipher_num - key_num) % 26


def text_to_nums(text):
    """Convert text string to list of KRYPTOS alphabet numbers."""
    return [CHAR_TO_NUM[ch] for ch in text]


def nums_to_text(nums):
    """Convert list of KRYPTOS alphabet numbers to text string."""
    return ''.join(NUM_TO_CHAR[n % 26] for n in nums)


def derive_key_from_crib(ct_text, plain_text, start_pos):
    """Derive the effective key values needed at positions [start_pos..start_pos+len-1]
       to decrypt ct_text[start_pos:...] to plain_text.
       key[i] = ct[i] - pt[i-start_pos] mod 26
    """
    ct_nums = text_to_nums(ct_text)
    pt_nums = text_to_nums(plain_text)
    keys = []
    for j in range(len(plain_text)):
        pos = start_pos + j
        k = (ct_nums[pos] - pt_nums[j]) % 26
        keys.append((pos, k))
    return keys  # list of (position, key_value)


def decrypt_full(ct_text, effective_key):
    """Decrypt full ciphertext using effective_key (list of 97 key values)."""
    ct_nums = text_to_nums(ct_text)
    pt_nums = [k_decrypt(ct_nums[i], effective_key[i]) for i in range(len(ct_text))]
    return nums_to_text(pt_nums)


def score_english(text, word_set, min_word_len=3):
    """Score text by counting English words found in it.
    Returns (count, list_of_words_found, total_chars_covered).
    Uses greedy longest-match approach.
    """
    text = text.upper()
    n = len(text)
    found_words = []
    covered = [False] * n

    # Try to find words from longest to shortest
    max_word_len = min(20, n)
    for wlen in range(max_word_len, min_word_len - 1, -1):
        for i in range(n - wlen + 1):
            # Skip if overlapping with already found word
            if any(covered[i:i + wlen]):
                continue
            substr = text[i:i + wlen]
            if substr in word_set:
                found_words.append((i, substr))
                for j in range(i, i + wlen):
                    covered[j] = True

    total_covered = sum(covered)
    return len(found_words), found_words, total_covered


def score_english_simple(text, word_set, min_word_len=4):
    """Simpler/faster scoring: count distinct words of length >= min_word_len found as substrings."""
    text = text.upper()
    found = set()
    for w in word_set:
        if len(w) >= min_word_len and w in text:
            found.add(w)
    return len(found), found


# ==============================================================================
# Derive known key constraints from cribs
# ==============================================================================

def get_crib_constraints():
    """Get the effective key values required at each crib position."""
    berlin_keys = derive_key_from_crib(CT, CRIB_BERLIN[0], CRIB_BERLIN[1])
    northeast_keys = derive_key_from_crib(CT, CRIB_NORTHEAST[0], CRIB_NORTHEAST[1])
    return berlin_keys, northeast_keys


# ==============================================================================
# Approach 1: Additive Progressive Key
# key_effective[i] = base_key[i % P] + floor(i / P) * shift  (mod 26)
# ==============================================================================

def test_additive_progressive(word_set, berlin_keys, northeast_keys):
    """Test additive progressive key for various periods and shifts."""
    print("=" * 80)
    print("APPROACH 1: Additive Progressive Key")
    print("  key_effective[i] = base_key[i % P] + floor(i / P) * shift  (mod 26)")
    print("=" * 80)

    results = []

    for period in range(26, 32):
        for shift in range(1, 26):
            # Derive base_key from BERLINCLOCK @ 63
            # key_effective[63+j] = base_key[(63+j) % P] + floor((63+j) / P) * shift
            # => base_key[(63+j) % P] = key_effective[63+j] - floor((63+j) / P) * shift
            base_key = [None] * period
            conflict = False

            # Fill base_key from Berlin crib
            for pos, kval in berlin_keys:
                cycle = pos // period
                slot = pos % period
                derived = (kval - cycle * shift) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    conflict = True
                    break
                base_key[slot] = derived

            if conflict:
                continue

            # Check Northeast crib consistency
            ne_ok = True
            for pos, kval in northeast_keys:
                cycle = pos // period
                slot = pos % period
                derived = (kval - cycle * shift) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    ne_ok = False
                    break
                # Tentatively set if not yet set
                base_key[slot] = derived

            if not ne_ok:
                continue

            # Fill remaining base_key slots with 0 (we'll try to brute force later,
            # but for now just fill with 0 to get a sense)
            unfilled = [i for i in range(period) if base_key[i] is None]
            # If too many unfilled, skip detailed analysis but note the match
            base_key_filled = list(base_key)
            for i in unfilled:
                base_key_filled[i] = 0

            # Build effective key
            eff_key = []
            for i in range(len(CT)):
                cycle = i // period
                slot = i % period
                eff_key.append((base_key_filled[slot] + cycle * shift) % 26)

            pt = decrypt_full(CT, eff_key)

            # Verify cribs
            berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
            ne_match = pt[16:16 + 9] == "NORTHEAST"

            if berlin_match and ne_match:
                nwords, words_found, chars_covered = score_english(pt, word_set)
                # Don't count the cribs themselves
                non_crib_words = [(p, w) for p, w in words_found
                                  if not (63 <= p < 74) and not (16 <= p < 25)]
                non_crib_count = len(non_crib_words)

                results.append({
                    'period': period, 'shift': shift,
                    'unfilled': len(unfilled),
                    'plaintext': pt,
                    'word_count': non_crib_count,
                    'words': non_crib_words,
                    'base_key': base_key_filled
                })

                if non_crib_count >= 1:
                    print(f"\n  Period={period}, Shift={shift}, Unfilled={len(unfilled)}, "
                          f"Extra words={non_crib_count}")
                    print(f"    PT: {pt}")
                    print(f"    Words: {non_crib_words}")
                    bk_str = ''.join(NUM_TO_CHAR[v] for v in base_key_filled)
                    print(f"    Base key: {bk_str}")

    # Summary
    both_match = [r for r in results if True]  # all results already have both cribs
    good = [r for r in results if r['word_count'] >= 3]

    print(f"\n  Total period/shift combos satisfying both cribs: {len(results)}")
    print(f"  Combos with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    P={r['period']} S={r['shift']} Words={r['word_count']}: "
                  f"{r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 2: Progressive Period
# Period starts at P0 and increases by 1 each cycle
# ==============================================================================

def test_progressive_period(word_set, berlin_keys, northeast_keys):
    """Test progressive period: period increases by 1 each cycle."""
    print("\n" + "=" * 80)
    print("APPROACH 2: Progressive Period")
    print("  Period starts at P0, increases by delta each cycle")
    print("=" * 80)

    results = []

    for p0 in range(20, 35):
        for delta in [-2, -1, 1, 2]:
            # Map position -> (cycle, slot within that cycle)
            # Cycle 0: positions 0..p0-1 (period = p0)
            # Cycle 1: positions p0..p0+(p0+delta)-1 (period = p0+delta)
            # etc.

            def pos_to_cycle_slot(pos):
                """Given a position, return (cycle_number, slot_in_cycle, period_of_cycle)."""
                remaining = pos
                cycle = 0
                while True:
                    cur_period = p0 + cycle * delta
                    if cur_period <= 0:
                        return None  # degenerate
                    if remaining < cur_period:
                        return (cycle, remaining, cur_period)
                    remaining -= cur_period
                    cycle += 1
                    if cycle > 100:  # safety
                        return None

            # Build slot->key mapping from Berlin crib
            # In progressive period, the "base key" concept is: key[slot] within each cycle
            # But the slot meaning changes each cycle. We need a different model.
            # Model: key_effective[i] = base_key[slot_in_cycle] where period varies
            # This means base_key has potentially different lengths each cycle.
            # Simpler model: base_key is of length p0, and we wrap with changing period.

            # Actually, let's model it as: the KEY is fixed length p0, but the period
            # of application changes. So key_effective[i] = base_key[slot % p0]
            # where slot is the position within the current cycle.

            base_key = [None] * p0
            conflict = False

            for pos, kval in berlin_keys:
                info = pos_to_cycle_slot(pos)
                if info is None:
                    conflict = True
                    break
                cycle, slot, cur_period = info
                # Key slot wraps around base key
                bk_slot = slot % p0
                if base_key[bk_slot] is not None and base_key[bk_slot] != kval:
                    conflict = True
                    break
                base_key[bk_slot] = kval

            if conflict:
                continue

            ne_ok = True
            for pos, kval in northeast_keys:
                info = pos_to_cycle_slot(pos)
                if info is None:
                    ne_ok = False
                    break
                cycle, slot, cur_period = info
                bk_slot = slot % p0
                if base_key[bk_slot] is not None and base_key[bk_slot] != kval:
                    ne_ok = False
                    break
                base_key[bk_slot] = kval

            if not ne_ok:
                continue

            # Fill unfilled slots with 0
            unfilled = sum(1 for v in base_key if v is None)
            base_key_filled = [v if v is not None else 0 for v in base_key]

            # Build effective key for all 97 positions
            eff_key = []
            for i in range(len(CT)):
                info = pos_to_cycle_slot(i)
                if info is None:
                    eff_key.append(0)
                    continue
                cycle, slot, cur_period = info
                bk_slot = slot % p0
                eff_key.append(base_key_filled[bk_slot])

            pt = decrypt_full(CT, eff_key)

            berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
            ne_match = pt[16:16 + 9] == "NORTHEAST"

            if berlin_match and ne_match:
                nwords, words_found, chars_covered = score_english(pt, word_set)
                non_crib_words = [(p, w) for p, w in words_found
                                  if not (63 <= p < 74) and not (16 <= p < 25)]

                results.append({
                    'p0': p0, 'delta': delta,
                    'unfilled': unfilled,
                    'plaintext': pt,
                    'word_count': len(non_crib_words),
                    'words': non_crib_words
                })

                if len(non_crib_words) >= 1:
                    print(f"\n  P0={p0}, Delta={delta}, Unfilled={unfilled}, "
                          f"Extra words={len(non_crib_words)}")
                    print(f"    PT: {pt}")
                    print(f"    Words: {non_crib_words}")

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs satisfying both cribs: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    P0={r['p0']} D={r['delta']} Words={r['word_count']}: {r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 3: Key with Linear Progression
# key_effective[i] = base_key[i % P] + i * slope  (mod 26)
# ==============================================================================

def test_linear_progression(word_set, berlin_keys, northeast_keys):
    """Test key with position-dependent linear offset."""
    print("\n" + "=" * 80)
    print("APPROACH 3: Linear Progression")
    print("  key_effective[i] = base_key[i % P] + i * slope  (mod 26)")
    print("=" * 80)

    results = []

    for period in range(26, 32):
        for slope_num in range(1, 26):
            for slope_den in [1, 2, 3, 5, 7, 13]:
                # slope = slope_num / slope_den, but we work in integers
                # key_effective[i] = base_key[i%P] + floor(i * slope_num / slope_den) mod 26

                base_key = [None] * period
                conflict = False

                for pos, kval in berlin_keys:
                    slot = pos % period
                    offset = (pos * slope_num) // slope_den
                    derived = (kval - offset) % 26
                    if base_key[slot] is not None and base_key[slot] != derived:
                        conflict = True
                        break
                    base_key[slot] = derived

                if conflict:
                    continue

                ne_ok = True
                for pos, kval in northeast_keys:
                    slot = pos % period
                    offset = (pos * slope_num) // slope_den
                    derived = (kval - offset) % 26
                    if base_key[slot] is not None and base_key[slot] != derived:
                        ne_ok = False
                        break
                    base_key[slot] = derived

                if not ne_ok:
                    continue

                unfilled = sum(1 for v in base_key if v is None)
                base_key_filled = [v if v is not None else 0 for v in base_key]

                eff_key = []
                for i in range(len(CT)):
                    slot = i % period
                    offset = (i * slope_num) // slope_den
                    eff_key.append((base_key_filled[slot] + offset) % 26)

                pt = decrypt_full(CT, eff_key)

                berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
                ne_match = pt[16:16 + 9] == "NORTHEAST"

                if berlin_match and ne_match:
                    nwords, words_found, _ = score_english(pt, word_set)
                    non_crib_words = [(p, w) for p, w in words_found
                                      if not (63 <= p < 74) and not (16 <= p < 25)]

                    results.append({
                        'period': period,
                        'slope_num': slope_num,
                        'slope_den': slope_den,
                        'unfilled': unfilled,
                        'plaintext': pt,
                        'word_count': len(non_crib_words),
                        'words': non_crib_words
                    })

                    if len(non_crib_words) >= 1:
                        print(f"\n  P={period}, Slope={slope_num}/{slope_den}, "
                              f"Unfilled={unfilled}, Extra words={len(non_crib_words)}")
                        print(f"    PT: {pt}")
                        print(f"    Words: {non_crib_words}")

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs satisfying both cribs: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    P={r['period']} S={r['slope_num']}/{r['slope_den']} "
                  f"Words={r['word_count']}: {r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 4: Fibonacci Progression
# key_effective[i] = base_key[i % P] + fib(floor(i/P))  (mod 26)
# Also test: base_key[i % P] + fib(i) mod 26
# ==============================================================================

def test_fibonacci_progression(word_set, berlin_keys, northeast_keys):
    """Test Fibonacci-based key progression."""
    print("\n" + "=" * 80)
    print("APPROACH 4: Fibonacci Progression")
    print("=" * 80)

    # Precompute Fibonacci mod 26
    fib = [0, 1]
    for i in range(2, 200):
        fib.append((fib[-1] + fib[-2]) % 26)

    results = []

    # Sub-approach 4a: fib applied per cycle
    print("\n  --- 4a: key_effective[i] = base_key[i%P] + fib(cycle) mod 26 ---")
    for period in range(26, 32):
        for fib_scale in range(1, 6):
            base_key = [None] * period
            conflict = False

            for pos, kval in berlin_keys:
                slot = pos % period
                cycle = pos // period
                offset = (fib[cycle] * fib_scale) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    conflict = True
                    break
                base_key[slot] = derived

            if conflict:
                continue

            ne_ok = True
            for pos, kval in northeast_keys:
                slot = pos % period
                cycle = pos // period
                offset = (fib[cycle] * fib_scale) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    ne_ok = False
                    break
                base_key[slot] = derived

            if not ne_ok:
                continue

            unfilled = sum(1 for v in base_key if v is None)
            base_key_filled = [v if v is not None else 0 for v in base_key]

            eff_key = []
            for i in range(len(CT)):
                slot = i % period
                cycle = i // period
                offset = (fib[cycle] * fib_scale) % 26
                eff_key.append((base_key_filled[slot] + offset) % 26)

            pt = decrypt_full(CT, eff_key)

            berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
            ne_match = pt[16:16 + 9] == "NORTHEAST"

            if berlin_match and ne_match:
                nwords, words_found, _ = score_english(pt, word_set)
                non_crib_words = [(p, w) for p, w in words_found
                                  if not (63 <= p < 74) and not (16 <= p < 25)]

                results.append({
                    'type': '4a_cycle', 'period': period, 'fib_scale': fib_scale,
                    'unfilled': unfilled, 'plaintext': pt,
                    'word_count': len(non_crib_words), 'words': non_crib_words
                })

                if len(non_crib_words) >= 1:
                    print(f"\n  P={period}, FibScale={fib_scale}, Unfilled={unfilled}, "
                          f"Extra words={len(non_crib_words)}")
                    print(f"    PT: {pt}")
                    print(f"    Words: {non_crib_words}")

    # Sub-approach 4b: fib applied per position
    print("\n  --- 4b: key_effective[i] = base_key[i%P] + fib(i) mod 26 ---")
    for period in range(26, 32):
        for fib_scale in range(1, 6):
            base_key = [None] * period
            conflict = False

            for pos, kval in berlin_keys:
                slot = pos % period
                offset = (fib[pos] * fib_scale) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    conflict = True
                    break
                base_key[slot] = derived

            if conflict:
                continue

            ne_ok = True
            for pos, kval in northeast_keys:
                slot = pos % period
                offset = (fib[pos] * fib_scale) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    ne_ok = False
                    break
                base_key[slot] = derived

            if not ne_ok:
                continue

            unfilled = sum(1 for v in base_key if v is None)
            base_key_filled = [v if v is not None else 0 for v in base_key]

            eff_key = []
            for i in range(len(CT)):
                slot = i % period
                offset = (fib[i] * fib_scale) % 26
                eff_key.append((base_key_filled[slot] + offset) % 26)

            pt = decrypt_full(CT, eff_key)

            berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
            ne_match = pt[16:16 + 9] == "NORTHEAST"

            if berlin_match and ne_match:
                nwords, words_found, _ = score_english(pt, word_set)
                non_crib_words = [(p, w) for p, w in words_found
                                  if not (63 <= p < 74) and not (16 <= p < 25)]

                results.append({
                    'type': '4b_pos', 'period': period, 'fib_scale': fib_scale,
                    'unfilled': unfilled, 'plaintext': pt,
                    'word_count': len(non_crib_words), 'words': non_crib_words
                })

                if len(non_crib_words) >= 1:
                    print(f"\n  P={period}, FibScale={fib_scale}, Unfilled={unfilled}, "
                          f"Extra words={len(non_crib_words)}")
                    print(f"    PT: {pt}")
                    print(f"    Words: {non_crib_words}")

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs satisfying both cribs: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    Type={r['type']} P={r['period']} FS={r['fib_scale']} "
                  f"Words={r['word_count']}: {r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 5: Berlin Clock / Timezone Progression
# key_effective[i] = base_key[i % P] + floor(i/P) * tz_shift  (mod 26)
# where tz_shift is related to timezone offsets (1-12, and also 24)
# Also: shift every N positions (not per cycle)
# ==============================================================================

def test_timezone_progression(word_set, berlin_keys, northeast_keys):
    """Test timezone-based key shifts."""
    print("\n" + "=" * 80)
    print("APPROACH 5: Berlin Clock / Timezone Progression")
    print("=" * 80)

    results = []

    # 5a: Shift per group of N positions
    print("\n  --- 5a: key_effective[i] = base_key[i%P] + floor(i/G)*tz (mod 26) ---")
    print("          Where G = group size (not necessarily = period)")

    tz_shifts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24]

    for period in range(26, 32):
        for group_size in [1, 2, 3, 4, 5, 6, 8, 12, 24, 29, 97]:
            for tz in tz_shifts:
                base_key = [None] * period
                conflict = False

                for pos, kval in berlin_keys:
                    slot = pos % period
                    offset = ((pos // group_size) * tz) % 26
                    derived = (kval - offset) % 26
                    if base_key[slot] is not None and base_key[slot] != derived:
                        conflict = True
                        break
                    base_key[slot] = derived

                if conflict:
                    continue

                ne_ok = True
                for pos, kval in northeast_keys:
                    slot = pos % period
                    offset = ((pos // group_size) * tz) % 26
                    derived = (kval - offset) % 26
                    if base_key[slot] is not None and base_key[slot] != derived:
                        ne_ok = False
                        break
                    base_key[slot] = derived

                if not ne_ok:
                    continue

                unfilled = sum(1 for v in base_key if v is None)
                base_key_filled = [v if v is not None else 0 for v in base_key]

                eff_key = []
                for i in range(len(CT)):
                    slot = i % period
                    offset = ((i // group_size) * tz) % 26
                    eff_key.append((base_key_filled[slot] + offset) % 26)

                pt = decrypt_full(CT, eff_key)

                berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
                ne_match = pt[16:16 + 9] == "NORTHEAST"

                if berlin_match and ne_match:
                    nwords, words_found, _ = score_english(pt, word_set)
                    non_crib_words = [(p, w) for p, w in words_found
                                      if not (63 <= p < 74) and not (16 <= p < 25)]

                    results.append({
                        'period': period, 'group': group_size, 'tz': tz,
                        'unfilled': unfilled, 'plaintext': pt,
                        'word_count': len(non_crib_words), 'words': non_crib_words
                    })

                    if len(non_crib_words) >= 1:
                        print(f"\n  P={period}, G={group_size}, TZ={tz}, "
                              f"Unfilled={unfilled}, Extra words={len(non_crib_words)}")
                        print(f"    PT: {pt}")
                        print(f"    Words: {non_crib_words}")

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs satisfying both cribs: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    P={r['period']} G={r['group']} TZ={r['tz']} "
                  f"Words={r['word_count']}: {r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 6 (Bonus): Quadratic progression
# key_effective[i] = base_key[i % P] + floor(i/P)^2 * c  (mod 26)
# ==============================================================================

def test_quadratic_progression(word_set, berlin_keys, northeast_keys):
    """Test quadratic key progression."""
    print("\n" + "=" * 80)
    print("APPROACH 6 (Bonus): Quadratic Progression")
    print("  key_effective[i] = base_key[i%P] + floor(i/P)^2 * c  (mod 26)")
    print("=" * 80)

    results = []

    for period in range(26, 32):
        for c in range(1, 26):
            base_key = [None] * period
            conflict = False

            for pos, kval in berlin_keys:
                slot = pos % period
                cycle = pos // period
                offset = (cycle * cycle * c) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    conflict = True
                    break
                base_key[slot] = derived

            if conflict:
                continue

            ne_ok = True
            for pos, kval in northeast_keys:
                slot = pos % period
                cycle = pos // period
                offset = (cycle * cycle * c) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    ne_ok = False
                    break
                base_key[slot] = derived

            if not ne_ok:
                continue

            unfilled = sum(1 for v in base_key if v is None)
            base_key_filled = [v if v is not None else 0 for v in base_key]

            eff_key = []
            for i in range(len(CT)):
                slot = i % period
                cycle = i // period
                offset = (cycle * cycle * c) % 26
                eff_key.append((base_key_filled[slot] + offset) % 26)

            pt = decrypt_full(CT, eff_key)

            berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
            ne_match = pt[16:16 + 9] == "NORTHEAST"

            if berlin_match and ne_match:
                nwords, words_found, _ = score_english(pt, word_set)
                non_crib_words = [(p, w) for p, w in words_found
                                  if not (63 <= p < 74) and not (16 <= p < 25)]

                results.append({
                    'period': period, 'c': c,
                    'unfilled': unfilled, 'plaintext': pt,
                    'word_count': len(non_crib_words), 'words': non_crib_words
                })

                if len(non_crib_words) >= 1:
                    print(f"\n  P={period}, c={c}, Unfilled={unfilled}, "
                          f"Extra words={len(non_crib_words)}")
                    print(f"    PT: {pt}")
                    print(f"    Words: {non_crib_words}")

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs satisfying both cribs: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    P={r['period']} c={r['c']} Words={r['word_count']}: {r['words']}")
            print(f"      PT: {r['plaintext']}")

    return results


# ==============================================================================
# Approach 7: Cumulative sum progression
# key_effective[i] = base_key[i % P] + sum(base_key[0..floor(i/P)-1]) (mod 26)
# The shift each cycle is the sum of the key letters from previous cycles
# ==============================================================================

def test_cumulative_key_sum(word_set, berlin_keys, northeast_keys):
    """Test progression where shift is derived from cumulative key sum."""
    print("\n" + "=" * 80)
    print("APPROACH 7: Cumulative Key Sum Progression")
    print("  key_effective[i] = base_key[i%P] + cumulative_key_sum(cycle) (mod 26)")
    print("  (Uses known period-29 key as base)")
    print("=" * 80)

    # Use the standard period 29 key
    STD_KEY_STR = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    # Note: this is 29 chars but the user says it's period 29 with key DIJJQELYOIECBAQKVAATCRDUMPABT (29 chars - check)
    # Actually user says it's 29 chars: D-I-J-J-Q-E-L-Y-O-I-E-C-B-A-Q-K-V-A-A-T-C-R-D-U-M-P-A-B-T = 29 chars
    assert len(STD_KEY_STR) == 29

    period = 29
    std_key = text_to_nums(STD_KEY_STR)
    key_sum = sum(std_key) % 26

    results = []

    # Test: shift by cumulative sum * scale each cycle
    for scale in range(1, 26):
        eff_key = []
        for i in range(len(CT)):
            slot = i % period
            cycle = i // period
            offset = (cycle * key_sum * scale) % 26
            eff_key.append((std_key[slot] + offset) % 26)

        pt = decrypt_full(CT, eff_key)

        berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
        ne_match = pt[16:16 + 9] == "NORTHEAST"

        if berlin_match and ne_match:
            nwords, words_found, _ = score_english(pt, word_set)
            non_crib_words = [(p, w) for p, w in words_found
                              if not (63 <= p < 74) and not (16 <= p < 25)]
            results.append({
                'scale': scale, 'plaintext': pt,
                'word_count': len(non_crib_words), 'words': non_crib_words
            })
            if len(non_crib_words) >= 1:
                print(f"\n  Scale={scale}, Extra words={len(non_crib_words)}")
                print(f"    PT: {pt}")

    # Also test: shift by position-dependent accumulation
    # key_effective[i] = std_key[i%P] + (sum of std_key[0..i-1]) * scale mod 26
    for scale in range(1, 6):
        eff_key = []
        running_sum = 0
        for i in range(len(CT)):
            slot = i % period
            offset = (running_sum * scale) % 26
            eff_key.append((std_key[slot] + offset) % 26)
            running_sum = (running_sum + std_key[slot]) % 26

        pt = decrypt_full(CT, eff_key)

        berlin_match = pt[63:63 + 11] == "BERLINCLOCK"
        ne_match = pt[16:16 + 9] == "NORTHEAST"

        nwords, words_found, _ = score_english(pt, word_set)
        non_crib_words = [(p, w) for p, w in words_found
                          if not (63 <= p < 74) and not (16 <= p < 25)]

        # Report regardless of crib match since this is a known key variant
        if len(non_crib_words) >= 2:
            print(f"\n  RunningSum Scale={scale}, Berlin={'Y' if berlin_match else 'N'}, "
                  f"NE={'Y' if ne_match else 'N'}, Extra words={len(non_crib_words)}")
            print(f"    PT: {pt}")
            print(f"    Words: {non_crib_words}")

        results.append({
            'type': 'running_sum', 'scale': scale,
            'berlin_match': berlin_match, 'ne_match': ne_match,
            'plaintext': pt, 'word_count': len(non_crib_words),
            'words': non_crib_words
        })

    good = [r for r in results if r['word_count'] >= 3]
    print(f"\n  Total configs tested: {len(results)}")
    print(f"  Configs with 3+ extra English words: {len(good)}")

    if good:
        print("\n  === TOP RESULTS (3+ extra words) ===")
        good.sort(key=lambda x: -x['word_count'])
        for r in good[:20]:
            print(f"    {r}")

    return results


# ==============================================================================
# Final comprehensive analysis: try ALL progression functions generically
# ==============================================================================

def test_comprehensive_progressions(word_set, berlin_keys, northeast_keys):
    """
    Comprehensive test combining multiple progression types.
    For each, derive base key from Berlin crib, check Northeast, score.
    """
    print("\n" + "=" * 80)
    print("COMPREHENSIVE: Testing all progression functions systematically")
    print("=" * 80)

    all_results = []

    # Define progression functions: f(position, period) -> offset
    def make_additive_cycle(shift):
        return lambda i, P: (i // P) * shift

    def make_linear_pos(slope):
        return lambda i, P: i * slope

    def make_quadratic_pos(c):
        return lambda i, P: i * i * c

    def make_triangular(c):
        return lambda i, P: (i * (i + 1) // 2) * c

    fib_cache = [0, 1]
    for _ in range(200):
        fib_cache.append(fib_cache[-1] + fib_cache[-2])

    def make_fib_pos(scale):
        return lambda i, P: fib_cache[min(i, 199)] * scale

    def make_fib_cycle(scale):
        return lambda i, P: fib_cache[min(i // P, 199)] * scale

    # Build a list of (name, function) pairs
    prog_funcs = []
    for s in range(1, 26):
        prog_funcs.append((f"additive_cycle_s{s}", make_additive_cycle(s)))
    for s in range(1, 14):
        prog_funcs.append((f"linear_pos_s{s}", make_linear_pos(s)))
    for c in range(1, 6):
        prog_funcs.append((f"quadratic_pos_c{c}", make_quadratic_pos(c)))
    for c in range(1, 4):
        prog_funcs.append((f"triangular_c{c}", make_triangular(c)))
    for s in range(1, 6):
        prog_funcs.append((f"fib_pos_s{s}", make_fib_pos(s)))
    for s in range(1, 6):
        prog_funcs.append((f"fib_cycle_s{s}", make_fib_cycle(s)))

    tested = 0
    matched = 0

    for period in range(26, 32):
        for name, func in prog_funcs:
            tested += 1
            base_key = [None] * period
            conflict = False

            for pos, kval in berlin_keys:
                slot = pos % period
                offset = func(pos, period) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    conflict = True
                    break
                base_key[slot] = derived

            if conflict:
                continue

            ne_ok = True
            for pos, kval in northeast_keys:
                slot = pos % period
                offset = func(pos, period) % 26
                derived = (kval - offset) % 26
                if base_key[slot] is not None and base_key[slot] != derived:
                    ne_ok = False
                    break
                base_key[slot] = derived

            if not ne_ok:
                continue

            matched += 1
            unfilled = sum(1 for v in base_key if v is None)
            base_key_filled = [v if v is not None else 0 for v in base_key]

            eff_key = []
            for i in range(len(CT)):
                slot = i % period
                offset = func(i, period) % 26
                eff_key.append((base_key_filled[slot] + offset) % 26)

            pt = decrypt_full(CT, eff_key)

            nwords, words_found, chars_covered = score_english(pt, word_set)
            non_crib_words = [(p, w) for p, w in words_found
                              if not (63 <= p < 74) and not (16 <= p < 25)]

            all_results.append({
                'name': name, 'period': period,
                'unfilled': unfilled, 'plaintext': pt,
                'word_count': len(non_crib_words), 'words': non_crib_words,
                'chars_covered': chars_covered,
                'base_key': base_key_filled
            })

    print(f"\n  Total combinations tested: {tested}")
    print(f"  Satisfying both cribs: {matched}")

    good = [r for r in all_results if r['word_count'] >= 3]
    print(f"  With 3+ extra English words: {len(good)}")

    if good:
        good.sort(key=lambda x: (-x['word_count'], -x['chars_covered']))
        print("\n  === ALL RESULTS WITH 3+ EXTRA ENGLISH WORDS ===")
        for r in good:
            bk_str = ''.join(NUM_TO_CHAR[v] for v in r['base_key'])
            print(f"\n    Function: {r['name']}, Period: {r['period']}, "
                  f"Unfilled: {r['unfilled']}")
            print(f"    Extra words ({r['word_count']}): {r['words']}")
            print(f"    Base key: {bk_str}")
            print(f"    Plaintext: {r['plaintext']}")
    else:
        # Show best results even if < 3
        all_results.sort(key=lambda x: (-x['word_count'], -x['chars_covered']))
        print("\n  === TOP 30 RESULTS (by word count) ===")
        for r in all_results[:30]:
            print(f"    {r['name']} P={r['period']} Unfilled={r['unfilled']} "
                  f"Words={r['word_count']}: {r['words']}")
            if r['word_count'] > 0:
                print(f"      PT: {r['plaintext']}")

    return all_results


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("K4 Progressive Key Hypothesis Testing")
    print("=" * 80)
    print(f"Ciphertext: {CT}")
    print(f"Length:     {len(CT)}")
    print(f"KRYPTOS alphabet: {KALPHA}")
    print()

    # Load dictionary
    word_set = load_dictionary(min_len=3)
    print(f"Dictionary loaded: {len(word_set)} words (min length 3)")

    # Derive crib constraints
    berlin_keys, northeast_keys = get_crib_constraints()
    print(f"\nBERLINCLOCK @ pos 63: effective key values at positions 63-73:")
    for pos, kval in berlin_keys:
        print(f"  pos {pos}: key={kval} ({NUM_TO_CHAR[kval]})")
    print(f"\nNORTHEAST @ pos 16: effective key values at positions 16-24:")
    for pos, kval in northeast_keys:
        print(f"  pos {pos}: key={kval} ({NUM_TO_CHAR[kval]})")

    # Show what the standard period-29 key produces
    print("\n" + "-" * 80)
    STD_KEY_STR = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    std_key = text_to_nums(STD_KEY_STR)
    eff_key_std = [std_key[i % 29] for i in range(len(CT))]
    pt_std = decrypt_full(CT, eff_key_std)
    print(f"Standard period-29 key: {STD_KEY_STR}")
    print(f"Standard decryption:    {pt_std}")
    nw, wf, _ = score_english(pt_std, word_set)
    non_crib = [(p, w) for p, w in wf if not (63 <= p < 74) and not (16 <= p < 25)]
    print(f"English words found (excl. cribs): {len(non_crib)}: {non_crib}")
    print("-" * 80)

    # Run all approaches
    r1 = test_additive_progressive(word_set, berlin_keys, northeast_keys)
    r2 = test_progressive_period(word_set, berlin_keys, northeast_keys)
    r3 = test_linear_progression(word_set, berlin_keys, northeast_keys)
    r4 = test_fibonacci_progression(word_set, berlin_keys, northeast_keys)
    r5 = test_timezone_progression(word_set, berlin_keys, northeast_keys)
    r6 = test_quadratic_progression(word_set, berlin_keys, northeast_keys)
    r7 = test_cumulative_key_sum(word_set, berlin_keys, northeast_keys)
    r8 = test_comprehensive_progressions(word_set, berlin_keys, northeast_keys)

    # ==============================================================================
    # Grand Summary
    # ==============================================================================
    print("\n" + "=" * 80)
    print("GRAND SUMMARY")
    print("=" * 80)

    all_approaches = [
        ("1. Additive Progressive", r1),
        ("2. Progressive Period", r2),
        ("3. Linear Progression", r3),
        ("4. Fibonacci Progression", r4),
        ("5. Timezone Progression", r5),
        ("6. Quadratic Progression", r6),
        ("7. Cumulative Key Sum", r7),
        ("8. Comprehensive (all funcs)", r8),
    ]

    grand_good = []
    for name, results in all_approaches:
        both_cribs = [r for r in results
                      if r.get('plaintext', '') and
                      r['plaintext'][63:74] == 'BERLINCLOCK' and
                      r['plaintext'][16:25] == 'NORTHEAST']
        good_3 = [r for r in both_cribs if r['word_count'] >= 3]
        print(f"\n  {name}:")
        print(f"    Both cribs matched: {len(both_cribs)}")
        print(f"    With 3+ extra words: {len(good_3)}")
        for r in good_3:
            grand_good.append((name, r))

    print(f"\n{'=' * 80}")
    print(f"TOTAL RESULTS WITH 3+ EXTRA ENGLISH WORDS: {len(grand_good)}")
    print(f"{'=' * 80}")

    if grand_good:
        # Sort by word count descending
        grand_good.sort(key=lambda x: (-x[1]['word_count'], -x[1].get('chars_covered', 0)))
        print(f"\n  === TOP 30 RESULTS (sorted by word count) ===")
        for approach_name, r in grand_good[:30]:
            print(f"\n  Approach: {approach_name}")
            config = {rk: rv for rk, rv in r.items() if rk not in ('plaintext', 'words', 'base_key')}
            print(f"  Config:   {config}")
            print(f"  Words:    {r['words']}")
            print(f"  PT:       {r['plaintext']}")

        # Check if any result has 5+ word coverage suggesting real plaintext
        best = grand_good[0]
        print(f"\n  BEST RESULT: {best[0]} with {best[1]['word_count']} extra words")
        print(f"  Config: {best[1]}")
    else:
        print("\nNo progressive key configuration produced 3+ extra English words")
        print("while satisfying both cribs simultaneously.")
        print("\nThis suggests either:")
        print("  (a) The progression function is more complex than tested")
        print("  (b) The unfilled key positions (set to 0) mask valid words")
        print("  (c) K4 does not use a simple progressive Vigenere")

        # Show the best results across all approaches
        print("\n  === BEST RESULTS ACROSS ALL APPROACHES ===")
        all_flat = []
        for name, results in all_approaches:
            for r in results:
                if r.get('plaintext', ''):
                    pt = r['plaintext']
                    if pt[63:74] == 'BERLINCLOCK' and pt[16:25] == 'NORTHEAST':
                        all_flat.append((name, r))

        if all_flat:
            all_flat.sort(key=lambda x: -x[1]['word_count'])
            for approach_name, r in all_flat[:15]:
                config = {rk: rv for rk, rv in r.items()
                          if rk not in ('plaintext', 'words', 'base_key', 'type')}
                print(f"\n    [{approach_name}] Words={r['word_count']}")
                print(f"      Config: {config}")
                if r['words']:
                    print(f"      Words: {r['words']}")
                print(f"      PT: {r['plaintext']}")

    print("\nDone.")


if __name__ == "__main__":
    main()
