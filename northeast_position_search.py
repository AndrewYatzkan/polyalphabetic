#!/usr/bin/env python3
"""
Search for NORTHEAST position and period combinations.
Tests all NORTHEAST positions (0-88) and periods (20-50).
Uses BERLINCLOCK@63 and NORTHEAST@N as cribs to derive key positions,
then scores the partial decryption by counting English words.
"""

import sys
from collections import defaultdict

# K4 ciphertext
CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# KRYPTOS alphabet (mixed alphabet used for K4)
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
assert len(KRYPTOS_ALPHA) == 26, f"Bad length: {len(KRYPTOS_ALPHA)}"

# Cribs
BERLINCLOCK = "BERLINCLOCK"  # confirmed at position 63
NORTHEAST = "NORTHEAST"     # somewhere in 0..88

# Load English word list
def load_words():
    words = set()
    try:
        with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 3:
                    words.add(w)
    except:
        pass
    # Also add known K4 words
    known = ["NORTHEAST","BERLINCLOCK","BERLIN","CLOCK","NORTH","EAST","WEST","SOUTH",
             "THE","AND","ITS","WAS","ARE","HAS","HAD","NOT","BUT","FOR","ALL",
             "THAT","WITH","THIS","FROM","THEY","HAVE","BEEN","WILL","YOUR",
             "WHAT","ABOUT","WHEN","WHICH","THEIR","THERE","TIME","WOULD","COULD",
             "SHOULD","BETWEEN","WITHIN","SHADOW","FORCE","LAYER","BELOW","ABOVE",
             "STILL","ONLY","JUST","MUCH","SOME","ALSO","MORE","THAN","INTO",
             "LIKE","WELL","DOES","OVER","SUCH","THESE","THOSE","DARK","LIGHT",
             "POINT","LEVEL","PLACE","WHERE","UNDER","NEVER","ALWAYS","EVERY",
             "BEFORE","AFTER","DURING","LITTLE","REALLY","THROUGH","AROUND","BECAUSE"]
    words.update(known)
    return words

ENGLISH_WORDS = load_words()

def kryptos_vigenere_decrypt(ciphertext, key_dict, alpha=KRYPTOS_ALPHA):
    """
    Decrypt positions where we know the key letter.
    key_dict: {position_in_ciphertext: key_letter}
    Returns dict of {position: plaintext_letter} for positions with known keys.
    """
    alpha_index = {c: i for i, c in enumerate(alpha)}
    result = {}

    for pos, key_letter in key_dict.items():
        if pos >= len(ciphertext):
            continue
        ct_letter = ciphertext[pos]
        if ct_letter not in alpha_index or key_letter not in alpha_index:
            continue
        ct_idx = alpha_index[ct_letter]
        key_idx = alpha_index[key_letter]
        # Vigenere decrypt: pt = (ct - key) mod 26
        pt_idx = (ct_idx - key_idx) % 26
        result[pos] = alpha[pt_idx]

    return result

def get_key_from_crib(ciphertext, crib, position, alpha=KRYPTOS_ALPHA):
    """
    Given that crib appears at position in the plaintext,
    derive key letters for those positions.
    Returns dict {pos: key_letter} or None if invalid.
    """
    alpha_index = {c: i for i, c in enumerate(alpha)}
    key_dict = {}

    for i, pt_letter in enumerate(crib):
        ct_pos = position + i
        if ct_pos >= len(ciphertext):
            return None
        ct_letter = ciphertext[ct_pos]
        if ct_letter not in alpha_index or pt_letter not in alpha_index:
            return None
        ct_idx = alpha_index[ct_letter]
        pt_idx = alpha_index[pt_letter]
        # Vigenere: ct = pt + key => key = ct - pt
        key_idx = (ct_idx - pt_idx) % 26
        key_dict[ct_pos] = alpha[key_idx]

    return key_dict

def derive_periodic_key(key_dict, period, cipher_len):
    """
    Given known key letters at absolute positions, derive the repeating key.
    key_dict: {abs_pos: key_letter}
    Returns:
      - partial_key: list of length `period`, None where unknown
      - full_pos_key: {abs_pos: key_letter} for all positions we can determine
      - conflicts: True if any period position has conflicting key letters
    """
    period_slots = {}  # {key_pos (mod period): key_letter}

    for abs_pos, key_letter in key_dict.items():
        kp = abs_pos % period
        if kp in period_slots:
            if period_slots[kp] != key_letter:
                return None, None, True  # conflict!
        else:
            period_slots[kp] = key_letter

    # Build full key dict for all ciphertext positions
    full_pos_key = {}
    for pos in range(cipher_len):
        kp = pos % period
        if kp in period_slots:
            full_pos_key[pos] = period_slots[kp]

    # Build partial key array
    partial_key = [period_slots.get(i) for i in range(period)]

    return partial_key, full_pos_key, False

