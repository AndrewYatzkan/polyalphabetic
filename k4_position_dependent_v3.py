#!/usr/bin/env python3
"""
K4 Position-Dependent: Focus on the RESULT candidate and nearby parameter space.
Also: systematic check of ALL possible (g0,g1,g2,g3) values with finer search.
"""

import math
from collections import defaultdict

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CT_LEN = len(CT)
PERIOD = 29

def k_index(ch): return KRYPTOS_ALPHA.index(ch)
def k_char(idx): return KRYPTOS_ALPHA[idx % 26]

class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        with open(filepath) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    gram, count = parts[0], int(parts[1])
                    self.quadgrams[gram] = count
                    self.total += count
        self.floor = math.log10(0.01 / self.total)
    def score(self, text):
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            if gram in self.quadgrams:
                s += math.log10(self.quadgrams[gram] / self.total)
            else:
                s += self.floor
        return s
    def score_per_char(self, text):
        if len(text) < 4: return -99
        return self.score(text) / (len(text) - 3)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

english_words = set()
with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
    for line in f:
        w = line.strip().upper()
        if len(w) >= 3:
            english_words.add(w)

def find_english_words(text, min_len=4):
    found = []
    text = text.upper()
    for length in range(min_len, min(len(text)+1, 15)):
        for start in range(len(text) - length + 1):
            word = text[start:start+length]
            if word in english_words:
                found.append((start, word))
    return found

def derive_key_for_g(g):
    """Derive the true 29-key for given [g0,g1,g2,g3] offsets."""
    true_key = [None] * 29
    # ENE positions 21-33
    for j in range(13):
        pos = 21 + j
        slot = pos % PERIOD
        period = pos // PERIOD
        pt_ch = "EASTNORTHEAST"[j]
        ek = (k_index(CT[pos]) - k_index(pt_ch)) % 26
        true_key[slot] = (ek - g[period]) % 26
    # BC positions 63-73
    for j in range(11):
        pos = 63 + j
        slot = pos % PERIOD
        period = pos // PERIOD
        pt_ch = "BERLINCLOCK"[j]
        ek = (k_index(CT[pos]) - k_index(pt_ch)) % 26
        true_key[slot] = (ek - g[period]) % 26
    return true_key

