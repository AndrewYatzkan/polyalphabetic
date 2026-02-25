#!/usr/bin/env python3
"""
K4 Position-Dependent Analysis: Summary of key findings.
Focus on the RESULT candidate and structural analysis.
"""

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
PERIOD = 29

def k_index(ch): return KRYPTOS_ALPHA.index(ch)
def k_char(idx): return KRYPTOS_ALPHA[idx % 26]

print("=" * 80)
print("K4 POSITION-DEPENDENT KEY MODIFICATION: EXECUTIVE SUMMARY")
print("=" * 80)

print("""
STRUCTURAL FINDING: THE KEY CONSISTENCY TEST IS INHERENTLY UNDERDETERMINED
=========================================================================

The two known cribs provide key derivations at these positions:

  EASTNORTHEAST (pos 21-33):
    Period 0 (pos 21-28) -> key slots 21, 22, 23, 24, 25, 26, 27, 28
    Period 1 (pos 29-33) -> key slots  0,  1,  2,  3,  4

  BERLINCLOCK (pos 63-73):
    Period 2 (pos 63-73) -> key slots  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15

CRITICAL OBSERVATION: Each key slot is derived from EXACTLY ONE period.
No key slot has derivations from multiple periods. This means:

  ANY function f(i) = g(i//29) that depends only on the period number
  will appear PERFECTLY CONSISTENT with the crib data.

  The "true key" just gets shifted by a constant per period:
    Slots 21-28: true_key = derived - g(0)
    Slots  0-4:  true_key = derived - g(1)
    Slots  5-15: true_key = derived - g(2)

  Since g(0), g(1), g(2) can be chosen freely, we have 26^3 = 17,576
  possible combinations that all satisfy the cribs perfectly.

IMPLICATION: Crib consistency alone CANNOT detect or rule out a
period-based second layer. Only English-quality plaintext can distinguish.
""")

print("=" * 80)
print("TOP CANDIDATE: THE 'RESULT' DECRYPTION")
print("=" * 80)

# The RESULT candidate: g=[0,25,19,?], unknown key slots KIQPL
g = [0, 25, 19, 0]
key_str = "SPQRPMXCFVMJIHRAKIQPLRDUMRIYW"
key_vals = [k_index(ch) for ch in key_str]

pt = []
for i in range(len(CT)):
    slot = i % PERIOD
    period = min(i // PERIOD, 3)
    pt.append(k_char((k_index(CT[i]) - key_vals[slot] - g[period]) % 26))
pt = ''.join(pt)

print(f"""
  g offsets:  [0, 25, 19, ?] (per period)
  Full key:   {key_str}
  Unknown 5:  KIQPL (slots 16-20)

  Plaintext (g3=0):
    Period 0 [00-28]: {pt[0:29]}
    Period 1 [29-57]: {pt[29:58]}
    Period 2 [58-86]: {pt[58:87]}
    Period 3 [87-96]: {pt[87:97]}

  Full: {pt}

  English words found:
    pos 17: WHOSE (5 letters)
    pos 45: RESULT (6 letters)
    pos 50: TASK (4 letters)
    pos 33: THAI (4 letters)
    pos 43: SORE (4 letters)
    pos 18: HOSE (4 letters)

  While WHOSE, RESULT, and TASK are suggestive, the surrounding text
  (ZOSKMGKVRMPRNMTD, XNSMF, TOWTITRYXJAMD) is not readable English.

  Score: -6.0024 (English typically scores -2.3 to -2.0)
""")

print("=" * 80)
print("ANALYSIS OF ALL TOP CANDIDATES")
print("=" * 80)

print("""
  Ranking by quadgram score:
  
  #1: g=[0,14,20,15] score=-5.875 "...EMBESW+ENE+KNROERGMOML+IAHANI+BC+SINTO..."
  #2: g=[0,14,20,25] score=-5.893 (same as #1, different g3)
  #3: g=[0,14, 8, 0] score=-5.898 "...EBARD+ENE+HAINZIRSNSO+BADYS+BC+ERRE..."
      Contains: BARD, THAI, LOCKER (6 letters!)
  
  Ranking by word count:
  #1: g=[0,25,19,*]  6 words: WHOSE, RESULT, TASK, HOSE, THAI, SORE
  
  None of these produce readable English sentences.
  The scores (-5.8 to -6.1) are well below English (-2.3 to -2.0)
  and closer to random text (-4.5).
""")

print("=" * 80)
print("CONCLUSIONS")
print("=" * 80)

print("""
1. STRUCTURAL LIMITATION: With the current two cribs (ENE and BC), it is
   IMPOSSIBLE to distinguish simple Vigenere from any period-based second
   layer using consistency checks alone. The cribs cover disjoint key slots
   in each period.

2. BRUTE FORCE LIMITATIONS: Even testing all 26^3 period offsets with
   beam-search over 5 unknown key positions, no combination produces
   plaintext that reads as coherent English.

3. BEST CANDIDATES: The highest-scoring plaintexts contain isolated
   English words (RESULT, WHOSE, TASK, LOCKER, BARD) but are embedded
   in gibberish. This is consistent with random chance given 97 characters
   of text being searched over thousands of parameter combinations.

4. WHAT WOULD HELP:
   a. A third crib that overlaps key slots with an existing crib but in
      a different period would directly reveal any period-dependent shift.
   b. Specifically: any known plaintext at positions 50-62 (period 1,
      key slots 21-28 or 0-4) would overlap with ENE-derived key slots
      from period 0 and could detect the shift.
   c. Similarly, plaintext at positions 5-20 (period 0, slots 5-20)
      would overlap with BC-derived slots from period 2.

5. THE FUNDAMENTAL CHALLENGE: K4 remains unsolved because:
   - The key has 5 unknown positions out of 29
   - There may or may not be a second cipher layer
   - The two known cribs, while valuable, are positioned such that they
     cannot disambiguate period-level modifications
   - The plaintext is only 97 characters, too short for reliable
     statistical discrimination between candidate solutions

6. PROMISING DIRECTIONS:
   - f(i) = c*(i//29) with c=25 and unknown slots KIQPL produced 6
     English words including the 6-letter RESULT - worth investigating
     further with alternative f(i) parameterizations
   - The LOCKER finding (from BERLINCLOCKERRE) at g=[0,14,8,*] is
     interesting since CLOCK is a known crib
   - Autokey variants, transposition layers, and non-period-based f(i)
     functions deserve continued exploration
""")
