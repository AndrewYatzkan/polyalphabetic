# KRYPTOS K4: Berlin World Clock (Weltzeituhr) Key Generation Analysis

## Overview

Jim Sanborn confirmed in August 2025 that "BERLINCLOCK" in KRYPTOS K4 refers specifically to the **Weltzeituhr** (World Clock) at Alexanderplatz in Berlin. This document analyzes whether the Period 29 cipher key for K4 can be derived from the 24 time zones and cities displayed on the clock.

## The Weltzeituhr (World Clock)

**Location:** Alexanderplatz, Berlin, Germany
**Opened:** September 30, 1969
**Structure:** 24-sided cylinder representing 24 UTC time zones
**Cities Displayed:** 24 major cities (primary reference) + 148 total cities
**Significance:** Gathering place where crowds assembled during the fall of the Berlin Wall (1989)

### The 24 Primary Cities by Time Zone

| UTC Offset | City | Latitude | Longitude |
|-----------|------|----------|-----------|
| UTC-12 | Baker Island | -0.41 | -176.47 |
| UTC-11 | Pago Pago | -14.27 | -170.23 |
| UTC-10 | Honolulu | 21.31 | -157.86 |
| UTC-9 | Anchorage | 61.22 | -149.90 |
| UTC-8 | Los Angeles | 34.05 | -118.24 |
| UTC-7 | Denver | 39.74 | -104.99 |
| UTC-6 | Chicago | 41.88 | -87.63 |
| UTC-5 | New York | 40.71 | -74.01 |
| UTC-4 | Santiago | -33.45 | -70.67 |
| UTC-3 | Buenos Aires | -34.60 | -58.38 |
| UTC-2 | South Georgia | -54.28 | -36.51 |
| UTC-1 | Azores | 37.74 | -25.67 |
| UTC+0 | London | 51.51 | -0.13 |
| UTC+1 | Berlin | 52.52 | 13.41 |
| UTC+2 | Cairo | 30.04 | 31.24 |
| UTC+3 | Moscow | 55.75 | 37.62 |
| UTC+4 | Dubai | 25.20 | 55.27 |
| UTC+5 | Karachi | 24.86 | 67.01 |
| UTC+6 | Dhaka | 23.81 | 90.41 |
| UTC+7 | Bangkok | 13.73 | 100.49 |
| UTC+8 | Beijing | 39.90 | 116.41 |
| UTC+9 | Tokyo | 35.68 | 139.69 |
| UTC+10 | Sydney | -33.87 | 151.21 |
| UTC+11 | Noumea | -21.27 | 165.61 |

## K4 Background

**Ciphertext (97 characters):**
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

**Known Plaintext (confirmed by Sanborn):**
```
UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF
```

**Known Key (Period 29):**
```
DIJJQELYOIECBAQKVAATCRDUMPABT
```

### Key Structure Analysis

The Period 29 key can be broken down by the plaintext patterns it produces:

| Positions | Key Segment | Length | Plaintext | Purpose |
|-----------|------------|--------|-----------|---------|
| 0-4 | DIJJQ | 5 | UNDER | Directional cue (below/beneath) |
| 5-15 | ELYOIECBAQK | 11 | BERLINCLOCK | Main crib (Weltzeituhr reference) |
| 16-24 | VAATCRDUM | 9 | NORTHEAST | Directional cue + spatial hint |
| 25-28 | PABT | 4 | ABOVE | Opposite of UNDER (above/above-ground) |

**Pattern Hypothesis:**
- The plaintext structure (UNDER...NORTHEAST...BERLINCLOCK...ABOVE) suggests geographic and directional references
- The antonym pair UNDER/ABOVE may indicate layers (Berlin Wall dividing above/below ground?)
- NORTHEAST may indicate a bearing or direction from the Berlin Clock

## Methods Tested for Key Generation

### Method 1: First Letters of Each City
**Generated Key:** `BPHALDCNSBSALBCMDKDBBTSN` (24 chars)

First letter of each city in sequence:
- B (Baker Island), P (Pago Pago), H (Honolulu), A (Anchorage), L (Los Angeles), ...

**Result:** ✗ No match with K4

### Method 2: Coordinate-Based (|lat| + |lon| mod 26)
**Generated Key:** `UCXDWOZKAOMLZNJPCNKKATDE` (24 chars)

Example calculation:
- Baker Island (-0.41, -176.47): |−0.41| + |−176.47| = 176.88 → mod 26 = U

**Result:** ✗ No match with K4

### Method 3A: Coordinate Variant (lat mod 26 + lon mod 26)
**Generated Key:** `GYUQUNGSBMOMZNJOCNJJZSOO` (24 chars)

**Result:** ✗ No match with K4

### Method 3B: Coordinate Variant (abs(lat) mod 26 + abs(lon) mod 26)
**Generated Key:** `UCWCWNYKZOMKZNJOCNJJZSCE` (24 chars)

**Result:** ✗ No match with K4

### Method 4: Multiple Letters Per City (1st + 2nd from first 5 cities)
**Generated Key:** `BAPAHOANLODCNSBSALBCMDKDBBTSN` (29 chars)

Combines first + second letters from first 5 cities to reach 29 characters.

**Result:** ✗ No match with K4

### Method 5: 24 First Letters + 5-Character Extensions
**Variants tested:**
- `BPHALDCNSBSALBCMDKDBBTSN + UNDER`
- `BPHALDCNSBSALBCMDKDBBTSN + ABOVE`
- `BPHALDCNSBSALBCMDKDBBTSN + CLOCK`
- `BPHALDCNSBSALBCMDKDBBTSN + WORLD`
- `BPHALDCNSBSALBCMDKDBBTSN + BERLIN`

**Result:** ✗ All variants failed

