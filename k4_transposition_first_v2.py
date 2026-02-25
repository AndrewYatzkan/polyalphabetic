#!/usr/bin/env python3
"""
K4 Transposition-First v2: Test hypothesis that K4 = Vigenere(Transposition(plaintext))

Decryption path:
  1. Vigenere-decrypt K4 with the period-29 key -> intermediate text
  2. Un-transpose the intermediate text -> plaintext

The intermediate text at known key positions is mostly gibberish.
The hypothesis is: that gibberish IS the transposed plaintext.
If we find the right un-transposition, the gibberish becomes English with
EASTNORTHEAST at positions 21-33 and BERLINCLOCK at positions 63-73.

We test:
  a. Columnar transposition (various key lengths, many orderings)
  b. Route ciphers (row-by-row, column-by-column, zigzag, spiral)
  c. Rail fence (2-10 rails)

For unknown key positions (16-20), we use '?' and check patterns ignoring those.
"""

import sys
import math
import time
import itertools
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = len(K4)  # 97

# Known key (period 29), positions 0-28
# Positions 16-20 are unknown (marked as None)
KNOWN_KEY_LETTERS = {
    0: 'O', 1: 'Y', 2: 'N', 3: 'K', 4: 'Y', 5: 'E', 6: 'L', 7: 'Y',
    8: 'O', 9: 'I', 10: 'E', 11: 'C', 12: 'B', 13: 'A', 14: 'Q', 15: 'K',
    # 16, 17, 18, 19, 20 are UNKNOWN
    21: 'R', 22: 'D', 23: 'U', 24: 'M', 25: 'R', 26: 'I', 27: 'Y', 28: 'W'
}

CRIB_EAST = "EASTNORTHEAST"
CRIB_EAST_POS = 21  # positions 21-33 in plaintext
CRIB_BERLIN = "BERLINCLOCK"
CRIB_BERLIN_POS = 63  # positions 63-73 in plaintext

print("=" * 80)
print("K4 TRANSPOSITION-FIRST v2")
print("Hypothesis: K4 = Vigenere(Transposition(plaintext))")
print("Decryption: Vig-decrypt -> intermediate -> un-transpose -> plaintext")
print("=" * 80)
print(f"K4 ciphertext ({N} chars): {K4}")


