#!/usr/bin/env python3
"""
Kryptos K4 W-Separator Hypothesis Tester
=========================================
2025 Sanborn clue: "The letter W may act as a separator splitting K4 into six segments."

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

W positions: 20, 36, 48, 58, 74 => 6 segments

Known cribs (from Sanborn's confirmed hints):
  - EASTNORTHEAST somewhere in K4 (confirmed at positions 21-33 in ciphertext stream,
    which maps to segment 2 positions 0-12)
  - BERLINCLOCK somewhere in K4 (confirmed at positions 63-73 in ciphertext stream,
    which maps to segment 5 positions 4-14)
"""

import math
import string
import itertools
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA  = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Split on W
w_positions = [i for i, c in enumerate(K4) if c == 'W']
segments_raw = K4.split('W')
segments = segments_raw  # 6 segments

# Known cribs
CRIB_ENE = "EASTNORTHEAST"   # 13 chars
CRIB_BC  = "BERLINCLOCK"     # 11 chars

# Candidate plaintext (Genie Engine / community speculation)
GENIE_PLAIN = "TOSETTHEEASTNORTHEASTHOURBYB EARINGBERLINCLOCDEGREESGGRIDPOINTNORTHWESTTOFI NDGROSSERSTERN"
# Cleaned versions for testing
GENIE_CANDIDATES = [
    "TOSETTHEEASTNORTHEASTHOURBYB EARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYBEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def load_quadgrams(path="/home/user/polyalphabetic/english_quadgrams.txt"):
    """Load English quadgram log-probabilities."""
    qg = {}
    total = 0
    try:
        with open(path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    qg[parts[0]] = int(parts[1])
                    total += int(parts[1])
        log_total = math.log10(total)
        floor = math.log10(0.01 / total)
        for k in qg:
            qg[k] = math.log10(qg[k]) - log_total
        return qg, floor
    except Exception as e:
        print(f"Warning: Could not load quadgrams: {e}")
        return {}, -10.0

def load_dictionary(path="/home/user/polyalphabetic/OxfordEnglishWords.txt"):
    """Load English dictionary as a set of uppercase words."""
    words = set()
    try:
        with open(path) as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 3:
                    words.add(w)
    except Exception as e:
        print(f"Warning: Could not load dictionary: {e}")
    return words

QUADGRAMS, QG_FLOOR = load_quadgrams()
DICTIONARY = load_dictionary()

def quadgram_score(text):
    """Score text using English quadgram frequencies."""
    if not QUADGRAMS:
        return -999999
    text = text.upper()
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QUADGRAMS.get(qg, QG_FLOOR)
    if len(text) <= 3:
        return -999999
    return score / (len(text) - 3)  # normalize per quadgram

def index_of_coincidence(text):
    """Compute IC of text."""
    text = ''.join(c for c in text.upper() if c.isalpha())
    n = len(text)
    if n <= 1:
        return 0.0
    freq = Counter(text)
    ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    return ic

def vigenere_decrypt(ct, key, alphabet=STANDARD_ALPHA):
    """Standard Vigenere decryption."""
    pt = []
    klen = len(key)
    alen = len(alphabet)
    for i, c in enumerate(ct):
        if c in alphabet:
            ci = alphabet.index(c)
            ki = alphabet.index(key[i % klen])
            pi = (ci - ki) % alen
            pt.append(alphabet[pi])
        else:
            pt.append(c)
    return ''.join(pt)

def beaufort_decrypt(ct, key, alphabet=STANDARD_ALPHA):
    """Beaufort cipher decryption (symmetric): P = K - C mod 26."""
    pt = []
    klen = len(key)
    alen = len(alphabet)
    for i, c in enumerate(ct):
        if c in alphabet:
            ci = alphabet.index(c)
            ki = alphabet.index(key[i % klen])
            pi = (ki - ci) % alen
            pt.append(alphabet[pi])
        else:
            pt.append(c)
    return ''.join(pt)

def variant_beaufort_decrypt(ct, key, alphabet=STANDARD_ALPHA):
    """Variant Beaufort: P = C - K mod 26 (same as Vigenere encrypt direction)."""
    pt = []
    klen = len(key)
    alen = len(alphabet)
    for i, c in enumerate(ct):
        if c in alphabet:
            ci = alphabet.index(c)
            ki = alphabet.index(key[i % klen])
            pi = (ci + ki) % alen  # Vigenere encrypt = variant Beaufort decrypt
            pt.append(alphabet[pi])
        else:
            pt.append(c)
    return ''.join(pt)

def caesar_decrypt(ct, shift, alphabet=STANDARD_ALPHA):
    """Caesar shift decryption."""
    alen = len(alphabet)
    return ''.join(alphabet[(alphabet.index(c) - shift) % alen] if c in alphabet else c for c in ct)

def atbash(ct, alphabet=STANDARD_ALPHA):
    """Atbash substitution."""
    alen = len(alphabet)
    return ''.join(alphabet[alen - 1 - alphabet.index(c)] if c in alphabet else c for c in ct)

def derive_vigenere_key(ct, pt, alphabet=STANDARD_ALPHA):
    """Given ciphertext and plaintext, derive the Vigenere key stream."""
    alen = len(alphabet)
    key = []
    for c, p in zip(ct, pt):
        ci = alphabet.index(c)
        pi = alphabet.index(p)
        ki = (ci - pi) % alen
        key.append(alphabet[ki])
    return ''.join(key)

def derive_beaufort_key(ct, pt, alphabet=STANDARD_ALPHA):
    """Given ciphertext and plaintext, derive the Beaufort key stream. K = C + P mod 26."""
    alen = len(alphabet)
    key = []
    for c, p in zip(ct, pt):
        ci = alphabet.index(c)
        pi = alphabet.index(p)
        ki = (pi + ci) % alen
        key.append(alphabet[ki])
    return ''.join(key)

def find_repeating_key(keystream, max_period=None):
    """Check if a keystream has a repeating pattern."""
    n = len(keystream)
    if max_period is None:
        max_period = n
    results = []
    for period in range(1, min(max_period + 1, n)):
        match = True
        for i in range(n):
            if keystream[i] != keystream[i % period]:
                match = False
                break
        if match:
            results.append((period, keystream[:period]))
    return results

def find_english_words(text, min_len=3):
    """Find all English words that appear in text."""
    text = text.upper()
    found = []
    for wlen in range(min_len, len(text) + 1):
        for i in range(len(text) - wlen + 1):
            substr = text[i:i+wlen]
            if substr in DICTIONARY:
                found.append((i, substr))
    # deduplicate, prefer longer
    found.sort(key=lambda x: -len(x[1]))
    return found

def is_english_like(text, threshold=-2.5):
    """Quick check if text scores above threshold for English."""
    return quadgram_score(text) > threshold

# ============================================================
# PRINT HEADER
# ============================================================

print("=" * 90)
print("KRYPTOS K4 -- W-SEPARATOR HYPOTHESIS ANALYSIS")
print("=" * 90)
print()
print(f"K4 = {K4}")
print(f"Length: {len(K4)}")
print(f"W positions (0-indexed): {w_positions}")
print()

# Show segments
print("SEGMENTS (split on W):")
print("-" * 70)
pos = 0
seg_info = []
for i, seg in enumerate(segments):
    end = pos + len(seg)
    print(f"  Segment {i+1}: K4[{pos}:{end}] = {seg} ({len(seg)} chars)")
    seg_info.append((pos, end, seg))
    pos = end + 1  # +1 for the W separator (except after last)
print()

# ============================================================
# TEST 1: SEGMENT-LEVEL FREQUENCY ANALYSIS & IC
# ============================================================

print("=" * 90)
print("TEST 1: SEGMENT-LEVEL FREQUENCY ANALYSIS (IC)")
print("=" * 90)
print()
print(f"  English IC ~ 0.0667, Random ~ 0.0385")
print()

for i, seg in enumerate(segments):
    ic = index_of_coincidence(seg)
    freq = Counter(seg)
    most_common = freq.most_common(5)
    mc_str = ', '.join(f"{c}:{n}" for c, n in most_common)
    label = ""
    if ic > 0.060:
        label = " <-- ELEVATED (possible simple substitution)"
    elif ic > 0.050:
        label = " <-- MODERATE"
    print(f"  Segment {i+1} ({len(seg):2d} chars): IC = {ic:.4f}{label}")
    print(f"    Top letters: {mc_str}")
    print(f"    Text: {seg}")
    print()

# Also check IC of full K4 without W's
k4_no_w = K4.replace('W', '')
print(f"  Full K4 (no W's, {len(k4_no_w)} chars): IC = {index_of_coincidence(k4_no_w):.4f}")
print(f"  Full K4 (with W's, {len(K4)} chars): IC = {index_of_coincidence(K4):.4f}")
print()

# ============================================================
# TEST 2: CRIB-BASED KEY DERIVATION FOR SEGMENT 2
# ============================================================

print("=" * 90)
print("TEST 2: CRIB ANALYSIS -- SEGMENT 2 (EASTNORTHEAST)")
print("=" * 90)
print()

seg2 = segments[1]  # FLRVQQPRNGKSSOT (15 chars)
print(f"  Segment 2 ciphertext: {seg2} ({len(seg2)} chars)")
print(f"  Known crib: EASTNORTHEAST at segment positions 0-12 (13 chars)")
print(f"  Unknown: positions 13-14 (2 chars)")
print()

# Derive key stream for known portion
for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"  --- Using {alpha_name} alphabet ---")
    
    # Vigenere key derivation
    vig_keystream = derive_vigenere_key(seg2[:13], CRIB_ENE, alpha)
    print(f"  Vigenere keystream (13 chars):  {vig_keystream}")
    repeats_v = find_repeating_key(vig_keystream, 13)
    if repeats_v:
        print(f"    Repeating patterns found: {repeats_v}")
    else:
        print(f"    No clean repeating pattern in keystream")
    
    # Beaufort key derivation
    beau_keystream = derive_beaufort_key(seg2[:13], CRIB_ENE, alpha)
    print(f"  Beaufort keystream (13 chars):  {beau_keystream}")
    repeats_b = find_repeating_key(beau_keystream, 13)
    if repeats_b:
        print(f"    Repeating patterns found: {repeats_b}")
    else:
        print(f"    No clean repeating pattern in keystream")
    
    # Try all periods 1-13 for Vigenere
    print()
    print(f"  Testing all Vigenere key periods 1-13 for Segment 2 ({alpha_name}):")
    for period in range(1, 14):
        # Check if first 13 key chars are consistent with this period
        consistent = True
        key_candidate = list(vig_keystream[:period])
        for j in range(13):
            expected = key_candidate[j % period]
            if vig_keystream[j] != expected:
                consistent = False
                break
        if consistent:
            key_str = ''.join(key_candidate)
            # Decrypt remaining 2 chars
            remaining_ct = seg2[13:]
            remaining_pt = vigenere_decrypt(remaining_ct, key_str[13 % period:] if 13 % period < len(key_str) else key_str, alpha)
            # Actually, need to continue the key properly
            full_key_for_seg = ''.join(key_str[j % period] for j in range(len(seg2)))
            full_pt = vigenere_decrypt(seg2, full_key_for_seg, alpha)
            print(f"    Period {period:2d}: key={key_str:15s} => plaintext = {full_pt}")
            words = find_english_words(full_pt, 4)
            if words:
                wlist = [w for _, w in words[:5]]
                print(f"              Words found: {wlist}")
    
    # Try all periods 1-13 for Beaufort
    print()
    print(f"  Testing all Beaufort key periods 1-13 for Segment 2 ({alpha_name}):")
    for period in range(1, 14):
        consistent = True
        key_candidate = list(beau_keystream[:period])
        for j in range(13):
            expected = key_candidate[j % period]
            if beau_keystream[j] != expected:
                consistent = False
                break
        if consistent:
            key_str = ''.join(key_candidate)
            full_key_for_seg = ''.join(key_str[j % period] for j in range(len(seg2)))
            full_pt = beaufort_decrypt(seg2, full_key_for_seg, alpha)
            print(f"    Period {period:2d}: key={key_str:15s} => plaintext = {full_pt}")
            words = find_english_words(full_pt, 4)
            if words:
                wlist = [w for _, w in words[:5]]
                print(f"              Words found: {wlist}")
    print()

# ============================================================
# TEST 3: BRUTE FORCE THE 2 UNKNOWN CHARS IN SEGMENT 2
# ============================================================

print("=" * 90)
print("TEST 3: BRUTE FORCE LAST 2 CHARS OF SEGMENT 2 PLAINTEXT")
print("=" * 90)
print()
print("  If segment 2 plaintext = EASTNORTHEAST + 2 chars,")
print("  test all 676 possibilities for repeating key patterns.")
print()

seg2_ct = seg2
best_seg2_results = []

for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"  --- {alpha_name} alphabet ---")
    alen = len(alpha)
    
    for c1 in alpha:
        for c2 in alpha:
            plain_candidate = CRIB_ENE + c1 + c2
            assert len(plain_candidate) == 15 == len(seg2_ct)
            
            # Derive full keystream
            ks_vig = derive_vigenere_key(seg2_ct, plain_candidate, alpha)
            ks_beau = derive_beaufort_key(seg2_ct, plain_candidate, alpha)
            
            for ks_name, ks in [("Vig", ks_vig), ("Beau", ks_beau)]:
                # Check for repeating patterns with period 1-7
                for period in range(1, 8):
                    if period > 15:
                        break
                    is_repeat = True
                    for j in range(15):
                        if ks[j] != ks[j % period]:
                            is_repeat = False
                            break
                    if is_repeat:
                        best_seg2_results.append((
                            alpha_name, ks_name, period, ks[:period], 
                            plain_candidate, c1+c2
                        ))

    if best_seg2_results:
        print(f"  Results with repeating keys (period <= 7):")
        for alpha_n, cipher, period, key, pt, suffix in best_seg2_results:
            if alpha_n == alpha_name:
                print(f"    {cipher} period={period} key={key} => {pt} (suffix={suffix})")
    else:
        print(f"  No repeating keys found with period <= 7")
    print()