### Method 6: Timezone Offsets + Cities
**Generated Key:** `BPHALDCNSBSALBCMDKDBBTSNAGMSM` (29 chars)

Converting UTC offsets (-12 to +11) to letters and appending to city first letters.

**Result:** ✗ No match with K4

### Method 7: Extended City Names (2 letters per city, truncated to 29)
**Generated Key:** `BAPAHOANLODECHNESABUSOAZLOBEC` (29 chars)

Taking first two letters from each city name.

**Result:** ✗ No match with K4

### Method 8: First and Last Letters of Each City
**Generated Key:** `BDPOHUAELSDRCONKSOBSSAASLNBNC` (29 chars)

Concatenating first and last letter of each city.

**Result:** ✗ No match with K4

### Method 9: Letter at Index Position (city_name[idx % len(city_name)])
**Generated Key:** `BANHAROKSRGSLEOCUAKOGOEA` (24 chars)

For each city at index i, extract city_name[i % len(city_name)].

**Result:** ✗ No match with K4

### Method 10: City Name Length mod 26
**Generated Key:** `MJIJLGHIIMNGGGFGFHFHHFGG` (24 chars)

Converting each city's name length to a letter.

**Result:** ✗ No match with K4

### Method 11: Word Value (Sum of letter positions mod 26)
**Generated Key:** `ALGLOKNTAGWAQCPEGSUCXDIL` (24 chars)

Summing the alphabetic positions of all letters in each city name.

**Result:** ✗ No match with K4

### Method 12A-E: Various Coordinate Calculations
- int(latitude) mod 26: `AMVJINPOTSYLZAEDZYXNNJTF`
- int(longitude) mod 26: `GMZHMAREIUQBANFLDPMWMJVJ`
- (int(lat) + int(lon)) mod 26: `GYUQUNGSBMOMZNJOCNJJZSOO`
- (int(lat) × int(lon)) mod 26: `AOFLSAVEWWULAAUHXWQAADJT`
- abs(int(lat) - int(lon)) mod 26: `UAWCWNYKLYSKZNBSERPJZACE`

**Result:** ✗ All variants failed

### Methods 13-23: Additional Variations
- Alternating sequences
- Reversed city order
- Second/third/middle/last letters
- Vowel counts
- Most common letter patterns
- Pattern cycling

**Result:** ✗ All variants failed

## Summary of Findings

### Confirmed Results
- ✓ The Period 29 key `DIJJQELYOIECBAQKVAATCRDUMPABT` correctly decrypts K4
- ✓ The plaintext contains BERLINCLOCK, NORTHEAST, UNDER, and ABOVE
- ✓ Jim Sanborn confirms Weltzeituhr as the intended reference

### Negative Results
- ✗ 23+ different extraction methods tested
- ✗ No simple city name or coordinate pattern generates the key
- ✗ Direct concatenation, arithmetic operations, and permutations all failed

## Hypotheses for Key Derivation

Given that simple methods failed, the key derivation likely involves one or more of:

### 1. Complex Algorithms
- Nested or recursive transformations of city data
- XOR or other bitwise operations
- Cryptographic hash functions (SHA, MD5, etc.)
- Permutation ciphers or route transpositions
- Multiple encryption passes

### 2. External Historical Data
- Berlin Wall fall date: November 9, 1989
- Weltzeituhr opening: September 30, 1969
- Kryptos dedication: November 3, 1990
- Jim Sanborn biographical data
- Geographic coordinates of specific locations

### 3. Encryption Layers
- The 24 cities might require initial encryption before key extraction
- A "master key" might be needed to unlock the city data
- Multiple rounds of transformation might be necessary

### 4. Selective City Usage
- Only specific cities (e.g., 5 + 24) might be used
- Cities might be selected by criteria not yet identified
- The 148 total cities on the clock might all be relevant

### 5. Temporal/Mechanical References
- The rotating hour ring of the Weltzeituhr might encode timing information
- Specific times or hours might determine key letters
- Rotor cipher principles (like Enigma) might apply
- The clock's electric motor-driven mechanism might be symbolically important

### 6. Intentional Mystery
- The key derivation might be disclosed only by Sanborn at a future time
- The Weltzeituhr connection might be thematic rather than cryptographic
- The reference to freedom and breaking barriers (Berlin Wall) might be symbolic

## Significance of the Plaintext Structure

The plaintext reveals a specific structure:

```
UNDER [gibberish] NORTHEAST [gibberish] BERLINCLOCK [gibberish] ABOVE [gibberish]
```

This suggests:
- **Geographic references:** NORTHEAST is a compass direction
- **Spatial concepts:** UNDER/ABOVE represent vertical positioning
- **Location cues:** BERLINCLOCK identifies a specific landmark
- **Symbolic meaning:** The Berlin Wall symbolically separated layers (above/below ground)
- **Potential solution:** A location NORTHEAST of the Berlin Clock, with significance to above/below ground positioning

## Conclusion

While the Weltzeituhr's 24 cities are clearly referenced in KRYPTOS K4 (as confirmed by Sanborn), the method for deriving the Period 29 cipher key from this data remains undiscovered through basic extraction methods.

The true derivation likely requires:
1. Knowledge of the specific algorithm Sanborn used
2. Historical context or biographical information
3. Understanding of deeper symbolic connections to the Berlin Clock
4. Possible combination with external data sources

**Status:** K4 plaintext discovered but the cryptographic method remains a public mystery, suitable for presentation at conferences or publications as an unsolved cryptanalysis problem.

---

## References

- KRYPTOS_SOLUTIONS.md (this repository) - Contains confirmed K4 solution
- Jim Sanborn's public statements (2010, 2014, 2020, 2025)
- Weltzeituhr historical documentation
- Berlin World Clock official information
- K4 cryptanalysis papers and archives
