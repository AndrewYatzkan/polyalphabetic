#!/usr/bin/env python3
"""
Comprehensive Gromark cipher analysis for Kryptos K4.

The Gromark (GROnsfeld with Mixed Alphabet and Running Key) cipher:
1. Uses a mixed/keyed alphabet for letter-to-number and number-to-letter mapping
2. Has a numeric "primer" (initial key digits, each 0-9)
3. Running key generation: each new digit = sum of two previous digits mod 10 (Fibonacci-style)
4. Each plaintext letter is shifted by the current key digit (0-9 only)

This script tests:
- Multiple alphabet constructions (KRYPTOS, standard, PALIMPSEST, ABSCISSA, BERLINCLOCK keywords)
- Brute-force primers of length 2-4
- Hill-climbing/SA for primers of length 5-8
- Crib verification (BERLINCLOCK at 63-73, EASTNORTHEAST at 21-33)
- Vigenere-Gromark connection hypothesis
- Special primers from known values (29, coordinates, Berlin Clock, etc.)
"""

import itertools
import math
import random
import sys
import time
from collections import defaultdict

# ============================================================================
# CONSTANTS
# ============================================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4)  # 97

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA  = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Known cribs
CRIB_BERLIN = ("BERLINCLOCK", 63, 74)    # positions 63-73 inclusive = 11 chars
CRIB_ENE    = ("EASTNORTHEAST", 21, 34)  # positions 21-33 inclusive = 13 chars

# Vigenere key (period 29) - known portion
VIG_KEY_KNOWN = "OYNKYELYOIECBAQK?????RDUMRIYW"  # ? = unknown positions 16-20

QUADGRAM_FILE = "/home/user/polyalphabetic/english_quadgrams.txt"

# ============================================================================
# ALPHABET GENERATION
# ============================================================================

def keyed_alphabet(keyword, base=STANDARD_ALPHA):
    """Generate a keyed alphabet: keyword letters first (deduplicated), then remaining."""
    seen = set()
    result = []
    for ch in keyword.upper():
        if ch in base and ch not in seen:
            seen.add(ch)
            result.append(ch)
    for ch in base:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return ''.join(result)

def build_alphabets():
    """Build all alphabet variants to test."""
    alphabets = {}
    alphabets['STANDARD'] = STANDARD_ALPHA
    alphabets['KRYPTOS'] = KRYPTOS_ALPHA
    alphabets['PALIMPSEST'] = keyed_alphabet("PALIMPSEST")
    alphabets['ABSCISSA'] = keyed_alphabet("ABSCISSA")
    alphabets['BERLINCLOCK'] = keyed_alphabet("BERLINCLOCK")
    alphabets['KRYPTOS_STD'] = keyed_alphabet("KRYPTOS")  # KRYPTOS keyword on standard base
    alphabets['SANBORN'] = keyed_alphabet("SANBORN")
    return alphabets

# ============================================================================
# QUADGRAM SCORING
# ============================================================================

class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        self.floor = 0
        self._load(filepath)

    def _load(self, filepath):
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    quad, count = parts[0], int(parts[1])
                    self.quadgrams[quad] = count
                    self.total += count
        # Convert to log probabilities
        self.log_quadgrams = {}
        for quad, count in self.quadgrams.items():
            self.log_quadgrams[quad] = math.log10(count / self.total)
        self.floor = math.log10(0.01 / self.total)

    def score(self, text):
        """Score text using quadgram log probabilities."""
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            quad = text[i:i+4]
            s += self.log_quadgrams.get(quad, self.floor)
        return s

    def score_per_char(self, text):
        """Normalized score per character."""
        if len(text) < 4:
            return self.floor
        return self.score(text) / (len(text) - 3)

# ============================================================================
# GROMARK CIPHER IMPLEMENTATION
# ============================================================================

def generate_running_key(primer_digits, length):
    """
    Generate Gromark running key from primer digits.
    Each new digit = (digit[i-1] + digit[i-2]) mod 10
    This is the standard Gromark lagged Fibonacci with lag (1,2).
    """
    key = list(primer_digits)
    while len(key) < length:
        new_digit = (key[-1] + key[-2]) % 10
        key.append(new_digit)
    return key[:length]

def generate_running_key_general(primer_digits, length, lag1=1, lag2=2):
    """
    Generate running key with general lags.
    digit[i] = (digit[i-lag1] + digit[i-lag2]) mod 10
    """
    key = list(primer_digits)
    while len(key) < length:
        idx = len(key)
        if idx - lag1 >= 0 and idx - lag2 >= 0:
            new_digit = (key[idx - lag1] + key[idx - lag2]) % 10
            key.append(new_digit)
        else:
            break
    return key[:length] if len(key) >= length else key

def gromark_encrypt(plaintext, primer_digits, alphabet):
    """
    Encrypt plaintext using Gromark cipher.
    - alphabet: the mixed alphabet (26 chars)
    - primer_digits: list of digits 0-9
    - Each PT letter -> find position in alphabet -> add key digit mod len(alphabet) -> CT letter
    """
    alpha_len = len(alphabet)
    key = generate_running_key(primer_digits, len(plaintext))
    ciphertext = []
    for i, ch in enumerate(plaintext.upper()):
        if ch in alphabet:
            pos = alphabet.index(ch)
            new_pos = (pos + key[i]) % alpha_len
            ciphertext.append(alphabet[new_pos])
        else:
            ciphertext.append(ch)
    return ''.join(ciphertext)

def gromark_decrypt(ciphertext, primer_digits, alphabet):
    """
    Decrypt ciphertext using Gromark cipher.
    - Find CT letter position in alphabet
    - Subtract key digit mod len(alphabet)
    - Result is PT letter
    """
    alpha_len = len(alphabet)
    key = generate_running_key(primer_digits, len(ciphertext))
    plaintext = []
    for i, ch in enumerate(ciphertext.upper()):
        if ch in alphabet:
            pos = alphabet.index(ch)
            new_pos = (pos - key[i]) % alpha_len
            plaintext.append(alphabet[new_pos])
        else:
            plaintext.append(ch)
    return ''.join(plaintext)

def gromark_decrypt_general(ciphertext, primer_digits, alphabet, lag1=1, lag2=2):
    """Decrypt with general lag parameters."""
    alpha_len = len(alphabet)
    key = generate_running_key_general(primer_digits, len(ciphertext), lag1, lag2)
    if len(key) < len(ciphertext):
        return None
    plaintext = []
    for i, ch in enumerate(ciphertext.upper()):
        if ch in alphabet:
            pos = alphabet.index(ch)
            new_pos = (pos - key[i]) % alpha_len
            plaintext.append(alphabet[new_pos])
        else:
            plaintext.append(ch)
    return ''.join(plaintext)

