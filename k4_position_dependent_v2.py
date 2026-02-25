#!/usr/bin/env python3
"""
Kryptos K4: DEEPER analysis of position-dependent key modification.

Key insight from v1: The two cribs (ENE and BC) cover DISJOINT key slots
from different periods. This means ANY f(i) = c * (i//29) will appear
"consistent" - we can only distinguish by checking if the full plaintext
looks like English.

This script focuses on the most promising candidates from v1 and does
deeper analysis.
"""

import math
from collections import defaultdict

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CT_LEN = len(CT)
PERIOD = 29

def k_index(ch):
    return KRYPTOS_ALPHA.index(ch)

def k_char(idx):
    return KRYPTOS_ALPHA[idx % 26]

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
        if len(text) < 4:
            return -99
        return self.score(text) / (len(text) - 3)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

# Load English words for checking
english_words = set()
with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
    for line in f:
        w = line.strip().upper()
        if len(w) >= 3:
            english_words.add(w)

def find_english_words(text, min_len=4):
    """Find all English words in plaintext."""
    found = []
    text = text.upper()
    for length in range(min_len, min(len(text)+1, 15)):
        for start in range(len(text) - length + 1):
            word = text[start:start+length]
            if word in english_words:
                found.append((start, word))
    return found

# Derived key from cribs (simple Vigenere)
derived_keys = {}
for j, pt_ch in enumerate("EASTNORTHEAST"):
    ct_pos = 21 + j
    dk = (k_index(CT[ct_pos]) - k_index(pt_ch)) % 26
    derived_keys[ct_pos] = dk

for j, pt_ch in enumerate("BERLINCLOCK"):
    ct_pos = 63 + j
    dk = (k_index(CT[ct_pos]) - k_index(pt_ch)) % 26
    derived_keys[ct_pos] = dk

print("=" * 80)
print("K4 POSITION-DEPENDENT KEY MODIFICATION: DEEP ANALYSIS V2")
print("=" * 80)

# ============================================================
# COMPREHENSIVE SEARCH: f(i) = c * (i // 29) for ALL c values
# with EXHAUSTIVE 5-slot brute force (26^5 = 11.8M too many)
# Use smarter approach: for each c, test 26^2 at a time
# ============================================================

print("\n" + "=" * 80)
print("PART 1: DETAILED ANALYSIS OF TOP f(i) = c*(i//29) CANDIDATES")
print("=" * 80)

