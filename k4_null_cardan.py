#!/usr/bin/env python3
"""
K4 Null Cipher / Cardan Grille Hypothesis Tester
=================================================
Tests the hypothesis that after Vigenere decryption, only certain positions
contain the real message (the rest are nulls/noise).

Architecture:
- Phase 1: Exhaustive 26^5 key search with ~80 extraction patterns (numpy batched)
- Phase 2: Exhaustive search with uncommon-letter filtering
- Phase 3: Detailed pattern analysis with CBNJQ key (500+ patterns)
- Phase 4: Keyword Cardan grille with CBNJQ
- Phase 5: Triple removal within period 29 (CBNJQ)
- Phase 6: Vowel/consonant and interleave analysis
- Phase 7: Direct ciphertext extraction (no Vigenere)
- Phase 8: Null extraction before Vigenere (reverse order)
"""

import math
import sys
import time
import numpy as np
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT_LEN = len(K4_CT)  # 97
PERIOD = 29

KNOWN_KEY_PART1 = "OYNKYELYOIECBAQK"
KNOWN_KEY_PART2 = "RDUMRIYW"

K2I = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}
I2K = KRYPTOS_ALPHA

CT_INT = np.array([K2I[c] for c in K4_CT], dtype=np.int8)
KEY1_INT = np.array([K2I[c] for c in KNOWN_KEY_PART1], dtype=np.int8)
KEY2_INT = np.array([K2I[c] for c in KNOWN_KEY_PART2], dtype=np.int8)

# Pre-classify positions
KNOWN_POS_LIST = []   # (ct_index, precomputed_pt_value)
UNKNOWN_POS_LIST = [] # (ct_index, unknown_key_index 0-4)

for i in range(CT_LEN):
    kp = i % PERIOD
    if kp < 16:
        KNOWN_POS_LIST.append((i, int((CT_INT[i] - KEY1_INT[kp]) % 26)))
    elif kp >= 21:
        KNOWN_POS_LIST.append((i, int((CT_INT[i] - KEY2_INT[kp - 21]) % 26)))
    else:
        UNKNOWN_POS_LIST.append((i, kp - 16))

UNKNOWN_BY_KEYPOS = [[] for _ in range(5)]
for ct_idx, uk_pos in UNKNOWN_POS_LIST:
    UNKNOWN_BY_KEYPOS[uk_pos].append(ct_idx)


# ============================================================
# QUADGRAM SCORER
# ============================================================

class QuadgramScorer:
    def __init__(self, filepath):
        self.log_probs_dict = {}
        total = 0
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    gram, count = parts[0], int(parts[1])
                    self.log_probs_dict[gram] = count
                    total += count
        self.log_total = math.log10(total)
        self.floor = math.log10(0.01 / total)

        for gram in self.log_probs_dict:
            self.log_probs_dict[gram] = math.log10(self.log_probs_dict[gram]) - self.log_total

        # Flat lookup array for numpy-based scoring
        self.flat = np.full(26**4, self.floor, dtype=np.float32)
        for gram, lp in self.log_probs_dict.items():
            try:
                idx = K2I[gram[0]]*17576 + K2I[gram[1]]*676 + K2I[gram[2]]*26 + K2I[gram[3]]
                self.flat[idx] = lp
            except KeyError:
                pass

    def score_str(self, text):
        if len(text) < 4:
            return -9999.0
        lp = self.log_probs_dict
        fl = self.floor
        s = 0.0
        for i in range(len(text) - 3):
            s += lp.get(text[i:i+4], fl)
        return s

    def score_per_char(self, text):
        if len(text) < 4:
            return -9999.0
        return self.score_str(text) / (len(text) - 3)

    def score_int_list(self, arr):
        """Score a list of KRYPTOS indices."""
        n = len(arr)
        if n < 4:
            return -9999.0
        flat = self.flat
        s = 0.0
        for i in range(n - 3):
            s += flat[arr[i] * 17576 + arr[i+1] * 676 + arr[i+2] * 26 + arr[i+3]]
        return float(s)

    def score_batch(self, pt_batch, indices):
        """
        Score batch of plaintexts extracting at given indices.
        pt_batch: (batch, CT_LEN) int8 array
        indices: numpy array of position indices
        Returns: (batch,) float64 score array
        """
        ext = pt_batch[:, indices]  # (batch, len(indices))
        n = ext.shape[1]
        if n < 4:
            return np.full(pt_batch.shape[0], -9999.0)
        scores = np.zeros(pt_batch.shape[0], dtype=np.float64)
        for i in range(n - 3):
            fidx = (ext[:, i].astype(np.int32) * 17576 +
                    ext[:, i+1].astype(np.int32) * 676 +
                    ext[:, i+2].astype(np.int32) * 26 +
                    ext[:, i+3].astype(np.int32))
            scores += self.flat[fidx]
        return scores


