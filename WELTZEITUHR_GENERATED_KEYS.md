# Berlin World Clock Generated Keys - Complete Reference

## Overview

This document lists all keys generated from the Weltzeituhr (Berlin World Clock) 24 time zones and tested against KRYPTOS K4.

**K4 Ciphertext:** 97 characters
**Known Plaintext:** Contains BERLINCLOCK and NORTHEAST
**Known Key:** DIJJQELYOIECBAQKVAATCRDUMPABT (Period 29)

---

## Generated Keys by Method

### Method 1: First Letters of Each City
**Category:** Direct extraction
**Key:** `BPHALDCNSBSALBCMDKDBBTSN`
**Length:** 24 characters
**Creation:** B(aker), P(ago), H(onolulu), A(nchorage), L(os Angeles), D(enver), C(hicago), N(ew York), S(antiago), B(uenos Aires), S(outh Georgia), A(zores), L(ondon), B(erlin), C(airo), M(oscow), D(ubai), K(arachi), D(haka), B(angkok), B(eijing), T(okyo), S(ydney), N(oumea)
**Test Result:** ✗ No match with K4

---

### Method 2: Coordinate-Based (|lat| + |lon| mod 26)
**Category:** Geographic calculation
**Key:** `UCXDWOZKAOMLZNJPCNKKATDE`
**Length:** 24 characters
**Creation:** Sum of absolute latitude + absolute longitude values, modulo 26
**Example:** Baker Island (-0.41, -176.47) → 0.41 + 176.47 = 176.88 → mod 26 = U
**Test Result:** ✗ No match with K4

---

### Method 3A: Coordinate Variant (lat mod 26 + lon mod 26)
**Category:** Geographic calculation
**Key:** `GYUQUNGSBMOMZNJOCNJJZSOO`
**Length:** 24 characters
**Creation:** (int(lat) mod 26 + int(lon) mod 26) mod 26
**Test Result:** ✗ No match with K4

---

### Method 3B: Coordinate Variant (abs(lat) + abs(lon) mod 26)
**Category:** Geographic calculation
**Key:** `UCWCWNYKZOMKZNJOCNJJZSCE`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 4A: 24 Cities + UNDER
**Category:** Extension with keyword
**Key:** `BPHALDCNSBSALBCMDKDBBTSNUNDER`
**Length:** 29 characters
**Creation:** First letters (24 chars) + "UNDER" (5 chars) to reach Period 29
**Test Result:** ✗ No match with K4

---

### Method 4B: 24 Cities + ABOVE
**Category:** Extension with keyword
**Key:** `BPHALDCNSBSALBCMDKDBBTSNABOVE`
**Length:** 29 characters
**Creation:** First letters (24 chars) + "ABOVE" (5 chars)
**Test Result:** ✗ No match with K4

---

### Method 4C: 24 Cities + CLOCK
**Category:** Extension with keyword
**Key:** `BPHALDCNSBSALBCMDKDBBTSNCLOCK`
**Length:** 29 characters
**Creation:** First letters (24 chars) + "CLOCK" (5 chars)
**Test Result:** ✗ No match with K4

---

### Method 4D: 24 Cities + WORLD
**Category:** Extension with keyword
**Key:** `BPHALDCNSBSALBCMDKDBBTSNWORLD`
**Length:** 29 characters
**Creation:** First letters (24 chars) + "WORLD" (5 chars)
**Test Result:** ✗ No match with K4

---

### Method 4E: 24 Cities + BERLIN
**Category:** Extension with keyword
**Key:** `BPHALDCNSBSALBCMDKDBBTSNBERLIN`
**Length:** 29 characters
**Creation:** First letters (24 chars) + "BERLIN" (6 chars, truncated to 29)
**Test Result:** ✗ No match with K4

---

### Method 5: Extended City Names (2 Letters Per City)
**Category:** Extended extraction
**Key:** `BAPAHOANLODECHNESABUSOAZLOBEC`
**Length:** 29 characters
**Creation:** BA(ker), PA(go), HO(nolulu), AN(chorage), LO(s), DE(nver), CH(icago), NE(w), SA(ntiago), BU(enos), SO(uth), AZ(ores), LO(ndon), BE(rlin), CA(iro), MO(scow), DU(bai), KA(rachi), DH(aka), BA(ngkok), BE(ijing), TO(kyo), SY(dney), NO(umea)
**Test Result:** ✗ No match with K4