def decrypt_with_g(true_key_29, g):
    """Full decrypt."""
    pt = []
    for i in range(CT_LEN):
        slot = i % PERIOD
        period = min(i // PERIOD, 3)
        pt_val = (k_index(CT[i]) - true_key_29[slot] - g[period]) % 26
        pt.append(k_char(pt_val))
    return ''.join(pt)

print("=" * 80)
print("K4 POSITION-DEPENDENT: FOCUSED ANALYSIS V3")
print("=" * 80)

# ============================================================
# PART 1: Deep dive on the RESULT candidate
# ============================================================
print("\n" + "=" * 80)
print("PART 1: DEEP DIVE ON THE 'RESULT' CANDIDATE")
print("RESULT found at: g1=25, g2=19, unk=KIQPL")
print("=" * 80)

g = [0, 25, 19, 0]
tk = derive_key_for_g(g)
# Fill unknown slots with the values found: KIQPL -> K=0, I=15, Q=20, P=3, L=17
unknown_vals = [0, 15, 20, 3, 17]  # K, I, Q, P, L in KRYPTOS
for k, slot in enumerate([16, 17, 18, 19, 20]):
    tk[slot] = unknown_vals[k]

pt = decrypt_with_g(tk, g)
key_str = ''.join(k_char(v) for v in tk)
print(f"\n  Key: {key_str}")
print(f"  g = {g}")
print(f"  PT: {pt}")
print(f"  Score: {scorer.score_per_char(pt):.4f}")

words = find_english_words(pt, 3)
print(f"\n  All words found (min 3 chars):")
for pos, word in words:
    print(f"    pos {pos}: {word}")

# Show breakdown
print(f"\n  Period 0 [00-28]: {pt[0:29]}")
print(f"  Period 1 [29-57]: {pt[29:58]}")
print(f"  Period 2 [58-86]: {pt[58:87]}")
print(f"  Period 3 [87-96]: {pt[87:97]}")

# ============================================================
# PART 2: Search nearby g3 values for RESULT candidate
# ============================================================
print("\n" + "=" * 80)
print("PART 2: VARY g3 FOR RESULT CANDIDATE")
print("=" * 80)

for g3 in range(26):
    g_test = [0, 25, 19, g3]
    pt = decrypt_with_g(tk, g_test)
    s = scorer.score_per_char(pt)
    p3 = pt[87:97]
    w3 = find_english_words(p3, 3)
    print(f"  g3={g3:2d}: score={s:.4f}, period3='{p3}', words={[w for _,w in w3]}")

# ============================================================
# PART 3: Exhaustive search around best candidates with wider beam
# ============================================================
print("\n" + "=" * 80)
print("PART 3: WIDER BEAM SEARCH FOR TOP (g1,g2) PAIRS")
print("=" * 80)

# Top pairs from v2 analysis
top_pairs = [
    (14, 8), (25, 7), (25, 19), (25, 5), (2, 8), (25, 8),
    (24, 4), (25, 11), (21, 2), (25, 10), (25, 2), (25, 6),
    (14, 20), (25, 20), (25, 24), (0, 0),  # include baseline
]

mega_results = []
for g1, g2 in top_pairs:
    for g3 in range(26):
        g = [0, g1, g2, g3]
        base_key = derive_key_for_g(g)
        
        # Beam search over 5 unknown slots
        beam = [(0.0, [None]*5)]
        for idx, unknown_slot in enumerate([16, 17, 18, 19, 20]):
            new_beam = []
            for _, partial in beam:
                for val in range(26):
                    test_key = list(base_key)
                    for k, s in enumerate([16, 17, 18, 19, 20][:idx]):
                        test_key[s] = partial[k]
                    test_key[unknown_slot] = val
                    
                    new_partial = list(partial)
                    new_partial[idx] = val
                    
                    pt = decrypt_with_g(test_key, g)
                    s = scorer.score_per_char(pt) if len(pt) >= 4 else -99
                    new_beam.append((s, new_partial))
            
            new_beam.sort(key=lambda x: -x[0])
            beam = new_beam[:80]
        
        # Top result for this g
        best_s, best_unk = beam[0]
        full_key = list(base_key)
        for k, slot in enumerate([16, 17, 18, 19, 20]):
            full_key[slot] = best_unk[k]
        pt = decrypt_with_g(full_key, g)
        unk_str = ''.join(k_char(v) for v in best_unk)
        key_str = ''.join(k_char(v) for v in full_key)
        words = find_english_words(pt, 4)
        extra = [f"{w}@{p}" for p,w in words if w not in ("EAST","NORTH","NORTHEAST","BERLIN","CLOCK")]
        
        mega_results.append((best_s, g1, g2, g3, unk_str, key_str, pt, extra))

mega_results.sort(key=lambda x: -x[0])

print(f"\n  Tested {len(top_pairs)*26} combinations. Top 40:\n")
for rank, (score, g1, g2, g3, unk, key, pt, extra) in enumerate(mega_results[:40]):
    print(f"  #{rank+1}: g=[0,{g1:2d},{g2:2d},{g3:2d}] unk={unk} score={score:.4f}")
    print(f"        key={key}")
    print(f"        PT: {pt}")
    if extra:
        print(f"        Words: {', '.join(extra[:12])}")
    print()

# ============================================================
# PART 4: OVERALL BEST - LOOK FOR READABLE MESSAGES
# ============================================================
print("\n" + "=" * 80)
print("PART 4: DETAILED ENGLISH ANALYSIS OF TOP 10")
print("=" * 80)

for rank, (score, g1, g2, g3, unk, key, pt, extra) in enumerate(mega_results[:10]):
    print(f"\n--- #{rank+1}: g=[0,{g1},{g2},{g3}], score={score:.4f} ---")
    print(f"  Key: {key}")
    print(f"  PT:  {pt}")
    
    # Try to read it as potential English with spaces
    # Look for common word boundaries
    all_words = find_english_words(pt, 3)
    # Sort by length descending
    all_words.sort(key=lambda x: -len(x[1]))
    print(f"  Longest words: {[(p,w) for p,w in all_words[:10]]}")
    
    # Look for 8+ char segments that score well
    good_segs = []
    for length in range(6, 20):
        for start in range(len(pt) - length + 1):
            seg = pt[start:start+length]
            seg_s = scorer.score_per_char(seg)
            if seg_s > -3.5:
                good_segs.append((seg_s, start, seg))
    good_segs.sort(key=lambda x: -x[0])
    if good_segs:
        print(f"  Best scoring segments:")
        for seg_s, start, seg in good_segs[:5]:
            print(f"    pos {start}: '{seg}' score={seg_s:.4f}")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
