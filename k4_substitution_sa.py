#!/usr/bin/env python3
"""
KEY HYPOTHESIS: K4 = Vigenere(Substitution(Plaintext), key)

The "masking" Scheidt described is a SIMPLE SUBSTITUTION applied to the
plaintext BEFORE Vigenere encryption. This would:
- Destroy English frequency patterns (explaining low IC)
- Be "simple, can be remembered, not mathematical"
- Explain why "frequency analysis won't help"

Since the two cribs cover DISJOINT key positions mod 29, ANY substitution
gives a consistent key. We optimize the substitution using SA to maximize
English-likeness of the final plaintext.

Process:
  CT[i] = Vig(Sub(PT[i]), key[i%29])   with KRYPTOS alphabet
  Our derived key assumes Sub = identity, giving wrong key if Sub != identity.

  true_key[i%29] = (CT_idx - Sub(PT)_idx) % 26
  our_key[i%29] = (CT_idx - PT_idx) % 26

  If we guess Sub, we can derive the TRUE key and decrypt everything.
"""
import math, random, time
from collections import Counter

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c): return KRYPTOS.index(c)
def k_chr(i): return KRYPTOS[i % 26]

# Load quadgrams
QG = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QG[parts[0]] = int(parts[1])
total = sum(QG.values())
QG_LOG = {k: math.log10(v/total) for k, v in QG.items()}
QG_FLOOR = math.log10(0.01/total)

def qscore(text):
    score = 0
    for i in range(len(text)-3):
        q = text[i:i+4]
        score += QG_LOG.get(q, QG_FLOOR)
    return score

# Known cribs
CRIB1_TEXT = "EASTNORTHEAST"
CRIB1_START = 21
CRIB2_TEXT = "BERLINCLOCK"
CRIB2_START = 63

def decrypt_with_sub(sub_perm):
    """Given a substitution permutation, derive the true key and decrypt.

    sub_perm maps plaintext index -> masked index.
    E.g., if PT letter has KRYPTOS index p, the masked letter has index sub_perm[p].

    true_key[kp] = (CT_idx - sub_perm[PT_idx]) % 26
    """
    # Derive key from crib 1
    key = {}
    for j, pt_char in enumerate(CRIB1_TEXT):
        ct_pos = CRIB1_START + j
        kp = ct_pos % 29
        pt_idx = k_idx(pt_char)
        ct_idx = k_idx(K4[ct_pos])
        key_val = (ct_idx - sub_perm[pt_idx]) % 26
        key[kp] = key_val

    # Derive key from crib 2
    for j, pt_char in enumerate(CRIB2_TEXT):
        ct_pos = CRIB2_START + j
        kp = ct_pos % 29
        pt_idx = k_idx(pt_char)
        ct_idx = k_idx(K4[ct_pos])
        key_val = (ct_idx - sub_perm[pt_idx]) % 26
        if kp in key:
            if key[kp] != key_val:
                return None, None  # Conflict! This sub doesn't work
        else:
            key[kp] = key_val

    # Fill unknown positions (16-20) with best guesses
    # For now, use IC-maximizing values
    for kp in range(29):
        if kp not in key:
            # Try all 26 values, pick the one that maximizes IC
            best_ic = -1
            best_val = 0
            positions = [i for i in range(97) if i % 29 == kp]
            ct_indices = [k_idx(K4[i]) for i in positions]
            for v in range(26):
                pt_indices = [(c - v) % 26 for c in ct_indices]
                # Then un-substitute
                inv_sub = [0] * 26
                for idx, s in enumerate(sub_perm):
                    inv_sub[s] = idx
                real_pt = [inv_sub[p] for p in pt_indices]
                counts = Counter(real_pt)
                n = len(real_pt)
                if n < 2:
                    continue
                ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
                if ic > best_ic:
                    best_ic = ic
                    best_val = v
            key[kp] = best_val

    # Decrypt all positions
    inv_sub = [0] * 26
    for idx, s in enumerate(sub_perm):
        inv_sub[s] = idx

    pt = []
    for i in range(97):
        kp = i % 29
        ct_idx = k_idx(K4[i])
        masked_idx = (ct_idx - key[kp]) % 26
        real_idx = inv_sub[masked_idx]
        pt.append(k_chr(real_idx))

    return ''.join(pt), key

print("=" * 80)
print("SUBSTITUTION + VIGENERE SA OPTIMIZATION")
print("=" * 80)

# Start with identity substitution
best_sub = list(range(26))
best_pt, best_key = decrypt_with_sub(best_sub)
best_score = qscore(best_pt) if best_pt else -999999
print(f"Identity sub score: {best_score:.2f}")
print(f"  PT: {best_pt}")

# SA to optimize substitution
T = 5.0
T_min = 0.001
alpha = 0.9998
current_sub = list(range(26))
current_pt = best_pt
current_score = best_score

iterations = 0
max_iter = 500000
restarts = 0
no_improve = 0

t0 = time.time()