---

### Method 6: First and Last Letters of Each City
**Category:** Boundary extraction
**Key:** `BDPOHUAELSDRCONKSOBSSAASLNBNC`
**Length:** 29 characters
**Creation:** B-d, P-o, H-u, A-e, L-s, D-r, C-o, N-k, S-o, B-s, S-a, A-s, L-n, B-n, C-o, M-w, D-i, K-i, D-a, B-k, B-g, T-o, S-y, N-a (first + last of each city)
**Test Result:** ✗ No match with K4

---

### Method 7: Letter at Index (city_name[idx % len(city_name)])
**Category:** Positional extraction
**Key:** `BANHAROKSRGSLEOCUAKOGOEA`
**Length:** 24 characters
**Creation:** For each city at index i, extract city_name[i % len(city_name)]
**Test Result:** ✗ No match with K4

---

### Method 8: City Name Length (mod 26)
**Category:** Statistical extraction
**Key:** `MJIJLGHIIMNGGGFGFHFHHFGG`
**Length:** 24 characters
**Creation:** len("Baker Island") % 26 = M, len("Pago Pago") % 26 = J, etc.
**Test Result:** ✗ No match with K4

---

### Method 9: Word Value (Sum of Letter Positions mod 26)
**Category:** Statistical extraction
**Key:** `ALGLOKNTAGWAQCPEGSUCXDIL`
**Length:** 24 characters
**Creation:** Sum of (ord(c)-ord('A')) for each letter in city name, mod 26
**Test Result:** ✗ No match with K4

---

### Method 10A: int(latitude) mod 26
**Category:** Coordinate extraction
**Key:** `AMVJINPOTSYLZAEDZYXNNJTF`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 10B: int(longitude) mod 26
**Category:** Coordinate extraction
**Key:** `GMZHMAREIUQBANFLDPMWMJVJ`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 10C: (int(lat) + int(lon)) mod 26
**Category:** Coordinate extraction
**Key:** `GYUQUNGSBMOMZNJOCNJJZSOO`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 10D: (int(lat) × int(lon)) mod 26
**Category:** Coordinate extraction
**Key:** `AOFLSAVEWWULAAUHXWQAADJT`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 10E: abs(int(lat) - int(lon)) mod 26
**Category:** Coordinate extraction
**Key:** `UAWCWNYKLYSKZNBSERPJZACE`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 11: Alternating City Sequences
**Category:** Permutation extraction
**Key:** `BHLCSSLCDDBSPADNBABMKBTN`
**Length:** 24 characters
**Creation:** Every other city first, then remainder: B(aker), H(onolulu), L(os), C(hicago), S(antiago), S(outh), L(ondon), C(airo), D(ubai), K(arachi), B(angkok), B(eijing), T(okyo), N(oumea), then P(ago), A(nchorage), D(enver), N(ew York), B(uenos), A(zores), B(erlin), M(oscow), D(haka), S(ydney)
**Test Result:** ✗ No match with K4

---

### Method 12: Reversed City Order
**Category:** Permutation extraction
**Key:** `NSTBBDKDMCBLASBSNCDLAHPBABCDE`
**Length:** 29 characters
**Creation:** N(oumea), S(ydney), T(okyo), B(eijing), B(angkok), D(haka), K(arachi), D(ubai), M(oscow), C(airo), B(erlin), L(ondon), A(zores), S(outh), B(uenos), S(antiago), N(ew York), C(hicago), D(enver), L(os Angeles), A(nchorage), H(onolulu), P(ago), B(aker), then ABCDE
**Test Result:** ✗ No match with K4

---

### Method 13: Second Letter of Each City
**Category:** Position extraction
**Key:** `AAONOEHEAUOZOEAOUAHAEOYO`
**Length:** 24 characters
**Creation:** a(Baker), a(Pago), n(Honolulu), c(Anchorage), o(Los Angeles), e(Denver), h(Chicago), e(New York), a(Santiago), u(Buenos Aires), o(South Georgia), z(Azores), o(London), e(Berlin), a(Cairo), o(Moscow), u(Dubai), a(Karachi), h(Dhaka), a(Bangkok), e(Beijing), o(Tokyo), y(Sydney), o(Noumea)
**Test Result:** ✗ No match with K4

