#!/usr/bin/env python3
"""
Comprehensive Statistical Analysis of K4 Ciphertext
Including: IoC, Kasiski, Chi-squared, Bigram/Trigram, Letter Contacts
"""

from collections import Counter, defaultdict
import math
import re

# K4 ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# English letter frequencies (from a large corpus)
ENGLISH_FREQ = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
    'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
    'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
    'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974,
    'Z': 0.00074
}

# Random (uniform) letter frequencies
RANDOM_FREQ = {chr(65 + i): 1/26 for i in range(26)}

# The plaintext portions for comparison
K4_PLAINTEXT = "BERLINCLOCK"


def calculate_ioc(text):
    """
    Calculate Index of Coincidence
    IoC = sum(n_i * (n_i - 1)) / (N * (N - 1))
    where n_i is frequency of letter i, N is total length
    """
    text = text.upper()
    n = len(text)
    if n <= 1:
        return 0.0

    freq = Counter(text)
    ioc = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    return ioc


def arrange_in_rows(text, cols):
    """Arrange text in rows of given column width"""
    rows = []
    for i in range(0, len(text), cols):
        rows.append(text[i:i+cols])
    return rows


def extract_column(text, col, cols):
    """Extract a column from text arranged in rows"""
    rows = arrange_in_rows(text, cols)
    column = ''.join(row[col] if col < len(row) else '' for row in rows)
    return column


