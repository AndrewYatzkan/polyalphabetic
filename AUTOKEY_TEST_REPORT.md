# Autokey Cipher Test Report - KRYPTOS K4

## Summary

Comprehensive testing of the autokey cipher applied to K4 of the KRYPTOS puzzle has been completed. The tests included:

- **Plaintext Autokey**: Key extended by plaintext (K = primer + plaintext)
- **Ciphertext Autokey**: Key extended by ciphertext (K = primer + ciphertext)
- **Multiple Variants**: Reverse subtraction, different alphabet handling, bidirectional processing
- **Primers Tested**: KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, BERLINCLOCK, NORTHEAST, UNDER, ABOVE, SHADOW, CLOCK
- **Target Searches**: Looking for BERLINCLOCK and NORTHEAST in decrypted output

## Test Data

**K4 Ciphertext** (97 chars):
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

**Alphabet**: KRYPTOSABCDEFGHIJLMNQUVWXZ (substitution cipher alphabet)

## Results

### Finding 1: Standard Autokey Decryptions

Testing plaintext autokey with all 10 primers produced no exact matches for target strings:

| Primer | Decrypted Output | Contains Targets? |
|--------|------------------|-------------------|
| KRYPTOS | OAXXLKMKBCJFPRKFDAPPMAFVLIIXVHBURRKZMZIREIRRSUQQMYZEUFJODYMDHAPHWXLZZGQAXUMBOUQNZETODBUJCJYJSUTYV | No |
| PALIMPSEST | YRCFPYMQADNISTPIGDSSUDIZQMMRZLEXTTPYUYMTHMTTCXWWUOYHXINBGOUGLDSLKRQYYJWDRXUEBXWVYHABGEXNFNONCXAOZ | No |
| ABSCISSA | XKQMSZMXIJWNDBANLHDDZHNPXVVOPUIYBBASZSVBMVBBGYRRZCSMYNWFLCZLUHDUTOXSSQRHOYZIFYRKSMEFLIYWJWCWGYECP | No |
| BERLIN | WWZDSFRBJLXQECBQMIEEKIQTZWWSTVJPCCBAKAWCNWCCHPYYKDANPQXGMDKMVIEVOSZAAUYISPKJGPYRANFGMJPXLXDXHPFDT | No |
| BERLINCLOCK | WWZDSFIHBOUQECBQMIEEKIQTZWWSTVJPCCBAKAWCNWCCHPYYKDANPQXGMDKMVIEVOSZAAUYISPKJGPYRANFGMJPXLXDXHPFDT | No |
| NORTHEAST | FPZWAQLZCYCOVQNOPKVVEKOIDBBLIARHQQNMEMBQTBQQZHGGEUMTHOCXPUEPAKVAJLDMMSGKLHERXHGFMTWXPRHCYCUCZHWUI | No |
| UNDER | DIJJQUHUPTEAXVUAOYXXGYALFDDNLCPJVVUQGQDVSDVVRJIIGWQSJAEKOWGOCYXCMNFQQBIYNJGPKJIHQSZKOPJETEWERJZWL | No |
| ABOVE | XKUODAKAIJWNDBANLHDDZHNPXVVOPUIYBBASZSVBMVBBGYRRZCSMYNWFLCZLUHDUTOXSSQRHOYZIFYRKSMEFLIYWJWCWGYECP | No |
| SHADOW | ZQNLJBZSHIVMCASMJGCCXGMYWUUTYQHRAASOXOUALUAAFRKKXBOLRMVEJBXJQGCQPTWOONKGTRXHERKZOLDEJHRVIVBVFRDBY | No |
| CLOCK | VLUMUCYCLMZUFDCUNJFFRJUOKXXAOWLTDDCBRBXDQXDDITPPREBQTUZHNERNWJFWSAKBBVPJATRLHTPYBQGHNLTZMZEZITGEO | No |

**Conclusion**: None of the standard autokey decryptions with tested primers produce the target strings BERLINCLOCK or NORTHEAST.

### Finding 2: Reverse Engineering Analysis

To understand what key would be needed to decrypt K4 to the target strings, we derived the required keys:

**If BERLINCLOCK is plaintext at position 0:**
- Required key: WWZDSFIHBOU
- This does NOT match any of the test primers

**If NORTHEAST is plaintext at position 0:**
- Required key: FPZWAQLZC
- This does NOT match any of the test primers

### Finding 3: Alternative Cipher Modes

Testing additional variants:
- **Ciphertext Autokey**: No targets found
- **Reverse Subtraction** (P = K - C instead of C - K): No targets found
- **Standard Alphabet Conversion**: No targets found
- **Bidirectional Processing**: No targets found
- **Reversed Primers**: No targets found

### Finding 4: Comparative Analysis

For context, standard Vigenere cipher (non-autokey) with the same primers also produced no matches for the target strings.

### Finding 5: English Quality Scoring

Analyzed decrypted outputs for English-like characteristics (vowel ratios, common bigrams, doubled letters):

**Highest Scoring Decryptions**:
1. BERLIN (score: 9)
2. BERLINCLOCK (score: 9)
3. NORTHEAST (score: 9)

All scores were relatively low (7-10), indicating the decrypted texts are largely gibberish or heavily enciphered text, not plain English.

## Interpretation

The autokey cipher does not appear to be used for K4 of KRYPTOS with the tested primers. The evidence suggests:

1. **K4 is not autokey with these primers**: The reverse engineering showed that completely different keys (WWZDSFIHBOU, FPZWAQLZC) would be needed to produce the target strings at the beginning of the plaintext.

2. **K4 is either**:
   - Encrypted with a different cipher altogether (not autokey)
   - Uses autokey but with a different primer/key not in our test set
   - Uses autokey with some variation or preprocessing we haven't tested
   - Uses a different alphabet or transformation

3. **Note on derivation keys**: The fact that the reverse engineering produced keys like "WWZDSFIHBOU" and "FPZWAQLZC" is interesting but doesn't immediately suggest a pattern with the KRYPTOS-related primers.

## Files Generated

- `test_autokey_k4.py` - Initial autokey tests
- `test_autokey_k4_v2.py` - Refined implementation with reverse engineering
- `test_autokey_k4_v3.py` - Additional variations (reverse subtraction, standard alphabet, bidirectional)
- `test_autokey_comprehensive.py` - Comprehensive mode testing
- `test_autokey_wordlist.py` - Word matching and English quality analysis
- `AUTOKEY_TEST_REPORT.md` - This report

## Recommendations for Further Testing

If autokey cipher is suspected:
1. Try other known plaintext-ciphertext pairs to derive the actual key
2. Test the cipher with completely different primers
3. Investigate if there's a preprocessing step (like reversal, substitution, or composition)
4. Consider if it's a variant autokey (e.g., key-extended-by-key instead of plaintext)
5. Test with longer, more complex key phrases
6. Consider if the KRYPTOS alphabet needs reverse mapping or different handling

## Conclusion

**Autokey cipher with tested primers is NOT the solution for K4.**

The systematic testing of 10 different primers across multiple autokey variants and modes produced no matches for BERLINCLOCK or NORTHEAST in the decrypted output.