# ============================================================
# BATCH DECRYPTION
# ============================================================

def decrypt_batch(suffixes):
    """Decrypt batch. suffixes: (batch, 5) int8. Returns (batch, CT_LEN) int8."""
    batch = suffixes.shape[0]
    pt = np.zeros((batch, CT_LEN), dtype=np.int8)
    for ci, pv in KNOWN_POS_LIST:
        pt[:, ci] = pv
    for ci, uk in UNKNOWN_POS_LIST:
        pt[:, ci] = (int(CT_INT[ci]) - suffixes[:, uk].astype(np.int16)) % 26
    return pt


# ============================================================
# PATTERN BUILDERS
# ============================================================

def get_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]


def build_phase1_patterns():
    """~80 patterns for exhaustive search."""
    patterns = []

    # Every Nth, offsets (N=2..7): ~27 patterns
    for n in range(2, 8):
        for offset in range(n):
            idx = list(range(offset, CT_LEN, n))
            if len(idx) >= 10:
                patterns.append((f"ev{n}_o{offset}", np.array(idx, dtype=np.int32)))

    # Remove every Nth (N=2..5): ~14 patterns
    for n in range(2, 6):
        for offset in range(n):
            rm = set(range(offset, CT_LEN, n))
            idx = [i for i in range(CT_LEN) if i not in rm]
            if len(idx) >= 10:
                patterns.append((f"rm{n}_o{offset}", np.array(idx, dtype=np.int32)))

    # First k of m (selected): ~12 patterns
    for m in range(2, 6):
        for k in range(1, min(m, 3)):
            idx = []
            for s in range(0, CT_LEN, m):
                for j in range(k):
                    if s + j < CT_LEN:
                        idx.append(s + j)
            if len(idx) >= 10:
                patterns.append((f"f{k}o{m}", np.array(idx, dtype=np.int32)))

    # Prime / non-prime: 2 patterns
    pr = get_primes(CT_LEN - 1)
    patterns.append(("prime", np.array(pr, dtype=np.int32)))
    non_pr = [i for i in range(CT_LEN) if i not in set(pr)]
    patterns.append(("non_prime", np.array(non_pr, dtype=np.int32)))

    # Period-29 single removal: 29 patterns
    for null_pos in range(PERIOD):
        rm = set(range(null_pos, CT_LEN, PERIOD))
        idx = [i for i in range(CT_LEN) if i not in rm]
        patterns.append((f"p29r{null_pos}", np.array(idx, dtype=np.int32)))

    # Period-29 alternating removal: 2 patterns
    for offset in range(2):
        nw = set(range(offset, PERIOD, 2))
        rm = set()
        for cs in range(0, CT_LEN, PERIOD):
            for n in nw:
                pos = cs + n
                if pos < CT_LEN:
                    rm.add(pos)
        idx = [i for i in range(CT_LEN) if i not in rm]
        patterns.append((f"p29alt{offset}", np.array(idx, dtype=np.int32)))

    return patterns