# ============================================================
# STEP 1: Vigenere-decrypt K4 with known key portions
# ============================================================
def vig_decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Decrypt a single character using Vigenere with KRYPTOS alphabet."""
    ct_idx = alpha.index(ct_char)
    key_idx = alpha.index(key_char)
    pt_idx = (ct_idx - key_idx) % len(alpha)
    return alpha[pt_idx]


def vig_encrypt_char(pt_char, key_char, alpha=KRYPTOS_ALPHA):
    """Encrypt a single character using Vigenere with KRYPTOS alphabet."""
    pt_idx = alpha.index(pt_char)
    key_idx = alpha.index(key_char)
    ct_idx = (pt_idx + key_idx) % len(alpha)
    return alpha[ct_idx]


def get_intermediate_text(key_slots_16_20=None):
    """
    Vigenere-decrypt K4 with the period-29 key.
    If key_slots_16_20 is None, unknown positions get '?'.
    If provided, it should be a 5-letter string for positions 16-20.
    """
    result = []
    for i in range(N):
        key_pos = i % 29
        if key_pos in KNOWN_KEY_LETTERS:
            key_char = KNOWN_KEY_LETTERS[key_pos]
        elif key_slots_16_20 is not None:
            key_char = key_slots_16_20[key_pos - 16]
        else:
            result.append('?')
            continue
        result.append(vig_decrypt_char(K4[i], key_char))
    return ''.join(result)


# Show the intermediate text with unknowns
intermediate_partial = get_intermediate_text()
print(f"\nIntermediate text (Vig-decrypt, '?' = unknown key positions):")
print(f"  {intermediate_partial}")

# Identify which positions in intermediate text are unknown
unknown_positions = [i for i in range(N) if intermediate_partial[i] == '?']
known_positions = [i for i in range(N) if intermediate_partial[i] != '?']
print(f"\nKnown positions: {len(known_positions)}/{N}")
print(f"Unknown positions ({len(unknown_positions)}): {unknown_positions}")
print(f"  (These are at K4 positions where key slot is 16,17,18,19, or 20)")


# ============================================================
# STEP 2: Load scoring resources
# ============================================================
def load_quadgrams(filepath):
    """Load quadgram frequencies for English text scoring."""
    quadgrams = {}
    total = 0
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    quadgrams[parts[0]] = int(parts[1])
                    total += int(parts[1])
    except FileNotFoundError:
        return None, 0
    return quadgrams, total


def load_words(filepath):
    """Load English words for dictionary checking."""
    words = set()
    try:
        with open(filepath, 'r') as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 3:
                    words.add(w)
    except FileNotFoundError:
        return set()
    return words


QUADGRAMS, QG_TOTAL = load_quadgrams("/home/user/polyalphabetic/english_quadgrams.txt")
WORDS = load_words("/home/user/polyalphabetic/OxfordEnglishWords.txt")

if QUADGRAMS:
    import math as _math
    QG_LOG = {}
    floor_val = _math.log10(0.01 / QG_TOTAL)
    for qg, cnt in QUADGRAMS.items():
        QG_LOG[qg] = _math.log10(cnt / QG_TOTAL)
    print(f"Loaded {len(QUADGRAMS)} quadgrams for scoring.")
else:
    QG_LOG = {}
    floor_val = -10
    print("WARNING: Could not load quadgrams.")

print(f"Loaded {len(WORDS)} dictionary words.")


def score_text_quadgrams(text):
    """Score text using quadgram frequencies. Higher = more English-like."""
    text = text.replace('?', '')
    score = 0.0
    count = 0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        if '?' not in qg:
            score += QG_LOG.get(qg, floor_val)
            count += 1
    return score / max(count, 1) if count > 0 else floor_val


def find_words_in_text(text, min_len=4):
    """Find English words in a text string."""
    found = []
    text_upper = text.upper().replace('?', '#')
    for length in range(min_len, min(15, len(text_upper) + 1)):
        for i in range(len(text_upper) - length + 1):
            substr = text_upper[i:i+length]
            if '#' not in substr and substr in WORDS:
                found.append((i, substr))
    return found


# ============================================================
# STEP 3: Transposition functions
# ============================================================

def columnar_transpose(text, num_cols, col_order):
    """
    Apply columnar transposition: write text into rows of num_cols,
    then read off columns in col_order.
    """
    rows = math.ceil(len(text) / num_cols)
    padded = text + '\x00' * (rows * num_cols - len(text))
    
    grid = []
    for r in range(rows):
        grid.append(padded[r * num_cols: (r + 1) * num_cols])
    
    result = []
    for c in col_order:
        for r in range(rows):
            ch = grid[r][c]
            if ch != '\x00':
                result.append(ch)
    
    return ''.join(result)


def columnar_untranspose(text, num_cols, col_order):
    """
    Reverse columnar transposition.
    """
    n = len(text)
    rows = math.ceil(n / num_cols)
    full_cols = n - (rows - 1) * num_cols
    
    col_lengths = {}
    for i, c in enumerate(col_order):
        if c < full_cols:
            col_lengths[c] = rows
        else:
            col_lengths[c] = rows - 1
    
    columns = {}
    pos = 0
    for c in col_order:
        length = col_lengths[c]
        columns[c] = text[pos:pos + length]
        pos += length
    
    result = []
    for r in range(rows):
        for c in range(num_cols):
            if r < len(columns.get(c, '')):
                result.append(columns[c][r])
    
    return ''.join(result)


def rail_fence_encrypt(text, rails):
    """Encrypt with rail fence cipher."""
    if rails <= 1 or rails >= len(text):
        return text
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for ch in text:
        fence[rail].append(ch)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return ''.join(''.join(row) for row in fence)


def rail_fence_decrypt(text, rails):
    """Decrypt rail fence cipher."""
    if rails <= 1 or rails >= len(text):
        return text
    n = len(text)
    fence_lens = [0] * rails
    rail = 0
    direction = 1
    for i in range(n):
        fence_lens[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    
    fences = []
    pos = 0
    for r in range(rails):
        fences.append(list(text[pos:pos + fence_lens[r]]))
        pos += fence_lens[r]
    
    result = []
    rail_indices = [0] * rails
    rail = 0
    direction = 1
    for i in range(n):
        result.append(fences[rail][rail_indices[rail]])
        rail_indices[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    
    return ''.join(result)


def route_cipher_patterns(text, num_rows, num_cols):
    """
    Generate various route cipher un-transpositions for a grid.
    Returns list of (name, result_text) pairs.
    """
    n = len(text)
    if num_rows * num_cols < n:
        return []
    
    results = []
    padded = text + '\x00' * (num_rows * num_cols - n)
    
    grid = []
    for r in range(num_rows):
        grid.append(list(padded[r * num_cols: (r + 1) * num_cols]))
    
    def read_grid(order):
        res = []
        for r, c in order:
            ch = grid[r][c]
            if ch != '\x00':
                res.append(ch)
        return ''.join(res)
    
    # Pattern 1: Read column-by-column (left to right)
    order = [(r, c) for c in range(num_cols) for r in range(num_rows)]
    results.append((f"col-LR-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 2: Read column-by-column (right to left)
    order = [(r, c) for c in range(num_cols - 1, -1, -1) for r in range(num_rows)]
    results.append((f"col-RL-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 3: Snake columns
    order = []
    for c in range(num_cols):
        if c % 2 == 0:
            order.extend((r, c) for r in range(num_rows))
        else:
            order.extend((r, c) for r in range(num_rows - 1, -1, -1))
    results.append((f"snake-col-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 4: Snake rows (boustrophedon)
    order = []
    for r in range(num_rows):
        if r % 2 == 0:
            order.extend((r, c) for c in range(num_cols))
        else:
            order.extend((r, c) for c in range(num_cols - 1, -1, -1))
    results.append((f"snake-row-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 5: Spiral inward (clockwise)
    order = []
    top, bottom, left, right = 0, num_rows - 1, 0, num_cols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            order.append((top, c))
        top += 1
        for r in range(top, bottom + 1):
            order.append((r, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((bottom, c))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((r, left))
            left += 1
    results.append((f"spiral-CW-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 6: Spiral inward (counter-clockwise)
    order = []
    top, bottom, left, right = 0, num_rows - 1, 0, num_cols - 1
    while top <= bottom and left <= right:
        for r in range(top, bottom + 1):
            order.append((r, left))
        left += 1
        for c in range(left, right + 1):
            order.append((bottom, c))
        bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((r, right))
            right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((top, c))
            top += 1
    results.append((f"spiral-CCW-{num_rows}x{num_cols}", read_grid(order)))
    
    # Pattern 7: Diagonal reading
    order = []
    for d in range(num_rows + num_cols - 1):
        for r in range(max(0, d - num_cols + 1), min(num_rows, d + 1)):
            c = d - r
            if 0 <= c < num_cols:
                order.append((r, c))
    results.append((f"diag-TLBR-{num_rows}x{num_cols}", read_grid(order)))
    
    return results


# ============================================================
# STEP 4: Checking cribs in candidate plaintext
# ============================================================

def check_cribs(candidate, allow_wildcards=True):
    """
    Check if EASTNORTHEAST appears around position 21 and 
    BERLINCLOCK appears around position 63 in the candidate plaintext.
    """
    total_match = 0
    details = []
    
    for crib, crib_pos in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]:
        best_match = 0
        best_offset = 0
        for offset in range(-3, 4):
            pos = crib_pos + offset
            if pos < 0 or pos + len(crib) > len(candidate):
                continue
            match = 0
            for j, ch in enumerate(crib):
                if pos + j < len(candidate):
                    cand_ch = candidate[pos + j]
                    if cand_ch == '?':
                        if allow_wildcards:
                            match += 0.5
                    elif cand_ch == ch:
                        match += 1
            if match > best_match:
                best_match = match
                best_offset = offset
        
        total_match += best_match
        details.append(f"{crib}@{crib_pos}+{best_offset}: {best_match}/{len(crib)}")
    
    return total_match, details


def check_cribs_strict(candidate):
    """Strict crib check: only exact letter matches."""
    total = 0
    for crib, crib_pos in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]:
        best = 0
        for offset in range(-3, 4):
            pos = crib_pos + offset
            if pos < 0 or pos + len(crib) > len(candidate):
                continue
            match = sum(1 for j, ch in enumerate(crib) 
                       if pos + j < len(candidate) and candidate[pos + j] == ch)
            best = max(best, match)
        total += best
    return total


# ============================================================
# STEP 5: Main search
# ============================================================

start_time = time.time()
MAX_TIME = 540  # 9 minutes

results = []

def report_result(score, name, candidate, details=""):
    """Store a result if it's promising."""
    results.append((score, name, candidate, details))
    if score >= 8:
        elapsed = time.time() - start_time
        print(f"\n*** PROMISING ({elapsed:.1f}s): {name}")
        print(f"    Score: {score}")
        print(f"    Text: {candidate[:40]}...{candidate[60:80]}...")
        print(f"    Details: {details}")
        words = find_words_in_text(candidate, min_len=4)
        if words:
            print(f"    Words found: {words[:10]}")


