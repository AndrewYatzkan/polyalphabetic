#!/usr/bin/env python3
"""
K4 Kryptos Brute Force Key Search

Brute forces the unknown key positions (0-4 and 25-28) using smart heuristics.
Scores results by English words, digraphs, trigraphs, IoC, and thematic words.
"""

import itertools
from collections import Counter
import re
import time

# Constants
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
PERIOD = 29

# Known key structure
# Positions 5-15: ELYOIECBAQK (from BERLINCLOCK crib at position 63)
# Positions 16-24: VAATCRDUM (from NORTHEAST crib at position 16)
# Unknown: positions 0,1,2,3,4 and 25,26,27,28

KNOWN_KEY = list("?????ELYOIECBAQKVAATCRDUM????")
UNKNOWN_POSITIONS_START = [0, 1, 2, 3, 4]
UNKNOWN_POSITIONS_END = [25, 26, 27, 28]
ALL_UNKNOWN = UNKNOWN_POSITIONS_START + UNKNOWN_POSITIONS_END

# Best candidate so far
BEST_CANDIDATE = "DXNZKELYOIECBAQKVAATCRDUMPABT"

# Common letters for smart search (by frequency)
COMMON_LETTERS = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
TOP_LETTERS = "ETAOINSHRDLU"  # Top 12 most common

# English word lists
COMMON_SHORT_WORDS = [
    'A', 'I', 'AN', 'AS', 'AT', 'BE', 'BY', 'DO', 'GO', 'HE', 'IF', 'IN',
    'IS', 'IT', 'ME', 'MY', 'NO', 'OF', 'ON', 'OR', 'SO', 'TO', 'UP', 'US', 'WE',
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS',
    'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'SAY', 'SHE', 'TWO', 'WAY', 'WHO',
    'DID', 'HIM', 'GET', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE'
]

COMMON_WORDS = [
    'TIME', 'VERY', 'WHEN', 'COME', 'MAKE', 'THAN', 'FIRST', 'BEEN', 'CALL',
    'FIND', 'LONG', 'DOWN', 'OVER', 'SUCH', 'TAKE', 'KNOW', 'ONLY', 'JUST',
    'THAT', 'THIS', 'HAVE', 'FROM', 'THEY', 'BEEN', 'HAVE', 'MANY', 'SOME',
    'THEM', 'THEN', 'THESE', 'THEIR', 'ABOUT', 'WOULD', 'THERE', 'COULD',
    'AFTER', 'UNDER', 'ABOVE', 'BELOW', 'FRONT', 'BACK', 'LEFT', 'RIGHT'
]

# Thematic words for Kryptos K4
THEMATIC_WORDS = [
    'CIA', 'KGB', 'SPY', 'NSA', 'FBI',
    'SECRET', 'HIDDEN', 'BURIED', 'SHADOW', 'LIGHT', 'DARK',
    'CLOCK', 'BERLIN', 'EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST',
    'DEGREES', 'MINUTES', 'SECONDS', 'LOCATION', 'COORDINATES',
    'LAYER', 'TWO', 'THREE', 'FOUR', 'LAYERS',
    'PALIMPSEST', 'ABSCISSA', 'VIRTUALLY', 'INVISIBLE',
    'DIGETAL', 'INTERPRETATU', 'UNDERGRUUND',  # Known K1-K3 words
    'ILLUSION', 'REVEAL', 'MASK', 'CODE', 'KEY',
    'LATITUDE', 'LONGITUDE', 'MONUMENT', 'SCULPTURE',
    'LANGLEY', 'VIRGINIA', 'AGENCY', 'INTELLIGENCE',
    'ENCODE', 'DECODE', 'CIPHER', 'VIGENERE',
    'UNDER', 'OVER', 'ABOVE', 'BELOW', 'BETWEEN',
    'TRUE', 'FALSE', 'REAL', 'FAKE', 'TRUTH',
    'BERLIN', 'WALL', 'COLD', 'WAR'
]

# Common English digraphs
COMMON_DIGRAPHS = [
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
    'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
    'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
    'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA'
]

# Common English trigraphs
COMMON_TRIGRAPHS = [
    'THE', 'AND', 'ING', 'ION', 'TIO', 'ENT', 'ERE', 'HER', 'ATE', 'VER',
    'TER', 'THA', 'ATI', 'FOR', 'HAT', 'ERS', 'HIS', 'RES', 'ILL', 'ARE',
    'CON', 'NCE', 'ALL', 'EVE', 'ITH', 'TED', 'AIN', 'EST', 'MAN', 'RED'
]

# Letter frequency in English (percentages)
ENG_FREQ = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
    'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
    'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
    'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07
}

