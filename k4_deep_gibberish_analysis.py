#!/usr/bin/env python3
"""
DEEP STATISTICAL ANALYSIS OF K4 GIBBERISH SECTIONS
Analyzes combined gibberish, individual gaps, and compares to K1, K2, K3
"""

import math
import collections
from collections import Counter, defaultdict
import string

# K4 Full text (confirmed)
K4_FULL = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# K1, K2, K3 full texts (for comparison)
K1_FULL = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K2_FULL = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
K3_FULL = "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWENATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAECTDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIMEHNLSSTTRTVDOHW"

# K4 COMBINED GIBBERISH (67 chars) - the parts NOT part of the solution keywords
# Based on: UNDER|NORTHEAST|BERLINCLOCK|ABOVE
# K4 gap structure: [gap1] UNDER [gap2] NORTHEAST [gap3] BERLINCLOCK [gap4] ABOVE [gap5]
# Let me recalculate based on the 97-char K4 full text

# Actually, let me work with the combined gibberish you provided
GIBBERISH_COMBINED = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

# Individual gaps
GAP1 = "QAPBZDBKZEL"
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

# English reference frequency (% of each letter)
ENGLISH_FREQ = {
    'A': 8.17, 'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.70, 'F': 2.23,
    'G': 2.02, 'H': 6.09, 'I': 6.97, 'J': 0.15, 'K': 0.77, 'L': 4.03,
    'M': 2.41, 'N': 6.75, 'O': 7.51, 'P': 1.93, 'Q': 0.10, 'R': 5.99,
    'S': 6.33, 'T': 9.06, 'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15,
    'Y': 1.97, 'Z': 0.07
}

# Random cipher reference frequency (uniform: 1/26 ≈ 3.85%)
RANDOM_FREQ = {chr(i): 100/26 for i in range(ord('A'), ord('Z')+1)}


def calculate_ioc(text):
    """Calculate Index of Coincidence"""
    text = text.upper()
    n = len(text)
    if n < 2:
        return 0.0

    freq = Counter(c for c in text if c in string.ascii_uppercase)

    ioc = sum(count * (count - 1) for count in freq.values()) / (n * (n - 1))
    return ioc


def calculate_entropy(text):
    """Calculate Shannon entropy (bits per character)"""
    text = text.upper()
    freq = Counter(c for c in text if c in string.ascii_uppercase)
    n = len([c for c in text if c in string.ascii_uppercase])

    if n == 0:
        return 0.0

    entropy = 0.0
    for count in freq.values():
        p = count / n
        entropy -= p * math.log2(p)

    return entropy


def get_letter_frequencies(text):
    """Get letter frequency distribution as percentage"""
    text = text.upper()
    freq = Counter(c for c in text if c in string.ascii_uppercase)
    total = sum(freq.values())

    result = {}
    for letter in string.ascii_uppercase:
        result[letter] = (freq.get(letter, 0) / total * 100) if total > 0 else 0.0

    return result


def chi_squared_test(observed_freq_dict, expected_freq_dict, total_chars):
    """
    Chi-squared test comparing observed vs expected frequencies
    observed_freq_dict: {letter: count}
    expected_freq_dict: {letter: percentage}
    total_chars: total character count
    """
    chi2 = 0.0

    for letter in string.ascii_uppercase:
        observed = observed_freq_dict.get(letter, 0)
        expected_percent = expected_freq_dict.get(letter, 0)
        expected = total_chars * expected_percent / 100.0

        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    return chi2


def analyze_repeated_sequences(text, min_len=2, max_len=6):
    """Find repeated sequences and their distances"""
    text = text.upper()
    repeats = defaultdict(list)

    for length in range(min_len, max_len + 1):
        for i in range(len(text) - length + 1):
            seq = text[i:i+length]
            if seq in text[i+1:]:
                if seq not in repeats:
                    repeats[seq] = []
                # Find all positions
                pos = i
                for j in range(i+1, len(text) - length + 1):
                    if text[j:j+length] == seq:
                        repeats[seq].append(j)

    return repeats


def analyze_bigrams_trigrams(text):
    """Analyze bigram and trigram frequencies"""
    text = text.upper()

    bigrams = Counter()
    trigrams = Counter()

    for i in range(len(text) - 1):
        bigrams[text[i:i+2]] += 1

    for i in range(len(text) - 2):
        trigrams[text[i:i+3]] += 1

    return bigrams, trigrams


def calculate_chi2_vs_english(text):
    """Calculate chi-squared vs English frequency"""
    text = text.upper()
    freq = Counter(c for c in text if c in string.ascii_uppercase)
    total = sum(freq.values())

    if total == 0:
        return 0.0

    chi2 = 0.0
    for letter in string.ascii_uppercase:
        observed = freq.get(letter, 0)
        expected = total * ENGLISH_FREQ[letter] / 100.0
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    return chi2