# ============================================================
# TEST 4: CRIB ANALYSIS -- SEGMENT 5 (BERLINCLOCK)
# ============================================================

print("=" * 90)
print("TEST 4: CRIB ANALYSIS -- SEGMENT 5 (BERLINCLOCK)")
print("=" * 90)
print()

seg5 = segments[4]  # INFBNYPVTTMZFPK (15 chars)
print(f"  Segment 5 ciphertext: {seg5} ({len(seg5)} chars)")
print(f"  Known crib: BERLINCLOCK at segment positions 4-14 (11 chars)")
print(f"  Unknown: positions 0-3 (4 chars before BERLINCLOCK)")
print()

# We know the plaintext at positions 4-14 is BERLINCLOCK
# Derive the key for those positions
for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"  --- Using {alpha_name} alphabet ---")
    alen = len(alpha)
    
    seg5_known_ct = seg5[4:15]   # 11 chars of ciphertext
    seg5_known_pt = CRIB_BC      # BERLINCLOCK (11 chars)
    
    vig_ks = derive_vigenere_key(seg5_known_ct, seg5_known_pt, alpha)
    beau_ks = derive_beaufort_key(seg5_known_ct, seg5_known_pt, alpha)
    
    print(f"  Vigenere keystream (positions 4-14): {vig_ks}")
    print(f"  Beaufort keystream (positions 4-14): {beau_ks}")
    
    # Check for repeating patterns
    for ks_name, ks in [("Vigenere", vig_ks), ("Beaufort", beau_ks)]:
        repeats = find_repeating_key(ks, 11)
        if repeats:
            print(f"    {ks_name} repeating patterns: {repeats}")
        
        # Try periods that would cover positions 0-3 too
        print(f"    {ks_name} -- testing periods 1-11:")
        for period in range(1, 12):
            # Check if ks (positions 4-14) is consistent with this period
            consistent = True
            # The key at position j in segment should be key[j % period]
            # We have key at positions 4..14
            key_slots = [None] * period
            for j in range(11):
                seg_pos = j + 4
                slot = seg_pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks[j]
                elif key_slots[slot] != ks[j]:
                    consistent = False
                    break
            
            if consistent:
                # Fill in unknown slots for positions 0-3
                unknown_slots = [s for s in range(period) if key_slots[s] is None]
                if not unknown_slots:
                    # All slots determined -- decrypt positions 0-3
                    full_key = ''.join(key_slots[j % period] for j in range(15))
                    full_pt = vigenere_decrypt(seg5, full_key, alpha) if ks_name == "Vigenere" else beaufort_decrypt(seg5, full_key, alpha)
                    print(f"      Period {period:2d}: key={''.join(k if k else '?' for k in key_slots):15s} => {full_pt}")
                    words = find_english_words(full_pt, 4)
                    if words:
                        print(f"                Words: {[w for _, w in words[:8]]}")
                else:
                    # Some slots unknown, enumerate
                    num_unknown = len(unknown_slots)
                    if num_unknown <= 3:  # feasible to enumerate
                        best_pt = []
                        for combo in itertools.product(alpha, repeat=num_unknown):
                            trial_key = list(key_slots)
                            for idx, s in enumerate(unknown_slots):
                                trial_key[s] = combo[idx]
                            full_key = ''.join(trial_key[j % period] for j in range(15))
                            if ks_name == "Vigenere":
                                pt = vigenere_decrypt(seg5, full_key, alpha)
                            else:
                                pt = beaufort_decrypt(seg5, full_key, alpha)
                            score = quadgram_score(pt)
                            best_pt.append((score, pt, ''.join(trial_key)))
                        best_pt.sort(reverse=True)
                        print(f"      Period {period:2d}: {num_unknown} unknown slot(s), top 5 results:")
                        for score, pt, key in best_pt[:5]:
                            print(f"        key={key:15s} => {pt}  (score={score:.3f})")
                            words = find_english_words(pt, 4)
                            if words:
                                print(f"          Words: {[w for _, w in words[:5]]}")
                    else:
                        print(f"      Period {period:2d}: {num_unknown} unknown slots (too many to enumerate)")
    print()

