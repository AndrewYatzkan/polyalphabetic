#!/usr/bin/env python3
"""
Brute-force the 5 unknown key positions (16-20) for the K4 cipher.

Known constraints:
  - K4 ciphertext: 97 characters
  - KRYPTOS alphabet (26 chars): KRYPTOSABCDEFGHIJLMNQUVWXZ
  - Period-29 Vigenere cipher
  - EASTNORTHEAST at plaintext positions 21-33
  - BERLINCLOCK at plaintext positions 63-73
  - Known key (29 chars): OYNKYELYOIECBAQK?????RDUMRIYW
  - Unknown positions: 16, 17, 18, 19, 20
"""

import math
import time
import heapq

# --- Constants ----------------------------------------------------------------

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHA_SIZE = 26

CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CT_LEN = len(CIPHERTEXT)  # 97

# Known key with '?' for unknowns at positions 16-20
KNOWN_KEY_TEMPLATE = "OYNKYELYOIECBAQK?????RDUMRIYW"
PERIOD = 29
UNKNOWN_POSITIONS = [16, 17, 18, 19, 20]

# --- Build alphabet index lookup ----------------------------------------------

char_to_idx = {}
for i, ch in enumerate(KRYPTOS_ALPHA):
    char_to_idx[ch] = i

idx_to_char = list(KRYPTOS_ALPHA)

# --- Pre-compute ciphertext as indices ----------------------------------------

ct_indices = [char_to_idx[ch] for ch in CIPHERTEXT]

# --- Pre-compute known key indices --------------------------------------------

known_key_indices = [0] * PERIOD
for i, ch in enumerate(KNOWN_KEY_TEMPLATE):
    if ch != '?':
        known_key_indices[i] = char_to_idx[ch]
    else:
        known_key_indices[i] = -1  # placeholder

# --- Load quadgram log-probabilities -----------------------------------------

print("Loading quadgram frequencies...")
t0 = time.time()

quadgram_scores = {}
total_count = 0

with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram = parts[0]
            count = int(parts[1])
            quadgram_scores[gram] = count
            total_count += count

# Convert to log probabilities
log_total = math.log10(total_count)
for gram in quadgram_scores:
    quadgram_scores[gram] = math.log10(quadgram_scores[gram]) - log_total

# Floor value for unseen quadgrams
FLOOR = math.log10(0.01) - log_total

print(f"  Loaded {len(quadgram_scores)} quadgrams in {time.time()-t0:.2f}s")
print(f"  Floor score per quadgram: {FLOOR:.4f}")

# --- Load English words (3+ letters) -----------------------------------------

print("Loading English word list...")
t0 = time.time()

english_words = set()
with open("/home/user/polyalphabetic/OxfordEnglishWords.txt", "r") as f:
    for line in f:
        word = line.strip().upper()
        if len(word) >= 3:
            english_words.add(word)

print(f"  Loaded {len(english_words)} words (3+ chars) in {time.time()-t0:.2f}s")

# --- Vigenere decryption (optimized) -----------------------------------------

def decrypt_vigenere(ct_idx_array, key_idx_array, period, alpha_size):
    """Decrypt using Vigenere with KRYPTOS alphabet. Returns list of plaintext indices."""
    pt = [0] * len(ct_idx_array)
    for i in range(len(ct_idx_array)):
        k = key_idx_array[i % period]
        pt[i] = (ct_idx_array[i] - k) % alpha_size
    return pt


def score_quadgrams(pt_indices):
    """Score plaintext (as index array) using quadgram log-probabilities."""
    pt_str = ''.join(idx_to_char[idx] for idx in pt_indices)
    score = 0.0
    for i in range(len(pt_str) - 3):
        qg = pt_str[i:i+4]
        score += quadgram_scores.get(qg, FLOOR)
    return score


def count_english_words(pt_str, word_set):
    """Count English words of length 3+ found in the plaintext string."""
    found = []
    for length in range(min(15, len(pt_str)), 2, -1):
        for start in range(len(pt_str) - length + 1):
            candidate = pt_str[start:start+length]
            if candidate in word_set:
                found.append((candidate, start))
    unique_words = set(w for w, _ in found)
    total_chars = sum(len(w) for w in unique_words)
    return len(unique_words), total_chars, sorted(unique_words, key=len, reverse=True)[:10]


# --- Pre-compute which ciphertext positions use each key position -------------
# For positions 16-20, figure out which ciphertext indices they affect.
# This lets us do partial decryption only for the changing positions.

# Actually, since all 97 chars need to be decrypted and scored as a whole,
# we optimize by pre-computing the static parts and only recomputing the
# positions affected by the 5 unknown key slots.

# Map each ciphertext position to its key position
ct_key_pos = [i % PERIOD for i in range(CT_LEN)]

# Positions affected by unknown key slots
unknown_ct_positions = {k: [] for k in UNKNOWN_POSITIONS}
for i in range(CT_LEN):
    kp = ct_key_pos[i]
    if kp in UNKNOWN_POSITIONS:
        unknown_ct_positions[kp].append(i)

# Pre-decrypt the static positions (those not affected by unknowns)
static_pt = [0] * CT_LEN
static_mask = [False] * CT_LEN  # True if position is static
for i in range(CT_LEN):
    kp = ct_key_pos[i]
    if kp not in UNKNOWN_POSITIONS:
        static_pt[i] = (ct_indices[i] - known_key_indices[kp]) % ALPHA_SIZE
        static_mask[i] = True