def decrypt_char(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt a single character."""
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt ciphertext with Vigenere cipher."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(decrypt_char(c, k, alpha))
    return ''.join(result)

def count_words(plaintext, word_list):
    """Count how many words from word_list appear in plaintext."""
    count = 0
    found = []
    for word in word_list:
        if word in plaintext:
            count += 1
            found.append(word)
    return count, found

def calculate_ioc(text):
    """Calculate Index of Coincidence."""
    n = len(text)
    if n <= 1:
        return 0

    freq = Counter(text)
    total = sum(f * (f - 1) for f in freq.values())
    return total / (n * (n - 1))

def count_digraphs(text):
    """Count common English digraphs."""
    count = 0
    for digraph in COMMON_DIGRAPHS:
        count += text.count(digraph)
    return count

def count_trigraphs(text):
    """Count common English trigraphs."""
    count = 0
    for trigraph in COMMON_TRIGRAPHS:
        count += text.count(trigraph)
    return count

def letter_frequency_score(text):
    """Score based on similarity to English letter frequency."""
    if not text:
        return 0

    freq = Counter(text)
    n = len(text)

    score = 0
    for letter, count in freq.items():
        observed = count / n * 100
        expected = ENG_FREQ.get(letter, 0)
        # Lower difference = better score
        score -= abs(observed - expected)

    return score

def score_plaintext(plaintext):
    """
    Comprehensive scoring function for plaintext quality.
    Returns (total_score, details_dict)
    """
    score = 0
    details = {}

    # 1. Count short common words (weight: 5 per word)
    short_count, short_found = count_words(plaintext, COMMON_SHORT_WORDS)
    score += short_count * 5
    details['short_words'] = short_found

    # 2. Count longer common words (weight: 10 per word)
    long_count, long_found = count_words(plaintext, COMMON_WORDS)
    score += long_count * 10
    details['common_words'] = long_found

    # 3. Count thematic words (weight: 20 per word - high bonus)
    thematic_count, thematic_found = count_words(plaintext, THEMATIC_WORDS)
    score += thematic_count * 20
    details['thematic_words'] = thematic_found

    # 4. Digraph score (weight: 1 per occurrence)
    digraph_score = count_digraphs(plaintext)
    score += digraph_score
    details['digraphs'] = digraph_score

    # 5. Trigraph score (weight: 2 per occurrence)
    trigraph_score = count_trigraphs(plaintext) * 2
    score += trigraph_score
    details['trigraphs'] = trigraph_score // 2

    # 6. Index of Coincidence (English is ~0.067)
    ioc = calculate_ioc(plaintext)
    # Score based on closeness to English IoC
    ioc_score = max(0, 100 - abs(ioc - 0.067) * 1000)
    score += ioc_score
    details['ioc'] = ioc

    # 7. Letter frequency similarity
    freq_score = letter_frequency_score(plaintext)
    score += freq_score * 0.5
    details['freq_score'] = freq_score

    # 8. Penalize unlikely patterns
    # Penalize repeated letters (e.g., QQQ, XXX)
    for letter in KRYPTOS_ALPHA:
        triple = letter * 3
        if triple in plaintext:
            score -= 20

    # Penalize very rare letter combinations
    rare_combos = ['QQ', 'XX', 'ZZ', 'JJ', 'VV', 'WW', 'QK', 'QX', 'QZ', 'JX', 'JZ', 'VX']
    for combo in rare_combos:
        if combo in plaintext:
            score -= 5

    details['total_words'] = len(short_found) + len(long_found) + len(thematic_found)

    return score, details

def build_key(prefix, suffix):
    """Build complete key from prefix (pos 0-4) and suffix (pos 25-28)."""
    key = list(KNOWN_KEY)
    for i, c in enumerate(prefix):
        key[i] = c
    for i, c in enumerate(suffix):
        key[25 + i] = c
    return ''.join(key)

def brute_force_search(top_n=20, prefix_letters=None, suffix_letters=None, max_combinations=None):
    """
    Brute force search for best key combinations.

    Args:
        top_n: Number of top results to return
        prefix_letters: Letters to try for positions 0-4
        suffix_letters: Letters to try for positions 25-28
        max_combinations: Maximum combinations to try (None = all)
    """
    if prefix_letters is None:
        prefix_letters = TOP_LETTERS
    if suffix_letters is None:
        suffix_letters = TOP_LETTERS

    results = []
    total = len(prefix_letters) ** 5 * len(suffix_letters) ** 4

    print(f"\nSearching {total:,} combinations...")
    print(f"Prefix letters: {prefix_letters}")
    print(f"Suffix letters: {suffix_letters}")

    start_time = time.time()
    count = 0

    # Generate all combinations
    prefix_combos = itertools.product(prefix_letters, repeat=5)

    for prefix_tuple in prefix_combos:
        prefix = ''.join(prefix_tuple)

        for suffix_tuple in itertools.product(suffix_letters, repeat=4):
            suffix = ''.join(suffix_tuple)

            key = build_key(prefix, suffix)
            plaintext = vigenere_decrypt(K4, key)
            score, details = score_plaintext(plaintext)

            # Only keep if it has at least one word
            if details['total_words'] > 0:
                results.append({
                    'key': key,
                    'plaintext': plaintext,
                    'score': score,
                    'details': details
                })

            count += 1

            if max_combinations and count >= max_combinations:
                break

            # Progress update every million iterations
            if count % 1000000 == 0:
                elapsed = time.time() - start_time
                rate = count / elapsed
                print(f"  Progress: {count:,} / {total:,} ({count/total*100:.1f}%) - {rate:.0f}/sec")

        if max_combinations and count >= max_combinations:
            break

    elapsed = time.time() - start_time
    print(f"\nSearched {count:,} combinations in {elapsed:.1f} seconds ({count/elapsed:.0f}/sec)")

    # Sort by score descending
    results.sort(key=lambda x: -x['score'])

    return results[:top_n]

def targeted_search(seed_prefixes=None, seed_suffixes=None, top_n=20):
    """
    Targeted search using specific seed values and variations.
    """
    if seed_prefixes is None:
        seed_prefixes = [
            'DXNZK',  # Current best
            'DXNZD', 'DXNZE', 'DXNZA', 'DXNZT', 'DXNZS',  # Variations
            'UNDER', 'ABOVE', 'BELOW', 'CLOCK', 'NORTH',
            'SOUTH', 'LAYER', 'THREE', 'SHADO', 'LIGHT',
            'KRYPT', 'PALIN', 'BERLI', 'INTEL', 'SECRE',
            'ETAOI', 'THATN', 'THERE', 'WHERE', 'AAAAA'
        ]

    if seed_suffixes is None:
        seed_suffixes = [
            'PABT',  # Current best
            'PABA', 'PABE', 'PABN', 'PABS', 'PABD',  # Variations
            'ABLE', 'TION', 'NESS', 'MENT', 'EAST',
            'WEST', 'WARD', 'SIDE', 'THER', 'OULD',
            'ETAO', 'INSR', 'AAAA', 'EEEE', 'TTTT'
        ]

    print(f"\nTargeted search with {len(seed_prefixes)} prefixes and {len(seed_suffixes)} suffixes")

    results = []

    # Try all combinations of seeds
    for prefix in seed_prefixes:
        for suffix in seed_suffixes:
            key = build_key(prefix, suffix)
            plaintext = vigenere_decrypt(K4, key)
            score, details = score_plaintext(plaintext)

            results.append({
                'key': key,
                'plaintext': plaintext,
                'score': score,
                'details': details
            })

    # Also try variations around each seed
    print("  Trying single-character variations around seeds...")
    for base_prefix in seed_prefixes[:5]:  # Top 5 prefixes
        for pos in range(5):
            for c in TOP_LETTERS:
                prefix = base_prefix[:pos] + c + base_prefix[pos+1:]
                for suffix in seed_suffixes[:5]:  # Top 5 suffixes
                    key = build_key(prefix, suffix)
                    plaintext = vigenere_decrypt(K4, key)
                    score, details = score_plaintext(plaintext)

                    if details['total_words'] > 2:
                        results.append({
                            'key': key,
                            'plaintext': plaintext,
                            'score': score,
                            'details': details
                        })

    for base_suffix in seed_suffixes[:5]:  # Top 5 suffixes
        for pos in range(4):
            for c in TOP_LETTERS:
                suffix = base_suffix[:pos] + c + base_suffix[pos+1:]
                for prefix in seed_prefixes[:5]:  # Top 5 prefixes
                    key = build_key(prefix, suffix)
                    plaintext = vigenere_decrypt(K4, key)
                    score, details = score_plaintext(plaintext)

                    if details['total_words'] > 2:
                        results.append({
                            'key': key,
                            'plaintext': plaintext,
                            'score': score,
                            'details': details
                        })

    # Sort and deduplicate
    seen_keys = set()
    unique_results = []
    for r in results:
        if r['key'] not in seen_keys:
            seen_keys.add(r['key'])
            unique_results.append(r)

    unique_results.sort(key=lambda x: -x['score'])
    print(f"  Found {len(unique_results)} unique results")

    return unique_results[:top_n]

def exhaustive_smart_search(top_n=20):
    """
    Exhaustive search with smart pruning and prioritization.
    Uses common letters more heavily.
    """
    print("\n" + "="*70)
    print("EXHAUSTIVE SMART SEARCH")
    print("="*70)

    # Tier 1: Top 8 letters (most common)
    tier1 = "ETAOINSR"
    # Tier 2: Next 8 letters
    tier2 = "HDLCUMWF"
    # Tier 3: Less common
    tier3 = "GYPBVKJXQZ"

    all_results = []

    # Phase 1: All combinations of tier 1 letters (8^9 = 134 million - too many)
    # Use tier 1 for first 3 positions, tier 1+2 for rest
    print("\nPhase 1: High-probability search (top 8 letters for all positions)")
    results1 = brute_force_search(top_n=100, prefix_letters=tier1[:8], suffix_letters=tier1[:8])
    all_results.extend(results1)

    # Phase 2: Mix in tier 2 letters
    print("\nPhase 2: Extended search with tier 2 letters")
    results2 = brute_force_search(top_n=100, prefix_letters=(tier1+tier2)[:12], suffix_letters=tier1[:6], max_combinations=10000000)
    all_results.extend(results2)

    # Phase 3: Targeted search
    print("\nPhase 3: Targeted search with known good patterns")
    results3 = targeted_search(top_n=100)
    all_results.extend(results3)

    # Deduplicate and sort
    seen_keys = set()
    unique_results = []
    for r in all_results:
        if r['key'] not in seen_keys:
            seen_keys.add(r['key'])
            unique_results.append(r)

    unique_results.sort(key=lambda x: -x['score'])

    return unique_results[:top_n]

def display_results(results, title="RESULTS"):
    """Display results in a formatted way."""
    print("\n" + "="*70)
    print(title)
    print("="*70)

    for i, r in enumerate(results, 1):
        print(f"\n--- Result #{i} (Score: {r['score']:.1f}) ---")
        print(f"Key: {r['key']}")
        print(f"Plaintext: {r['plaintext']}")

        all_words = r['details'].get('short_words', []) + \
                   r['details'].get('common_words', []) + \
                   r['details'].get('thematic_words', [])

        if all_words:
            print(f"Words found ({len(all_words)}): {', '.join(sorted(set(all_words), key=len, reverse=True))}")

        print(f"IoC: {r['details'].get('ioc', 0):.4f} (English ~0.067)")
        print(f"Digraphs: {r['details'].get('digraphs', 0)}, Trigraphs: {r['details'].get('trigraphs', 0)}")

def analyze_best_candidate():
    """Analyze the current best candidate key."""
    print("="*70)
    print("ANALYZING BEST CANDIDATE KEY")
    print("="*70)

    key = BEST_CANDIDATE
    plaintext = vigenere_decrypt(K4, key)
    score, details = score_plaintext(plaintext)

    print(f"\nKey: {key}")
    print(f"Plaintext: {plaintext}")
    print(f"\nScore: {score:.1f}")

    all_words = details.get('short_words', []) + \
               details.get('common_words', []) + \
               details.get('thematic_words', [])

    print(f"\nWords found ({len(all_words)}):")
    for word in sorted(set(all_words), key=len, reverse=True):
        # Find position in plaintext
        pos = plaintext.find(word)
        print(f"  {word} (position {pos})")

    print(f"\nIndex of Coincidence: {details['ioc']:.4f}")
    print(f"Common digraphs: {details['digraphs']}")
    print(f"Common trigraphs: {details['trigraphs']}")

def main():
    print("="*70)
    print("K4 KRYPTOS BRUTE FORCE KEY SEARCH")
    print("="*70)
    print(f"\nCiphertext: {K4}")
    print(f"Length: {len(K4)}")
    print(f"\nKnown key structure (Period 29):")
    print(f"  Positions 5-15:  ELYOIECBAQK (from BERLINCLOCK crib)")
    print(f"  Positions 16-24: VAATCRDUM (from NORTHEAST crib)")
    print(f"  Unknown: positions 0-4 and 25-28 (9 positions)")
    print(f"\nBest candidate so far: {BEST_CANDIDATE}")

    # First, analyze the best candidate
    analyze_best_candidate()

    # Run exhaustive smart search
    print("\n" + "="*70)
    print("STARTING BRUTE FORCE SEARCH")
    print("="*70)

    results = exhaustive_smart_search(top_n=20)

    # Display top 20 results
    display_results(results, "TOP 20 RESULTS")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if results:
        best = results[0]
        print(f"\nBest result found:")
        print(f"  Key: {best['key']}")
        print(f"  Score: {best['score']:.1f}")
        print(f"  Plaintext: {best['plaintext']}")

        all_words = best['details'].get('short_words', []) + \
                   best['details'].get('common_words', []) + \
                   best['details'].get('thematic_words', [])
        print(f"  Words: {', '.join(sorted(set(all_words), key=len, reverse=True))}")

if __name__ == "__main__":
    main()