# ============================================================
# TEST 5: CROSS-SEGMENT KEY CONSISTENCY
# ============================================================

print("=" * 90)
print("TEST 5: CROSS-SEGMENT KEY CONSISTENCY (MASTER KEY HYPOTHESIS)")
print("=" * 90)
print()
print("  If all segments use the SAME repeating key, the key positions")
print("  would continue across W separators.")
print()

# Under this hypothesis, the W's are just separators removed before/after encryption.
# The ciphertext without W's would be encrypted with a single Vigenere key.
# The key positions for each segment would depend on whether W counts or not.

# Hypothesis A: W's are removed, key applies to concatenated text
k4_no_w = K4.replace('W', '')
print(f"  K4 without W's: {k4_no_w} ({len(k4_no_w)} chars)")
print()

# We know that in the concatenated text:
# positions 0-19 = segment 1
# positions 20-34 = segment 2 (EASTNORTHEAST at 20-32)
# positions 35-45 = segment 3
# positions 46-54 = segment 4
# positions 55-69 = segment 5 (BERLINCLOCK at 59-69)
# positions 70-91 = segment 6

# From segment 2: EASTNORTHEAST at concatenated positions 20-32
# From segment 5: BERLINCLOCK at concatenated positions 59-69

# Derive key at those positions
for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"  --- {alpha_name} alphabet ---")
    alen = len(alpha)
    
    # Key positions from ENE crib (positions 20-32 in concatenated text)
    ene_ct = k4_no_w[20:33]
    ene_pt = CRIB_ENE
    vig_ks_ene = derive_vigenere_key(ene_ct, ene_pt, alpha)
    beau_ks_ene = derive_beaufort_key(ene_ct, ene_pt, alpha)
    
    # Key positions from BC crib (positions 59-69 in concatenated text)
    bc_ct = k4_no_w[59:70]
    bc_pt = CRIB_BC
    vig_ks_bc = derive_vigenere_key(bc_ct, bc_pt, alpha)
    beau_ks_bc = derive_beaufort_key(bc_ct, bc_pt, alpha)
    
    print(f"  Vigenere ENE keystream (pos 20-32): {vig_ks_ene}")
    print(f"  Vigenere BC  keystream (pos 59-69): {vig_ks_bc}")
    print(f"  Beaufort ENE keystream (pos 20-32): {beau_ks_ene}")
    print(f"  Beaufort BC  keystream (pos 59-69): {beau_ks_bc}")
    print()
    
    # Test master key periods that are consistent with BOTH cribs
    print(f"  Testing master key periods 1-30 for consistency between cribs:")
    for period in range(1, 31):
        for cipher_name, ks_ene, ks_bc in [
            ("Vigenere", vig_ks_ene, vig_ks_bc),
            ("Beaufort", beau_ks_ene, beau_ks_bc)
        ]:
            # Build key constraints from ENE
            key_slots = [None] * period
            consistent = True
            for j in range(13):
                pos = 20 + j
                slot = pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks_ene[j]
                elif key_slots[slot] != ks_ene[j]:
                    consistent = False
                    break
            
            if not consistent:
                continue
            
            # Add constraints from BC
            for j in range(11):
                pos = 59 + j
                slot = pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks_bc[j]
                elif key_slots[slot] != ks_bc[j]:
                    consistent = False
                    break
            
            if consistent:
                known = sum(1 for s in key_slots if s is not None)
                key_display = ''.join(s if s else '?' for s in key_slots)
                unknowns = period - known
                print(f"    {cipher_name} period={period:2d}: key=[{key_display}] ({unknowns} unknown)")
                
                if unknowns == 0:
                    # Fully determined key -- decrypt everything
                    full_key = ''.join(key_slots[j % period] for j in range(len(k4_no_w)))
                    if cipher_name == "Vigenere":
                        pt = vigenere_decrypt(k4_no_w, full_key, alpha)
                    else:
                        pt = beaufort_decrypt(k4_no_w, full_key, alpha)
                    score = quadgram_score(pt)
                    print(f"      Plaintext: {pt}")
                    print(f"      Score: {score:.3f}")
                    words = find_english_words(pt, 5)
                    if words:
                        print(f"      Long words: {[w for _, w in words[:10]]}")
                elif unknowns <= 4:
                    # Enumerate unknown positions
                    unknown_slots = [s for s in range(period) if key_slots[s] is None]
                    print(f"      Enumerating {alen}^{unknowns} = {alen**unknowns} possibilities...")
                    best_results = []
                    for combo in itertools.product(alpha, repeat=unknowns):
                        trial_key = list(key_slots)
                        for idx, s in enumerate(unknown_slots):
                            trial_key[s] = combo[idx]
                        full_key = ''.join(trial_key[j % period] for j in range(len(k4_no_w)))
                        if cipher_name == "Vigenere":
                            pt = vigenere_decrypt(k4_no_w, full_key, alpha)
                        else:
                            pt = beaufort_decrypt(k4_no_w, full_key, alpha)
                        score = quadgram_score(pt)
                        if len(best_results) < 5 or score > best_results[-1][0]:
                            best_results.append((score, pt, ''.join(trial_key)))
                            best_results.sort(reverse=True)
                            best_results = best_results[:5]
                    
                    for score, pt, key in best_results:
                        print(f"      key={key} => {pt[:40]}...  (score={score:.3f})")
                        words = find_english_words(pt, 5)
                        if words:
                            print(f"        Words: {[w for _, w in words[:8]]}")
    print()