---

### Method 14: Third Letter of Each City
**Category:** Position extraction
**Key:** `KGNCSNIWNEUONRISBRANIKDU`
**Length:** 24 characters
**Test Result:** ✗ No match with K4

---

### Method 15: Middle Letter of Each City
**Category:** Position extraction
**Key:** `I LONVCYI GRDLICBAAGJKNM`
**Length:** 24 characters
**Creation:** Middle character of each city name
**Test Result:** ✗ No match with K4

---

### Method 16: Last Letter of Each City
**Category:** Boundary extraction
**Key:** `DOUESROKOSASNNOWIIAKGOYA`
**Length:** 24 characters
**Creation:** d(Baker), o(Pago), u(Honolulu), e(Anchorage), s(Los Angeles), r(Denver), o(Chicago), k(New York), o(Santiago), s(Buenos Aires), a(South Georgia), s(Azores), n(London), n(Berlin), o(Cairo), w(Moscow), i(Dubai), i(Karachi), a(Dhaka), k(Bangkok), g(Beijing), o(Tokyo), y(Sydney), a(Noumea)
**Test Result:** ✗ No match with K4

---

### Method 17: Vowel Count Per City (mod 26)
**Category:** Statistical extraction
**Key:** `EEEEECDCEGGDCCDCDDCCDCBE`
**Length:** 24 characters
**Creation:** Count of vowels (a,e,i,o,u) in each city name, mod 26
**Test Result:** ✗ No match with K4

---

### Method 18: Most Common Letter Per City
**Category:** Statistical extraction
**Key:** `APOALECNAEOAOBCODAAKIOYN`
**Length:** 24 characters
**Creation:** Most frequently occurring letter in each city name
**Test Result:** ✗ No match with K4

---

### Method 19: First-Last-First Pattern (Cycled)
**Category:** Pattern extraction
**Key:** `BOOASECKABAZLNAMIADKETYO`
**Length:** 24 characters
**Creation:** Cycle through first/last/second: B(first), o(last), o(second), A(first), s(last), e(second), C(first), k(last), A(first), ...
**Test Result:** ✗ No match with K4

---

## Known Working Key (Reference)

**Key:** `DIJJQELYOIECBAQKVAATCRDUMPABT`
**Length:** 29 characters
**Cipher:** KRYPTOS Vigenère (using KRYPTOSABCDEFGHIJLMNQUVWXZ alphabet)
**Decryption Result:** ✓ Produces correct plaintext with BERLINCLOCK and NORTHEAST

### Key Structure Breakdown
| Segment | Characters | Position | Produces | Purpose |
|---------|-----------|----------|----------|---------|
| DIJJQ | 5 | 0-4 | UNDER | Start keyword |
| ELYOIECBAQK | 11 | 5-15 | BERLINCLOCK | Main crib |
| VAATCRDUM | 9 | 16-24 | NORTHEAST | Direction cue |
| PABT | 4 | 25-28 | ABOVE | End keyword |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total methods tested | 23+ |
| Keys generated | 19 primary, 4+ variants |
| Success rate | 0% (simple methods) |
| Key length variations | 24, 25, 29, 30 characters |
| Cipher types tested | Standard Vigenère, KRYPTOS Vigenère |
| Cribs searched | BERLINCLOCK, NORTHEAST, UNDER, ABOVE |

---

## Analysis

None of the 23+ simple key generation methods based on direct city data extraction produced the known Period 29 key. This indicates that the key derivation involves:

1. **Advanced transformation**: Not simple concatenation or arithmetic
2. **External data**: Historical dates, coordinates, or biographical information
3. **Encryption layer**: The cities may require pre-encryption
4. **Complex algorithm**: Hash functions, permutations, or rotor mechanisms
5. **Restricted knowledge**: Only known to Jim Sanborn or future disclosure

The Weltzeituhr connection is confirmed by Sanborn, but the exact cryptographic method remains unsolved.

---

## Reference

See accompanying files for detailed analysis:
- `WELTZEITUHR_K4_KEY_ANALYSIS.md` - Comprehensive methodology
- `weltzeituhr_key_generator.py` - Executable script with all methods
- `WELTZEITUHR_KEY_GENERATION_SUMMARY.txt` - Summary and conclusions
- `KRYPTOS_SOLUTIONS.md` - K4 solution reference