def time_check():
    """Return True if we should continue, False if time is up."""
    return (time.time() - start_time) < MAX_TIME


# ----------------------------------------------------------
# 5a. RAIL FENCE
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 1: Rail Fence Cipher (2-20 rails)")
print("=" * 80)

for rails in range(2, 21):
    if not time_check():
        break
    candidate = rail_fence_decrypt(intermediate_partial, rails)
    score, details = check_cribs(candidate)
    report_result(score, f"rail-fence-{rails}", candidate, '; '.join(details))
    
    candidate2 = rail_fence_encrypt(intermediate_partial, rails)
    score2, details2 = check_cribs(candidate2)
    report_result(score2, f"rail-fence-{rails}-inv", candidate2, '; '.join(details2))

print(f"  Rail fence: tested {2 * 19} configurations")


# ----------------------------------------------------------
# 5b. COLUMNAR TRANSPOSITION - Keyword-based
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 2: Columnar Transposition (keyword-based orderings)")
print("=" * 80)

KEYWORDS = [
    'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'BERLINCLOCK',
    'SANBORN', 'SCULPTURE', 'LANGLEY', 'CIA', 'NSA', 'SHADOW', 'LIGHT',
    'LUCID', 'MEMORY', 'BETWEEN', 'SUBTLE', 'LAYER', 'UNDERGROUND',
    'COMPASS', 'NORTH', 'EAST', 'NORTHEAST', 'MORSE', 'DIGETAL',
    'VIRTUALLY', 'INVISIBLE', 'IQLUSION', 'DESPERAT', 'SLOWLY',
    'SOS', 'RQ', 'DYAHR', 'THOMPSON', 'WEBSTER', 'SCHEIDT',
    'MEDUSA', 'ANTIPODES', 'MAGNETIC',
    'TWENTYNINE', 'NINETYSEVEN',
]


def keyword_to_order(keyword):
    """Convert a keyword to a column ordering."""
    indexed = [(ch, i) for i, ch in enumerate(keyword.upper())]
    sorted_indexed = sorted(indexed, key=lambda x: (x[0], x[1]))
    order = [0] * len(keyword)
    for rank, (ch, orig_idx) in enumerate(sorted_indexed):
        order[orig_idx] = rank
    return order


kw_count = 0
for keyword in KEYWORDS:
    if not time_check():
        break
    col_order = keyword_to_order(keyword)
    num_cols = len(keyword)
    
    try:
        candidate = columnar_untranspose(intermediate_partial, num_cols, col_order)
        score, details = check_cribs(candidate)
        report_result(score, f"col-kw-{keyword}", candidate, '; '.join(details))
        kw_count += 1
    except Exception:
        pass
    
    try:
        candidate2 = columnar_transpose(intermediate_partial, num_cols, col_order)
        score2, details2 = check_cribs(candidate2)
        report_result(score2, f"col-kw-{keyword}-inv", candidate2, '; '.join(details2))
        kw_count += 1
    except Exception:
        pass

print(f"  Keyword-based columnar: tested {kw_count} configurations")


# ----------------------------------------------------------
# 5c. COLUMNAR TRANSPOSITION - All permutations for small widths
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 3: Columnar Transposition (exhaustive permutations for small widths)")
print("=" * 80)