# ============================================================================
# CRIB-BASED PRIMER EXTRACTION
# ============================================================================

def extract_key_from_crib(ciphertext_segment, plaintext_crib, alphabet):
    """
    Given a CT segment and known PT, extract the key digits needed.
    key[i] = (CT_pos - PT_pos) mod alpha_len
    Returns list of required key digits, or None if impossible (digit > 9).
    """
    alpha_len = len(alphabet)
    digits = []
    for ct_ch, pt_ch in zip(ciphertext_segment, plaintext_crib):
        if ct_ch not in alphabet or pt_ch not in alphabet:
            return None
        ct_pos = alphabet.index(ct_ch)
        pt_pos = alphabet.index(pt_ch)
        d = (ct_pos - pt_pos) % alpha_len
        if d > 9:
            return None  # Gromark only uses digits 0-9
        digits.append(d)
    return digits

def reverse_engineer_primer_from_crib(ciphertext, crib_text, crib_start, alphabet, max_primer_len=8):
    """
    Given a crib at a known position, reverse-engineer possible primers.

    1. Extract key digits at crib positions
    2. Use Fibonacci relation to work backwards to find the primer
    """
    ct_segment = ciphertext[crib_start:crib_start + len(crib_text)]
    key_digits = extract_key_from_crib(ct_segment, crib_text, alphabet)

    if key_digits is None:
        return None, None

    # Now we have key digits at positions [crib_start, crib_start + len(crib_text) - 1]
    # Standard: key[i] = (key[i-1] + key[i-2]) mod 10
    # Backward: key[i-2] = (key[i] - key[i-1]) mod 10

    # Start with known digits and propagate backward
    backward = list(key_digits)
    for _ in range(crib_start):
        if len(backward) >= 2:
            prev = (backward[0] - backward[1]) % 10
            backward.insert(0, prev)

    return key_digits, backward

# ============================================================================
# BRUTE FORCE SEARCH (SHORT PRIMERS)
# ============================================================================

def brute_force_primers(ciphertext, alphabet, alpha_name, primer_length, scorer,
                        top_n=20, check_cribs=True, verbose=True):
    """
    Brute force all primer combinations of given length (digits 0-9).
    """
    total = 10 ** primer_length
    if verbose:
        print(f"\n{'='*70}")
        print(f"Brute force: primer_len={primer_length}, alphabet={alpha_name}, combos={total}")
        print(f"{'='*70}")

    best_results = []
    crib_matches = []
    count = 0
    start_time = time.time()

    for combo in itertools.product(range(10), repeat=primer_length):
        primer = list(combo)
        pt = gromark_decrypt(ciphertext, primer, alphabet)
        score = scorer.score(pt)

        # Track best
        if len(best_results) < top_n or score > best_results[-1][0]:
            best_results.append((score, primer, pt))
            best_results.sort(key=lambda x: x[0], reverse=True)
            best_results = best_results[:top_n]

        # Check cribs
        if check_cribs:
            bc_match = pt[63:74] == "BERLINCLOCK"
            ene_match = pt[21:34] == "EASTNORTHEAST"
            if bc_match or ene_match:
                crib_matches.append((primer, pt, bc_match, ene_match))

        count += 1
        if verbose and count % 200000 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            print(f"  Progress: {count}/{total} ({100*count/total:.1f}%) - {rate:.0f}/sec - best={best_results[0][0]:.2f}")

    elapsed = time.time() - start_time

    if verbose:
        print(f"\n  Completed in {elapsed:.1f}s")
        print(f"  Top {min(5, len(best_results))} results:")
        for i, (score, primer, pt) in enumerate(best_results[:5]):
            print(f"    #{i+1}: primer={primer} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")
            print(f"          PT[21:34]={pt[21:34]}  PT[63:74]={pt[63:74]}")

        if crib_matches:
            print(f"\n  *** CRIB MATCHES FOUND: {len(crib_matches)} ***")
            for primer, pt, bc, ene in crib_matches:
                print(f"    Primer={primer} BERLIN={bc} ENE={ene}")
                print(f"    PT: {pt}")
        else:
            print(f"  No crib matches found.")

    return best_results, crib_matches

# ============================================================================
# HILL CLIMBING / SIMULATED ANNEALING (LONGER PRIMERS)
# ============================================================================