def calculate_chi2_vs_random(text):
    """Calculate chi-squared vs random (uniform) frequency"""
    text = text.upper()
    freq = Counter(c for c in text if c in string.ascii_uppercase)
    total = sum(freq.values())

    if total == 0:
        return 0.0

    chi2 = 0.0
    expected_per_letter = total / 26.0

    for letter in string.ascii_uppercase:
        observed = freq.get(letter, 0)
        if expected_per_letter > 0:
            chi2 += (observed - expected_per_letter) ** 2 / expected_per_letter

    return chi2


def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        padding = (80 - len(title) - 4) // 2
        print("\n" + "=" * padding + " " + title + " " + "=" * padding)
    else:
        print("=" * 80)


def analyze_text(text, name, compare_to_english=True, compare_to_random=True):
    """Comprehensive analysis of text"""
    text = text.upper()

    print(f"\n{'─' * 80}")
    print(f"Analysis of: {name}")
    print(f"Length: {len(text)} characters")
    print(f"{'─' * 80}")

    # 1. Letter Frequency
    freq = Counter(c for c in text if c in string.ascii_uppercase)
    print(f"\n1. LETTER FREQUENCY")
    print(f"{'Letter':<8} {'Count':<8} {'Percent':<12} {'English%':<12} {'Diff':<10}")
    print("─" * 50)

    total = sum(freq.values())
    for letter in sorted(string.ascii_uppercase):
        count = freq.get(letter, 0)
        percent = (count / total * 100) if total > 0 else 0.0
        eng_percent = ENGLISH_FREQ[letter]
        diff = percent - eng_percent
        print(f"{letter:<8} {count:<8} {percent:>6.2f}% {eng_percent:>11.2f}% {diff:>8.2f}%")

    # 2. Index of Coincidence
    ioc = calculate_ioc(text)
    print(f"\n2. INDEX OF COINCIDENCE (IoC)")
    print(f"Text IoC: {ioc:.6f}")
    print(f"English IoC: ~0.067")
    print(f"Random IoC: ~0.038")
    if ioc > 0.060:
        classification = "ENGLISH-LIKE (probable plaintext or weakly encrypted)"
    elif ioc > 0.045:
        classification = "INTERMEDIATE (possible polyalphabetic or mixed)"
    else:
        classification = "RANDOM-LIKE (strongly encrypted or truly random)"
    print(f"Classification: {classification}")

    # 3. Entropy
    entropy = calculate_entropy(text)
    print(f"\n3. SHANNON ENTROPY")
    print(f"Text entropy: {entropy:.4f} bits/char")
    print(f"Maximum entropy (random): {math.log2(26):.4f} bits/char")
    print(f"Percentage of maximum: {(entropy/math.log2(26)*100):.1f}%")

    # 4. Unique letters
    unique = len(freq)
    print(f"\n4. UNIQUE LETTERS")
    print(f"Unique letters: {unique}/26")
    print(f"Missing letters: {26 - unique}")
    missing = [l for l in string.ascii_uppercase if l not in freq]
    if missing:
        print(f"Missing: {' '.join(missing)}")

    # 5. Chi-squared tests
    chi2_english = calculate_chi2_vs_english(text)
    chi2_random = calculate_chi2_vs_random(text)

    print(f"\n5. CHI-SQUARED TESTS")
    print(f"vs English frequency: χ² = {chi2_english:.2f}")
    print(f"  (Lower is better match to English)")
    print(f"vs Random frequency: χ² = {chi2_random:.2f}")
    print(f"  (Lower is better match to random)")

    # Critical value for df=25 at α=0.05
    critical_value = 37.65
    print(f"Critical value (df=25, α=0.05): {critical_value:.2f}")
    if chi2_english > critical_value:
        print(f"Result: Significantly different from English (p < 0.05)")
    else:
        print(f"Result: Not significantly different from English")

    # 6. Most/least frequent letters
    most_common = freq.most_common(10)
    print(f"\n6. MOST FREQUENT LETTERS")
    for letter, count in most_common:
        print(f"  {letter}: {count} times ({count/total*100:.1f}%)")

    # 7. Bigrams and Trigrams
    bigrams, trigrams = analyze_bigrams_trigrams(text)
    print(f"\n7. BIGRAM/TRIGRAM ANALYSIS")
    print(f"Unique bigrams: {len(bigrams)}")
    print(f"Unique trigrams: {len(trigrams)}")
    print(f"Most common bigrams:")
    for bigram, count in bigrams.most_common(10):
        print(f"  {bigram}: {count}")

    # 8. Doubled letters
    doubled = 0
    double_count = Counter()
    for i in range(len(text) - 1):
        if text[i] == text[i+1]:
            doubled += 1
            double_count[text[i:i+2]] += 1

    print(f"\n8. DOUBLED LETTERS")
    print(f"Total doubled letters: {doubled}")
    if total > 0:
        print(f"Percentage: {doubled/total*100:.2f}%")
    if double_count:
        print(f"Doubled letter counts:")
        for double, count in double_count.most_common():
            print(f"  {double}: {count}")

    # 9. Repeating sequences
    print(f"\n9. REPEATING SEQUENCES")
    repeats = analyze_repeated_sequences(text, min_len=2, max_len=4)
    if repeats:
        for seq, positions in sorted(repeats.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            print(f"  '{seq}' at positions {positions}, distances: {distances}")
    else:
        print("  No repeating sequences found")

    return {
        'text': text,
        'length': len(text),
        'ioc': ioc,
        'entropy': entropy,
        'chi2_english': chi2_english,
        'chi2_random': chi2_random,
        'unique_letters': unique,
        'frequency': freq,
    }


def print_comparison(analyses):
    """Compare multiple analyses"""
    print_separator("COMPARATIVE ANALYSIS")

    print(f"\n{'Metric':<25} " + "".join(f"{name:<15}" for name in analyses.keys()))
    print("─" * (25 + 15 * len(analyses)))

    # Length
    print(f"{'Length':<25} " + "".join(f"{data['length']:<15}" for data in analyses.values()))

    # IoC
    print(f"{'Index of Coincidence':<25} " + "".join(f"{data['ioc']:<15.6f}" for data in analyses.values()))

    # Entropy
    print(f"{'Entropy (bits/char)':<25} " + "".join(f"{data['entropy']:<15.4f}" for data in analyses.values()))

    # Unique letters
    print(f"{'Unique Letters':<25} " + "".join(f"{data['unique_letters']:<15}/26" for data in analyses.values()))

    # Chi-squared vs English
    print(f"{'Chi² vs English':<25} " + "".join(f"{data['chi2_english']:<15.2f}" for data in analyses.values()))

    # Chi-squared vs Random
    print(f"{'Chi² vs Random':<25} " + "".join(f"{data['chi2_random']:<15.2f}" for data in analyses.values()))


def main():
    print_separator("DEEP STATISTICAL ANALYSIS: K4 GIBBERISH")
    print("\nThis analysis examines the 67-character K4 gibberish combined text")
    print("and compares individual gaps to determine encryption characteristics.\n")

    # Analyze combined gibberish
    print_separator("SECTION 1: COMBINED GIBBERISH (67 chars)")
    combined = analyze_text(GIBBERISH_COMBINED, "COMBINED K4 GIBBERISH")

    # Analyze individual gaps
    print_separator("SECTION 2: INDIVIDUAL GAPS")

    gap1 = analyze_text(GAP1, f"GAP1 ({len(GAP1)} chars)")
    gap2 = analyze_text(GAP2, f"GAP2 ({len(GAP2)} chars)")
    gap3 = analyze_text(GAP3, f"GAP3 ({len(GAP3)} chars)")
    gap4 = analyze_text(GAP4, f"GAP4 ({len(GAP4)} chars)")

    # Analyze K1, K2, K3 for comparison
    print_separator("SECTION 3: K1, K2, K3 COMPARISON")

    k1 = analyze_text(K1_FULL, f"K1 CIPHERTEXT ({len(K1_FULL)} chars)")
    k2 = analyze_text(K2_FULL, f"K2 CIPHERTEXT ({len(K2_FULL)} chars)")
    k3 = analyze_text(K3_FULL, f"K3 CIPHERTEXT ({len(K3_FULL)} chars)")

    # Comparative analysis
    analyses = {
        'Gibberish': combined,
        'Gap1': gap1,
        'Gap2': gap2,
        'Gap3': gap3,
        'Gap4': gap4,
        'K1': k1,
        'K2': k2,
        'K3': k3,
    }

    print_comparison(analyses)

    # Statistical interpretation
    print_separator("SECTION 4: STATISTICAL INTERPRETATION")

    print("\n1. GIBBERISH NATURE ANALYSIS")
    print(f"   Combined gibberish IoC: {combined['ioc']:.6f}")
    if combined['ioc'] > 0.060:
        print("   → ENGLISH ENCRYPTED: Low IoC suggests encrypted English or multiple layers")
    elif combined['ioc'] > 0.045:
        print("   → INTERMEDIATE: Possibly polyalphabetic encryption")
    else:
        print("   → RANDOM/STRONGLY ENCRYPTED: Low IoC suggests true randomness or strong encryption")

    print(f"\n2. ENTROPY ANALYSIS")
    print(f"   Combined gibberish entropy: {combined['entropy']:.4f} bits/char")
    max_entropy = math.log2(26)
    entropy_ratio = combined['entropy'] / max_entropy
    print(f"   Entropy ratio: {entropy_ratio*100:.1f}% of maximum")
    if entropy_ratio > 0.95:
        print("   → Nearly perfect randomness (low entropy)")
    elif entropy_ratio > 0.75:
        print("   → High entropy, likely encrypted")
    else:
        print("   → Moderate entropy, possibly structured data")

    print(f"\n3. CHI-SQUARED ANALYSIS")
    print(f"   vs English: {combined['chi2_english']:.2f} (lower = more English-like)")
    print(f"   vs Random:  {combined['chi2_random']:.2f} (lower = more random-like)")
    if combined['chi2_english'] > 37.65:
        print("   → Significantly deviates from English distribution")
    if combined['chi2_random'] < 37.65:
        print("   → Could match random distribution")

    print(f"\n4. GAP COMPARISON")
    print(f"   Gap IoC values: {gap1['ioc']:.4f}, {gap2['ioc']:.4f}, {gap3['ioc']:.4f}, {gap4['ioc']:.4f}")
    gaps_ioc = [gap1['ioc'], gap2['ioc'], gap3['ioc'], gap4['ioc']]
    if max(gaps_ioc) - min(gaps_ioc) > 0.03:
        print("   → Gaps have DIFFERENT IoC signatures (possible multiple encryption methods)")
    else:
        print("   → Gaps have SIMILAR IoC signatures (consistent encryption method)")

    print(f"\n5. COMPARISON TO K1, K2, K3")
    print(f"   K1 IoC: {k1['ioc']:.6f}")
    print(f"   K2 IoC: {k2['ioc']:.6f}")
    print(f"   K3 IoC: {k3['ioc']:.6f}")
    print(f"   Gibberish IoC: {combined['ioc']:.6f}")

    if combined['ioc'] < min([k1['ioc'], k2['ioc'], k3['ioc']]):
        print("   → Gibberish is MORE encrypted than K1, K2, K3")
    elif combined['ioc'] > max([k1['ioc'], k2['ioc'], k3['ioc']]):
        print("   → Gibberish is LESS encrypted than K1, K2, K3")
    else:
        print("   → Gibberish has INTERMEDIATE encryption level")

    # Final determination
    print_separator("FINAL ASSESSMENT")

    print("\nThe K4 gibberish is characterized as:")

    conditions = []

    if combined['ioc'] < 0.045:
        conditions.append("- LOW ENTROPY/RANDOMNESS (IoC < 0.045)")
    else:
        conditions.append("- MEDIUM ENTROPY (IoC ≥ 0.045)")

    if combined['entropy'] > math.log2(26) * 0.9:
        conditions.append("- HIGHLY RANDOM DISTRIBUTION (entropy > 90%)")
    elif combined['entropy'] > math.log2(26) * 0.7:
        conditions.append("- MODERATELY RANDOM (entropy 70-90%)")
    else:
        conditions.append("- STRUCTURED PATTERNS (entropy < 70%)")

    if combined['chi2_english'] > 300:
        conditions.append("- STRONGLY DEVIATES FROM ENGLISH")
    else:
        conditions.append("- MODERATELY DEVIATES FROM ENGLISH")

    if max(gaps_ioc) - min(gaps_ioc) > 0.03:
        conditions.append("- HETEROGENEOUS GAPS (different encryption methods or padding)")
    else:
        conditions.append("- HOMOGENEOUS GAPS (consistent encryption across all sections)")

    for condition in conditions:
        print(condition)

    print("\nCONCLUSION:")
    if combined['ioc'] > 0.060:
        print("The gibberish is ENCRYPTED ENGLISH")
        print("  Likely scenario: Multi-layer encryption of actual plaintext")
        print("  Action: Focus on cryptanalysis of encryption schemes")
    elif combined['ioc'] > 0.045:
        print("The gibberish is MIXED/INTERMEDIATE")
        print("  Likely scenario: Polyalphabetic encryption with fallback")
        print("  Action: Test Vigenere, Playfair, and other classical ciphers")
    else:
        print("The gibberish appears RANDOM or STRONGLY ENCRYPTED")
        print("  Likely scenario: True random data or very strong encryption")
        print("  Possibility: Coordinates, metadata, or structured data encoded as gibberish")
        print("  Action: Look for non-linguistic patterns (numbers, coordinates, dates)")


if __name__ == "__main__":
    main()