def score_decryption(plaintext_dict, cipher_len):
    """
    Score the partial decryption by counting English words.
    plaintext_dict: {pos: char}
    Returns (score, words_found)
    """
    # Build the plaintext string with '?' for unknowns
    pt_arr = ['?'] * cipher_len
    for pos, ch in plaintext_dict.items():
        pt_arr[pos] = ch
    pt_str = ''.join(pt_arr)

    words_found = []
    score = 0

    # Find runs of known characters
    # Split by '?' and check segments
    segments = []
    start = None
    for i, ch in enumerate(pt_arr):
        if ch != '?':
            if start is None:
                start = i
        else:
            if start is not None:
                segments.append((start, ''.join(pt_arr[start:i])))
                start = None
    if start is not None:
        segments.append((start, ''.join(pt_arr[start:])))

    # For each contiguous segment, look for words
    for seg_start, seg_text in segments:
        if len(seg_text) < 3:
            continue
        # Slide a window through the segment
        for wlen in range(3, min(len(seg_text)+1, 15)):
            for offset in range(len(seg_text) - wlen + 1):
                word = seg_text[offset:offset+wlen]
                if word in ENGLISH_WORDS:
                    words_found.append((seg_start + offset, word))
                    score += wlen * wlen  # weight longer words more

    # Deduplicate words (remove subsets)
    # Keep track of unique words
    unique_words = list({w for _, w in words_found})

    return score, unique_words, pt_str