def hill_climb_primer(ciphertext, alphabet, alpha_name, primer_length, scorer,
                      iterations=50000, restarts=20, verbose=True):
    """
    Use hill climbing with random restarts to find good primers of given length.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Hill climbing: primer_len={primer_length}, alphabet={alpha_name}")
        print(f"  iterations={iterations}, restarts={restarts}")
        print(f"{'='*70}")

    global_best_score = -float('inf')
    global_best_primer = None
    global_best_pt = None
    all_results = []
    crib_matches = []

    for restart in range(restarts):
        # Random starting primer
        primer = [random.randint(0, 9) for _ in range(primer_length)]
        pt = gromark_decrypt(ciphertext, primer, alphabet)
        current_score = scorer.score(pt)

        best_score = current_score
        best_primer = list(primer)
        best_pt = pt

        temperature = 10.0

        for it in range(iterations):
            # Mutate: change one random digit
            new_primer = list(primer)
            pos = random.randint(0, primer_length - 1)
            new_primer[pos] = random.randint(0, 9)

            new_pt = gromark_decrypt(ciphertext, new_primer, alphabet)
            new_score = scorer.score(new_pt)

            # Simulated annealing acceptance
            temp = temperature * (1 - it / iterations)
            if temp < 0.01:
                temp = 0.01

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / temp):
                primer = new_primer
                current_score = new_score
                pt = new_pt

                if current_score > best_score:
                    best_score = current_score
                    best_primer = list(primer)
                    best_pt = pt

            # Check cribs
            if new_pt[63:74] == "BERLINCLOCK" or new_pt[21:34] == "EASTNORTHEAST":
                crib_matches.append((list(new_primer), new_pt,
                                    new_pt[63:74] == "BERLINCLOCK",
                                    new_pt[21:34] == "EASTNORTHEAST"))

        all_results.append((best_score, best_primer, best_pt))

        if best_score > global_best_score:
            global_best_score = best_score
            global_best_primer = best_primer
            global_best_pt = best_pt

        if verbose and (restart + 1) % 5 == 0:
            print(f"  Restart {restart+1}/{restarts}: best_score={global_best_score:.2f}")

    all_results.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"\n  Top 5 results:")
        for i, (score, primer, pt) in enumerate(all_results[:5]):
            print(f"    #{i+1}: primer={primer} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")
            print(f"          PT[21:34]={pt[21:34]}  PT[63:74]={pt[63:74]}")

        if crib_matches:
            print(f"\n  *** CRIB MATCHES FOUND: {len(crib_matches)} ***")
            for primer, pt, bc, ene in crib_matches:
                print(f"    Primer={primer} BERLIN={bc} ENE={ene}")
                print(f"    PT: {pt}")

    return all_results[:20], crib_matches

# ============================================================================
# CRIB-DRIVEN ANALYSIS
# ============================================================================

def crib_driven_analysis(ciphertext, alphabets, verbose=True):
    """
    For each alphabet, extract key digits required by each crib.
    Check if digits are all 0-9 (Gromark constraint).
    If so, check if both cribs are consistent with same running key.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"CRIB-DRIVEN ANALYSIS")
        print(f"Checking if Gromark (shifts 0-9) can produce known cribs")
        print(f"{'='*70}")

    results = {}

    for alpha_name, alphabet in alphabets.items():
        if verbose:
            print(f"\n  Alphabet: {alpha_name} = {alphabet}")

        # Extract key digits for BERLINCLOCK at positions 63-73
        bc_ct = ciphertext[63:74]
        bc_keys = extract_key_from_crib(bc_ct, "BERLINCLOCK", alphabet)

        # Extract key digits for EASTNORTHEAST at positions 21-33
        ene_ct = ciphertext[21:34]
        ene_keys = extract_key_from_crib(ene_ct, "EASTNORTHEAST", alphabet)

        if verbose:
            print(f"    BERLINCLOCK  @ 63-73: CT={bc_ct}")
            if bc_keys is not None:
                print(f"      Key digits needed: {bc_keys}")
                # Check internal Fibonacci consistency
                fib_ok = True
                for i in range(2, len(bc_keys)):
                    if bc_keys[i] != (bc_keys[i-1] + bc_keys[i-2]) % 10:
                        fib_ok = False
                        break
                print(f"      Internal Fibonacci consistency: {'YES' if fib_ok else 'NO'}")
            else:
                print(f"      IMPOSSIBLE - requires shift > 9")

            print(f"    EASTNORTHEAST @ 21-33: CT={ene_ct}")
            if ene_keys is not None:
                print(f"      Key digits needed: {ene_keys}")
                fib_ok = True
                for i in range(2, len(ene_keys)):
                    if ene_keys[i] != (ene_keys[i-1] + ene_keys[i-2]) % 10:
                        fib_ok = False
                        break
                print(f"      Internal Fibonacci consistency: {'YES' if fib_ok else 'NO'}")
            else:
                print(f"      IMPOSSIBLE - requires shift > 9")

        # If both are possible, check cross-consistency
        if bc_keys is not None and ene_keys is not None:
            _, bc_backward = reverse_engineer_primer_from_crib(
                ciphertext, "BERLINCLOCK", 63, alphabet, max_primer_len=8)
            _, ene_backward = reverse_engineer_primer_from_crib(
                ciphertext, "EASTNORTHEAST", 21, alphabet, max_primer_len=8)

            if bc_backward is not None and ene_backward is not None:
                if verbose:
                    print(f"    Reverse-engineered key from BERLINCLOCK (back to pos 0):")
                    print(f"      {bc_backward[:20]}...")
                    print(f"    Reverse-engineered key from EASTNORTHEAST (back to pos 0):")
                    print(f"      {ene_backward[:20]}...")

                    # Check if they agree on overlapping positions
                    min_len = min(len(bc_backward), len(ene_backward))
                    agree = True
                    disagreements = []
                    for i in range(min_len):
                        if bc_backward[i] != ene_backward[i]:
                            agree = False
                            disagreements.append((i, bc_backward[i], ene_backward[i]))
                    if agree:
                        print(f"    *** BOTH CRIBS AGREE ON KEY! Primer = {bc_backward[:8]} ***")
                    else:
                        print(f"    DISAGREEMENT at {len(disagreements)} positions (first 5):")
                        for pos, bc_val, ene_val in disagreements[:5]:
                            print(f"      pos {pos}: BC->{bc_val}, ENE->{ene_val}")

        results[alpha_name] = {
            'bc_keys': bc_keys,
            'ene_keys': ene_keys,
        }

    return results

# ============================================================================
# VIGENERE-GROMARK CONNECTION
# ============================================================================