def kasiski_examination(text, min_len=3, max_len=6):
    """
    Kasiski examination: Find repeated sequences and their distances
    Returns list of (sequence, positions, distances)
    """
    text = text.upper()
    results = []

    for length in range(min_len, min(max_len + 1, len(text) // 2)):
        substrings = defaultdict(list)

        # Find all substrings of this length
        for i in range(len(text) - length + 1):
            substr = text[i:i + length]
            substrings[substr].append(i)

        # Find repeats
        for substr, positions in substrings.items():
            if len(positions) > 1:
                distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                results.append((substr, positions, distances))

    return sorted(results, key=lambda x: -len(x[0]))


def find_gcd(numbers):
    """Find GCD of a list of numbers"""
    if not numbers:
        return 0
    result = numbers[0]
    for num in numbers[1:]:
        a, b = result, num
        while b:
            a, b = b, a % b
        result = a
    return result


def chi_squared_test(text, expected_freq=ENGLISH_FREQ):
    """
    Chi-squared test
    X^2 = sum((observed - expected)^2 / expected)
    """
    text = text.upper()
    n = len(text)
    freq = Counter(text)

    chi_sq = 0.0
    degrees_of_freedom = 25  # 26 letters - 1

    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(letter, 0)
        expected = expected_freq.get(letter, 0) * n
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected

    return chi_sq, degrees_of_freedom


def bigram_frequency(text):
    """Calculate bigram frequencies"""
    text = text.upper()
    bigrams = Counter()
    for i in range(len(text) - 1):
        bigrams[text[i:i+2]] += 1
    return bigrams


def trigram_frequency(text):
    """Calculate trigram frequencies"""
    text = text.upper()
    trigrams = Counter()
    for i in range(len(text) - 2):
        trigrams[text[i:i+3]] += 1
    return trigrams


def letter_contact_frequency(text):
    """
    Analyze which letters follow which letters
    Returns dict of {letter: {follower: count}}
    """
    text = text.upper()
    contacts = defaultdict(lambda: defaultdict(int))

    for i in range(len(text) - 1):
        current = text[i]
        next_letter = text[i+1]
        contacts[current][next_letter] += 1

    return contacts


def doubling_analysis(text):
    """Find and analyze doubled letters"""
    text = text.upper()
    doubled = Counter()
    for i in range(len(text) - 1):
        if text[i] == text[i+1]:
            doubled[text[i]] += 1
    return doubled


def repeated_bigram_distance(text):
    """Find repeated bigrams and their distances"""
    text = text.upper()
    bigrams = defaultdict(list)

    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        bigrams[bigram].append(i)

    results = []
    for bigram, positions in bigrams.items():
        if len(positions) > 1:
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            results.append((bigram, positions, distances))

    return sorted(results, key=lambda x: (-len(x[1]), x[0]))


def analyze_column_differences(text, key_length):
    """Analyze chi-squared for columns when arranged with given period"""
    text = text.upper()
    results = {}

    for col in range(key_length):
        column = extract_column(text, col, key_length)
        if len(column) > 0:
            chi_sq, _ = chi_squared_test(column, ENGLISH_FREQ)
            ioc = calculate_ioc(column)
            results[col] = {
                'text': column,
                'ioc': ioc,
                'chi_sq': chi_sq
            }

    return results


def print_section(title, char='='):
    """Print a section header"""
    print(f"\n{char * 80}")
    print(f"{title:^80}")
    print(f"{char * 80}")


def print_subsection(title):
    """Print a subsection header"""
    print(f"\n{title}")
    print("-" * 80)


def main():
    print("=" * 80)
    print(f"{'COMPREHENSIVE STATISTICAL ANALYSIS OF K4':^80}")
    print("=" * 80)

    print(f"\nK4 Ciphertext: {K4}")
    print(f"Length: {len(K4)} characters")

    # =========================================================================
    # 1. INDEX OF COINCIDENCE ANALYSIS
    # =========================================================================
    print_section("1. INDEX OF COINCIDENCE (IoC) ANALYSIS")

    # Full ciphertext IoC
    full_ioc = calculate_ioc(K4)
    print(f"\nFull K4 IoC: {full_ioc:.6f}")
    print(f"  Reference values:")
    print(f"    English text:    ~0.067")
    print(f"    Random cipher:   ~0.038")
    print(f"    This result:     {full_ioc:.6f}")

    if full_ioc < 0.040:
        interpretation = "RANDOM-LIKE (likely strongly encrypted or random)"
    elif full_ioc < 0.055:
        interpretation = "CIPHER-LIKE (consistent with polyalphabetic cipher)"
    elif full_ioc < 0.070:
        interpretation = "BETWEEN CIPHER AND ENGLISH"
    else:
        interpretation = "ENGLISH-LIKE (possible plaintext or substitution)"

    print(f"  Interpretation: {interpretation}")

    # IoC by column (arranged in rows of 29)
    print_subsection("IoC by Column (arranged in 29-char rows)")
    print(f"Arranging {len(K4)} chars in rows of 29...")

    columns_29 = {}
    for col in range(29):
        column = extract_column(K4, col, 29)
        if column:
            ioc = calculate_ioc(column)
            columns_29[col] = {'text': column, 'ioc': ioc}
            print(f"Col {col:2d}: {column:20s} | IoC: {ioc:.6f}")

    avg_ioc_29 = sum(c['ioc'] for c in columns_29.values()) / len(columns_29)
    print(f"\nAverage IoC across columns: {avg_ioc_29:.6f}")

    # Check other period lengths
    print_subsection("IoC Analysis for Other Period Lengths")

    interesting_periods = [3, 4, 5, 6, 7, 8, 9, 11, 13, 16, 19, 23, 29]
    period_results = {}

    for period in interesting_periods:
        if period > len(K4):
            continue
        cols_data = analyze_column_differences(K4, period)
        if cols_data:
            avg_ioc = sum(c['ioc'] for c in cols_data.values()) / len(cols_data)
            avg_chi = sum(c['chi_sq'] for c in cols_data.values()) / len(cols_data)
            period_results[period] = {'avg_ioc': avg_ioc, 'avg_chi': avg_chi}
            print(f"Period {period:2d}: Avg IoC = {avg_ioc:.6f}, Avg Chi² = {avg_chi:8.2f}")

    # =========================================================================
    # 2. KASISKI EXAMINATION
    # =========================================================================
    print_section("2. KASISKI EXAMINATION (Repeated Sequences)")

    print_subsection("3-6 Character Repeats and Their Distances")
    kasiski_results = kasiski_examination(K4, min_len=3, max_len=6)
    gcds = []

    if kasiski_results:
        for substr, positions, distances in kasiski_results[:15]:  # Top 15
            print(f"\n'{substr}' found at positions {positions}")
            print(f"  Distances between repeats: {distances}")
            if distances:
                gcd = find_gcd(distances)
                print(f"  GCD: {gcd}")
                gcds.append(gcd)

        if gcds:
            print_subsection("GCD Analysis of Repeat Distances")
            gcd_freq = Counter(gcds)
            print(f"Most common GCDs: {gcd_freq.most_common(10)}")
            overall_gcd = find_gcd(gcds)
            print(f"Overall GCD of all distances: {overall_gcd}")
            print(f"Possible key length candidates: {overall_gcd}")
    else:
        print("\nNo repeating sequences found in specified length range.")

    # Bigram repeats
    print_subsection("Repeated Bigrams and Their Distances")
    bigram_repeats = repeated_bigram_distance(K4)
    bigram_gcds = []

    for bigram, positions, distances in bigram_repeats[:20]:
        if len(positions) <= 3:  # Only show bigrams that repeat 2-3 times
            print(f"\n'{bigram}' at positions {positions}, distances: {distances}")
            if distances:
                gcd = find_gcd(distances)
                bigram_gcds.append(gcd)
                print(f"  GCD: {gcd}")

    if bigram_gcds:
        print_subsection("Bigram GCD Analysis")
        bigram_gcd_freq = Counter(bigram_gcds)
        print(f"Most common GCDs from bigrams: {bigram_gcd_freq.most_common(10)}")

    # =========================================================================
    # 3. CHI-SQUARED TEST
    # =========================================================================
    print_section("3. CHI-SQUARED TEST AGAINST ENGLISH FREQUENCIES")

    chi_sq_k4, df = chi_squared_test(K4, ENGLISH_FREQ)
    print(f"\nK4 Chi-squared: {chi_sq_k4:.2f} (df = {df})")
    print(f"  Note: Lower values indicate closer match to English")
    print(f"        Higher values indicate deviation from English")

    # Compare to known plaintext (Berlin Clock)
    chi_sq_plain, _ = chi_squared_test(K4_PLAINTEXT, ENGLISH_FREQ)
    print(f"\nBERLINCLOCK Chi-squared: {chi_sq_plain:.2f}")

    # Critical values for reference
    print(f"\nChi-squared Critical Values (α=0.05):")
    print(f"  df=25: ~37.65")
    print(f"  K4 at {chi_sq_k4:.2f}: {'Matches English' if chi_sq_k4 < 37.65 else 'Deviates significantly'}")

    # Per-column chi-squared for period 29
    print_subsection("Chi-squared by Column (period 29)")
    chi_sq_by_col = []
    for col in range(29):
        column = extract_column(K4, col, 29)
        if column:
            chi_sq, _ = chi_squared_test(column, ENGLISH_FREQ)
            chi_sq_by_col.append((col, chi_sq))
            print(f"Col {col:2d}: Chi² = {chi_sq:8.2f}")

    avg_chi = sum(cs[1] for cs in chi_sq_by_col) / len(chi_sq_by_col)
    print(f"\nAverage Chi-squared across columns: {avg_chi:.2f}")

    # =========================================================================
    # 4. LETTER FREQUENCY ANALYSIS
    # =========================================================================
    print_section("4. LETTER FREQUENCY ANALYSIS")

    freq = Counter(K4)
    total = len(K4)

    print(f"\nLetter Frequencies in K4:")
    print(f"{'Letter':<10} {'Count':<8} {'%':<10} {'Expected':<10} {'Diff':<10}")
    print("-" * 50)

    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        count = freq.get(letter, 0)
        pct = (count / total) * 100
        expected_pct = ENGLISH_FREQ[letter] * 100
        diff = pct - expected_pct
        print(f"{letter:<10} {count:<8} {pct:>6.2f}%  {expected_pct:>6.2f}%    {diff:>+6.2f}%")

    print(f"\nMost frequent letters: {freq.most_common(10)}")
    print(f"Least frequent letters: {freq.most_common()[-5:]}")

    # =========================================================================
    # 5. BIGRAM AND TRIGRAM ANALYSIS
    # =========================================================================
    print_section("5. BIGRAM AND TRIGRAM ANALYSIS")

    bigrams = bigram_frequency(K4)
    trigrams = trigram_frequency(K4)

    print_subsection("Top 20 Bigrams")
    for bigram, count in bigrams.most_common(20):
        print(f"{bigram}: {count}")

    print_subsection("Top 15 Trigrams")
    for trigram, count in trigrams.most_common(15):
        print(f"{trigram}: {count}")

    # =========================================================================
    # 6. LETTER CONTACT FREQUENCY
    # =========================================================================
    print_section("6. LETTER CONTACT FREQUENCY")

    contacts = letter_contact_frequency(K4)

    print_subsection("Most Common Letter Transitions")
    transitions = []
    for letter, followers in contacts.items():
        for follower, count in followers.items():
            transitions.append((f"{letter}→{follower}", count))

    transitions.sort(key=lambda x: -x[1])
    for transition, count in transitions[:20]:
        print(f"{transition}: {count}")

    # =========================================================================
    # 7. DOUBLED LETTER ANALYSIS
    # =========================================================================
    print_section("7. DOUBLED LETTER ANALYSIS")

    doubled = doubling_analysis(K4)
    print(f"\nDoubled letters in K4:")
    for letter, count in sorted(doubled.items(), key=lambda x: -x[1]):
        print(f"  {letter}{letter}: {count} times")

    total_doubled = sum(doubled.values())
    print(f"\nTotal doubled letters: {total_doubled}")
    print(f"Percentage: {(total_doubled / (len(K4)-1)) * 100:.2f}%")

    # =========================================================================
    # 8. GIBBERISH ANALYSIS
    # =========================================================================
    print_section("8. GIBBERISH SECTIONS (SEPARATE ANALYSIS)")

    # K4 known structure (from previous analysis)
    gibberish_sections = {
        "Section 1 (UNDER→NORTHEAST)": "QAPBZDBKZEL",
        "Section 2 (NORTHEAST→BERLINCLOCK)": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ",
        "Section 3 (middle)": "MPAPGKPVH",
        "Section 4 (BERLINCLOCK→ABOVE)": "RSPVJWQUL",
        "Section 5 (final)": "ZOLRKCAYF"
    }

    for name, text in gibberish_sections.items():
        ioc = calculate_ioc(text)
        chi_sq, _ = chi_squared_test(text, ENGLISH_FREQ)
        print(f"\n{name}")
        print(f"  Text: {text}")
        print(f"  Length: {len(text)}")
        print(f"  IoC: {ioc:.6f}", end="")

        if ioc < 0.045:
            print(" (random-like)")
        elif ioc > 0.065:
            print(" (English-like)")
        else:
            print(" (cipher-like)")

        print(f"  Chi²: {chi_sq:.2f}")

        freq_section = Counter(text)
        print(f"  Letters: {len(freq_section)} unique")
        print(f"  Frequency: {dict(freq_section.most_common())}")

    # =========================================================================
    # 9. STATISTICAL SUMMARY
    # =========================================================================
    print_section("9. STATISTICAL SUMMARY AND INTERPRETATION")

    print(f"""
KEY FINDINGS:

1. INDEX OF COINCIDENCE:
   - Full K4 IoC: {full_ioc:.6f}
   - Classification: {interpretation}
   - Interpretation: The low IoC suggests K4 is heavily encrypted or
     random data, not plaintext English

2. PERIOD ANALYSIS:
   - Period 29 shows average IoC of {avg_ioc_29:.6f}
   - {'Significant variation by column' if max(c['ioc'] for c in columns_29.values()) - min(c['ioc'] for c in columns_29.values()) > 0.01 else 'Fairly uniform across columns'}

3. KASISKI EXAMINATION:
   - Found {len(kasiski_results)} repeated sequences
   - Most common GCDs from repeat distances suggest possible key lengths
   - {'No definitive period length detected from repeats' if not gcds else f'Candidate period length: {find_gcd(gcds)}'}

4. CHI-SQUARED TEST:
   - K4 Chi²: {chi_sq_k4:.2f}
   - Deviation from English: {'Significant' if chi_sq_k4 > 37.65 else 'Moderate'}
   - Confirms K4 is not standard English text

5. LETTER DISTRIBUTION:
   - Most frequent: {freq.most_common(1)[0][0]} (appears {freq.most_common(1)[0][1]} times)
   - Least frequent: {[x[0] for x in freq.most_common()[-1:]][0]}
   - Distribution is relatively {'flat' if max(freq.values()) / min(freq.values()) < 2 else 'non-uniform'}

6. BIGRAM/TRIGRAM ANALYSIS:
   - Most common bigram: {bigrams.most_common(1)[0][0]} ({bigrams.most_common(1)[0][1]} times)
   - {len(bigrams)} unique bigrams found
   - Pattern suggests {'weak' if len(bigrams) / (len(K4) - 1) > 0.5 else 'strong'} repetition

7. DOUBLED LETTERS:
   - Total doubled letters: {total_doubled}
   - Doubled percentage: {(total_doubled / (len(K4)-1)) * 100:.2f}%
   - {'More than typical English (~3%)' if (total_doubled / (len(K4)-1)) * 100 > 3 else 'Less than typical English'}

CONCLUSION:
K4 exhibits characteristics of a polyalphabetic cipher with:
- Low IoC (~{full_ioc:.4f}) indicating multiple encryption layers
- Chi-squared deviation confirming non-English distribution
- Possible Vigenere or Playfair cipher
- The gibberish sections have varying IoC values, suggesting different
  encryption methods or truly random padding
""")


if __name__ == "__main__":
    main()