# ============================================================
# TEST 5b: Hypothesis B - W's count in key position
# ============================================================

print("  --- Hypothesis B: W's count as positions in the key ---")
print()

# Under this hypothesis, the key position advances even for W characters
# ENE is at K4 positions 21-33, BC at positions 63-73
for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"  --- {alpha_name} alphabet ---")
    alen = len(alpha)
    
    ene_ct = K4[21:34]  # should be same letters
    bc_ct = K4[63:74]
    
    vig_ks_ene = derive_vigenere_key(ene_ct, CRIB_ENE, alpha)
    vig_ks_bc = derive_vigenere_key(bc_ct, CRIB_BC, alpha)
    beau_ks_ene = derive_beaufort_key(ene_ct, CRIB_ENE, alpha)
    beau_ks_bc = derive_beaufort_key(bc_ct, CRIB_BC, alpha)
    
    print(f"  Vigenere ENE keystream (K4 pos 21-33): {vig_ks_ene}")
    print(f"  Vigenere BC  keystream (K4 pos 63-73): {vig_ks_bc}")
    print(f"  Beaufort ENE keystream (K4 pos 21-33): {beau_ks_ene}")
    print(f"  Beaufort BC  keystream (K4 pos 63-73): {beau_ks_bc}")
    print()
    
    print(f"  Testing master key periods 1-30 (W positions count):")
    for period in range(1, 31):
        for cipher_name, ks_ene, ks_bc in [
            ("Vigenere", vig_ks_ene, vig_ks_bc),
            ("Beaufort", beau_ks_ene, beau_ks_bc)
        ]:
            key_slots = [None] * period
            consistent = True
            for j in range(13):
                pos = 21 + j
                slot = pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks_ene[j]
                elif key_slots[slot] != ks_ene[j]:
                    consistent = False
                    break
            if not consistent:
                continue
            for j in range(11):
                pos = 63 + j
                slot = pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks_bc[j]
                elif key_slots[slot] != ks_bc[j]:
                    consistent = False
                    break
            if consistent:
                known = sum(1 for s in key_slots if s is not None)
                key_display = ''.join(s if s else '?' for s in key_slots)
                unknowns = period - known
                print(f"    {cipher_name} period={period:2d}: key=[{key_display}] ({unknowns} unknown)")
                
                if unknowns == 0:
                    # Decrypt full K4 (treating W as encrypted too)
                    full_key = ''.join(key_slots[j % period] for j in range(len(K4)))
                    if cipher_name == "Vigenere":
                        pt = vigenere_decrypt(K4, full_key, alpha)
                    else:
                        pt = beaufort_decrypt(K4, full_key, alpha)
                    score = quadgram_score(pt)
                    print(f"      Plaintext: {pt}")
                    print(f"      Score: {score:.3f}")
                elif unknowns <= 4:
                    unknown_slots = [s for s in range(period) if key_slots[s] is None]
                    print(f"      Enumerating {alen}^{unknowns} = {alen**unknowns} possibilities...")
                    best_results = []
                    for combo in itertools.product(alpha, repeat=unknowns):
                        trial_key = list(key_slots)
                        for idx, s in enumerate(unknown_slots):
                            trial_key[s] = combo[idx]
                        full_key = ''.join(trial_key[j % period] for j in range(len(K4)))
                        if cipher_name == "Vigenere":
                            pt = vigenere_decrypt(K4, full_key, alpha)
                        else:
                            pt = beaufort_decrypt(K4, full_key, alpha)
                        score = quadgram_score(pt)
                        if len(best_results) < 5 or score > best_results[-1][0]:
                            best_results.append((score, pt, ''.join(trial_key)))
                            best_results.sort(reverse=True)
                            best_results = best_results[:5]
                    for score, pt, key in best_results:
                        print(f"      key={key} => {pt[:50]}...  (score={score:.3f})")
    print()

# ============================================================
# TEST 6: INDEPENDENT SEGMENT CIPHER METHODS
# ============================================================

print("=" * 90)
print("TEST 6: INDEPENDENT CIPHER PER SEGMENT (Caesar, Atbash)")
print("=" * 90)
print()

