#!/usr/bin/env python3
"""
K4 Position-Dependent: Fixed version - comprehensive search with wider beam.
"""

import math

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
                    self.quadgrams[parts[0]] = int(parts[1])
                    self.total += int(parts[1])
        self.floor = math.log10(0.01 / self.total)
    def score_per_char(self, text):
        if len(text) < 4: return -99
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            s += math.log10(self.quadgrams[gram] / self.total) if gram in self.quadgrams else self.floor
        return s / (len(text) - 3)

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
    true_key = [None] * 29
    for j in range(13):
        pos = 21 + j
        slot = pos % PERIOD
        period = pos // PERIOD
        true_key[slot] = (k_index(CT[pos]) - k_index("EASTNORTHEAST"[j]) - g[period]) % 26
    for j in range(11):
        pos = 63 + j
        slot = pos % PERIOD
        period = pos // PERIOD
        true_key[slot] = (k_index(CT[pos]) - k_index("BERLINCLOCK"[j]) - g[period]) % 26
    return true_key

def decrypt_with_g(key29, g):
    pt = []
    for i in range(CT_LEN):
        slot = i % PERIOD
        period = min(i // PERIOD, 3)
        if key29[slot] is None:
            pt.append('?')
        else:
            pt.append(k_char((k_index(CT[i]) - key29[slot] - g[period]) % 26))
    return ''.join(pt)

print("=" * 80)
print("K4 POSITION-DEPENDENT: COMPREHENSIVE SEARCH V3 FIXED")
print("=" * 80)

# ============================================================
# PART 1: Top (g1,g2) pairs + all g3 + beam over unknowns
# ============================================================
top_pairs = [
    (14, 8), (25, 7), (25, 19), (25, 5), (2, 8), (25, 8),
    (24, 4), (25, 11), (21, 2), (25, 10), (25, 2), (25, 6),
    (14, 20), (25, 20), (25, 24), (0, 0),
]

mega_results = []
count = 0

for g1, g2 in top_pairs:
    for g3 in range(26):
        g = [0, g1, g2, g3]
        base_key = derive_key_for_g(g)
        
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
                    
                    # Score only on positions where key is known
                    pt = decrypt_with_g(test_key, g)
                    known = pt.replace('?', '')
                    s = scorer.score_per_char(known) if len(known) >= 4 else -99
                    new_beam.append((s, new_partial))
            
            new_beam.sort(key=lambda x: -x[0])
            beam = new_beam[:80]
        
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
        count += 1

mega_results.sort(key=lambda x: -x[0])

print(f"\n  Tested {count} combinations. Top 50:\n")
for rank, (score, g1, g2, g3, unk, key, pt, extra) in enumerate(mega_results[:50]):
    # Check for special patterns
    specials = []
    for target in ["SLOWLY", "DESPER", "ATELY", "UNDER", "GROUND", "LAYER",
                    "BURIED", "THEEAR", "WHERE", "TOTAL", "LANGLEY", "COMPA",
                    "POINT", "COORD", "LOCAT", "RUINS", "ANCIENT", "SHADOW",
                    "LIGHT", "TIME", "PALIMPSEST", "RESULT", "SECRET",
                    "HIDDEN", "INVISIBLE", "BETWEEN", "DIGETAL", "CLOCK",
                    "WHOSE", "THERE"]:
        if target in pt:
            specials.append(target)
    
    marker = " ***" if len(extra) >= 3 or specials else ""
    print(f"  #{rank+1}: g=[0,{g1:2d},{g2:2d},{g3:2d}] unk={unk} score={score:.4f}{marker}")
    print(f"        PT: {pt}")
    if extra:
        print(f"        Words: {', '.join(extra[:12])}")
    if specials:
        print(f"        SPECIAL: {specials}")
    print()

# ============================================================
# PART 2: Focus on candidates with most English words
# ============================================================
print("\n" + "=" * 80)
print("PART 2: CANDIDATES RANKED BY NUMBER OF ENGLISH WORDS (4+ CHARS)")
print("=" * 80)

by_wordcount = sorted(mega_results, key=lambda x: (-len(x[7]), -x[0]))

for rank, (score, g1, g2, g3, unk, key, pt, extra) in enumerate(by_wordcount[:20]):
    print(f"  #{rank+1}: {len(extra)} extra words, g=[0,{g1},{g2},{g3}] unk={unk} score={score:.4f}")
    print(f"        PT: {pt}")
    print(f"        Words: {', '.join(extra[:15])}")
    print()

# ============================================================
# PART 3: Check for any candidate where period 3 forms a word
# ============================================================
print("\n" + "=" * 80)
print("PART 3: CANDIDATES WHERE PERIOD 3 (pos 87-96) CONTAINS WORDS")
print("=" * 80)

p3_words = []
for score, g1, g2, g3, unk, key, pt, extra in mega_results:
    p3 = pt[87:97]
    w3 = find_english_words(p3, 4)
    if w3:
        p3_words.append((score, g1, g2, g3, unk, pt, [(p,w) for p,w in w3]))

p3_words.sort(key=lambda x: -x[0])
print(f"\n  Found {len(p3_words)} candidates with words in period 3:\n")
for score, g1, g2, g3, unk, pt, w3 in p3_words[:20]:
    print(f"  g=[0,{g1},{g2},{g3}] unk={unk} score={score:.4f}")
    print(f"    PT: {pt}")
    print(f"    Period 3 words: {w3}")
    print()

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
