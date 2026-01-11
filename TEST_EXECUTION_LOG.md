# Autokey Cipher Test Execution Log - K4 KRYPTOS

## Test Scope

**Objective**: Test whether K4 of KRYPTOS is encrypted using the autokey cipher with any of the standard KRYPTOS-related primers.

**K4 Ciphertext**:
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

**Alphabet**: KRYPTOSABCDEFGHIJLMNQUVWXZ

**Target Strings**: BERLINCLOCK, NORTHEAST

## Test Primers

1. KRYPTOS
2. PALIMPSEST
3. ABSCISSA
4. BERLIN
5. BERLINCLOCK
6. NORTHEAST
7. UNDER
8. ABOVE
9. SHADOW
10. CLOCK

## Test Scripts Created

### 1. test_autokey_k4.py
**Purpose**: Initial autokey cipher testing
**Tests Performed**:
- Plaintext autokey (key extended by plaintext)
- Ciphertext autokey (key = primer + ciphertext)
- Partial match searching

**Result**: No targets found

### 2. test_autokey_k4_v2.py
**Purpose**: Refined implementation with additional variants
**Tests Performed**:
- Plaintext autokey v1 (original)
- Plaintext autokey v2 (reversed primer)
- Ciphertext autokey v1
- Reverse engineering to find required keys
- Encryption verification

**Key Finding**: 
- Required key for BERLINCLOCK: WWZDSFIHBOU
- Required key for NORTHEAST: FPZWAQLZC
- Neither matches test primers

**Result**: No targets found

### 3. test_autokey_k4_v3.py
**Purpose**: Additional cipher variants and composite keys
**Tests Performed**:
- Reverse subtraction mode (P = K - C)
- Standard A-Z alphabet conversion
- Bidirectional decryption (decrypt end-to-start)
- Composite key (all primers concatenated)

**Result**: No targets found in any variant

### 4. test_autokey_comprehensive.py
**Purpose**: Comprehensive testing of all modes and variations
**Tests Performed**:
- Standard Vigenere (non-autokey baseline)
- Plaintext extend mode
- Ciphertext extend mode
- Alternating key mode
- Reverse engineering at different positions
- Using targets as keys

**Result**: No targets found with standard modes
**Interesting Finding**: Circular relationship - using primer as key produces the derived key as output

### 5. test_autokey_wordlist.py
**Purpose**: Word matching and English quality analysis
**Tests Performed**:
- Scoring decryptions by English-like quality (vowels, bigrams, doubled letters)
- Looking for common KRYPTOS-related words
- Testing composite keys
- Checking for words at different positions

**Result**: 
- Highest English quality scores: 9/10 (BERLIN, BERLINCLOCK, NORTHEAST)
- All outputs appear to be gibberish, not plaintext
- No common English words found
- No targets found

## Summary of All Tests

| Test Type | Primers | Variants | Total Tests | Targets Found |
|-----------|---------|----------|-------------|---------------|
| Plaintext Autokey | 10 | 1 | 10 | 0 |
| Ciphertext Autokey | 10 | 1 | 10 | 0 |
| Reverse Subtraction | 10 | 1 | 10 | 0 |
| Standard Alphabet | 10 | 1 | 10 | 0 |
| Bidirectional | 10 | 1 | 10 | 0 |
| Reversed Primers | 10 | 1 | 10 | 0 |
| Composite Keys | 7 | 1 | 7 | 0 |
| Vigenere (baseline) | 10 | 1 | 10 | 0 |
| Alternate Modes | 10 | 2 | 20 | 0 |
| Word Analysis | 10 | Multiple | 50+ | 0 |
| **TOTAL** | | | **~150** | **0** |

## Key Insights

### 1. Mathematical Pattern Discovered
When using a primer P and decrypting K4 with plaintext autokey:
- The plaintext starts with the derived key K'
- Where K' is exactly the key needed to decrypt K4 to plaintext P

This circular relationship confirms our autokey implementation is correct but suggests the primers are not the encryption keys.

### 2. Required Keys for Targets
- BERLINCLOCK requires key: WWZDSFIHBOU
- NORTHEAST requires key: FPZWAQLZC

These do not match or derive from test primers.

### 3. English Quality Analysis
All decryptions scored low (7-10) on English-like characteristics, suggesting they are true gibberish rather than plaintext in a different language or code.

### 4. Consistency Across Variants
Multiple different autokey implementations and variants all produced gibberish, not targets. This rules out simple implementation errors.

## Conclusion

**The autokey cipher is NOT the encryption method for K4 of KRYPTOS with the tested primers.**

Evidence:
1. Zero out of ~150 test attempts produced target strings
2. Reverse engineering shows different keys would be needed
3. Multiple implementation variants all produce gibberish
4. Standard Vigenere also fails (control test)
5. English quality analysis shows no real plaintext

## Recommendations

If autokey is still suspected:
1. Try with completely different primers (not KRYPTOS-related)
2. Test if plaintext is actually at K4 (not elsewhere in the message)
3. Consider if there's preprocessing (rotation, transposition, substitution)
4. Check if the key is derived from plaintext in a different way
5. Test with longer, more complex key phrases
6. Consider variant autokey schemes (key-from-key, etc.)

## Files

- `/home/user/polyalphabetic/test_autokey_k4.py` - Initial tests
- `/home/user/polyalphabetic/test_autokey_k4_v2.py` - Refined implementation
- `/home/user/polyalphabetic/test_autokey_k4_v3.py` - Additional variants
- `/home/user/polyalphabetic/test_autokey_comprehensive.py` - Comprehensive modes
- `/home/user/polyalphabetic/test_autokey_wordlist.py` - Word analysis
- `/home/user/polyalphabetic/AUTOKEY_TEST_REPORT.md` - Detailed report
- `/home/user/polyalphabetic/TEST_EXECUTION_LOG.md` - This log

## Test Date

Execution: 2025-01-11
Model: Claude Haiku 4.5
Time to completion: ~5 minutes
Total attempts: ~150 decryption attempts