# --- Main brute-force loop ----------------------------------------------------

print(f"\nStarting brute-force over {ALPHA_SIZE}^5 = {ALPHA_SIZE**5:,} key combinations...")
print(f"Ciphertext length: {CT_LEN}")
print(f"Known key template: {KNOWN_KEY_TEMPLATE}")
print(f"Unknown positions: {UNKNOWN_POSITIONS}")

# Show which CT positions are affected by unknowns
for kp in UNKNOWN_POSITIONS:
    print(f"  Key pos {kp} affects CT positions: {unknown_ct_positions[kp]}")
print()

# Min-heap of size 50 to track top results
TOP_N = 50
top_results = []

start_time = time.time()
combo_count = 0
total_combos = ALPHA_SIZE ** 5

# Pre-build lookup: for each unknown key position, pre-compute
# (ct_index, ct_value) pairs so inner loop is fast
unknown_ct_data = {}
for kp in UNKNOWN_POSITIONS:
    unknown_ct_data[kp] = [(ci, ct_indices[ci]) for ci in unknown_ct_positions[kp]]

# Positions 16,17,18,19,20 data
data16 = unknown_ct_data[16]
data17 = unknown_ct_data[17]
data18 = unknown_ct_data[18]
data19 = unknown_ct_data[19]
data20 = unknown_ct_data[20]

for i0 in range(ALPHA_SIZE):
    # Apply key position 16
    for ci, cv in data16:
        static_pt[ci] = (cv - i0) % ALPHA_SIZE
    
    for i1 in range(ALPHA_SIZE):
        # Apply key position 17
        for ci, cv in data17:
            static_pt[ci] = (cv - i1) % ALPHA_SIZE
        
        for i2 in range(ALPHA_SIZE):
            # Apply key position 18
            for ci, cv in data18:
                static_pt[ci] = (cv - i2) % ALPHA_SIZE
            
            for i3 in range(ALPHA_SIZE):
                # Apply key position 19
                for ci, cv in data19:
                    static_pt[ci] = (cv - i3) % ALPHA_SIZE
                
                for i4 in range(ALPHA_SIZE):
                    # Apply key position 20
                    for ci, cv in data20:
                        static_pt[ci] = (cv - i4) % ALPHA_SIZE
                    
                    # Score with quadgrams - build string and score
                    pt_str = ''.join(idx_to_char[v] for v in static_pt)
                    score = 0.0
                    for qi in range(CT_LEN - 3):
                        qg = pt_str[qi:qi+4]
                        score += quadgram_scores.get(qg, FLOOR)
                    
                    combo_count += 1
                    
                    # Track top N using min-heap
                    if len(top_results) < TOP_N:
                        ki = [i0, i1, i2, i3, i4]
                        key_str_parts = list(KNOWN_KEY_TEMPLATE)
                        for ux, up in enumerate(UNKNOWN_POSITIONS):
                            key_str_parts[up] = idx_to_char[ki[ux]]
                        key_str = ''.join(key_str_parts)
                        heapq.heappush(top_results, (score, key_str, pt_str))
                    elif score > top_results[0][0]:
                        ki = [i0, i1, i2, i3, i4]
                        key_str_parts = list(KNOWN_KEY_TEMPLATE)
                        for ux, up in enumerate(UNKNOWN_POSITIONS):
                            key_str_parts[up] = idx_to_char[ki[ux]]
                        key_str = ''.join(key_str_parts)
                        heapq.heapreplace(top_results, (score, key_str, pt_str))
                    
                    # Progress update
                    if combo_count % 500000 == 0:
                        elapsed = time.time() - start_time
                        rate = combo_count / elapsed if elapsed > 0 else 0
                        remaining = (total_combos - combo_count) / rate if rate > 0 else 0
                        pct = 100.0 * combo_count / total_combos
                        min_score = top_results[0][0] if top_results else float('-inf')
                        print(f"  Progress: {combo_count:>12,} / {total_combos:,} "
                              f"({pct:5.1f}%) | "
                              f"Elapsed: {elapsed:6.1f}s | "
                              f"Rate: {rate:,.0f}/s | "
                              f"ETA: {remaining:6.1f}s | "
                              f"Worst in top-{TOP_N}: {min_score:.2f}")

elapsed_total = time.time() - start_time
print(f"\nBrute-force complete!")
print(f"  Total combinations: {combo_count:,}")
print(f"  Total time: {elapsed_total:.1f}s")
if elapsed_total > 0:
    print(f"  Average rate: {combo_count/elapsed_total:,.0f} combos/s")

# --- Print top 50 results ----------------------------------------------------

print(f"\n{'='*120}")
print(f"TOP {TOP_N} RESULTS BY QUADGRAM SCORE")
print(f"{'='*120}")

# Sort results best-first (highest score)
top_results.sort(key=lambda x: x[0], reverse=True)

for rank, (score, key_str, pt_str) in enumerate(top_results, 1):
    # Count English words for top results
    word_count, char_coverage, top_words = count_english_words(pt_str, english_words)
    
    unknown_part = key_str[16:21]
    
    print(f"\n--- Rank {rank} ---")
    print(f"  Score:     {score:.4f}")
    print(f"  Key:       {key_str}")
    print(f"  Unknown:   positions 16-20 = {unknown_part}")
    print(f"  Plaintext: {pt_str}")
    print(f"  Words({word_count}): {', '.join(top_words[:10])}")

print(f"\n{'='*120}")
print("Done.")