perm_count = 0
for num_cols in range(2, 10):
    if not time_check():
        print(f"  Time limit reached at {num_cols} columns")
        break
    
    n_perms = math.factorial(num_cols)
    print(f"  Testing {num_cols} columns ({n_perms} permutations)...")
    
    if n_perms > 500000:
        print(f"    Skipping: too many permutations ({n_perms})")
        continue
    
    for perm in itertools.permutations(range(num_cols)):
        if not time_check():
            break
        col_order = list(perm)
        
        try:
            candidate = columnar_untranspose(intermediate_partial, num_cols, col_order)
            score = check_cribs_strict(candidate)
            if score >= 5:
                _, details = check_cribs(candidate)
                report_result(score, f"col-perm-{num_cols}-{col_order}", candidate, '; '.join(details))
            perm_count += 1
        except:
            pass
        
        try:
            candidate2 = columnar_transpose(intermediate_partial, num_cols, col_order)
            score2 = check_cribs_strict(candidate2)
            if score2 >= 5:
                _, details2 = check_cribs(candidate2)
                report_result(score2, f"col-perm-{num_cols}-{col_order}-inv", candidate2, '; '.join(details2))
            perm_count += 1
        except:
            pass

print(f"  Exhaustive permutations: tested {perm_count} configurations")


# ----------------------------------------------------------
# 5d. ROUTE CIPHERS
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 4: Route Ciphers (various grid dimensions)")
print("=" * 80)

route_count = 0
for num_rows in range(2, 50):
    if not time_check():
        break
    for num_cols in range(2, 50):
        if not time_check():
            break
        if num_rows * num_cols < N or num_rows * num_cols > N + max(num_rows, num_cols):
            continue

        for name, candidate in route_cipher_patterns(intermediate_partial, num_rows, num_cols):
            score = check_cribs_strict(candidate)
            if score >= 5:
                _, details = check_cribs(candidate)
                report_result(score, name, candidate, '; '.join(details))
            route_count += 1

print(f"  Route ciphers: tested {route_count} configurations")


# ----------------------------------------------------------
# 5e. COLUMNAR with KRYPTOS-derived orderings for larger widths
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 5: Columnar with KRYPTOS-alphabet-derived orderings (widths 10-20)")
print("=" * 80)

kryptos_count = 0

extended_keywords = KEYWORDS + [
    KRYPTOS_ALPHA[:i] for i in range(10, 21)
] + [
    'EASTNORTHEAST', 'OBKRUOXOGHULBSO',
    'KRYPTOSABCDEFGH', 'ABCDEFGHIJLMNQU',
]

for keyword in extended_keywords:
    if not time_check():
        break
    if len(keyword) < 10 or len(keyword) > 20:
        continue
    
    col_order = keyword_to_order(keyword)
    num_cols = len(keyword)
    
    try:
        candidate = columnar_untranspose(intermediate_partial, num_cols, col_order)
        score = check_cribs_strict(candidate)
        if score >= 4:
            _, details = check_cribs(candidate)
            report_result(score, f"col-ext-{keyword[:15]}", candidate, '; '.join(details))
        kryptos_count += 1
    except:
        pass
    
    try:
        candidate2 = columnar_transpose(intermediate_partial, num_cols, col_order)
        score2 = check_cribs_strict(candidate2)
        if score2 >= 4:
            _, details2 = check_cribs(candidate2)
            report_result(score2, f"col-ext-{keyword[:15]}-inv", candidate2, '; '.join(details2))
        kryptos_count += 1
    except:
        pass

print(f"  Extended keyword columnar: tested {kryptos_count} configurations")


# ----------------------------------------------------------
# 5f. SIMPLE PERIOD/OFFSET TRANSPOSITIONS
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 6: Simple periodic transpositions (skip ciphers)")
print("=" * 80)

skip_count = 0
for period in range(2, 50):
    if not time_check():
        break
    for start in range(period):
        indices = list(range(start, N, period))
        used = set(indices)
        for i in range(N):
            if i not in used:
                indices.append(i)
        
        if len(indices) != N:
            continue
        
        candidate = ''.join(intermediate_partial[i] for i in indices)
        score = check_cribs_strict(candidate)
        if score >= 5:
            _, details = check_cribs(candidate)
            report_result(score, f"skip-{period}-start{start}", candidate, '; '.join(details))
        skip_count += 1
        
        inv_indices = [0] * N
        for new_pos, old_pos in enumerate(indices):
            inv_indices[old_pos] = new_pos
        candidate2 = ''.join(intermediate_partial[inv_indices[i]] if inv_indices[i] < N else '?' for i in range(N))
        score2 = check_cribs_strict(candidate2)
        if score2 >= 5:
            _, details2 = check_cribs(candidate2)
            report_result(score2, f"skip-{period}-start{start}-inv", candidate2, '; '.join(details2))
        skip_count += 1

print(f"  Skip ciphers: tested {skip_count} configurations")


# ----------------------------------------------------------
# 5g. CONSTRAINT-BASED APPROACH with unknown key positions
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 7: Constraint-based approach with unknown key positions")
print("=" * 80)
print("\nFor each transposition, check if BOTH cribs are simultaneously consistent")
print("with the Vigenere key (including deriving unknown positions 16-20).\n")

constraint_hits = 0