for i, seg in enumerate(segments):
    print(f"  Segment {i+1}: {seg} ({len(seg)} chars)")
    
    # Caesar (all 26 shifts)
    best_caesar = []
    for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
        for shift in range(len(alpha)):
            pt = caesar_decrypt(seg, shift, alpha)
            score = quadgram_score(pt)
            best_caesar.append((score, pt, shift, alpha_name))
    best_caesar.sort(reverse=True)
    print(f"    Best Caesar:")
    for score, pt, shift, aname in best_caesar[:3]:
        print(f"      shift={shift:2d} ({aname}): {pt}  (score={score:.3f})")
    
    # Atbash
    for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
        pt = atbash(seg, alpha)
        score = quadgram_score(pt)
        print(f"    Atbash ({alpha_name}): {pt}  (score={score:.3f})")
    
    print()

# ============================================================
# TEST 7: SHORT VIGENERE KEYS PER SEGMENT (brute force periods 1-5)
# ============================================================

print("=" * 90)
print("TEST 7: SHORT VIGENERE KEYS PER SEGMENT (periods 1-5)")
print("=" * 90)
print()

for seg_idx, seg in enumerate(segments):
    print(f"  Segment {seg_idx+1}: {seg} ({len(seg)} chars)")
    best_for_seg = []
    
    for alpha_name, alpha in [("STD", STANDARD_ALPHA)]:
        alen = len(alpha)
        for period in range(1, min(6, len(seg))):
            # For period 1-3, brute force all keys
            if alen ** period > 500000:
                # Too many, skip or sample
                continue
            for key_tuple in itertools.product(range(alen), repeat=period):
                key = ''.join(alpha[k] for k in key_tuple)
                full_key = ''.join(key[j % period] for j in range(len(seg)))
                
                # Vigenere
                pt = vigenere_decrypt(seg, full_key, alpha)
                score = quadgram_score(pt)
                if len(best_for_seg) < 10 or score > best_for_seg[-1][0]:
                    best_for_seg.append((score, pt, f"Vig-{alpha_name}", key))
                    best_for_seg.sort(reverse=True)
                    best_for_seg = best_for_seg[:10]
                
                # Beaufort
                pt = beaufort_decrypt(seg, full_key, alpha)
                score = quadgram_score(pt)
                if len(best_for_seg) < 10 or score > best_for_seg[-1][0]:
                    best_for_seg.append((score, pt, f"Beau-{alpha_name}", key))
                    best_for_seg.sort(reverse=True)
                    best_for_seg = best_for_seg[:10]
    
    print(f"    Top 5 results:")
    for score, pt, method, key in best_for_seg[:5]:
        print(f"      {method} key={key}: {pt}  (score={score:.3f})")
        words = find_english_words(pt, 4)
        if words:
            print(f"        Words: {[w for _, w in words[:5]]}")
    print()

# ============================================================
# TEST 8: GENIE PLAINTEXT ALIGNMENT WITH W SEPARATORS
# ============================================================

print("=" * 90)
print("TEST 8: W POSITIONS AS WORD BOUNDARIES IN CANDIDATE PLAINTEXT")
print("=" * 90)
print()

# K4 positions where W appears: 20, 36, 48, 58, 74
# If W marks word boundaries in the plaintext, what words result?

# Test the community plaintext hypothesis
genie_clean = "TOSETTHEEASTNORTHEASTHOURBYBEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"
# Length check
print(f"  K4 length (no W's): {len(k4_no_w)} = {len(k4_no_w)}")
print(f"  Genie plaintext length: {len(genie_clean)}")
print()

# The W's split K4 into segments of lengths: 20, 15, 11, 9, 15, 22
# If those correspond to word groups:
seg_lens = [len(s) for s in segments]
print(f"  Segment lengths: {seg_lens}")
print(f"  Sum: {sum(seg_lens)} (should be {len(k4_no_w)})")
print()

# Split candidate plaintexts at same positions
print("  Splitting Genie plaintext at segment boundaries:")
pos = 0
for i, slen in enumerate(seg_lens):
    chunk = genie_clean[pos:pos+slen] if pos + slen <= len(genie_clean) else genie_clean[pos:]
    print(f"    Segment {i+1} ({slen:2d} chars): {chunk}")
    pos += slen
print()

# Also check: does the Genie plaintext have spaces/word boundaries at W positions?
# First, reconstruct with spaces
genie_spaced = "TO SET THE EASTNORTHEAST HOUR BY BEARING BERLINCLOCK DEGREES GRID POINT NORTHWEST TO FIND GROSSER STERN"
# What are the letter-only positions where spaces fall?
letter_pos = 0
space_at_letter_pos = []
for ch in genie_spaced:
    if ch == ' ':
        space_at_letter_pos.append(letter_pos)
    else:
        letter_pos += 1

print(f"  Word boundary positions in Genie spaced text: {space_at_letter_pos}")
print(f"  W positions in K4 (0-indexed): {w_positions}")
print(f"  W positions correspond to letter positions (in no-W text): ", end="")
# Each W at K4 position p corresponds to position p - (number of W's before p) in the no-W text
w_as_letterpos = []
for wp in w_positions:
    # count W's before this position
    n_w_before = sum(1 for w in w_positions if w < wp)
    w_as_letterpos.append(wp - n_w_before)
print(w_as_letterpos)
print()

# Check overlap
overlap = set(space_at_letter_pos) & set(w_as_letterpos)
print(f"  Overlap between word boundaries and W positions: {overlap}")
print()

# ============================================================
# TEST 9: W's THEMSELVES ENCODE SOMETHING
# ============================================================

print("=" * 90)
print("TEST 9: DO THE W's ENCODE SOMETHING?")
print("=" * 90)
print()

print(f"  W positions in K4: {w_positions}")
print(f"  Differences between W positions: {[w_positions[i+1] - w_positions[i] for i in range(len(w_positions)-1)]}")
print(f"  Segment lengths: {seg_lens}")
print()

# Check if W positions mod 26 spell something
print(f"  W positions mod 26: {[p % 26 for p in w_positions]}")
print(f"  As letters (A=0): {''.join(STANDARD_ALPHA[p % 26] for p in w_positions)}")
print(f"  As letters (A=1): {''.join(STANDARD_ALPHA[(p-1) % 26] for p in w_positions)}")
print()

# Segment lengths as letters
print(f"  Segment lengths: {seg_lens}")
print(f"  As letters (A=1): {''.join(STANDARD_ALPHA[n-1] for n in seg_lens)}")
print()

# Differences
diffs = [w_positions[i+1] - w_positions[i] for i in range(len(w_positions)-1)]
print(f"  Inter-W distances: {diffs}")
print(f"  As letters (A=1): {''.join(STANDARD_ALPHA[d-1] for d in diffs)}")
print()

# ============================================================
# TEST 10: SEGMENT-SPECIFIC VIGENERE WITH KRYPTOS-THEMED KEYS
# ============================================================

