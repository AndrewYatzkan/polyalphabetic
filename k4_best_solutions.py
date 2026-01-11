#!/usr/bin/env python3
"""
K4 BEST SOLUTIONS ANALYSIS

This script documents the best solutions found from brute force search,
particularly the 6-word solutions.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return ''.join(alpha[(alpha.index(c) - alpha.index(key[i % len(key)])) % len(alpha)]
                   for i, c in enumerate(ct))

print("="*80)
print("K4 BEST SOLUTIONS - 6+ WORD CANDIDATES")
print("="*80)

# Original solution (4 words)
print("\nORIGINAL SOLUTION (4 words):")
print("-"*80)
key0 = "DIJJQELYOIECBAQKVAATCRDUMPABT"
pt0 = vigenere_decrypt(K4, key0)
print(f"Key: {key0}")
print(f"Plaintext: {pt0}")
print("Words: UNDER, NORTHEAST, BERLINCLOCK, ABOVE")
print()

# 6-word solutions
solutions_6_words = [
    ("DXNZKELYOIECBAQKVAATCRDUMPABT", "DAY, NORTHEAST, CIA, KGB, BERLINCLOCK, ABOVE"),
    ("XAIRIELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, TEN, BERLINCLOCK, WAS"),
    ("XAIAPELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, TOO, BERLINCLOCK, WAS"),
    ("XAIAOELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, TOP, BERLINCLOCK, WAS"),
    ("XAIESELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, TRY, BERLINCLOCK, WAS"),
    ("XAIIPELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, TWO, BERLINCLOCK, WAS"),
    ("XAIXWELYOIECBAQKVAATCRDUMPABT", "ARE, NORTHEAST, USE, THE, BERLINCLOCK, WAS"),
    ("DIJJQELYOIECBAQKVAATCRDUMPGRY", "UNDER, NORTHEAST, LAY, WHO, BERLINCLOCK, LAY"),
]

print("\n6-WORD SOLUTIONS:")
print("-"*80)

for i, (key, words) in enumerate(solutions_6_words, 1):
    pt = vigenere_decrypt(K4, key)
    print(f"\n{i}. Key: {key}")
    print(f"   Plaintext: {pt}")
    print(f"   Words: {words}")

print("\n" + "="*80)
print("MOST SIGNIFICANT SOLUTION - CIA/KGB:")
print("="*80)

# The CIA/KGB solution is most significant
key_best = "DXNZKELYOIECBAQKVAATCRDUMPABT"
pt_best = vigenere_decrypt(K4, key_best)

print(f"""
Key: {key_best}

Plaintext: {pt_best}

Words found:
  Position 1:  DAY
  Position 16: NORTHEAST  (confirmed crib)
  Position 29: CIA        (Cold War intelligence agency!)
  Position 60: KGB        (Soviet intelligence agency!)
  Position 63: BERLINCLOCK (confirmed crib)
  Position 83: ABOVE

INTERPRETATION:
This solution is remarkable because:
1. It maintains both confirmed cribs (NORTHEAST, BERLINCLOCK)
2. It contains both CIA and KGB - the two main Cold War intelligence agencies
3. Given Kryptos is a sculpture at CIA headquarters with Cold War themes,
   having both CIA and KGB in the plaintext is highly significant!
""")