def constraint_check_transposition(mapping_pt_to_int, method_name):
    """
    Given a mapping from plaintext positions to intermediate positions,
    check if the cribs are consistent.
    
    For each crib letter at plaintext position p:
      - The intermediate position is mapping_pt_to_int[p]
      - The K4 character at that intermediate position is K4[mapping_pt_to_int[p]]
      - The key slot is mapping_pt_to_int[p] % 29
      - If key slot is known: Vig_decrypt(K4[int_pos], key) must equal crib letter
      - If key slot is 16-20: compute what the key MUST be
    
    Returns (is_consistent, required_key_slots, match_count)
    """
    required = {}
    match_count = 0
    
    for crib, crib_start in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]:
        for j, crib_letter in enumerate(crib):
            pt_pos = crib_start + j
            if pt_pos not in mapping_pt_to_int:
                return False, {}, 0
            
            int_pos = mapping_pt_to_int[pt_pos]
            if int_pos < 0 or int_pos >= N:
                return False, {}, 0
            
            key_slot = int_pos % 29
            ct_char = K4[int_pos]
            
            if key_slot in KNOWN_KEY_LETTERS:
                key_char = KNOWN_KEY_LETTERS[key_slot]
                decrypted = vig_decrypt_char(ct_char, key_char)
                if decrypted == crib_letter:
                    match_count += 1
                else:
                    return False, {}, match_count
            else:
                ct_idx = KRYPTOS_ALPHA.index(ct_char)
                pt_idx = KRYPTOS_ALPHA.index(crib_letter)
                key_idx = (ct_idx - pt_idx) % len(KRYPTOS_ALPHA)
                needed_key = KRYPTOS_ALPHA[key_idx]
                
                if key_slot in required:
                    if required[key_slot] != needed_key:
                        return False, {}, match_count
                else:
                    required[key_slot] = needed_key
                
                match_count += 1
    
    return True, required, match_count


def get_columnar_mapping(n, num_cols, col_order):
    """
    Return mapping: plaintext_pos -> intermediate_pos
    for columnar transposition where:
      intermediate = columnar_transpose(plaintext, num_cols, col_order)
    """
    rows = math.ceil(n / num_cols)
    full_cols_count = n - (rows - 1) * num_cols
    
    int_pos = 0
    fwd = {}
    for c in col_order:
        col_len = rows if c < full_cols_count else rows - 1
        for r in range(col_len):
            pt_pos = r * num_cols + c
            if pt_pos < n:
                fwd[int_pos] = pt_pos
                int_pos += 1
    
    inv = {v: k for k, v in fwd.items()}
    return inv


def get_rail_fence_mapping(n, rails):
    """Return mapping: plaintext_pos -> intermediate_pos for rail fence."""
    if rails <= 1 or rails >= n:
        return {i: i for i in range(n)}
    
    rail_assignment = []
    rail = 0
    direction = 1
    for i in range(n):
        rail_assignment.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    
    rail_counts = [0] * rails
    for r_assign in rail_assignment:
        rail_counts[r_assign] += 1
    
    cum = [0] * rails
    for r in range(1, rails):
        cum[r] = cum[r - 1] + rail_counts[r - 1]
    
    rail_pos = [0] * rails
    mapping = {}
    for i in range(n):
        r = rail_assignment[i]
        mapping[i] = cum[r] + rail_pos[r]
        rail_pos[r] += 1
    
    return mapping


def process_constraint_hit(name, mapping_pt_to_int, required_keys):
    """Process a constraint hit: generate full plaintext and score it."""
    global constraint_hits
    constraint_hits += 1
    
    full_key = dict(KNOWN_KEY_LETTERS)
    full_key.update(required_keys)
    
    # Generate full intermediate text
    if len(full_key) >= 29:
        key_16_20 = ''.join(full_key.get(i, 'A') for i in range(16, 21))
        intermediate_full = get_intermediate_text(key_16_20)
    else:
        intermediate_full = intermediate_partial
    
    # Generate plaintext by inverting the mapping
    inv_map = {v: k for k, v in mapping_pt_to_int.items()}
    candidate_chars = ['?'] * N
    for pt_pos in range(N):
        if pt_pos in mapping_pt_to_int:
            int_pos = mapping_pt_to_int[pt_pos]
            if int_pos < len(intermediate_full):
                candidate_chars[pt_pos] = intermediate_full[int_pos]
    candidate = ''.join(candidate_chars)
    
    print(f"\n  *** CONSISTENT: {name}")
    print(f"      Required unknown key slots: {required_keys}")
    full_key_str = ''.join(full_key.get(i, '?') for i in range(29))
    print(f"      Full key: {full_key_str}")
    print(f"      Plaintext: {candidate}")
    
    # Verify cribs
    east_region = candidate[CRIB_EAST_POS:CRIB_EAST_POS+len(CRIB_EAST)]
    berlin_region = candidate[CRIB_BERLIN_POS:CRIB_BERLIN_POS+len(CRIB_BERLIN)]
    print(f"      Pos 21-33: {east_region} (want: {CRIB_EAST})")
    print(f"      Pos 63-73: {berlin_region} (want: {CRIB_BERLIN})")
    
    words = find_words_in_text(candidate, min_len=4)
    if words:
        print(f"      Words: {words[:15]}")
    
    qg_score = score_text_quadgrams(candidate)
    print(f"      Quadgram score: {qg_score:.4f}")
    
    report_result(24 + qg_score, f"CONSTRAINT-{name}", candidate,
                 f"required_keys={required_keys}, full_key={full_key_str}, qg={qg_score:.4f}")
    
    return candidate, qg_score