print("=" * 90)
print("TEST 10: THEMED KEYS PER SEGMENT")
print("=" * 90)
print()

themed_keys = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "CLOCK", "BERLIN", "NORTH",
    "EAST", "WEST", "SOUTH", "COMPASS", "DEGREE", "GRID", "POINT",
    "STERN", "TIME", "HOUR", "BEARING", "SANBORN", "CIA", "LANGLEY",
    "SHADOW", "ENIGMA", "LUCID", "DYAD", "NYPVTT", "GROSS",
    "NORTHWEST", "NORTHEAST", "SOUTHEAST", "SOUTHWEST",
    "GROSSERSTERN", "SOS", "KEY", "LIGHT", "DARK", "TRUTH",
    "HIDDEN", "SECRET", "MORSE", "CODE", "CIPHER", "VIGENERE",
    "BEAUFORT", "IQLUSION", "ILLUSION", "UNDERGRUUND", "UNDERGROUND",
    "VIRTUALLY", "INVISIBLE", "BURIED",
]

for seg_idx, seg in enumerate(segments):
    print(f"  Segment {seg_idx+1}: {seg} ({len(seg)} chars)")
    best_themed = []
    
    for key in themed_keys:
        for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
            for cipher_name, decrypt_fn in [("Vig", vigenere_decrypt), ("Beau", beaufort_decrypt)]:
                pt = decrypt_fn(seg, key, alpha)
                score = quadgram_score(pt)
                if len(best_themed) < 5 or score > best_themed[-1][0]:
                    best_themed.append((score, pt, cipher_name, alpha_name, key))
                    best_themed.sort(reverse=True)
                    best_themed = best_themed[:5]
    
    print(f"    Top 3 themed results:")
    for score, pt, cipher, aname, key in best_themed[:3]:
        print(f"      {cipher}-{aname} key={key}: {pt}  (score={score:.3f})")
        words = find_english_words(pt, 4)
        if words:
            print(f"        Words: {[w for _, w in words[:5]]}")
    print()

# ============================================================
# TEST 11: AUTOKEY CIPHER PER SEGMENT
# ============================================================

print("=" * 90)
print("TEST 11: AUTOKEY VIGENERE PER SEGMENT")
print("=" * 90)
print()

def autokey_vigenere_decrypt(ct, primer, alphabet=STANDARD_ALPHA):
    """Autokey Vigenere: key = primer + plaintext."""
    alen = len(alphabet)
    pt = []
    key_stream = list(primer)
    for i, c in enumerate(ct):
        ci = alphabet.index(c)
        ki = alphabet.index(key_stream[i])
        pi = (ci - ki) % alen
        p = alphabet[pi]
        pt.append(p)
        key_stream.append(p)
    return ''.join(pt)

def autokey_beaufort_decrypt(ct, primer, alphabet=STANDARD_ALPHA):
    """Autokey Beaufort: key = primer + plaintext, P = K - C."""
    alen = len(alphabet)
    pt = []
    key_stream = list(primer)
    for i, c in enumerate(ct):
        ci = alphabet.index(c)
        ki = alphabet.index(key_stream[i])
        pi = (ki - ci) % alen
        p = alphabet[pi]
        pt.append(p)
        key_stream.append(p)
    return ''.join(pt)

# Test autokey with short primers on each segment
for seg_idx, seg in enumerate(segments):
    if len(seg) < 6:
        continue
    print(f"  Segment {seg_idx+1}: {seg} ({len(seg)} chars)")
    best_autokey = []
    
    for alpha_name, alpha in [("STD", STANDARD_ALPHA)]:
        alen = len(alpha)
        # Primers of length 1-3
        for plen in range(1, 4):
            if alen ** plen > 20000:
                continue
            for primer_tuple in itertools.product(range(alen), repeat=plen):
                primer = ''.join(alpha[k] for k in primer_tuple)
                
                pt = autokey_vigenere_decrypt(seg, primer, alpha)
                score = quadgram_score(pt)
                if len(best_autokey) < 5 or score > best_autokey[-1][0]:
                    best_autokey.append((score, pt, f"AKVig-{alpha_name}", primer))
                    best_autokey.sort(reverse=True)
                    best_autokey = best_autokey[:5]
                
                pt = autokey_beaufort_decrypt(seg, primer, alpha)
                score = quadgram_score(pt)
                if len(best_autokey) < 5 or score > best_autokey[-1][0]:
                    best_autokey.append((score, pt, f"AKBeau-{alpha_name}", primer))
                    best_autokey.sort(reverse=True)
                    best_autokey = best_autokey[:5]
    
    print(f"    Top 3 autokey results:")
    for score, pt, method, primer in best_autokey[:3]:
        print(f"      {method} primer={primer}: {pt}  (score={score:.3f})")
        words = find_english_words(pt, 4)
        if words:
            print(f"        Words: {[w for _, w in words[:5]]}")
    print()

# ============================================================
# TEST 12: SEGMENT 2 DETAILED -- What 2-char suffix makes English?
# ============================================================

print("=" * 90)
print("TEST 12: SEGMENT 2 -- BEST PLAINTEXT COMPLETIONS (EASTNORTHEAST + ??)")
print("=" * 90)
print()

seg2 = segments[1]
print(f"  Segment 2 CT: {seg2}")
print(f"  If PT starts with EASTNORTHEAST, what are the last 2 chars?")
print()

# For each alphabet and cipher, derive key from first 13, 
# then try all 676 suffixes and score the full key for regularity

best_completions = []

for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
    alen = len(alpha)
    
    for c1_idx in range(alen):
        for c2_idx in range(alen):
            c1, c2 = alpha[c1_idx], alpha[c2_idx]
            plain15 = CRIB_ENE + c1 + c2
            
            # Vigenere key
            ks = derive_vigenere_key(seg2, plain15, alpha)
            
            # Score the keystream for patterns
            # Check: is it a short repeating key?
            for period in range(1, 8):
                is_periodic = all(ks[j] == ks[j % period] for j in range(15))
                if is_periodic:
                    best_completions.append((
                        period, "Vig", alpha_name, ks[:period], plain15, c1+c2
                    ))
            
            # Also check Beaufort
            ks = derive_beaufort_key(seg2, plain15, alpha)
            for period in range(1, 8):
                is_periodic = all(ks[j] == ks[j % period] for j in range(15))
                if is_periodic:
                    best_completions.append((
                        period, "Beau", alpha_name, ks[:period], plain15, c1+c2
                    ))