def decrypt_full(ct, true_key_29, c_period):
    """Decrypt with key and period-step c."""
    pt = []
    for i in range(len(ct)):
        slot = i % PERIOD
        fi = (c_period * (i // PERIOD)) % 26
        pt_val = (k_index(ct[i]) - true_key_29[slot] - fi) % 26
        pt.append(k_char(pt_val))
    return ''.join(pt)

# For each c, derive the true key for known slots, then search unknown slots
best_overall = []

for c in range(26):
    # Derive true key from cribs
    true_key = [None] * 29
    
    # Period 0 slots (21-28): true_key[s] = ek[s] - c*0 = ek[s]
    for j in range(8):
        pos = 21 + j
        slot = pos % PERIOD
        ek = (k_index(CT[pos]) - k_index("EASTNORTHEAST"[j])) % 26
        true_key[slot] = (ek - c * (pos // PERIOD)) % 26
    
    # Period 1 slots (0-4): true_key[s] = ek[s] - c*1
    for j in range(8, 13):
        pos = 21 + j
        slot = pos % PERIOD
        ek = (k_index(CT[pos]) - k_index("EASTNORTHEAST"[j])) % 26
        true_key[slot] = (ek - c * (pos // PERIOD)) % 26
    
    # Period 2 slots (5-15): true_key[s] = ek[s] - c*2
    for j in range(11):
        pos = 63 + j
        slot = pos % PERIOD
        ek = (k_index(CT[pos]) - k_index("BERLINCLOCK"[j])) % 26
        true_key[slot] = (ek - c * (pos // PERIOD)) % 26
    
    # Unknown slots: 16, 17, 18, 19, 20
    # Beam search
    beam = [(0.0, [None]*5)]
    
    for idx, unknown_slot in enumerate([16, 17, 18, 19, 20]):
        new_beam = []
        for _, partial in beam:
            for val in range(26):
                test_key = list(true_key)
                for k, s in enumerate([16, 17, 18, 19, 20][:idx]):
                    test_key[s] = partial[k]
                test_key[unknown_slot] = val
                
                new_partial = list(partial)
                new_partial[idx] = val
                
                # Decrypt and score
                pt = []
                for i in range(CT_LEN):
                    slot = i % PERIOD
                    if test_key[slot] is not None:
                        fi = (c * (i // PERIOD)) % 26
                        pt_val = (k_index(CT[i]) - test_key[slot] - fi) % 26
                        pt.append(k_char(pt_val))
                    else:
                        pt.append('?')
                
                pt_str = ''.join(pt)
                known = pt_str.replace('?', '')
                score = scorer.score_per_char(known) if len(known) >= 4 else -99
                new_beam.append((score, new_partial))
        
        new_beam.sort(key=lambda x: -x[0])
        beam = new_beam[:100]
    
    # Take top 3 for this c value
    for score, unknown_vals in beam[:3]:
        full_key = list(true_key)
        for k, s in enumerate([16, 17, 18, 19, 20]):
            full_key[s] = unknown_vals[k]
        
        pt = decrypt_full(CT, full_key, c)
        key_str = ''.join(k_char(v) for v in full_key)
        unk_str = ''.join(k_char(v) for v in unknown_vals)
        
        # Find English words
        words = find_english_words(pt, 4)
        
        best_overall.append((score, c, unk_str, key_str, pt, words))

best_overall.sort(key=lambda x: -x[0])

print(f"\nTop 30 candidates across all c values:\n")
for rank, (score, c, unk, key, pt, words) in enumerate(best_overall[:30]):
    word_strs = [f"{w}@{p}" for p, w in words if w not in ("EAST", "NORTH", "NORTHEAST", "BERLIN", "CLOCK")]
    print(f"  #{rank+1}: c={c:2d}, score={score:.4f}, unk={unk}, key={key}")
    print(f"        PT: {pt}")
    if word_strs:
        print(f"        Words: {', '.join(word_strs[:10])}")
    print()

# ============================================================
# PART 2: ANALYZE PATTERNS IN TOP PLAINTEXTS
# ============================================================
print("\n" + "=" * 80)
print("PART 2: SEGMENT-BY-SEGMENT ANALYSIS OF TOP CANDIDATES")
print("=" * 80)

for rank, (score, c, unk, key, pt, words) in enumerate(best_overall[:5]):
    print(f"\n--- Candidate #{rank+1}: c={c}, key={key} ---")
    print(f"    Score: {score:.4f}")
    print(f"    Period 0 [00-28]: {pt[0:29]}")
    print(f"    Period 1 [29-57]: {pt[29:58]}")
    print(f"    Period 2 [58-86]: {pt[58:87]}")
    print(f"    Period 3 [87-96]: {pt[87:97]}")
    
    # Score each segment
    for name, start, end in [("Period 0", 0, 29), ("Period 1", 29, 58), 
                              ("Period 2", 58, 87), ("Period 3", 87, 97)]:
        seg = pt[start:end]
        seg_score = scorer.score_per_char(seg) if len(seg) >= 4 else -99
        seg_words = find_english_words(seg, 3)
        print(f"    {name}: score={seg_score:.4f}, words: {[w for _,w in seg_words]}")

# ============================================================
# PART 3: FOCUS ON READABLE FRAGMENTS
# ============================================================
print("\n" + "=" * 80)
print("PART 3: LOOKING FOR READABLE FRAGMENTS IN TOP CANDIDATES")
print("=" * 80)

# Check if any candidate has substantial English-like segments
# Look at substrings of length 8+ that score well
for rank, (score, c, unk, key, pt, words) in enumerate(best_overall[:15]):
    good_segments = []
    for length in [8, 10, 12, 15, 20]:
        for start in range(len(pt) - length + 1):
            seg = pt[start:start+length]
            seg_score = scorer.score_per_char(seg)
            if seg_score > -3.0:
                good_segments.append((seg_score, start, length, seg))
    
    if good_segments:
        good_segments.sort(key=lambda x: -x[0])
        print(f"\n  Candidate #{rank+1} (c={c}, unk={unk}):")
        for seg_score, start, length, seg in good_segments[:5]:
            print(f"    pos {start}-{start+length-1}: {seg} (score={seg_score:.4f})")

# ============================================================
# PART 4: NON-LINEAR PERIOD FUNCTIONS
# ============================================================
print("\n" + "=" * 80)
print("PART 4: NON-LINEAR PERIOD FUNCTIONS f(i) = g(i//29)")
print("=" * 80)

# Instead of f(i) = c * (i//29), test f(i) = g0, g1, g2, g3 for each period
# We have 4 periods (0, 1, 2, 3). g0 can be set to 0 (baseline).
# Then g1 and g2 are free parameters, and g3 affects only pos 87-96.
# Since cribs are in periods 0-2, g3 only affects period 3 decryption.
# g0=0 (baseline), g1 in 0..25, g2 in 0..25, g3 in 0..25

print("\nTesting all (g1, g2) pairs with g0=0...")
print("(g3 has minimal effect since period 3 is only 10 chars with no cribs)\n")

nl_results = []
for g1 in range(26):
    for g2 in range(26):
        g = [0, g1, g2, 0]  # g3=0 for now
        
        # Derive true key
        true_key = [None] * 29
        for j in range(8):
            pos = 21 + j
            slot = pos % PERIOD
            ek = (k_index(CT[pos]) - k_index("EASTNORTHEAST"[j])) % 26
            true_key[slot] = (ek - g[pos // PERIOD]) % 26
        for j in range(8, 13):
            pos = 21 + j
            slot = pos % PERIOD
            ek = (k_index(CT[pos]) - k_index("EASTNORTHEAST"[j])) % 26
            true_key[slot] = (ek - g[pos // PERIOD]) % 26
        for j in range(11):
            pos = 63 + j
            slot = pos % PERIOD
            ek = (k_index(CT[pos]) - k_index("BERLINCLOCK"[j])) % 26
            true_key[slot] = (ek - g[pos // PERIOD]) % 26
        
        # Quick decrypt with unknown slots as ? 
        pt = []
        for i in range(CT_LEN):
            slot = i % PERIOD
            if true_key[slot] is not None:
                fi = g[min(i // PERIOD, 3)]
                pt_val = (k_index(CT[i]) - true_key[slot] - fi) % 26
                pt.append(k_char(pt_val))
            else:
                pt.append('?')
        
        pt_str = ''.join(pt)
        known = pt_str.replace('?', '')
        score = scorer.score_per_char(known) if len(known) >= 4 else -99
        
        if score > -6.5:
            nl_results.append((score, g1, g2, pt_str, true_key))

nl_results.sort(key=lambda x: -x[0])
print(f"  Found {len(nl_results)} (g1,g2) pairs with score > -6.5\n")

for score, g1, g2, pt, tk in nl_results[:20]:
    key_str = ''.join(k_char(v) if v is not None else '?' for v in tk)
    words = find_english_words(pt.replace('?', ''), 4)
    extra_words = [w for _,w in words if w not in ("EAST", "NORTH", "NORTHEAST", "BERLIN", "CLOCK")]
    print(f"  g1={g1:2d}, g2={g2:2d}: score={score:.4f}, key={key_str}")
    print(f"    {pt}")
    if extra_words:
        print(f"    Extra words: {extra_words[:8]}")
    print()

# ============================================================
# PART 5: BEST NON-LINEAR + UNKNOWN SLOT SEARCH
# ============================================================
print("\n" + "=" * 80)
print("PART 5: TOP NON-LINEAR + 5-SLOT BRUTE FORCE")
print("=" * 80)

# Take top 20 (g1,g2) and do beam search over 5 unknown slots
top_nl = nl_results[:30] if nl_results else []
combined_best = []

for score0, g1, g2, pt0, tk0 in top_nl:
    g = [0, g1, g2, 0]
    true_key = list(tk0)
    
    # Beam search over unknown slots
    beam = [(0.0, [None]*5)]
    for idx, unknown_slot in enumerate([16, 17, 18, 19, 20]):
        new_beam = []
        for _, partial in beam:
            for val in range(26):
                test_key = list(true_key)
                for k, s in enumerate([16, 17, 18, 19, 20][:idx]):
                    test_key[s] = partial[k]
                test_key[unknown_slot] = val
                
                new_partial = list(partial)
                new_partial[idx] = val
                
                pt = []
                for i in range(CT_LEN):
                    slot = i % PERIOD
                    if test_key[slot] is not None:
                        fi = g[min(i // PERIOD, 3)]
                        pt_val = (k_index(CT[i]) - test_key[slot] - fi) % 26
                        pt.append(k_char(pt_val))
                    else:
                        pt.append('?')
                
                pt_str = ''.join(pt)
                s = scorer.score_per_char(pt_str) if len(pt_str) >= 4 else -99
                new_beam.append((s, new_partial))
        
        new_beam.sort(key=lambda x: -x[0])
        beam = new_beam[:50]
    
    # Take best for this g1,g2
    for s, unknown_vals in beam[:2]:
        full_key = list(true_key)
        for k, slot in enumerate([16, 17, 18, 19, 20]):
            full_key[slot] = unknown_vals[k]
        
        pt = []
        for i in range(CT_LEN):
            slot = i % PERIOD
            fi = g[min(i // PERIOD, 3)]
            pt_val = (k_index(CT[i]) - full_key[slot] - fi) % 26
            pt.append(k_char(pt_val))
        pt_str = ''.join(pt)
        
        key_str = ''.join(k_char(v) for v in full_key)
        unk_str = ''.join(k_char(v) for v in unknown_vals)
        words = find_english_words(pt_str, 4)
        extra = [f"{w}@{p}" for p,w in words if w not in ("EAST","NORTH","NORTHEAST","BERLIN","CLOCK")]
        
        combined_best.append((s, g1, g2, unk_str, key_str, pt_str, extra))

combined_best.sort(key=lambda x: -x[0])

print(f"\nTop 25 overall candidates:\n")
for rank, (score, g1, g2, unk, key, pt, extra) in enumerate(combined_best[:25]):
    print(f"  #{rank+1}: g1={g1:2d}, g2={g2:2d}, unk={unk}, score={score:.4f}")
    print(f"        key={key}")
    print(f"        PT: {pt}")
    if extra:
        print(f"        Words: {', '.join(extra[:10])}")
    
    # Check for interesting patterns
    for target in ["SLOWLY", "DESPER", "ATELY", "UNDER", "GROUND", "LAYER",
                    "BURIED", "THEEAR", "SOME", "WHERE", "TOTAL", "WEST",
                    "LANGLEY", "COMPA", "POINT", "COORD", "LOCAT", "RUINS",
                    "ANCIENT", "SHADOW", "LIGHT", "TIME", "PALIMPSEST"]:
        if target in pt:
            print(f"        *** FOUND: {target} ***")
    print()

# ============================================================
# PART 6: ALSO TEST g3 VARIATION FOR TOP CANDIDATES 
# ============================================================
print("\n" + "=" * 80)
print("PART 6: TESTING g3 VARIATION FOR TOP 5 CANDIDATES")
print("=" * 80)

for rank, (score0, g1, g2, unk0, key0, pt0, extra0) in enumerate(combined_best[:5]):
    print(f"\n  Candidate #{rank+1} base (g1={g1}, g2={g2}):")
    best_g3 = (-99, 0, "")
    for g3 in range(26):
        g = [0, g1, g2, g3]
        # Re-derive full key (g3 doesn't change slots 0-28 derivation)
        # But does affect period 3 decryption
        full_key = [k_index(ch) for ch in key0]
        
        pt = []
        for i in range(CT_LEN):
            slot = i % PERIOD
            fi = g[min(i // PERIOD, 3)]
            pt_val = (k_index(CT[i]) - full_key[slot] - fi) % 26
            pt.append(k_char(pt_val))
        pt_str = ''.join(pt)
        
        s = scorer.score_per_char(pt_str)
        if s > best_g3[0]:
            best_g3 = (s, g3, pt_str)
    
    print(f"    Best g3={best_g3[1]}: score={best_g3[0]:.4f}")
    print(f"    PT: {best_g3[2]}")
    words = find_english_words(best_g3[2], 4)
    extra = [f"{w}@{p}" for p,w in words if w not in ("EAST","NORTH","NORTHEAST","BERLIN","CLOCK")]
    if extra:
        print(f"    Words: {', '.join(extra[:10])}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