def test_vigenere_gromark_connection(ciphertext, scorer, verbose=True):
    """
    Test if the known period-29 Vigenere key could be derived from a Gromark running key.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"VIGENERE-GROMARK CONNECTION ANALYSIS")
        print(f"{'='*70}")

    vig_key_str = "OYNKYELYOIECBAQK"  # known first 16 chars
    vig_key_nums = [ord(c) - ord('A') for c in vig_key_str]

    if verbose:
        print(f"  Known Vigenere key (first 16): {vig_key_str}")
        print(f"  As numbers (A=0): {vig_key_nums}")
        print(f"  Max value: {max(vig_key_nums)}, Min: {min(vig_key_nums)}")

        # Check which are 0-9
        in_range = [d for d in vig_key_nums if d <= 9]
        print(f"  Digits 0-9: {len(in_range)}/{len(vig_key_nums)} = {100*len(in_range)/len(vig_key_nums):.0f}%")
        print(f"  Digits > 9: {[d for d in vig_key_nums if d > 9]}")

    # Test 1: What if Vigenere shifts mod 10 give the Gromark digits?
    vig_mod10 = [d % 10 for d in vig_key_nums]
    if verbose:
        print(f"\n  Vig key mod 10: {vig_mod10}")
        fib_fails = 0
        for i in range(2, len(vig_mod10)):
            expected = (vig_mod10[i-1] + vig_mod10[i-2]) % 10
            if vig_mod10[i] != expected:
                fib_fails += 1
                print(f"    pos {i}: got {vig_mod10[i]}, expected {expected} -- FAIL")
        if fib_fails == 0:
            print(f"    ALL positions satisfy Fibonacci mod 10!")
        else:
            print(f"    {fib_fails} positions fail Fibonacci mod 10")

    # Test 2: Check Fibonacci mod 26
    if verbose:
        print(f"\n  Test: Check Fibonacci mod 26 on Vig key values:")
        fib26_fails = 0
        for i in range(2, len(vig_key_nums)):
            expected = (vig_key_nums[i-1] + vig_key_nums[i-2]) % 26
            if vig_key_nums[i] != expected:
                fib26_fails += 1
                print(f"    pos {i}: got {vig_key_nums[i]}, expected {expected} -- FAIL")
        if fib26_fails == 0:
            print(f"    ALL positions satisfy Fibonacci mod 26!")
        else:
            print(f"    {fib26_fails} positions fail Fibonacci mod 26")

    # Test 3: For each 2-digit primer, check how many of the 16 vig key values match
    if verbose:
        print(f"\n  Test: Can any 2-digit Gromark primer generate the Vig key (mod 10)?")
    best_match = 0
    best_primers_vig = []
    for d1 in range(10):
        for d2 in range(10):
            key = generate_running_key([d1, d2], 29)
            match_count = 0
            for i in range(16):
                if key[i] == vig_key_nums[i] % 10:
                    match_count += 1
            if match_count > best_match:
                best_match = match_count
                best_primers_vig = [(d1, d2)]
            elif match_count == best_match and match_count > 5:
                best_primers_vig.append((d1, d2))
    if verbose:
        print(f"    Best match: {best_match}/16 positions")
        if best_match > 5:
            for p in best_primers_vig[:5]:
                print(f"      Primer {list(p)}: {best_match}/16 match")

# ============================================================================
# SPECIAL PRIMER TESTS
# ============================================================================

def test_special_primers(ciphertext, alphabets, scorer, verbose=True):
    """
    Test primers derived from known Kryptos-related values.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"SPECIAL PRIMER TESTS")
        print(f"{'='*70}")

    special_primers = {
        # From the number 29
        '29': [2, 9],
        '29_ext': [0, 2, 9],
        '292': [2, 9, 2],

        # Berlin Clock time values
        'BC_midnight': [0, 0, 0, 0],
        'BC_noon': [1, 2, 0, 0],
        'BC_1103': [1, 1, 0, 3],
        'BC_2200': [2, 2, 0, 0],

        # Kryptos coordinates: 38 57 6.5 N, 77 8 44 W
        'coord_38576': [3, 8, 5, 7, 6],
        'coord_77844': [7, 7, 8, 4, 4],
        'coord_3857': [3, 8, 5, 7],
        'coord_7784': [7, 7, 8, 4],
        'coord_38': [3, 8],
        'coord_57': [5, 7],
        'coord_77': [7, 7],
        'coord_44': [4, 4],
        'coord_06': [0, 6],
        'coord_08': [0, 8],

        # KRYPTOS letter positions (A=0) mod 10
        'KRYPTOS_mod10': [0, 7, 4, 5, 9, 4, 8],
        'KRYPTOS_first3': [0, 7, 4],
        'KRYPTOS_first4': [0, 7, 4, 5],

        # Digits of pi, e, phi
        'pi': [3, 1, 4, 1, 5, 9],
        'e': [2, 7, 1, 8, 2, 8],
        'phi': [1, 6, 1, 8, 0, 3],

        # Berlin Wall dates
        'BW_fall_1989': [1, 9, 8, 9],
        'BW_1109': [1, 1, 0, 9],
        'BW_110989': [1, 1, 0, 9, 8, 9],

        # Simple patterns
        'zeros': [0, 0],
        'ones': [1, 1],
        'seq_12': [1, 2],
        'seq_123': [1, 2, 3],
        'seq_1234': [1, 2, 3, 4],

        # Sanborn-related
        'SANBORN_mod10': [8, 0, 3, 1, 4, 7, 3],

        # From known Vigenere key first two chars
        'vig_OY_mod10': [4, 4],  # O=14%10=4, Y=24%10=4
        'vig_ON_mod10': [4, 3],  # O=14%10=4, N=13%10=3
    }

    all_results = []
    crib_hits = []

    for primer_name, primer in special_primers.items():
        primer_use = [d % 10 for d in primer[:8]]
        if len(primer_use) < 2:
            continue

        for alpha_name, alphabet in alphabets.items():
            pt = gromark_decrypt(ciphertext, primer_use, alphabet)
            score = scorer.score(pt)

            bc_match = pt[63:74] == "BERLINCLOCK"
            ene_match = pt[21:34] == "EASTNORTHEAST"

            all_results.append((score, primer_name, primer_use, alpha_name, pt))

            if bc_match or ene_match:
                crib_hits.append((primer_name, primer_use, alpha_name, pt, bc_match, ene_match))

    all_results.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"\n  Top 10 special primer results:")
        for i, (score, pname, primer, aname, pt) in enumerate(all_results[:10]):
            print(f"    #{i+1}: {pname} primer={primer} alpha={aname} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")

        if crib_hits:
            print(f"\n  *** CRIB MATCHES: {len(crib_hits)} ***")
            for pname, primer, aname, pt, bc, ene in crib_hits:
                print(f"    {pname} primer={primer} alpha={aname}")
                print(f"    BERLIN={bc} ENE={ene}")
                print(f"    PT: {pt}")
        else:
            print(f"  No crib matches from special primers.")

    return all_results, crib_hits

# ============================================================================
# GENERALIZED LAG TESTING
# ============================================================================