if best_completions:
    best_completions.sort(key=lambda x: x[0])  # sort by period
    print(f"  Found {len(best_completions)} completions with repeating keys (period <= 7):")
    for period, cipher, aname, key, pt, suffix in best_completions:
        # Check if this key, applied to other segments, produces English
        print(f"    {cipher}-{aname} period={period} key={key} => EASTNORTHEAST{suffix}")
        
        # Apply this key to all other segments
        for si, seg in enumerate(segments):
            if si == 1:
                continue  # skip segment 2 itself
            full_key = ''.join(key[j % period] for j in range(len(seg)))
            if cipher == "Vig":
                spt = vigenere_decrypt(seg, full_key, STANDARD_ALPHA if aname == "STD" else KRYPTOS_ALPHA)
            else:
                spt = beaufort_decrypt(seg, full_key, STANDARD_ALPHA if aname == "STD" else KRYPTOS_ALPHA)
            sc = quadgram_score(spt)
            words = find_english_words(spt, 4)
            wstr = f" words={[w for _, w in words[:3]]}" if words else ""
            print(f"      Seg{si+1}: {spt} (score={sc:.3f}){wstr}")
else:
    print("  No completions found with short repeating keys.")
    print("  Trying: best suffix by quadgram score of full 15-char plaintext:")
    best_by_score = []
    for alpha_name, alpha in [("STD", STANDARD_ALPHA)]:
        alen = len(alpha)
        for c1_idx in range(alen):
            for c2_idx in range(alen):
                c1, c2 = alpha[c1_idx], alpha[c2_idx]
                plain15 = CRIB_ENE + c1 + c2
                score = quadgram_score(plain15)
                best_by_score.append((score, plain15, c1+c2))
    best_by_score.sort(reverse=True)
    print(f"  Top 10 by English score of EASTNORTHEAST+XX:")
    for score, pt, suffix in best_by_score[:10]:
        print(f"    {pt} (suffix={suffix}, score={score:.3f})")

print()

# ============================================================
# TEST 13: SEGMENT 5 DETAILED -- What 4-char prefix precedes BERLINCLOCK?
# ============================================================

print("=" * 90)
print("TEST 13: SEGMENT 5 -- BEST PLAINTEXT COMPLETIONS (???? + BERLINCLOCK)")
print("=" * 90)
print()

seg5 = segments[4]
print(f"  Segment 5 CT: {seg5}")
print(f"  If PT has BERLINCLOCK at positions 4-14, what are the first 4 chars?")
print()

best_seg5_completions = []

for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
    alen = len(alpha)
    
    for prefix_tuple in itertools.product(range(alen), repeat=4):
        prefix = ''.join(alpha[k] for k in prefix_tuple)
        plain15 = prefix + CRIB_BC
        
        # Vigenere
        ks = derive_vigenere_key(seg5, plain15, alpha)
        for period in range(1, 8):
            is_periodic = all(ks[j] == ks[j % period] for j in range(15))
            if is_periodic:
                best_seg5_completions.append((
                    period, "Vig", alpha_name, ks[:period], plain15, prefix
                ))
        
        # Beaufort
        ks = derive_beaufort_key(seg5, plain15, alpha)
        for period in range(1, 8):
            is_periodic = all(ks[j] == ks[j % period] for j in range(15))
            if is_periodic:
                best_seg5_completions.append((
                    period, "Beau", alpha_name, ks[:period], plain15, prefix
                ))

if best_seg5_completions:
    best_seg5_completions.sort(key=lambda x: x[0])
    print(f"  Found {len(best_seg5_completions)} completions with repeating keys (period <= 7):")
    for period, cipher, aname, key, pt, prefix in best_seg5_completions[:30]:
        alph = STANDARD_ALPHA if aname == "STD" else KRYPTOS_ALPHA
        print(f"    {cipher}-{aname} period={period} key={key} => {prefix}BERLINCLOCK")
        
        # Apply this key to segment 2 -- does it produce EASTNORTHEAST?
        seg2_key = ''.join(key[j % period] for j in range(len(segments[1])))
        if cipher == "Vig":
            seg2_pt = vigenere_decrypt(segments[1], seg2_key, alph)
        else:
            seg2_pt = beaufort_decrypt(segments[1], seg2_key, alph)
        
        ene_match = "YES!" if seg2_pt[:13] == CRIB_ENE else "no"
        score2 = quadgram_score(seg2_pt)
        print(f"      Seg2: {seg2_pt} (ENE match: {ene_match}, score={score2:.3f})")
        
        if ene_match == "YES!":
            print(f"      *** CROSS-VALIDATION SUCCESS: Same key produces both cribs! ***")
            # Decrypt all segments
            for si, seg in enumerate(segments):
                full_key = ''.join(key[j % period] for j in range(len(seg)))
                if cipher == "Vig":
                    spt = vigenere_decrypt(seg, full_key, alph)
                else:
                    spt = beaufort_decrypt(seg, full_key, alph)
                sc = quadgram_score(spt)
                print(f"      Seg{si+1}: {spt} (score={sc:.3f})")
else:
    print("  No completions with short repeating keys found.")

print()

# ============================================================
# TEST 14: CROSS-SEGMENT KEY MATCHING (same short key for seg 2 and 5)
# ============================================================

print("=" * 90)
print("TEST 14: SAME KEY FOR SEGMENTS 2 AND 5 (cross-crib validation)")
print("=" * 90)
print()

# For segment 2, we know 13/15 chars of plaintext
# For segment 5, we know 11/15 chars of plaintext
# If both use the same key, the key must be consistent

for alpha_name, alpha in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
    alen = len(alpha)
    print(f"  --- {alpha_name} alphabet ---")
    
    for cipher_name in ["Vigenere", "Beaufort"]:
        # Derive partial keystreams
        if cipher_name == "Vigenere":
            ks2 = derive_vigenere_key(segments[1][:13], CRIB_ENE, alpha)  # seg2 pos 0-12
            ks5 = derive_vigenere_key(segments[4][4:15], CRIB_BC, alpha)  # seg5 pos 4-14
        else:
            ks2 = derive_beaufort_key(segments[1][:13], CRIB_ENE, alpha)
            ks5 = derive_beaufort_key(segments[4][4:15], CRIB_BC, alpha)
        
        print(f"  {cipher_name}:")
        print(f"    Seg2 keystream (pos 0-12): {ks2}")
        print(f"    Seg5 keystream (pos 4-14): {ks5}")
        
        # For each period, check consistency
        for period in range(1, 16):
            key_slots = [None] * period
            consistent = True
            
            # Constraints from seg2 (positions 0-12)
            for j in range(13):
                slot = j % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks2[j]
                elif key_slots[slot] != ks2[j]:
                    consistent = False
                    break
            
            if not consistent:
                continue
            
            # Constraints from seg5 (positions 4-14)
            for j in range(11):
                seg5_pos = j + 4
                slot = seg5_pos % period
                if key_slots[slot] is None:
                    key_slots[slot] = ks5[j]
                elif key_slots[slot] != ks5[j]:
                    consistent = False
                    break
            
            if consistent:
                key_display = ''.join(s if s else '?' for s in key_slots)
                unknowns = sum(1 for s in key_slots if s is None)
                print(f"    Period {period:2d}: key=[{key_display}] ({unknowns} unknown)")
                
                if unknowns <= 3:
                    unknown_slots = [s for s in range(period) if key_slots[s] is None]
                    best = []
                    
                    for combo in itertools.product(alpha, repeat=unknowns) if unknowns > 0 else [()]:
                        trial_key = list(key_slots)
                        for idx, s in enumerate(unknown_slots):
                            trial_key[s] = combo[idx]
                        key_str = ''.join(trial_key)
                        
                        # Decrypt all 6 segments
                        all_pt = []
                        total_score = 0
                        for si, seg in enumerate(segments):
                            fk = ''.join(key_str[j % period] for j in range(len(seg)))
                            if cipher_name == "Vigenere":
                                pt = vigenere_decrypt(seg, fk, alpha)
                            else:
                                pt = beaufort_decrypt(seg, fk, alpha)
                            all_pt.append(pt)
                            total_score += quadgram_score(pt) * len(pt)
                        
                        avg_score = total_score / sum(len(s) for s in segments)
                        if len(best) < 3 or avg_score > best[-1][0]:
                            best.append((avg_score, all_pt, key_str))
                            best.sort(reverse=True)
                            best = best[:3]
                    
                    for avg_score, all_pt, key_str in best[:2]:
                        print(f"      key={key_str} (avg score={avg_score:.3f})")
                        for si, pt in enumerate(all_pt):
                            sc = quadgram_score(pt)
                            words = find_english_words(pt, 4)
                            wstr = f" {[w for _, w in words[:3]]}" if words else ""
                            print(f"        Seg{si+1}: {pt} ({sc:.3f}){wstr}")
        print()

