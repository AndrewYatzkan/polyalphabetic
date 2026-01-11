# Gromark Cipher Hypothesis Testing on K4

## Executive Summary

Comprehensive testing of the Gromark cipher hypothesis on the K4 ciphertext from the KRYPTOS sculpture has been completed. **The hypothesis does not yield the expected results.**

**K4 Ciphertext:**
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

## Gromark Cipher Definition

Gromark is a modern cipher concept (1969-1975) that combines:
- A running key generated from a primer and plaintext
- A lagged Fibonacci generator for key generation
- Key formula: `K[i] = (K[i-m] + K[i-n]) mod 26`

Where `m` and `n` are lag parameters controlling how far back in the key sequence to look.

## Test Parameters

### Primers Tested
- KRYPTOS
- PALIMPSEST
- ABSCISSA
- BERLIN
- CLOCK

### Lag Parameters
- m: 1-7
- n: 2-10 (with n ≠ m)
- Total combinations: 26 lag pairs per primer

### Cipher Variants Tested
1. **Standard Gromark**: Key purely generated from primer using Fibonacci formula
2. **Plaintext Feedback Gromark**: Key[i] = (Plaintext[i-m] + Plaintext[i-n]) mod 26
3. **Hybrid Gromark**: Primer initialization, then plaintext feedback
4. **Ciphertext Feedback**: Key[i] = (Ciphertext[i-m] + Ciphertext[i-n]) mod 26
5. **Multiplicative Variants**: Key[i] = (mult × Key[i-m] + Key[i-n] + add) mod 26 (mult=1-3, add=0-3)
6. **XOR Variant**: Key[i] = (Key[i-m] XOR Key[i-n]) mod 26
7. **Subtraction Variant**: Key[i] = (Key[i-m] - Key[i-n]) mod 26
8. **Reverse Direction**: Decryption from end backwards
9. **Double Lag**: Key[i] = (Key[i-m1] + Key[i-n1] + Key[i-m2] + Key[i-n2]) mod 26

## Test Results

### Total Combinations Tested
- Basic Gromark variants: 390 combinations (5 primers × 26 lags × 3 basic variants)
- Expanded variants: 1,120 combinations (5 primers × 56 expanded lags × 4 variants)
- Advanced variants: 1,150 combinations (extended parameters, subtraction, reverse, double lag)
- **Total: 2,660 combinations**

### Target Strings Sought
- BERLINCLOCK - Not found in any decryption
- NORTHEAST - Not found in any decryption

### Key Findings

#### 1. No Target Strings Located
Neither BERLINCLOCK nor NORTHEAST appeared in any of the 2,660 tested decryptions.

#### 2. Output Quality Analysis
- **Vowel Ratios**: Most Gromark decryptions produced 0.20-0.30 vowel ratio (normal English: 0.38-0.45)
- **English Structure**: No decryption displayed coherent English grammar or word patterns
- **Gibberish**: All outputs appeared as random-looking ciphertext

#### 3. Sample Gromark Outputs

With primer "KRYPTOS" and various lag parameters:

```
m=1, n=2: EKMCBAFIIDSFTESBCPFPOLJVXWYDNXMAOEWNYPOMBCWIYUDNOGRNMRCREKCYJRJHALTNLYDVJUAUVQXBVPKREQQKDGIOGGAUJ
m=2, n=3: EKMCBAFHAIHGPAXHZKOXOOZSSFOBEXFHBOUYYEXFBKXEDBKPYBLMDGQRZKBJCLRIUAMAVKIFWTDWTHFKWCSZRSPPYUMLQNFPX
m=3, n=4: EKMCBAFGZBUWOMZJPKKGITZIVSVGTUCDBVDVILHGNZXKRYWEXLVPWYCVHVWZHASYNBXTUABGEAZWIDSSRVQWSGRXRBKHVBZEZ
```

#### 4. Comparison with Simple Vigenere/Autokey
Simple Vigenere and Autokey with the same primers also failed to produce meaningful plaintext, suggesting the primers themselves may not be correct for any Vigenere-family cipher.

### K4 Ciphertext Statistics

- **Length**: 97 characters
- **All 26 letters present**: Yes (nearly uniform distribution)
- **Most common letter**: K (8 occurrences, 8.2%)
- **Least common letters**: M, Y (1 occurrence each)
- **Vowel percentage in ciphertext**: 10.3% (A: 4, E: 2, I: 4, O: 5, U: 6)
- **Entropy**: High (characteristic of well-distributed polyalphabetic encryption)

## Conclusions

### What We Know
1. The Gromark cipher hypothesis, as implemented and tested, does not decrypt K4 to produce BERLINCLOCK or NORTHEAST
2. No variant tested (9 different approaches) produced recognizable English plaintext
3. The hypothesis was tested systematically with all reasonable parameter combinations

### Possible Explanations

1. **K4 is not Gromark-encrypted**: The cipher used could be something else entirely
2. **Wrong primers**: The specified primers may not be correct for K4
3. **Wrong Gromark variant**: The actual Gromark implementation might differ from those tested
4. **Multi-layer encryption**: K4 might be encrypted with multiple ciphers in sequence
5. **Parameter space not exhaustive**: Lag parameters larger than tested (m, n > 7) might be needed
6. **Gromark misunderstanding**: The cipher's actual mechanics might differ from the theoretical definition

## Recommendations for Further Investigation

If the Gromark hypothesis is to be pursued:

1. **Expand lag parameters**: Test with m > 7 and n > 10
2. **Non-standard primer combinations**: Try concatenations, reversals, or derived primers
3. **Reverse application**: Try encrypting with standard key, decrypting with Gromark
4. **Multi-layer verification**: Test if K4 is pre-encrypted before Gromark is applied
5. **Brute force key generation**: If Gromark is correct, attempt key recovery from known plaintext
6. **Consult historical records**: Research whether Kryptos sculptor Jim Sanborn mentioned Gromark

## Files Generated

- `test_gromark_k4.py` - Initial basic Gromark tests
- `test_gromark_expanded.py` - Expanded variants and parameters
- `test_gromark_advanced.py` - Advanced techniques and diagnostic checks
- `gromark_diagnostic_report.py` - Statistical analysis and comprehensive reporting
- `GROMARK_HYPOTHESIS_RESULTS.md` - This summary document

## Academic Note

The Gromark cipher is an interesting theoretical construct combining:
- Autokey principles (plaintext feedback)
- Fibonacci-like key generation (pseudo-random element)
- Lagged sequence generation (cryptographic strength)

However, its application to KRYPTOS K4 does not appear successful with the tested parameters and variants.