# 7a. Columnar transpositions - exhaustive for small widths
print("7a. Columnar constraint check (widths 2-9, all permutations)...")
for num_cols in range(2, 10):
    if not time_check():
        break
    n_perms = math.factorial(num_cols)
    if n_perms > 500000:
        continue
    
    tested = 0
    for perm in itertools.permutations(range(num_cols)):
        if not time_check():
            break
        col_order = list(perm)
        mapping = get_columnar_mapping(N, num_cols, col_order)
        
        is_ok, required_keys, match_count = constraint_check_transposition(mapping, f"col-{num_cols}")
        if is_ok and match_count == len(CRIB_EAST) + len(CRIB_BERLIN):
            process_constraint_hit(f"columnar-{num_cols}-cols-order-{col_order}", mapping, required_keys)
        tested += 1
    
    if tested > 0:
        print(f"    {num_cols} cols: tested {tested} permutations")

print(f"  Columnar constraint hits so far: {constraint_hits}")

# 7b. Rail fence constraint check
print("\n7b. Rail fence constraint check (2-50 rails)...")
rf_hits_before = constraint_hits
for rails in range(2, 51):
    if not time_check():
        break
    mapping = get_rail_fence_mapping(N, rails)
    
    is_ok, required_keys, match_count = constraint_check_transposition(mapping, f"rail-{rails}")
    if is_ok and match_count == len(CRIB_EAST) + len(CRIB_BERLIN):
        process_constraint_hit(f"rail-fence-{rails}-rails", mapping, required_keys)

print(f"  Rail fence constraint hits: {constraint_hits - rf_hits_before}")

# 7c. Keyword-based columnar with constraint check (larger widths)
print("\n7c. Keyword columnar constraint check...")
kw_hits_before = constraint_hits
all_kws = KEYWORDS + [
    KRYPTOS_ALPHA[:i] for i in range(2, 27)
] + [
    'EASTNORTHEAST', 'BERLINCLOCK', 'EASTBERLIN',
    'NORTHEASTBERLIN', 'CLOCKBERLIN', 'SHADOWFORCE',
    'IQLUSION', 'PALIMPSESTABSCISSA',
    # Some numeric patterns as keywords
    'ABCDEFG', 'ZYXWVUT', 'QWERTY', 'ASDFGH',
]

for keyword in all_kws:
    if not time_check():
        break
    if len(keyword) < 2:
        continue
    
    col_order = keyword_to_order(keyword)
    num_cols = len(keyword)
    mapping = get_columnar_mapping(N, num_cols, col_order)
    
    is_ok, required_keys, match_count = constraint_check_transposition(mapping, f"kw-{keyword}")
    if is_ok and match_count == len(CRIB_EAST) + len(CRIB_BERLIN):
        process_constraint_hit(f"keyword-{keyword}-({num_cols}-cols)", mapping, required_keys)

print(f"  Keyword constraint hits: {constraint_hits - kw_hits_before}")

# 7d. Route cipher constraint check
print("\n7d. Route cipher constraint check (all grid dimensions)...")
route_hits_before = constraint_hits

def get_route_mapping_forward(n, num_rows, num_cols, route_order):
    """
    Forward: plaintext written row-by-row, read by route_order -> intermediate
    intermediate[i] = plaintext[route_order[i] as grid pos]
    plaintext_pos -> intermediate_pos
    """
    mapping = {}
    for int_pos, (r, c) in enumerate(route_order):
        pt_pos = r * num_cols + c
        if pt_pos < n and int_pos < n:
            mapping[pt_pos] = int_pos
    return mapping


def get_route_mapping_reverse(n, num_rows, num_cols, route_order):
    """
    Reverse: plaintext written along route_order, read row-by-row -> intermediate
    intermediate[r*num_cols+c] = plaintext[route_step_k] where route_order[k]=(r,c)
    plaintext_pos k -> intermediate_pos r*num_cols+c
    """
    mapping = {}
    for k, (r, c) in enumerate(route_order):
        int_pos = r * num_cols + c
        if k < n and int_pos < n:
            mapping[k] = int_pos
    return mapping