def build_extended_patterns():
    """Full set of patterns for detailed analysis (~700+)."""
    patterns = build_phase1_patterns()

    # Last k of m
    for m in range(3, 10):
        for k in range(1, m):
            idx = []
            for s in range(0, CT_LEN, m):
                ge = min(s + m, CT_LEN)
                gl = ge - s
                for j in range(max(0, gl - k), gl):
                    idx.append(s + j)
            if len(idx) >= 10:
                patterns.append((f"l{k}o{m}", np.array(idx, dtype=np.int32)))

    # More first-k-of-m
    for m in range(6, 12):
        for k in range(1, min(m, 5)):
            idx = []
            for s in range(0, CT_LEN, m):
                for j in range(k):
                    if s + j < CT_LEN:
                        idx.append(s + j)
            if len(idx) >= 10:
                patterns.append((f"f{k}o{m}", np.array(idx, dtype=np.int32)))

    # Period-relative for other periods (single removal)
    for period in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 23]:
        for null_pos in range(period):
            rm = set(range(null_pos, CT_LEN, period))
            idx = [i for i in range(CT_LEN) if i not in rm]
            if len(idx) >= 10:
                patterns.append((f"p{period}r{null_pos}", np.array(idx, dtype=np.int32)))

    # Period-29 double removal
    for p1 in range(PERIOD):
        for p2 in range(p1 + 1, PERIOD):
            rm = set(range(p1, CT_LEN, PERIOD)) | set(range(p2, CT_LEN, PERIOD))
            idx = [i for i in range(CT_LEN) if i not in rm]
            if len(idx) >= 10:
                patterns.append((f"p29r{p1}_{p2}", np.array(idx, dtype=np.int32)))

    # Every 3rd within period 29
    for offset in range(3):
        nw = set(range(offset, PERIOD, 3))
        rm = set()
        for cs in range(0, CT_LEN, PERIOD):
            for n in nw:
                pos = cs + n
                if pos < CT_LEN:
                    rm.add(pos)
        idx = [i for i in range(CT_LEN) if i not in rm]
        if len(idx) >= 10:
            patterns.append((f"p29e3o{offset}", np.array(idx, dtype=np.int32)))

    # Remove every Nth for more values
    for n in range(6, 10):
        for offset in range(n):
            rm = set(range(offset, CT_LEN, n))
            idx = [i for i in range(CT_LEN) if i not in rm]
            if len(idx) >= 10:
                patterns.append((f"rm{n}_o{offset}", np.array(idx, dtype=np.int32)))

    return patterns


# ============================================================
# MAIN
# ============================================================