def test_general_lags(ciphertext, alphabets, scorer, verbose=True):
    """
    Test non-standard lag pairs (not just lag 1,2).
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"GENERALIZED LAG TESTING")
        print(f"Testing different Fibonacci lag pairs with brute-force 2-digit primers")
        print(f"{'='*70}")

    lag_pairs = [(1,2), (1,3), (2,3), (1,4), (2,4), (3,4), (1,5), (2,5), (3,5)]

    best_overall = []
    crib_hits = []

    for lag1, lag2 in lag_pairs:
        for alpha_name, alphabet in [('STANDARD', STANDARD_ALPHA), ('KRYPTOS', KRYPTOS_ALPHA)]:
            best_for_config = None

            # Need primer of length >= max(lag1, lag2)
            min_primer_len = max(lag1, lag2)
            if min_primer_len <= 2:
                primer_len = 2
            else:
                primer_len = min_primer_len

            for combo in itertools.product(range(10), repeat=primer_len):
                primer = list(combo)
                pt = gromark_decrypt_general(ciphertext, primer, alphabet, lag1, lag2)
                if pt is None:
                    continue
                score = scorer.score(pt)

                if best_for_config is None or score > best_for_config[0]:
                    best_for_config = (score, primer, pt, alpha_name, lag1, lag2)

                bc_match = pt[63:74] == "BERLINCLOCK"
                ene_match = pt[21:34] == "EASTNORTHEAST"
                if bc_match or ene_match:
                    crib_hits.append((primer, alpha_name, lag1, lag2, pt, bc_match, ene_match))

            if best_for_config:
                best_overall.append(best_for_config)

    best_overall.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"\n  Top 10 across all lag pairs:")
        for i, (score, primer, pt, aname, l1, l2) in enumerate(best_overall[:10]):
            print(f"    #{i+1}: lag=({l1},{l2}) primer={primer} alpha={aname} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")

        if crib_hits:
            print(f"\n  *** CRIB MATCHES: {len(crib_hits)} ***")
            for primer, aname, l1, l2, pt, bc, ene in crib_hits:
                print(f"    lag=({l1},{l2}) primer={primer} alpha={aname}")
                print(f"    BERLIN={bc} ENE={ene} PT: {pt}")
        else:
            print(f"  No crib matches from generalized lags.")

    return best_overall, crib_hits

# ============================================================================
# REVERSE AND VARIANT TESTING
# ============================================================================

def test_reverse_and_variants(ciphertext, alphabets, scorer, verbose=True):
    """
    Test additional Gromark variants:
    1. Reverse ciphertext
    2. Subtraction-based key generation
    3. Mod-26 running key instead of mod 10
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"VARIANT TESTING: reverse, subtraction, mod-26 key")
        print(f"{'='*70}")

    variants_tested = 0
    best_results = []
    crib_hits = []

    for alpha_name, alphabet in [('STANDARD', STANDARD_ALPHA), ('KRYPTOS', KRYPTOS_ALPHA)]:
        alpha_len = len(alphabet)

        for d1 in range(10):
            for d2 in range(10):
                primer = [d1, d2]

                # Variant B: Reversed ciphertext
                rev_ct = ciphertext[::-1]
                pt = gromark_decrypt(rev_ct, primer, alphabet)
                score = scorer.score(pt)
                best_results.append((score, f"REVERSED primer={primer} alpha={alpha_name}", pt))
                if pt[63:74] == "BERLINCLOCK" or pt[21:34] == "EASTNORTHEAST":
                    crib_hits.append(("REVERSED", primer, alpha_name, pt))

                # Variant C: Key subtraction: key[i] = (key[i-2] - key[i-1]) mod 10
                key = list(primer)
                while len(key) < K4_LEN:
                    new_d = (key[-2] - key[-1]) % 10
                    key.append(new_d)
                pt_list = []
                for i, ch in enumerate(ciphertext):
                    pos = alphabet.index(ch)
                    new_pos = (pos - key[i]) % alpha_len
                    pt_list.append(alphabet[new_pos])
                pt = ''.join(pt_list)
                score = scorer.score(pt)
                best_results.append((score, f"SUBKEY primer={primer} alpha={alpha_name}", pt))
                if pt[63:74] == "BERLINCLOCK" or pt[21:34] == "EASTNORTHEAST":
                    crib_hits.append(("SUBKEY", primer, alpha_name, pt))

                # Variant D: Mod-26 running key (Fibonacci mod 26, shifts 0-25)
                key26 = list(primer)
                while len(key26) < K4_LEN:
                    new_d = (key26[-1] + key26[-2]) % 26
                    key26.append(new_d)
                pt_list = []
                for i, ch in enumerate(ciphertext):
                    pos = alphabet.index(ch)
                    new_pos = (pos - key26[i]) % alpha_len
                    pt_list.append(alphabet[new_pos])
                pt = ''.join(pt_list)
                score = scorer.score(pt)
                best_results.append((score, f"MOD26KEY primer={primer} alpha={alpha_name}", pt))
                if pt[63:74] == "BERLINCLOCK" or pt[21:34] == "EASTNORTHEAST":
                    crib_hits.append(("MOD26KEY", primer, alpha_name, pt))

                variants_tested += 3

    best_results.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"  Tested {variants_tested} variant configurations")
        print(f"\n  Top 10 variant results:")
        for i, (score, desc, pt) in enumerate(best_results[:10]):
            print(f"    #{i+1}: {desc} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")

        if crib_hits:
            print(f"\n  *** CRIB MATCHES: {len(crib_hits)} ***")
            for variant, primer, aname, pt in crib_hits:
                print(f"    {variant} primer={primer} alpha={aname}")
                print(f"    PT: {pt}")
        else:
            print(f"  No crib matches from variants.")

    return best_results, crib_hits

# ============================================================================
# EXHAUSTIVE CRIB VERIFICATION
# ============================================================================