def generate_route_orders(num_rows, num_cols):
    """Generate standard route orders for a grid."""
    routes = []
    
    # Column-by-column LR
    order = [(r, c) for c in range(num_cols) for r in range(num_rows)]
    routes.append(("col-LR", order))
    
    # Column-by-column RL
    order = [(r, c) for c in range(num_cols - 1, -1, -1) for r in range(num_rows)]
    routes.append(("col-RL", order))
    
    # Column-by-column LR, bottom-to-top
    order = [(r, c) for c in range(num_cols) for r in range(num_rows - 1, -1, -1)]
    routes.append(("col-LR-BT", order))
    
    # Snake columns
    order = []
    for c in range(num_cols):
        if c % 2 == 0:
            order.extend((r, c) for r in range(num_rows))
        else:
            order.extend((r, c) for r in range(num_rows - 1, -1, -1))
    routes.append(("snake-col", order))
    
    # Snake rows
    order = []
    for r in range(num_rows):
        if r % 2 == 0:
            order.extend((r, c) for c in range(num_cols))
        else:
            order.extend((r, c) for c in range(num_cols - 1, -1, -1))
    routes.append(("snake-row", order))
    
    # Row-by-row bottom to top
    order = [(r, c) for r in range(num_rows - 1, -1, -1) for c in range(num_cols)]
    routes.append(("row-BT", order))
    
    # Row-by-row right to left
    order = [(r, c) for r in range(num_rows) for c in range(num_cols - 1, -1, -1)]
    routes.append(("row-RL", order))
    
    # Spiral CW
    order = []
    top, bottom, left, right = 0, num_rows - 1, 0, num_cols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            order.append((top, c))
        top += 1
        for r in range(top, bottom + 1):
            order.append((r, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((bottom, c))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((r, left))
            left += 1
    routes.append(("spiral-CW", order))
    
    # Spiral CCW
    order = []
    top, bottom, left, right = 0, num_rows - 1, 0, num_cols - 1
    while top <= bottom and left <= right:
        for r in range(top, bottom + 1):
            order.append((r, left))
        left += 1
        for c in range(left, right + 1):
            order.append((bottom, c))
        bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((r, right))
            right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((top, c))
            top += 1
    routes.append(("spiral-CCW", order))
    
    # Diagonal TL-BR
    order = []
    for d in range(num_rows + num_cols - 1):
        for r in range(max(0, d - num_cols + 1), min(num_rows, d + 1)):
            c = d - r
            if 0 <= c < num_cols:
                order.append((r, c))
    routes.append(("diag-TLBR", order))
    
    # Diagonal TR-BL
    order = []
    for d in range(num_rows + num_cols - 1):
        for r in range(max(0, d - num_cols + 1), min(num_rows, d + 1)):
            c = (num_cols - 1) - (d - r)
            if 0 <= c < num_cols:
                order.append((r, c))
    routes.append(("diag-TRBL", order))
    
    return routes


route_tested = 0
for num_rows in range(2, 50):
    if not time_check():
        break
    for num_cols in range(2, 50):
        if not time_check():
            break
        if num_rows * num_cols < N or num_rows * num_cols > N + max(num_rows, num_cols):
            continue
        
        routes = generate_route_orders(num_rows, num_cols)
        
        for route_name, route_order in routes:
            # Direction 1: plaintext row-by-row, read by route -> intermediate
            mapping = get_route_mapping_forward(N, num_rows, num_cols, route_order)
            
            all_present = all(
                crib_start + j in mapping 
                for crib, crib_start in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]
                for j in range(len(crib))
            )
            
            if all_present:
                is_ok, required_keys, match_count = constraint_check_transposition(mapping, route_name)
                if is_ok and match_count == len(CRIB_EAST) + len(CRIB_BERLIN):
                    process_constraint_hit(f"route-fwd-{route_name}-{num_rows}x{num_cols}", mapping, required_keys)
            route_tested += 1
            
            # Direction 2: plaintext along route, read row-by-row -> intermediate
            mapping2 = get_route_mapping_reverse(N, num_rows, num_cols, route_order)
            
            all_present2 = all(
                crib_start + j in mapping2
                for crib, crib_start in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]
                for j in range(len(crib))
            )
            
            if all_present2:
                is_ok2, required_keys2, match_count2 = constraint_check_transposition(mapping2, route_name)
                if is_ok2 and match_count2 == len(CRIB_EAST) + len(CRIB_BERLIN):
                    process_constraint_hit(f"route-rev-{route_name}-{num_rows}x{num_cols}", mapping2, required_keys2)
            route_tested += 1

print(f"  Route cipher configurations tested: {route_tested}")
print(f"  Route cipher constraint hits: {constraint_hits - route_hits_before}")


# ----------------------------------------------------------
# 5h. DOUBLE COLUMNAR (two passes)
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 8: Double columnar transposition (keyword pairs)")
print("=" * 80)

double_col_hits_before = constraint_hits
double_count = 0

# For double columnar, test pairs of small keywords
small_keywords = [kw for kw in KEYWORDS if 2 <= len(kw) <= 8]
# Also add numeric orderings
for w in range(2, 8):
    small_keywords.append('A' * w)  # identity
    # reversed
    small_keywords.append(''.join(chr(ord('Z') - i) for i in range(w)))

for kw1 in small_keywords[:20]:
    if not time_check():
        break
    for kw2 in small_keywords[:20]:
        if not time_check():
            break
        order1 = keyword_to_order(kw1)
        order2 = keyword_to_order(kw2)
        n1 = len(kw1)
        n2 = len(kw2)
        
        # Apply two columnar untranspositions
        try:
            step1 = columnar_untranspose(intermediate_partial, n1, order1)
            candidate = columnar_untranspose(step1, n2, order2)
            score = check_cribs_strict(candidate)
            if score >= 6:
                _, details = check_cribs(candidate)
                report_result(score, f"double-col-{kw1}-{kw2}", candidate, '; '.join(details))
            double_count += 1
        except:
            pass

print(f"  Double columnar: tested {double_count} configurations")


# ----------------------------------------------------------
# 5i. SWAPPED HALVES / REVERSAL
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 9: Simple permutations (reverse, swap halves, etc.)")
print("=" * 80)

simple_count = 0

# Reverse
candidate = intermediate_partial[::-1]
score, details = check_cribs(candidate)
report_result(score, "reverse", candidate, '; '.join(details))
simple_count += 1

# Swap halves
for split in range(20, 80):
    candidate = intermediate_partial[split:] + intermediate_partial[:split]
    score = check_cribs_strict(candidate)
    if score >= 4:
        _, details = check_cribs(candidate)
        report_result(score, f"rotate-{split}", candidate, '; '.join(details))
    simple_count += 1

# Reverse + rotate
for split in range(20, 80):
    rev = intermediate_partial[::-1]
    candidate = rev[split:] + rev[:split]
    score = check_cribs_strict(candidate)
    if score >= 4:
        _, details = check_cribs(candidate)
        report_result(score, f"rev-rotate-{split}", candidate, '; '.join(details))
    simple_count += 1