# ============================================================
# TEST 15: COMPREHENSIVE SUMMARY
# ============================================================

print("=" * 90)
print("COMPREHENSIVE SUMMARY")
print("=" * 90)
print()
print("K4 split into 6 segments by W separators:")
for i, seg in enumerate(segments):
    ic = index_of_coincidence(seg)
    print(f"  Seg{i+1}: {seg:25s} (len={len(seg):2d}, IC={ic:.4f})")
print()
print("Key observations from all tests above:")
print("  1. Check which segments have elevated IC (closer to 0.067)")
print("  2. Check which cross-segment key periods are consistent with both cribs")
print("  3. Check if any single short key decrypts multiple segments to English")
print("  4. Check if Genie plaintext word boundaries align with W positions")
print()

# Final special test: what if each segment uses a key that starts at a different
# position within a longer master key?
print("=" * 90)
print("TEST 16: MASTER KEY WITH SEGMENT-SPECIFIC OFFSETS")
print("=" * 90)
print()
print("  If a master key of length L is used, but each segment starts")
print("  at a different offset into the key, can we find L and offsets?")
print()

# With cribs, we know:
# Seg2 key positions 0-12 (from ENE)
# Seg5 key positions 4-14 (from BC)
# If both are windows into the same master key at different offsets,
# there might be an offset difference that makes them overlap

for alpha_name, alpha in [("STD", STANDARD_ALPHA)]:
    for cipher_name in ["Vigenere", "Beaufort"]:
        if cipher_name == "Vigenere":
            ks2 = derive_vigenere_key(segments[1][:13], CRIB_ENE, alpha)
            ks5 = derive_vigenere_key(segments[4][4:15], CRIB_BC, alpha)
        else:
            ks2 = derive_beaufort_key(segments[1][:13], CRIB_ENE, alpha)
            ks5 = derive_beaufort_key(segments[4][4:15], CRIB_BC, alpha)
        
        print(f"  {cipher_name} ({alpha_name}):")
        print(f"    Seg2 keystream [0:13]: {ks2}")
        print(f"    Seg5 keystream [4:15]: {ks5}")
        
        # Try all relative offsets: seg5 key position 4 = seg2 key position (4 + offset) 
        # i.e., ks5[j] should equal ks2[j + offset] for some offset
        # Or more generally, if master key position for seg2[i] = i + off2
        # and master key position for seg5[i] = i + off5
        # then ks2[i] and ks5[j] should match when (i + off2) = (j + off5) mod L
        
        # Simple check: overlap in keystreams
        # ks2 covers master positions off2..off2+12
        # ks5 covers master positions off5+4..off5+14
        # Try off5 - off2 from -20 to +20
        print(f"    Checking relative offsets (seg5_start - seg2_start) = delta:")
        
        for delta in range(-20, 21):
            # Seg2 positions 0..12 map to master key positions 0..12
            # Seg5 positions 4..14 map to master key positions 4+delta..14+delta
            # Check overlap
            overlap_matches = 0
            overlap_total = 0
            for j2 in range(13):  # seg2 positions
                mk_pos = j2  # master key position (relative to seg2 start)
                # seg5 position that maps to same master key position
                j5 = mk_pos - delta  # seg5[j5] maps to master pos j5 + delta
                if 4 <= j5 <= 14:
                    overlap_total += 1
                    if ks2[j2] == ks5[j5 - 4]:  # ks5 is indexed from 0 (= seg5 pos 4)
                        overlap_matches += 1
            
            if overlap_total > 0 and overlap_matches == overlap_total:
                print(f"      delta={delta:+3d}: PERFECT match on {overlap_total} overlapping positions")
                # Reconstruct combined keystream
                # seg2 covers master positions 0..12
                # seg5 covers master positions delta+4..delta+14
                min_pos = min(0, delta + 4)
                max_pos = max(12, delta + 14)
                master_ks = {}
                for j in range(13):
                    master_ks[j] = ks2[j]
                for j in range(11):
                    master_ks[delta + 4 + j] = ks5[j]
                
                mk_display = []
                for p in range(min_pos, max_pos + 1):
                    if p in master_ks:
                        mk_display.append(master_ks[p])
                    else:
                        mk_display.append('?')
                print(f"        Master key positions {min_pos}..{max_pos}: {''.join(mk_display)}")
                
                # Check for periodicity
                mk_list = [(p, master_ks[p]) for p in sorted(master_ks.keys())]
                for period in range(1, max_pos - min_pos + 2):
                    periodic = True
                    for p, v in mk_list:
                        if (p % period) in {pp % period: vv for pp, vv in mk_list}:
                            expected = {pp % period: vv for pp, vv in mk_list}.get(p % period)
                            if expected and expected != v:
                                periodic = False
                                break
                    if periodic:
                        # Build key
                        key_build = [None] * period
                        for p, v in mk_list:
                            if key_build[p % period] is None:
                                key_build[p % period] = v
                            elif key_build[p % period] != v:
                                periodic = False
                                break
                        if periodic:
                            unknowns = sum(1 for x in key_build if x is None)
                            kd = ''.join(x if x else '?' for x in key_build)
                            if unknowns <= 4:
                                print(f"        Period {period}: [{kd}] ({unknowns} unknown)")
                                break  # show only shortest period
            elif overlap_total > 2 and overlap_matches > overlap_total * 0.8:
                print(f"      delta={delta:+3d}: {overlap_matches}/{overlap_total} positions match")
        
        print()

print()
print("=" * 90)
print("ANALYSIS COMPLETE")
print("=" * 90)