def exhaustive_crib_check(ciphertext, alphabets, verbose=True):
    """
    For each alphabet, exhaustively check ALL possible 2-4 digit primers
    to see if either crib appears at the correct position.
    This is the definitive test.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"EXHAUSTIVE CRIB VERIFICATION")
        print(f"Testing all 2-4 digit primers for crib matches")
        print(f"{'='*70}")

    total_crib_hits = []

    for alpha_name, alphabet in alphabets.items():
        alpha_len = len(alphabet)

        for primer_len in [2, 3, 4]:
            bc_hits = 0
            ene_hits = 0
            both_hits = 0

            for combo in itertools.product(range(10), repeat=primer_len):
                primer = list(combo)
                key = generate_running_key(primer, K4_LEN)

                # Check BERLINCLOCK at positions 63-73
                bc_match = True
                for j, expected_ch in enumerate("BERLINCLOCK"):
                    pos = 63 + j
                    ct_pos = alphabet.index(ciphertext[pos])
                    pt_pos = (ct_pos - key[pos]) % alpha_len
                    if alphabet[pt_pos] != expected_ch:
                        bc_match = False
                        break

                # Check EASTNORTHEAST at positions 21-33
                ene_match = True
                for j, expected_ch in enumerate("EASTNORTHEAST"):
                    pos = 21 + j
                    ct_pos = alphabet.index(ciphertext[pos])
                    pt_pos = (ct_pos - key[pos]) % alpha_len
                    if alphabet[pt_pos] != expected_ch:
                        ene_match = False
                        break

                if bc_match:
                    bc_hits += 1
                    pt = gromark_decrypt(ciphertext, primer, alphabet)
                    if verbose and primer_len <= 3:
                        print(f"  BERLINCLOCK match: primer={primer} alpha={alpha_name}")
                        print(f"      PT[21:34]={pt[21:34]} PT[63:74]={pt[63:74]}")
                if ene_match:
                    ene_hits += 1
                    pt = gromark_decrypt(ciphertext, primer, alphabet)
                    if verbose and primer_len <= 3:
                        print(f"  EASTNORTHEAST match: primer={primer} alpha={alpha_name}")
                        print(f"      PT[21:34]={pt[21:34]} PT[63:74]={pt[63:74]}")
                if bc_match and ene_match:
                    both_hits += 1
                    pt = gromark_decrypt(ciphertext, primer, alphabet)
                    total_crib_hits.append((primer, alpha_name, pt))
                    if verbose:
                        print(f"  *** BOTH CRIBS MATCH! primer={primer} alpha={alpha_name} ***")
                        print(f"      PT: {pt}")

            total = 10 ** primer_len
            if verbose:
                print(f"  [{alpha_name}] primer_len={primer_len}: BC={bc_hits}/{total} ENE={ene_hits}/{total} BOTH={both_hits}/{total}")

    return total_crib_hits

# ============================================================================
# GROMARK WITH AUTOKEY FEEDBACK
# ============================================================================

def test_gromark_autokey(ciphertext, alphabets, scorer, verbose=True):
    """
    Test Gromark variant where the running key uses plaintext feedback:
    After primer is exhausted, key[i] = (PT_pos[i-1] + PT_pos[i-2]) mod 10
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"GROMARK WITH AUTOKEY (PLAINTEXT FEEDBACK)")
        print(f"{'='*70}")

    best_results = []
    crib_hits = []

    for alpha_name, alphabet in [('STANDARD', STANDARD_ALPHA), ('KRYPTOS', KRYPTOS_ALPHA)]:
        alpha_len = len(alphabet)

        for d1 in range(10):
            for d2 in range(10):
                primer = [d1, d2]
                plaintext = []

                for i in range(K4_LEN):
                    ct_pos = alphabet.index(ciphertext[i])

                    if i < len(primer):
                        k = primer[i]
                    else:
                        # Use plaintext feedback
                        pt1_pos = alphabet.index(plaintext[i-1])
                        pt2_pos = alphabet.index(plaintext[i-2])
                        k = (pt1_pos + pt2_pos) % 10

                    pt_pos = (ct_pos - k) % alpha_len
                    plaintext.append(alphabet[pt_pos])

                pt = ''.join(plaintext)
                score = scorer.score(pt)
                best_results.append((score, primer, alpha_name, pt))

                if pt[63:74] == "BERLINCLOCK" or pt[21:34] == "EASTNORTHEAST":
                    crib_hits.append((primer, alpha_name, pt,
                                    pt[63:74] == "BERLINCLOCK",
                                    pt[21:34] == "EASTNORTHEAST"))

    best_results.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"\n  Top 10 autokey Gromark results:")
        for i, (score, primer, aname, pt) in enumerate(best_results[:10]):
            print(f"    #{i+1}: primer={primer} alpha={aname} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")

        if crib_hits:
            print(f"\n  *** CRIB MATCHES: {len(crib_hits)} ***")
            for primer, aname, pt, bc, ene in crib_hits:
                print(f"    primer={primer} alpha={aname} BERLIN={bc} ENE={ene}")
                print(f"    PT: {pt}")
        else:
            print(f"  No crib matches from autokey variant.")

    return best_results, crib_hits

# ============================================================================
# SELF-VALIDATION TEST
# ============================================================================

def self_validation(verbose=True):
    """
    Verify our Gromark implementation is correct by encrypting and decrypting.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"SELF-VALIDATION TEST")
        print(f"{'='*70}")

    all_pass = True

    test_pt = "HELLOWORLD"
    test_primer = [3, 7]

    for alpha_name, alphabet in [('STANDARD', STANDARD_ALPHA), ('KRYPTOS', KRYPTOS_ALPHA)]:
        ct = gromark_encrypt(test_pt, test_primer, alphabet)
        pt_recovered = gromark_decrypt(ct, test_primer, alphabet)

        key = generate_running_key(test_primer, len(test_pt))

        ok = pt_recovered == test_pt
        if not ok:
            all_pass = False
        if verbose:
            print(f"\n  Alphabet: {alpha_name}")
            print(f"  Plaintext:  {test_pt}")
            print(f"  Primer:     {test_primer}")
            print(f"  Key stream: {key}")
            print(f"  Ciphertext: {ct}")
            print(f"  Recovered:  {pt_recovered}")
            print(f"  Match: {'PASS' if ok else 'FAIL'}")

    # Test Fibonacci key generation
    test_fib = generate_running_key([3, 7], 20)
    expected = [3, 7, 0, 7, 7, 4, 1, 5, 6, 1, 7, 8, 5, 3, 8, 1, 9, 0, 9, 9]
    fib_ok = test_fib == expected
    if not fib_ok:
        all_pass = False
    if verbose:
        print(f"\n  Fibonacci key test: primer=[3,7], len=20")
        print(f"  Generated: {test_fib}")
        print(f"  Expected:  {expected}")
        print(f"  Match: {'PASS' if fib_ok else 'FAIL'}")

    # Test with longer primer
    test_pt2 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    test_primer2 = [1, 2, 3, 4, 5]
    for alpha_name, alphabet in [('STANDARD', STANDARD_ALPHA)]:
        ct2 = gromark_encrypt(test_pt2, test_primer2, alphabet)
        pt2_recovered = gromark_decrypt(ct2, test_primer2, alphabet)
        ok2 = pt2_recovered == test_pt2
        if not ok2:
            all_pass = False
        if verbose:
            print(f"\n  Long test with 5-digit primer:")
            print(f"  PT: {test_pt2}")
            print(f"  CT: {ct2}")
            print(f"  Recovered: {pt2_recovered}")
            print(f"  Match: {'PASS' if ok2 else 'FAIL'}")

    if verbose:
        print(f"\n  Overall validation: {'ALL PASS' if all_pass else 'SOME FAILURES'}")

    return all_pass

# ============================================================================
# MOD-26 FIBONACCI GROMARK (Richard Bean style)
# ============================================================================

def test_mod26_fibonacci_gromark(ciphertext, alphabets, scorer, verbose=True):
    """
    Test variant where Fibonacci key runs mod 26 (not mod 10):
    key[i] = (key[i-1] + key[i-2]) mod 26
    Shift = key[i] (0-25)
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"MOD-26 FIBONACCI KEY GROMARK (Bean-style)")
        print(f"Brute force all 26x26 = 676 two-element primers per alphabet")
        print(f"{'='*70}")

    best_results = []
    crib_hits = []

    for alpha_name, alphabet in alphabets.items():
        alpha_len = len(alphabet)

        for d1 in range(26):
            for d2 in range(26):
                # Generate mod-26 Fibonacci key
                key = [d1, d2]
                while len(key) < K4_LEN:
                    key.append((key[-1] + key[-2]) % 26)

                # Decrypt
                pt_list = []
                for i, ch in enumerate(ciphertext):
                    pos = alphabet.index(ch)
                    new_pos = (pos - key[i]) % alpha_len
                    pt_list.append(alphabet[new_pos])
                pt = ''.join(pt_list)

                score = scorer.score(pt)
                best_results.append((score, [d1, d2], alpha_name, pt))

                bc_match = pt[63:74] == "BERLINCLOCK"
                ene_match = pt[21:34] == "EASTNORTHEAST"
                if bc_match or ene_match:
                    crib_hits.append(([d1, d2], alpha_name, pt, bc_match, ene_match))

    best_results.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print(f"\n  Top 10 mod-26 Fibonacci results:")
        for i, (score, primer, aname, pt) in enumerate(best_results[:10]):
            print(f"    #{i+1}: primer={primer} alpha={aname} score={score:.2f}")
            print(f"          PT: {pt[:60]}...")
            print(f"          PT[21:34]={pt[21:34]}  PT[63:74]={pt[63:74]}")

        if crib_hits:
            print(f"\n  *** CRIB MATCHES: {len(crib_hits)} ***")
            for primer, aname, pt, bc, ene in crib_hits:
                print(f"    primer={primer} alpha={aname} BERLIN={bc} ENE={ene}")
                print(f"    PT: {pt}")
        else:
            print(f"  No crib matches from mod-26 Fibonacci.")

    return best_results, crib_hits