# Interleave odd/even
evens = intermediate_partial[::2]
odds = intermediate_partial[1::2]
for combo_name, candidate in [
    ("even-odd", evens + odds),
    ("odd-even", odds + evens),
    ("interleave-eo", ''.join(a+b for a,b in zip(evens, odds)) + (evens[len(odds):] if len(evens) > len(odds) else '')),
    ("interleave-oe", ''.join(a+b for a,b in zip(odds, evens)) + (odds[len(evens):] if len(odds) > len(evens) else '')),
]:
    if len(candidate) >= N:
        candidate = candidate[:N]
    score = check_cribs_strict(candidate)
    if score >= 3:
        _, details = check_cribs(candidate)
        report_result(score, combo_name, candidate, '; '.join(details))
    simple_count += 1

print(f"  Simple permutations: tested {simple_count} configurations")


# ----------------------------------------------------------
# PHASE 10: Extended columnar with constraint (widths 10-20)
# using systematic numeric orderings
# ----------------------------------------------------------
print("\n" + "=" * 80)
print("PHASE 10: Systematic columnar constraint (widths 10-15)")
print("=" * 80)

# For widths 10+, we can't enumerate all permutations.
# But with constraint checking, we can be smarter:
# We know which plaintext positions need to map to which intermediate positions.
# For columnar transposition with W columns:
#   plaintext[r*W+c] -> intermediate[position in column c's segment]
# 
# The crib at plaintext pos 21-33 tells us which columns those positions are in.
# The crib at plaintext pos 63-73 tells us which columns those positions are in.
# We can check if there's a consistent column ordering.

sys10_count = 0
for num_cols in range(10, 16):
    if not time_check():
        break
    
    rows = math.ceil(N / num_cols)
    full_cols = N - (rows - 1) * num_cols
    
    # For each crib letter, determine which column it's in (from plaintext position)
    # and what its row is
    crib_requirements = []  # (crib_letter, pt_pos, column, row_in_col)
    
    for crib, crib_start in [(CRIB_EAST, CRIB_EAST_POS), (CRIB_BERLIN, CRIB_BERLIN_POS)]:
        for j, letter in enumerate(crib):
            pt_pos = crib_start + j
            col = pt_pos % num_cols
            row = pt_pos // num_cols
            crib_requirements.append((letter, pt_pos, col, row))
    
    # For a given column ordering, the column at rank r in the ordering
    # starts at position sum of lengths of columns with rank < r.
    # Column c has length: rows if c < full_cols else rows-1
    
    # We need to find a permutation of columns such that:
    # for each crib requirement, the intermediate position maps correctly.
    
    # The intermediate position of plaintext[r*W+c] is:
    # sum of column lengths for columns that come before c in the ordering, plus row
    
    # This is the full columnar mapping, which we already have.
    # Since we can't enumerate all perms for 10+ columns, let's try:
    # 1. Random sampling
    # 2. Building partial orderings from constraints
    
    import random
    random.seed(42)
    
    # Try 10000 random permutations for each width
    for trial in range(10000):
        if not time_check():
            break
        perm = list(range(num_cols))
        random.shuffle(perm)
        
        mapping = get_columnar_mapping(N, num_cols, perm)
        is_ok, required_keys, match_count = constraint_check_transposition(mapping, f"col-{num_cols}-rand")
        if is_ok and match_count == len(CRIB_EAST) + len(CRIB_BERLIN):
            process_constraint_hit(f"columnar-{num_cols}-random-{perm}", mapping, required_keys)
        sys10_count += 1

print(f"  Systematic columnar (10-15): tested {sys10_count} configurations")
print(f"  Total constraint hits: {constraint_hits}")


# ============================================================
# FINAL SUMMARY
# ============================================================
elapsed = time.time() - start_time
print("\n" + "=" * 80)
print(f"FINAL SUMMARY (elapsed: {elapsed:.1f}s)")
print("=" * 80)

results.sort(key=lambda x: -x[0])

print(f"\nTotal results stored: {len(results)}")

# Show top 30 results
print(f"\nTop 30 results by crib match score:")
print("-" * 80)
for i, (score, name, candidate, details) in enumerate(results[:30]):
    print(f"\n{i+1}. Score={score:.1f}  Method: {name}")
    print(f"   Text: {candidate}")
    if details:
        print(f"   Details: {details[:150]}")
    words = find_words_in_text(candidate, min_len=5)
    if words:
        print(f"   Words (5+): {words[:8]}")

# Specifically highlight any constraint-based hits
constraint_results = [r for r in results if 'CONSTRAINT' in r[1]]
if constraint_results:
    print(f"\n{'='*80}")
    print(f"CONSTRAINT-BASED HITS (full crib consistency): {len(constraint_results)}")
    print(f"{'='*80}")
    for score, name, candidate, details in constraint_results:
        print(f"\n  Method: {name}")
        print(f"  Score: {score:.2f}")
        print(f"  Plaintext: {candidate}")
        print(f"  Details: {details}")
        words = find_words_in_text(candidate, min_len=4)
        if words:
            print(f"  Words: {words[:20]}")
        qg = score_text_quadgrams(candidate)
        print(f"  Quadgram score: {qg:.4f}")
else:
    print(f"\nNo constraint-based hits found (no transposition produced consistent cribs).")
    print("This suggests either:")
    print("  1. The transposition type tested is not the one used")
    print("  2. The 'transposition first' hypothesis may not be correct for these methods")
    print("  3. The crib positions may have slight variations")
    print("  4. A more exotic transposition (e.g., Myszkowski, irregular columnar) is needed")

print(f"\nScript completed in {elapsed:.1f} seconds.")