def run_analysis():
    cipher_len = len(CIPHERTEXT)
    print(f"K4 ciphertext length: {cipher_len}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Testing NORTHEAST positions 0-{cipher_len - len(NORTHEAST)}, periods 20-50")
    print("="*80)

    # Get BERLINCLOCK key (fixed at position 63)
    berlin_key_dict = get_key_from_crib(CIPHERTEXT, BERLINCLOCK, 63)
    if not berlin_key_dict:
        print("ERROR: Could not derive BERLINCLOCK key!")
        return

    print(f"BERLINCLOCK@63 key positions: {berlin_key_dict}")
    print()

    results = []

    ne_max = cipher_len - len(NORTHEAST)

    for ne_pos in range(ne_max + 1):
        # Get NORTHEAST key
        ne_key_dict = get_key_from_crib(CIPHERTEXT, NORTHEAST, ne_pos)
        if not ne_key_dict:
            continue

        # Combine both cribs
        combined_key = {}
        combined_key.update(berlin_key_dict)

        # Check for direct conflicts between cribs at same positions
        conflict = False
        for pos, letter in ne_key_dict.items():
            if pos in combined_key and combined_key[pos] != letter:
                conflict = True
                break
            combined_key[pos] = letter

        if conflict:
            continue  # Cribs conflict at the raw position level

        for period in range(20, 51):
            # Derive periodic key
            partial_key, full_pos_key, has_conflict = derive_periodic_key(
                combined_key, period, cipher_len
            )

            if has_conflict:
                continue  # Period causes key conflict

            # Count how many key positions are known
            known_count = sum(1 for k in partial_key if k is not None)
            coverage_pct = known_count / period * 100

            # Decrypt known positions
            pt_dict = kryptos_vigenere_decrypt(CIPHERTEXT, full_pos_key)

            # Score
            score, words, pt_str = score_decryption(pt_dict, cipher_len)

            if score > 0 or words:
                results.append({
                    'ne_pos': ne_pos,
                    'period': period,
                    'score': score,
                    'words': words,
                    'partial_key': partial_key,
                    'known_count': known_count,
                    'coverage_pct': coverage_pct,
                    'pt_str': pt_str,
                    'full_pos_key': full_pos_key,
                })

    # Sort by score descending
    results.sort(key=lambda x: (-x['score'], -len(x['words']), -x['coverage_pct']))

    print(f"Total compatible combinations found: {len(results)}")
    print(f"(Combinations with at least one English word in partial decryption)")
    print()

    # Show top 10
    print("="*80)
    print("TOP 10 RESULTS")
    print("="*80)

    shown = 0
    for r in results[:10]:
        shown += 1
        print(f"\nRank {shown}: Period={r['period']}, NORTHEAST@{r['ne_pos']}, Score={r['score']}")
        print(f"  Key coverage: {r['known_count']}/{r['period']} positions = {r['coverage_pct']:.1f}%")

        # Show partial key
        key_str = ''.join(k if k is not None else '_' for k in r['partial_key'])
        print(f"  Partial key: {key_str}")

        # Show decrypted text
        print(f"  Partial decrypt: {r['pt_str']}")

        # Show words found
        print(f"  English words ({len(r['words'])}): {', '.join(sorted(r['words']))}")

    print()
    print("="*80)
    print("ADDITIONAL ANALYSIS: All combinations by period")
    print("="*80)

    # Group by period and show best for each
    by_period = defaultdict(list)
    for r in results:
        by_period[r['period']].append(r)

    period_summary = []
    for period in range(20, 51):
        if period in by_period:
            best = by_period[period][0]  # Already sorted
            period_summary.append((period, len(by_period[period]), best['score'], best['ne_pos']))

    period_summary.sort(key=lambda x: -x[2])

    print(f"\n{'Period':>8} | {'Combos':>8} | {'Best Score':>10} | {'Best NE pos':>12}")
    print("-"*50)
    for period, count, score, ne_pos in period_summary:
        print(f"{period:>8} | {count:>8} | {score:>10} | {ne_pos:>12}")

    print()
    print("="*80)
    print("NORTHEAST POSITION SUMMARY (top scoring for each NE position)")
    print("="*80)

    by_ne = defaultdict(list)
    for r in results:
        by_ne[r['ne_pos']].append(r)

    ne_summary = []
    for ne_pos in range(ne_max + 1):
        if ne_pos in by_ne:
            best = by_ne[ne_pos][0]
            ne_summary.append((ne_pos, len(by_ne[ne_pos]), best['score'], best['period']))

    ne_summary.sort(key=lambda x: -x[2])

    print(f"\n{'NE pos':>8} | {'Combos':>8} | {'Best Score':>10} | {'Best Period':>12}")
    print("-"*50)
    for ne_pos, count, score, period in ne_summary[:30]:
        print(f"{ne_pos:>8} | {count:>8} | {score:>10} | {period:>12}")

    # Special check: what words appear specifically
    print()
    print("="*80)
    print("WORD FREQUENCY ACROSS ALL RESULTS")
    print("="*80)

    word_freq = defaultdict(int)
    for r in results:
        for w in r['words']:
            word_freq[w] += 1

    word_list = sorted(word_freq.items(), key=lambda x: (-len(x[0]), -x[1]))
    print("\nWords found (sorted by length, then frequency):")
    for word, freq in word_list[:50]:
        print(f"  {word:20s}: {freq:5d} combinations")

    # Check specifically for NE=16 (original assumption)
    print()
    print("="*80)
    print("DETAIL: NORTHEAST at position 16 (original assumption)")
    print("="*80)
    ne16_results = [r for r in results if r['ne_pos'] == 16]
    if ne16_results:
        ne16_results.sort(key=lambda x: -x['score'])
        print(f"Found {len(ne16_results)} compatible periods for NE@16")
        for r in ne16_results[:5]:
            key_str = ''.join(k if k is not None else '_' for k in r['partial_key'])
            print(f"  Period={r['period']}: key={key_str}, score={r['score']}, words={r['words']}")
            print(f"    Decrypt: {r['pt_str']}")
    else:
        print("No results for NE@16 (may have zero-score or conflict)")
        # Show why (conflict check)
        ne_key_dict_16 = get_key_from_crib(CIPHERTEXT, NORTHEAST, 16)
        print(f"  NE@16 raw key: {ne_key_dict_16}")
        print(f"  Berlin@63 raw key: {berlin_key_dict}")
        for period in [29, 30, 25]:
            partial_key, full_pos_key, conflict = derive_periodic_key(
                {**berlin_key_dict, **ne_key_dict_16}, period, cipher_len
            )
            print(f"  Period {period}: conflict={conflict}, key={''.join(k if k else '_' for k in (partial_key or []))}")

if __name__ == "__main__":
    run_analysis()