# ============================================================================
# DEEP CRIB SHIFT ANALYSIS
# ============================================================================

def deep_crib_shift_analysis(ciphertext, alphabets, verbose=True):
    """
    Analyze the exact shifts needed at crib positions for each alphabet.
    Tells us whether Gromark's 0-9 constraint is even feasible.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"DEEP CRIB SHIFT ANALYSIS")
        print(f"What shifts does each alphabet need at crib positions?")
        print(f"{'='*70}")

    feasibility = {}

    for alpha_name, alphabet in alphabets.items():
        alpha_len = len(alphabet)
        if verbose:
            print(f"\n  Alphabet: {alpha_name} ({alphabet})")

        # BERLINCLOCK at positions 63-73
        bc_shifts = []
        for j, pt_ch in enumerate("BERLINCLOCK"):
            pos = 63 + j
            ct_ch = ciphertext[pos]
            ct_idx = alphabet.index(ct_ch)
            pt_idx = alphabet.index(pt_ch)
            shift = (ct_idx - pt_idx) % alpha_len
            bc_shifts.append(shift)

        bc_feasible = all(s <= 9 for s in bc_shifts)

        if verbose:
            print(f"    BERLINCLOCK shifts (pos 63-73): {bc_shifts}")
            print(f"    All shifts 0-9? {'YES' if bc_feasible else 'NO'}")
            if not bc_feasible:
                print(f"    Shifts > 9: {[(i+63, s) for i, s in enumerate(bc_shifts) if s > 9]}")
            else:
                fib_ok = True
                for i in range(2, len(bc_shifts)):
                    if bc_shifts[i] != (bc_shifts[i-1] + bc_shifts[i-2]) % 10:
                        fib_ok = False
                        break
                print(f"    Internal Fibonacci consistency: {'YES' if fib_ok else 'NO'}")
                if not fib_ok:
                    for i in range(2, len(bc_shifts)):
                        exp = (bc_shifts[i-1] + bc_shifts[i-2]) % 10
                        if bc_shifts[i] != exp:
                            print(f"      pos {63+i}: got {bc_shifts[i]}, expected {exp}")

        # EASTNORTHEAST at positions 21-33
        ene_shifts = []
        for j, pt_ch in enumerate("EASTNORTHEAST"):
            pos = 21 + j
            ct_ch = ciphertext[pos]
            ct_idx = alphabet.index(ct_ch)
            pt_idx = alphabet.index(pt_ch)
            shift = (ct_idx - pt_idx) % alpha_len
            ene_shifts.append(shift)

        ene_feasible = all(s <= 9 for s in ene_shifts)

        if verbose:
            print(f"    EASTNORTHEAST shifts (pos 21-33): {ene_shifts}")
            print(f"    All shifts 0-9? {'YES' if ene_feasible else 'NO'}")
            if not ene_feasible:
                print(f"    Shifts > 9: {[(i+21, s) for i, s in enumerate(ene_shifts) if s > 9]}")
            else:
                fib_ok = True
                for i in range(2, len(ene_shifts)):
                    if ene_shifts[i] != (ene_shifts[i-1] + ene_shifts[i-2]) % 10:
                        fib_ok = False
                        break
                print(f"    Internal Fibonacci consistency: {'YES' if fib_ok else 'NO'}")
                if not fib_ok:
                    for i in range(2, len(ene_shifts)):
                        exp = (ene_shifts[i-1] + ene_shifts[i-2]) % 10
                        if ene_shifts[i] != exp:
                            print(f"      pos {21+i}: got {ene_shifts[i]}, expected {exp}")

        feasibility[alpha_name] = {
            'bc_feasible': bc_feasible,
            'ene_feasible': ene_feasible,
            'both_feasible': bc_feasible and ene_feasible,
            'bc_shifts': bc_shifts,
            'ene_shifts': ene_shifts,
        }

    # Summary
    if verbose:
        print(f"\n  FEASIBILITY SUMMARY:")
        print(f"  {'Alphabet':<16} {'BC 0-9?':<10} {'ENE 0-9?':<10} {'Both?':<8}")
        print(f"  {'-'*44}")
        for alpha_name, f in feasibility.items():
            print(f"  {alpha_name:<16} {'YES' if f['bc_feasible'] else 'NO':<10} {'YES' if f['ene_feasible'] else 'NO':<10} {'YES' if f['both_feasible'] else 'NO':<8}")

    return feasibility

# ============================================================================
# EXTENDED HILL CLIMBING WITH ALL ALPHABETS
# ============================================================================

def extended_hill_climb(ciphertext, alphabets, scorer, verbose=True):
    """
    Run SA/hill-climbing for primer lengths 5-8 across key alphabets.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"EXTENDED HILL CLIMBING (primers 5-8)")
        print(f"{'='*70}")

    all_crib_hits = []

    for primer_len in [5, 6, 7, 8]:
        for alpha_name in ['STANDARD', 'KRYPTOS']:
            alphabet = alphabets[alpha_name]
            results, crib_hits = hill_climb_primer(
                ciphertext, alphabet, alpha_name, primer_len, scorer,
                iterations=30000, restarts=15, verbose=verbose
            )
            all_crib_hits.extend(crib_hits)

    return all_crib_hits

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("COMPREHENSIVE GROMARK CIPHER ANALYSIS FOR KRYPTOS K4")
    print("=" * 70)
    print(f"K4 ciphertext ({K4_LEN} chars): {K4}")
    print(f"Cribs: BERLINCLOCK@63-73, EASTNORTHEAST@21-33")

    # Load scorer
    print(f"\nLoading quadgram scorer...")
    scorer = QuadgramScorer(QUADGRAM_FILE)
    print(f"  Loaded {len(scorer.quadgrams)} quadgrams")

    # Build alphabets
    alphabets = build_alphabets()
    print(f"\nAlphabets to test:")
    for name, alpha in alphabets.items():
        print(f"  {name}: {alpha}")

    # ======================================================================
    # Phase 0: Self-validation
    # ======================================================================
    self_validation(verbose=True)

    # ======================================================================
    # Phase 1: Deep crib shift analysis (most informative - do first)
    # ======================================================================
    feasibility = deep_crib_shift_analysis(K4, alphabets, verbose=True)

    # ======================================================================
    # Phase 2: Crib-driven analysis
    # ======================================================================
    crib_driven_analysis(K4, alphabets, verbose=True)

    # ======================================================================
    # Phase 3: Exhaustive crib verification (2-4 digit primers)
    # ======================================================================
    exhaustive_hits = exhaustive_crib_check(K4, alphabets, verbose=True)

    # ======================================================================
    # Phase 4: Brute force search (2-3 digit primers, best scoring)
    # ======================================================================
    all_bf_cribs = []
    for alpha_name in ['STANDARD', 'KRYPTOS']:
        for plen in [2, 3]:
            _, cribs = brute_force_primers(K4, alphabets[alpha_name], alpha_name, plen, scorer,
                                           top_n=10, check_cribs=True, verbose=True)
            all_bf_cribs.extend(cribs)

    # 4-digit for STANDARD and KRYPTOS
    for alpha_name in ['STANDARD', 'KRYPTOS']:
        _, cribs = brute_force_primers(K4, alphabets[alpha_name], alpha_name, 4, scorer,
                                       top_n=10, check_cribs=True, verbose=True)
        all_bf_cribs.extend(cribs)

    # ======================================================================
    # Phase 5: Hill climbing for longer primers (5-8 digits)
    # ======================================================================
    hc_cribs = extended_hill_climb(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 6: Special primers
    # ======================================================================
    _, special_cribs = test_special_primers(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 7: Generalized lag testing
    # ======================================================================
    _, lag_cribs = test_general_lags(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 8: Gromark autokey variant
    # ======================================================================
    _, autokey_cribs = test_gromark_autokey(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 9: Reverse and other variants
    # ======================================================================
    _, variant_cribs = test_reverse_and_variants(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 10: Mod-26 Fibonacci Gromark (Bean-style)
    # ======================================================================
    _, mod26_cribs = test_mod26_fibonacci_gromark(K4, alphabets, scorer, verbose=True)

    # ======================================================================
    # Phase 11: Vigenere-Gromark connection
    # ======================================================================
    test_vigenere_gromark_connection(K4, scorer, verbose=True)

    # ======================================================================
    # FINAL SUMMARY
    # ======================================================================
    print(f"\n{'='*70}")
    print(f"FINAL SUMMARY")
    print(f"{'='*70}")

    # Feasibility recap
    print(f"\n  CRIB FEASIBILITY (shifts 0-9 only):")
    for alpha_name, f in feasibility.items():
        if f['both_feasible']:
            print(f"    {alpha_name}: BOTH cribs feasible with 0-9 shifts")
        elif f['bc_feasible']:
            print(f"    {alpha_name}: Only BERLINCLOCK feasible")
        elif f['ene_feasible']:
            print(f"    {alpha_name}: Only EASTNORTHEAST feasible")
        else:
            print(f"    {alpha_name}: NEITHER crib feasible with 0-9 shifts")

    all_cribs = all_bf_cribs + hc_cribs + special_cribs + lag_cribs + autokey_cribs + variant_cribs + mod26_cribs

    if exhaustive_hits:
        print(f"\n  EXHAUSTIVE CRIB HITS (both cribs at correct positions):")
        for primer, aname, pt in exhaustive_hits:
            print(f"    primer={primer} alpha={aname}")
            print(f"    PT: {pt}")

    if all_cribs:
        print(f"\n  TOTAL CRIB MATCHES FOUND (from all search methods): {len(all_cribs)}")
        seen = set()
        for item in all_cribs:
            key = str(item[:3]) if len(item) > 3 else str(item)
            if key not in seen:
                seen.add(key)
                print(f"  {item}")
    else:
        print(f"\n  NO CRIB MATCHES FOUND across all tests.")
        print(f"  This means:")
        print(f"  1. Standard Gromark (mod-10 Fibonacci running key) does NOT produce")
        print(f"     both BERLINCLOCK and EASTNORTHEAST at the known positions")
        print(f"     for any tested alphabet or primer.")
        print(f"  2. Mod-26 Fibonacci variants also failed.")
        print(f"  3. Autokey variants also failed.")
        print(f"  4. The cipher is likely NOT a standard Gromark, or uses a")
        print(f"     non-standard key generation mechanism, or uses a different")
        print(f"     mixed alphabet not tested here.")

    print(f"\n  TESTS PERFORMED:")
    print(f"  - 7 alphabets: STANDARD, KRYPTOS, PALIMPSEST, ABSCISSA, BERLINCLOCK, KRYPTOS_STD, SANBORN")
    print(f"  - Primer lengths 2-8 digits (brute force 2-4, hill climbing 5-8)")
    print(f"  - Standard mod-10 Fibonacci key generation")
    print(f"  - Extended mod-26 Fibonacci key generation")
    print(f"  - 9 lag pairs: (1,2), (1,3), (2,3), (1,4), (2,4), (3,4), (1,5), (2,5), (3,5)")
    print(f"  - Autokey (plaintext feedback) variant")
    print(f"  - Reversed ciphertext")
    print(f"  - Subtraction-based key generation")
    print(f"  - 30+ special primers (coordinates, dates, constants, keywords)")
    print(f"  - Vigenere-Gromark connection analysis")

    print(f"\nAnalysis complete.")

if __name__ == "__main__":
    random.seed(42)  # Reproducibility
    main()
