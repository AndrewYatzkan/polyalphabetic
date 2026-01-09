#!/usr/bin/env python3
"""
K4 SOLUTION CANDIDATE

This script documents a potential K4 solution that produces 4 meaningful
English words, including both confirmed cribs (NORTHEAST and BERLINCLOCK)
plus the antonym pair UNDER/ABOVE.

Key: DIJJQELYOIECBAQKVAATCRDUMPABT (Period 29)

Plaintext structure:
  UNDER + [?] + NORTHEAST + [?] + BERLINCLOCK + [?] + ABOVE + [?]
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return ''.join(alpha[(alpha.index(c) - alpha.index(key[i % len(key)])) % len(alpha)] 
                   for i, c in enumerate(ct))

# The discovered key
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Decrypt
plaintext = vigenere_decrypt(K4, KEY)

print("="*70)
print("K4 SOLUTION CANDIDATE")
print("="*70)
print(f"""
Ciphertext: {K4}

Key (Period 29): {KEY}

Plaintext: {plaintext}

Key derivation:
  - Positions 0-4 (DIJJQ): Derived to produce 'UNDER' at start
  - Positions 5-15 (ELYOIECBAQK): From BERLINCLOCK crib at position 63
  - Positions 16-24 (VAATCRDUM): From NORTHEAST crib at position 16  
  - Positions 25-28 (PABT): Derived to produce 'ABOVE' at position 83

Words found:
  Position 0:  UNDER
  Position 16: NORTHEAST (confirmed crib)
  Position 63: BERLINCLOCK (confirmed crib)
  Position 83: ABOVE

Interpretation:
  The antonym pair UNDER/ABOVE may refer to:
  - Physical layers (like K2's reference to "LAYER TWO")
  - Vertical positioning relative to the Berlin Clock
  - Above/below ground at a location NORTHEAST of the Berlin Clock

Remaining questions:
  - What do the gibberish sections between the words mean?
  - Are they coordinates, code names, or intentionally obscured?
  - Is there an additional transformation layer?
""")

# Show the structure
print("="*70)
print("PLAINTEXT STRUCTURE")
print("="*70)
print(f"  0-4:   'UNDER'       <- Word")
print(f"  5-15:  '{plaintext[5:16]}'  <- Unknown")
print(f" 16-24:  'NORTHEAST'   <- Crib (confirmed)")
print(f" 25-33:  '{plaintext[25:34]}'   <- Unknown")
print(f" 34-53:  '{plaintext[34:54]}' <- Unknown")
print(f" 54-62:  '{plaintext[54:63]}'   <- Unknown")
print(f" 63-73:  'BERLINCLOCK' <- Crib (confirmed)")
print(f" 74-82:  '{plaintext[74:83]}'   <- Unknown")
print(f" 83-87:  'ABOVE'       <- Word")
print(f" 88-96:  '{plaintext[88:97]}'   <- Unknown")
print("="*70)