while restarts < 10:
    T = 5.0
    iterations = 0

    while T > T_min and iterations < max_iter:
        iterations += 1

        # Mutate: swap two positions in the substitution
        new_sub = current_sub[:]
        i, j = random.sample(range(26), 2)
        new_sub[i], new_sub[j] = new_sub[j], new_sub[i]

        new_pt, new_key = decrypt_with_sub(new_sub)
        if new_pt is None:
            T *= alpha
            continue

        new_score = qscore(new_pt)

        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / T):
            current_sub = new_sub
            current_pt = new_pt
            current_score = new_score

            if current_score > best_score:
                best_score = current_score
                best_sub = current_sub[:]
                best_pt = current_pt
                best_key = new_key
                no_improve = 0

                if best_score > -600:
                    elapsed = time.time() - t0
                    print(f"\n  *** NEW BEST: {best_score:.2f} ({elapsed:.1f}s) ***")
                    print(f"  PT: {best_pt}")
                    sub_str = ''.join(k_chr(s) for s in best_sub)
                    print(f"  Sub: {sub_str}")
                    # Check for words
                    for w in ["THE", "AND", "THAT", "THIS", "WITH", "FROM", "HAVE",
                              "BERLIN", "CLOCK", "EAST", "NORTH", "SLOWLY", "BETWEEN",
                              "SHADOW", "HIDDEN", "SECRET", "LIGHT", "DARK", "TIME"]:
                        if w in best_pt:
                            pos = best_pt.index(w)
                            print(f"  *** Found '{w}' at position {pos} ***")

        T *= alpha

    restarts += 1
    elapsed = time.time() - t0
    print(f"\n  Restart {restarts}: best={best_score:.2f} ({elapsed:.1f}s)")

    # Restart from a random permutation
    current_sub = list(range(26))
    random.shuffle(current_sub)
    pt, key = decrypt_with_sub(current_sub)
    if pt:
        current_pt = pt
        current_score = qscore(pt)
    else:
        current_sub = list(range(26))
        current_pt = best_pt
        current_score = best_score

# Also try specific substitutions
print("\n" + "=" * 80)
print("SPECIFIC SUBSTITUTION TESTS")
print("=" * 80)

# Atbash in KRYPTOS alphabet
atbash = [(25 - i) % 26 for i in range(26)]
pt, key = decrypt_with_sub(atbash)
if pt:
    s = qscore(pt)
    print(f"\nAtbash: score={s:.2f}")
    print(f"  PT: {pt}")

# Caesar shifts
for shift in range(1, 26):
    caesar = [(i + shift) % 26 for i in range(26)]
    pt, key = decrypt_with_sub(caesar)
    if pt:
        s = qscore(pt)
        if s > -600:
            print(f"\nCaesar shift {shift}: score={s:.2f}")
            print(f"  PT: {pt}")

# Keyed substitution alphabets
for keyword in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "SHADOW",
                "SANBORN", "SCHEIDT", "LANGLEY", "COMPASS", "SECRET"]:
    # Build keyed alphabet
    seen = set()
    keyed = []
    for c in keyword:
        if c not in seen and c in KRYPTOS:
            keyed.append(k_idx(c))
            seen.add(c)
    for i in range(26):
        c = KRYPTOS[i]
        if c not in seen:
            keyed.append(i)
            seen.add(c)

    if len(keyed) == 26:
        pt, key = decrypt_with_sub(keyed)
        if pt:
            s = qscore(pt)
            if s > -620:
                print(f"\nKeyed '{keyword}': score={s:.2f}")
                print(f"  PT: {pt}")

# Show final best result
print("\n" + "=" * 80)
print("BEST RESULT")
print("=" * 80)
print(f"Score: {best_score:.2f}")
print(f"PT: {best_pt}")
sub_str = ''.join(k_chr(s) for s in best_sub)
print(f"Sub mapping: {sub_str}")
print(f"Sub (plain->masked): ", end="")
for i in range(26):
    print(f"{KRYPTOS[i]}->{KRYPTOS[best_sub[i]]}", end=" ")
print()

# Check IC of result
from collections import Counter
counts = Counter(best_pt)
n = len(best_pt)
ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
print(f"IC: {ic:.4f}")

# Check for English words
WORDS = ["THE", "AND", "THAT", "THIS", "WITH", "FROM", "HAVE", "WILL",
         "BERLIN", "CLOCK", "EAST", "NORTH", "POINT", "SLOWLY", "BETWEEN",
         "SHADOW", "HIDDEN", "SECRET", "LAYER", "COMPASS", "DEGREE", "HOLD",
         "UNDER", "GROUND", "TIME", "LIGHT", "DARK", "WATCH", "THEY",
         "THERE", "WHERE", "WHICH", "THEIR", "ABOUT", "COULD", "WOULD",
         "WHAT", "WHEN", "THAN", "BEEN", "INTO", "SOME", "ONLY"]
found = [w for w in WORDS if w in best_pt]
if found:
    print(f"English words found: {found}")

print("\nDone.")