def main():
    t0 = time.time()
    print("=" * 80)
    print("K4 NULL CIPHER / CARDAN GRILLE HYPOTHESIS TESTER")
    print("=" * 80)
    print(f"Ciphertext: {K4_CT}")
    print(f"CT length: {CT_LEN}, Period: {PERIOD}")
    print(f"Known key: {KNOWN_KEY_PART1}?????{KNOWN_KEY_PART2}")
    print(f"Search space: 26^5 = {26**5:,} keys")
    print()
    print(f"Unknown positions by key index:")
    for uk in range(5):
        print(f"  Key pos {uk+16}: CT positions {UNKNOWN_BY_KEYPOS[uk]}")
    print()

    scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

    # Baselines
    eng = scorer.score_per_char("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG")
    rnd = scorer.score_per_char("KRYPTOSABCDEFGHIJLMNQUVWXZ" * 4)
    print(f"Score baselines:")
    print(f"  English: {eng:.4f}/char")
    print(f"  Random:  {rnd:.4f}/char")
    print(f"  Threshold for Phase 1: -2.0/char")
    print(f"  (Good English typically scores -1.7 to -1.9/char)")

    # CBNJQ reference
    cbnjq_suf = np.array([[K2I[c] for c in "CBNJQ"]], dtype=np.int8)
    pt_cbnjq = decrypt_batch(cbnjq_suf)[0]
    pt_cbnjq_str = ''.join(I2K[x] for x in pt_cbnjq)
    print(f"\nCBNJQ reference:")
    print(f"  Key: {KNOWN_KEY_PART1}CBNJQ{KNOWN_KEY_PART2}")
    print(f"  PT:  {pt_cbnjq_str}")
    print(f"  Score: {scorer.score_per_char(pt_cbnjq_str):.4f}/char")
    print(f"  Pos 21-33: {pt_cbnjq_str[21:34]} (expect EASTNORTHEAST)")
    print(f"  Pos 63-73: {pt_cbnjq_str[63:74]} (expect BERLINCLOCK)")
    print()

    # ================================================================
    # PHASE 1: Exhaustive 26^5 with ~80 extraction patterns
    # ================================================================
    print("=" * 80)
    print("PHASE 1: Exhaustive 26^5 key search")
    print("=" * 80)

    phase1_patterns = build_phase1_patterns()
    print(f"Patterns: {len(phase1_patterns)}")
    for name, idx in phase1_patterns[:5]:
        print(f"  {name}: {len(idx)} positions")
    print(f"  ... and {len(phase1_patterns)-5} more")

    THRESHOLD = -2.0
    BATCH_SIZE = 676  # 26*26
    total_keys = 26**5
    results = []
    top_full_keys = []

    start = time.time()
    keys_done = 0

    for b0 in range(26):
        for b1 in range(26):
            for b2 in range(26):
                # Build batch
                batch_suf = np.zeros((BATCH_SIZE, 5), dtype=np.int8)
                idx = 0
                for b3 in range(26):
                    for b4 in range(26):
                        batch_suf[idx] = [b0, b1, b2, b3, b4]
                        idx += 1

                pt_batch = decrypt_batch(batch_suf)

                # Full plaintext score
                full_sc = scorer.score_batch(pt_batch, np.arange(CT_LEN, dtype=np.int32))
                full_spc = full_sc / (CT_LEN - 3)

                # Track top full keys
                good_full = np.where(full_spc > -2.5)[0]
                for gi in good_full:
                    s_str = ''.join(I2K[x] for x in batch_suf[gi])
                    p_str = ''.join(I2K[x] for x in pt_batch[gi])
                    top_full_keys.append((float(full_spc[gi]), s_str, p_str))

                # Test extraction patterns
                for pat_name, pat_idx in phase1_patterns:
                    n_ext = len(pat_idx)
                    scores = scorer.score_batch(pt_batch, pat_idx)
                    spc = scores / (n_ext - 3)

                    hits = np.where(spc > THRESHOLD)[0]
                    for h in hits:
                        s_str = ''.join(I2K[x] for x in batch_suf[h])
                        ext = ''.join(I2K[pt_batch[h, j]] for j in pat_idx)
                        results.append((float(spc[h]), float(scores[h]), ext,
                                       s_str, pat_name, n_ext))

                keys_done += BATCH_SIZE
                if keys_done % (26**3) == 0:
                    el = time.time() - start
                    pct = keys_done / total_keys * 100
                    rate = keys_done / el if el > 0 else 0
                    eta = (total_keys - keys_done) / rate if rate > 0 else 0
                    print(f"  {keys_done:>10,}/{total_keys:,} ({pct:5.1f}%) "
                          f"| {rate:,.0f}/s | ETA {eta:,.0f}s | hits={len(results)}")
                    sys.stdout.flush()

    el = time.time() - start
    print(f"\nPhase 1 done: {el:.1f}s, {len(results)} hits above {THRESHOLD}/char")

    # Sort and report
    results.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    print(f"\nTop Phase 1 results (deduplicated):")
    count = 0
    for spc, sc, ext, suf, pat, n in results:
        if ext in seen:
            continue
        seen.add(ext)
        count += 1
        if count > 80:
            break
        fk = KNOWN_KEY_PART1 + suf + KNOWN_KEY_PART2
        print(f"  #{count}: key={fk} pat={pat} sc={spc:.4f}/c len={n} | {ext}")

    top_full_keys.sort(reverse=True)
    print(f"\nTop 20 full-plaintext keys:")
    for i, (spc, suf, text) in enumerate(top_full_keys[:20]):
        fk = KNOWN_KEY_PART1 + suf + KNOWN_KEY_PART2
        print(f"  #{i+1}: key={fk} sc={spc:.4f}/c | {text}")

    # ================================================================
    # PHASE 2: Uncommon letter filtering (top keys from Phase 1 + CBNJQ)
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 2: Uncommon letter filtering (top keys + exhaustive fast)")
    print("=" * 80)

    UNCOMMON = [
        ("JQXZV", set([K2I[c] for c in "JQXZV"])),
        ("QXZ", set([K2I[c] for c in "QXZ"])),
        ("JQXZ", set([K2I[c] for c in "JQXZ"])),
        ("JV", set([K2I[c] for c in "JV"])),
        ("QZ", set([K2I[c] for c in "QZ"])),
    ]

    p2_results = []

    # Collect candidate keys: top full keys + CBNJQ + any partial hits
    candidate_suffixes = set()
    candidate_suffixes.add("CBNJQ")
    for _, suf, _ in top_full_keys[:500]:
        candidate_suffixes.add(suf)
    # Also add suffixes from Phase 1 results
    for _, _, _, suf, _, _ in results[:500]:
        candidate_suffixes.add(suf)

    print(f"Testing {len(candidate_suffixes)} candidate keys with uncommon letter filtering...")

    for suf_str in candidate_suffixes:
        suf_ints = np.array([[K2I[c] for c in suf_str]], dtype=np.int8)
        pt_row = decrypt_batch(suf_ints)[0]

        for uc_name, uc_set in UNCOMMON:
            kept = [int(x) for x in pt_row if int(x) not in uc_set]
            n_f = len(kept)
            if n_f < 10:
                continue
            sc = scorer.score_int_list(kept)
            spc = sc / (n_f - 3)
            if spc > THRESHOLD:
                e_str = ''.join(I2K[x] for x in kept)
                p2_results.append((spc, sc, e_str, suf_str, f"rm_{uc_name}", n_f))

    print(f"\nPhase 2 done: {len(p2_results)} hits from {len(candidate_suffixes)} candidate keys")
    p2_results.sort(key=lambda x: x[0], reverse=True)
    seen2 = set()
    count = 0
    for spc, sc, ext, suf, pat, n in p2_results:
        if ext in seen2:
            continue
        seen2.add(ext)
        count += 1
        if count > 50:
            break
        fk = KNOWN_KEY_PART1 + suf + KNOWN_KEY_PART2
        print(f"  #{count}: key={fk} pat={pat} sc={spc:.4f}/c len={n} | {ext}")

    # ================================================================
    # PHASE 3: Extended patterns with CBNJQ key only
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 3: Extended patterns (CBNJQ key)")
    print("=" * 80)

    ext_patterns = build_extended_patterns()
    print(f"Testing {len(ext_patterns)} patterns on CBNJQ plaintext...")

    pt_str = pt_cbnjq_str
    pt_arr = [int(x) for x in pt_cbnjq]

    p3_results = []
    for pat_name, pat_idx in ext_patterns:
        ext_list = [pt_arr[i] for i in pat_idx if i < CT_LEN]
        n = len(ext_list)
        if n < 8:
            continue
        sc = scorer.score_int_list(ext_list)
        spc = sc / (n - 3)
        p3_results.append((spc, sc, ''.join(I2K[x] for x in ext_list), pat_name, n))

    p3_results.sort(reverse=True)
    print(f"\nTop 50 extraction patterns for CBNJQ:")
    for i, (spc, sc, text, pat, n) in enumerate(p3_results[:50]):
        print(f"  #{i+1}: pat={pat} sc={spc:.4f}/c len={n} | {text}")

    # ================================================================
    # PHASE 4: Keyword Cardan Grille (CBNJQ)
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 4: Keyword Cardan Grille (CBNJQ key)")
    print("=" * 80)

    GRILLE_KEYWORDS = [
        "KRYPTOS", "SHADOW", "CLOCK", "BERLIN", "PALIMPSEST", "ABSCISSA",
        "SANBORN", "CIA", "LANGLEY", "NORTH", "EAST", "COMPASS",
        "LUCID", "MEMORY", "LAYER", "MASK", "NULL", "HIDE", "SECRET",
        "TIME", "WALL", "GATE", "KEY", "CODE", "SPY", "AGENT",
        "BETWEEN", "SUBTLE", "SHADING", "IQLUSION", "UNDERGRUUND",
        "DESPERATELY", "VIRTUALLY", "INVISIBLE", "DIGETAL",
        "SLOWLYDESPERATELY", "TOTALLYINVISIBLE", "SHADOWFORCES",
    ]

    p4_results = []
    for kw in GRILLE_KEYWORDS:
        schemes = {}

        # A: KRYPTOS index
        schemes['kidx'] = sorted(set(K2I.get(c, -1) for c in kw.upper()) - {-1})
        schemes['kidx'] = [p for p in schemes['kidx'] if p < CT_LEN]

        # B: Cumulative KRYPTOS
        cum = 0; pb = []
        for c in kw.upper():
            if c in K2I:
                cum += K2I[c] + 1
                if cum < CT_LEN:
                    pb.append(cum)
        schemes['kcum'] = pb

        # C: Standard index
        schemes['sidx'] = sorted(set(ord(c)-65 for c in kw.upper() if 'A' <= c <= 'Z'))
        schemes['sidx'] = [p for p in schemes['sidx'] if 0 <= p < CT_LEN]

        # D: Cumulative standard
        cum = 0; pd = []
        for c in kw.upper():
            if 'A' <= c <= 'Z':
                cum += ord(c) - 64
                if cum < CT_LEN:
                    pd.append(cum)
        schemes['scum'] = pd

        # E: Keyword values mod 29 as positions within each period cycle
        kw_vals = sorted(set(K2I.get(c, 0) % PERIOD for c in kw.upper() if c in K2I))
        pe = []
        for cs in range(0, CT_LEN, PERIOD):
            for v in kw_vals:
                if cs + v < CT_LEN:
                    pe.append(cs + v)
        schemes['psel'] = pe

        # F: Fibonacci-like: start from keyword values, generate positions
        fib_pos = []
        kv = [K2I.get(c, 0) for c in kw.upper() if c in K2I]
        if len(kv) >= 2:
            a, b = kv[0], kv[1]
            while a < CT_LEN:
                fib_pos.append(a)
                a, b = b, (a + b) % CT_LEN
                if len(fib_pos) > 50:
                    break
            schemes['fib'] = sorted(set(p for p in fib_pos if p < CT_LEN))

        for sn, positions in schemes.items():
            if len(positions) < 4:
                continue
            positions = [p for p in positions if p < CT_LEN]

            # Extract
            ext = ''.join(pt_str[p] for p in positions)
            if len(ext) >= 4:
                spc = scorer.score_per_char(ext)
                if spc > -2.5:
                    p4_results.append((spc, ext, kw, sn, 'extract'))
                    print(f"  KW='{kw}' {sn}: sc={spc:.4f}/c len={len(ext)} | {ext}")

            # Complement
            ps = set(positions)
            ext2 = ''.join(pt_str[i] for i in range(CT_LEN) if i not in ps)
            if len(ext2) >= 10:
                spc2 = scorer.score_per_char(ext2)
                if spc2 > -2.3:
                    p4_results.append((spc2, ext2, kw, sn, 'complement'))
                    print(f"  KW='{kw}' {sn}(C): sc={spc2:.4f}/c len={len(ext2)} | {ext2}")

    # ================================================================
    # PHASE 5: Triple removal within period 29 (CBNJQ)
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 5: Triple removal within period 29 (CBNJQ)")
    print("=" * 80)

    p5_results = []
    for p1 in range(PERIOD):
        for p2 in range(p1+1, PERIOD):
            for p3 in range(p2+1, PERIOD):
                rm = (set(range(p1, CT_LEN, PERIOD)) |
                      set(range(p2, CT_LEN, PERIOD)) |
                      set(range(p3, CT_LEN, PERIOD)))
                kept = [pt_arr[i] for i in range(CT_LEN) if i not in rm]
                n = len(kept)
                if n < 10:
                    continue
                sc = scorer.score_int_list(kept)
                spc = sc / (n - 3)
                if spc > -2.1:
                    ext = ''.join(I2K[x] for x in kept)
                    p5_results.append((spc, ext, f"rm_{p1}_{p2}_{p3}", n))

    p5_results.sort(reverse=True)
    print(f"Found {len(p5_results)} patterns > -2.1/char")
    for i, (spc, text, pat, n) in enumerate(p5_results[:30]):
        print(f"  #{i+1}: {pat} sc={spc:.4f}/c len={n} | {text}")

    # ================================================================
    # PHASE 6: Vowel/consonant + interleave (CBNJQ)
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 6: Vowel/consonant and interleave (CBNJQ)")
    print("=" * 80)

    VOWELS = set("AEIOU")
    v_only = ''.join(c for c in pt_str if c in VOWELS)
    c_only = ''.join(c for c in pt_str if c not in VOWELS)
    print(f"Vowels ({len(v_only)}): {v_only}")
    print(f"  Score: {scorer.score_per_char(v_only):.4f}/c")
    print(f"Consonants ({len(c_only)}): {c_only}")
    print(f"  Score: {scorer.score_per_char(c_only):.4f}/c")
    print(f"Vowel fraction: {len(v_only)/CT_LEN:.3f} (English ~0.40)")
    v_pos = [i for i in range(CT_LEN) if pt_str[i] in VOWELS]
    print(f"Vowel positions: {v_pos}")

    print("\nInterleave streams:")
    for split in range(2, 10):
        for stream in range(split):
            ext = pt_str[stream::split]
            spc = scorer.score_per_char(ext)
            flag = " <---" if spc > -2.3 else ""
            print(f"  {stream}/{split} ({len(ext)}ch): sc={spc:.4f}/c | {ext}{flag}")

    # ================================================================
    # PHASE 7: Direct ciphertext extraction (no Vigenere)
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 7: Direct CT extraction (no Vigenere)")
    print("=" * 80)

    for n in range(2, 20):
        for offset in range(n):
            ext = K4_CT[offset::n]
            if len(ext) >= 8:
                spc = scorer.score_per_char(ext)
                if spc > -2.5:
                    print(f"  ev{n}_o{offset}: sc={spc:.4f}/c len={len(ext)} | {ext}")

    # Removal patterns on CT
    print("\nRemoval patterns on CT:")
    for n in range(2, 12):
        for offset in range(n):
            ext = ''.join(K4_CT[i] for i in range(CT_LEN) if i % n != offset)
            if len(ext) >= 10:
                spc = scorer.score_per_char(ext)
                if spc > -2.5:
                    print(f"  CT_rm{n}_o{offset}: sc={spc:.4f}/c len={len(ext)} | {ext}")

    # ================================================================
    # PHASE 8: Null extraction BEFORE Vigenere
    # ================================================================
    print("\n" + "=" * 80)
    print("PHASE 8: Extract from CT then decrypt")
    print("=" * 80)

    full_key = KNOWN_KEY_PART1 + "CBNJQ" + KNOWN_KEY_PART2

    # Extract subset of CT, then decrypt with key mapped to original positions
    for n in range(2, 8):
        for offset in range(n):
            # Keep every Nth
            keep = list(range(offset, CT_LEN, n))
            pt_chars = []
            for ci in keep:
                cv = K2I[K4_CT[ci]]
                kv = K2I[full_key[ci % PERIOD]]
                pt_chars.append(I2K[(cv - kv) % 26])
            pt_ext = ''.join(pt_chars)
            spc = scorer.score_per_char(pt_ext)
            if spc > -2.5:
                print(f"  keep_ev{n}_o{offset}: sc={spc:.4f}/c | {pt_ext}")

            # Remove every Nth
            keep2 = [i for i in range(CT_LEN) if i % n != offset]
            pt_chars2 = []
            for ci in keep2:
                cv = K2I[K4_CT[ci]]
                kv = K2I[full_key[ci % PERIOD]]
                pt_chars2.append(I2K[(cv - kv) % 26])
            pt_ext2 = ''.join(pt_chars2)
            spc2 = scorer.score_per_char(pt_ext2)
            if spc2 > -2.5:
                print(f"  rm_ev{n}_o{offset}: sc={spc2:.4f}/c | {pt_ext2}")

    # Also: remove positions from CT then decrypt with a SEQUENTIAL key
    # (i.e., if nulls were inserted, the real message maps to consecutive key positions)
    print("\nSequential key mapping after null removal:")
    for n in range(2, 6):
        for offset in range(n):
            keep = [i for i in range(CT_LEN) if i % n != offset]
            ct_kept = [K2I[K4_CT[i]] for i in keep]
            # Now decrypt with key applied sequentially (not by original position)
            for key_try in ["CBNJQ"]:
                fk = KNOWN_KEY_PART1 + key_try + KNOWN_KEY_PART2
                fk_ints = [K2I[c] for c in fk]
                pt_chars = []
                for j, cv in enumerate(ct_kept):
                    kv = fk_ints[j % PERIOD]
                    pt_chars.append(I2K[(cv - kv) % 26])
                pt_ext = ''.join(pt_chars)
                spc = scorer.score_per_char(pt_ext)
                if spc > -2.5:
                    print(f"  rm{n}_o{offset}_seqkey: sc={spc:.4f}/c | {pt_ext}")

    # ================================================================
    # GRAND SUMMARY
    # ================================================================
    print("\n" + "=" * 80)
    print("GRAND SUMMARY")
    print("=" * 80)

    all_res = results + p2_results
    all_res.sort(key=lambda x: x[0], reverse=True)

    seen_final = set()
    print("\nTOP 30 RESULTS ACROSS ALL EXHAUSTIVE PHASES:")
    count = 0
    for item in all_res:
        spc, sc, ext, suf, pat = item[0], item[1], item[2], item[3], item[4]
        n_ext = item[5] if len(item) > 5 else len(ext)
        if ext in seen_final:
            continue
        seen_final.add(ext)
        count += 1
        if count > 30:
            break
        fk = KNOWN_KEY_PART1 + suf + KNOWN_KEY_PART2
        print(f"\n  #{count}:")
        print(f"    Key: {fk}")
        print(f"    Pattern: {pat}")
        print(f"    Score: {spc:.4f}/char ({sc:.2f} total)")
        print(f"    Length: {n_ext}")
        print(f"    Text: {ext}")

    if count == 0:
        print("\n  No results exceeded threshold across exhaustive search.")
        print("  This suggests the null cipher hypothesis with fixed positional")
        print("  patterns is unlikely, OR the threshold needs adjustment,")
        print("  OR the masking technique is more complex than tested.")

    # CBNJQ analysis
    print(f"\n{'='*80}")
    print("CBNJQ PLAINTEXT ANALYSIS")
    print(f"{'='*80}")
    print(f"Plaintext: {pt_cbnjq_str}")
    freq = Counter(pt_cbnjq_str)
    print(f"\nLetter frequencies:")
    for ch, cnt in sorted(freq.items(), key=lambda x: -x[1]):
        print(f"  {ch}: {cnt:2d} {'#' * cnt}")

    # Digram analysis
    print(f"\nCommon digrams in plaintext:")
    digrams = Counter(pt_cbnjq_str[i:i+2] for i in range(CT_LEN - 1))
    for dg, cnt in digrams.most_common(15):
        print(f"  {dg}: {cnt}")

    total_time = time.time() - t0
    print(f"\nTotal runtime: {total_time:.1f}s ({total_time/60:.1f}min)")
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
