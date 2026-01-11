#!/usr/bin/env python3
"""
Systematic analysis of Kryptos gap sections to extract missing coordinates:
38 (latitude degrees), 6 (latitude seconds), 77 (longitude degrees)
"""

from itertools import combinations
from collections import Counter

# Gap sections
gaps = {
    'Gap1': 'QAPBZDBKZEL',
    'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'Gap3': 'RSPVJWQUL',
    'Gap4': 'ZOLRKCAYF',
}

# Target numbers
targets = [38, 6, 77]

def letter_to_num(letter):
    """Convert letter to 1-26 (A=1, Z=26)"""
    return ord(letter.upper()) - ord('A') + 1

def mod_analysis(text, mod_val, gap_name=''):
    """Analyze using modulo operations"""
    results = []
    for i, char in enumerate(text):
        num = letter_to_num(char)
        mod_result = num % mod_val
        if mod_result == 0:
            mod_result = mod_val
        results.append((char, num, mod_result))
    return results

def position_based_extraction(text, gap_name=''):
    """Extract numbers based on character positions"""
    results = []
    for i, char in enumerate(text):
        num = letter_to_num(char)
        # Try various position-based combinations
        results.append({
            'char': char,
            'value': num,
            'pos_1indexed': i + 1,
            'value_sum_with_pos': num + (i + 1),
            'value_times_pos': num * (i + 1),
        })
    return results

def letter_pair_sums(text, gap_name=''):
    """Sum pairs of letters"""
    results = []
    for i in range(0, len(text) - 1, 2):
        char1, char2 = text[i], text[i + 1]
        num1, num2 = letter_to_num(char1), letter_to_num(char2)
        pair_sum = num1 + num2
        results.append({
            'pair': char1 + char2,
            'num1': num1,
            'num2': num2,
            'sum': pair_sum,
            'product': num1 * num2,
            'diff': abs(num1 - num2),
            'sum_mod10': pair_sum % 10,
            'sum_mod26': pair_sum % 26 or 26,
        })
    return results

def reverse_extraction(text, gap_name=''):
    """Extract from reversed text"""
    reversed_text = text[::-1]
    results = []
    for i, char in enumerate(reversed_text):
        num = letter_to_num(char)
        results.append({
            'char': char,
            'original_pos': len(text) - 1 - i,
            'reversed_pos': i,
            'value': num,
        })
    return results

def first_last_extraction(text, gap_name=''):
    """Extract using first/last characters"""
    results = []
    if len(text) >= 2:
        first = letter_to_num(text[0])
        last = letter_to_num(text[-1])
        results.append({
            'first': text[0],
            'first_val': first,
            'last': text[-1],
            'last_val': last,
            'sum': first + last,
            'diff': abs(first - last),
            'product': first * last,
            'concat_fl': int(str(first) + str(last)),
            'concat_lf': int(str(last) + str(first)),
        })
    return results

def ascii_sum_analysis(text, gap_name=''):
    """Analyze ASCII sum patterns"""
    results = []
    total_sum = sum(ord(c) for c in text)
    total_letters = sum(letter_to_num(c) for c in text)

    results.append({
        'ascii_sum': total_sum,
        'letter_values_sum': total_letters,
        'ascii_mod10': total_sum % 10,
        'ascii_mod26': total_sum % 26 or 26,
        'letters_mod10': total_letters % 10,
        'letters_mod26': total_letters % 26 or 26,
        'ascii_divmod10': (total_sum // 10, total_sum % 10),
        'letters_divmod10': (total_letters // 10, total_letters % 10),
        'unique_letters': len(set(text)),
        'total_length': len(text),
    })

    return results

def gap_combined_analysis(gap_dict):
    """Analyze combinations of gaps"""
    results = []

    # Try concatenating different gaps
    g1 = gap_dict['Gap1']
    g2 = gap_dict['Gap2']
    g3 = gap_dict['Gap3']
    g4 = gap_dict['Gap4']

    combinations_to_test = [
        ('G1+G3', g1 + g3),
        ('G1+G4', g1 + g4),
        ('G3+G4', g3 + g4),
        ('G1+G2', g1 + g2),
        ('G2+G3', g2 + g3),
        ('G2+G4', g2 + g4),
    ]

    for name, combined in combinations_to_test:
        total = sum(letter_to_num(c) for c in combined)
        results.append({
            'combination': name,
            'length': len(combined),
            'total_value': total,
            'total_mod10': total % 10,
            'total_mod100': total % 100,
            'divmod10': (total // 10, total % 10),
        })

    return results

def test_modulo_patterns():
    """Test all modulo patterns for targets"""
    print("\n" + "="*80)
    print("MODULO PATTERN ANALYSIS")
    print("="*80)

    for mod_val in [5, 8, 10, 26]:
        print(f"\n--- MOD {mod_val} ANALYSIS ---")
        for gap_name, text in gaps.items():
            print(f"\n{gap_name}: {text}")
            results = mod_analysis(text, mod_val, gap_name)
            mod_results = [r[2] for r in results]

            # Check for target sequences
            for target in targets:
                if target in mod_results:
                    indices = [i for i, r in enumerate(results) if r[2] == target]
                    print(f"  >>> MOD {mod_val}: Found {target} at positions {indices}: {[results[i][0] for i in indices]}")

def test_position_based():
    """Test position-based extraction"""
    print("\n" + "="*80)
    print("POSITION-BASED EXTRACTION")
    print("="*80)

    for gap_name, text in gaps.items():
        print(f"\n{gap_name}: {text}")
        results = position_based_extraction(text, gap_name)

        # Extract digits that match targets
        all_values = [r['value'] for r in results]

        # Check for consecutive patterns
        for i in range(len(all_values) - 1):
            combined = int(str(all_values[i]) + str(all_values[i+1]))
            if combined in targets or combined in [38, 6, 77]:
                print(f"  >>> Position {i},{i+1}: {all_values[i]},{all_values[i+1]} = {combined}")

            # Check sum_with_pos
            if results[i]['value_sum_with_pos'] in targets:
                print(f"  >>> Position {i}: value({results[i]['value']}) + pos({results[i]['pos_1indexed']}) = {results[i]['value_sum_with_pos']}")

def test_letter_pairs():
    """Test letter pair sums"""
    print("\n" + "="*80)
    print("LETTER PAIR ANALYSIS")
    print("="*80)

    for gap_name, text in gaps.items():
        print(f"\n{gap_name}: {text}")
        results = letter_pair_sums(text, gap_name)

        for i, r in enumerate(results):
            if r['sum'] in targets:
                print(f"  >>> Pair {i}: {r['pair']} = {r['num1']}+{r['num2']} = {r['sum']}")
            if r['sum'] in [38, 6, 77, 16]:
                if r['sum'] >= 38:
                    print(f"  >>> Pair {i}: {r['pair']} = {r['num1']}+{r['num2']} = {r['sum']}")

def test_reverse_patterns():
    """Test reverse order extraction"""
    print("\n" + "="*80)
    print("REVERSE ORDER EXTRACTION")
    print("="*80)

    for gap_name, text in gaps.items():
        print(f"\n{gap_name}: {text}")
        reversed_text = text[::-1]
        print(f"  Reversed: {reversed_text}")

        # Check for numeric patterns in reversed
        reversed_nums = [letter_to_num(c) for c in reversed_text]

        # Check consecutive pairs in reversed
        for i in range(len(reversed_nums) - 1):
            combined = int(str(reversed_nums[i]) + str(reversed_nums[i+1]))
            if combined in [38, 6, 77, 6]:
                print(f"  >>> Reversed positions {i},{i+1}: {reversed_nums[i]},{reversed_nums[i+1]} = {combined}")

def test_first_last():
    """Test first/last character extraction"""
    print("\n" + "="*80)
    print("FIRST/LAST CHARACTER ANALYSIS")
    print("="*80)

    for gap_name, text in gaps.items():
        results = first_last_extraction(text, gap_name)
        for r in results:
            print(f"\n{gap_name}: {text}")
            print(f"  First: {r['first']}({r['first_val']}) Last: {r['last']}({r['last_val']})")
            print(f"    Sum: {r['sum']}")
            print(f"    Diff: {r['diff']}")
            print(f"    Product: {r['product']}")
            print(f"    Concat (FL): {r['concat_fl']}")
            print(f"    Concat (LF): {r['concat_lf']}")

            if r['sum'] in targets:
                print(f"    >>> SUM MATCHES: {r['sum']}")
            if r['product'] in targets:
                print(f"    >>> PRODUCT MATCHES: {r['product']}")
            if r['concat_fl'] in targets:
                print(f"    >>> CONCAT FL MATCHES: {r['concat_fl']}")
            if r['concat_lf'] in targets:
                print(f"    >>> CONCAT LF MATCHES: {r['concat_lf']}")

def test_ascii_sums():
    """Test ASCII and letter value sums"""
    print("\n" + "="*80)
    print("ASCII SUM ANALYSIS")
    print("="*80)

    for gap_name, text in gaps.items():
        results = ascii_sum_analysis(text, gap_name)
        for r in results:
            print(f"\n{gap_name} ({len(text)} chars, {r['unique_letters']} unique):")
            print(f"  Total letter values: {r['letter_values_sum']}")
            print(f"  Letters mod 10: {r['letters_mod10']}")
            print(f"  Letters mod 26: {r['letters_mod26']}")
            print(f"  DivMod 10: {r['letters_divmod10']}")

            if r['letter_values_sum'] in targets or r['letter_values_sum'] in [38, 77]:
                print(f"    >>> TOTAL MATCHES TARGET: {r['letter_values_sum']}")

def test_gap_combinations():
    """Test combinations of gaps"""
    print("\n" + "="*80)
    print("GAP COMBINATION ANALYSIS")
    print("="*80)

    results = gap_combined_analysis(gaps)
    for r in results:
        print(f"\n{r['combination']}: {r['total_value']} (length={r['length']})")
        print(f"  Mod 10: {r['total_mod10']}")
        print(f"  Mod 100: {r['total_mod100']}")
        print(f"  DivMod 10: {r['divmod10']}")

        if r['total_value'] in targets:
            print(f"  >>> TOTAL MATCHES: {r['total_value']}")
        if r['divmod10'][0] in targets or r['divmod10'][1] in targets:
            print(f"  >>> DIVMOD COMPONENT MATCHES: {r['divmod10']}")

def test_gap3_gap4_special():
    """Special analysis for Gap3 and Gap4 (all unique letters)"""
    print("\n" + "="*80)
    print("GAP 3 & 4 SPECIAL ANALYSIS (All Unique Letters)")
    print("="*80)

    for gap_name in ['Gap3', 'Gap4']:
        text = gaps[gap_name]
        print(f"\n{gap_name}: {text}")
        print(f"  Length: {len(text)} (all unique: {len(text) == len(set(text))})")
        print(f"  Unique letters: {set(text)}")

        # Since all letters are unique, analyze patterns
        nums = [letter_to_num(c) for c in text]
        print(f"  Values: {nums}")
        print(f"  Sum: {sum(nums)}")
        print(f"  Product: {eval('*'.join(map(str, nums)))}")

        # Try different combinations
        print(f"\n  Testing consecutive pairs:")
        for i in range(len(nums) - 1):
            pair_sum = nums[i] + nums[i+1]
            if pair_sum in targets:
                print(f"    >>> {text[i]}{text[i+1]}: {nums[i]}+{nums[i+1]} = {pair_sum} MATCHES")

            # Also check if concatenation matches
            concat = int(str(nums[i]) + str(nums[i+1]))
            if concat in targets:
                print(f"    >>> {text[i]}{text[i+1]}: concat {concat} MATCHES")

        # Check first-last
        first_last_sum = nums[0] + nums[-1]
        first_last_concat = int(str(nums[0]) + str(nums[-1]))
        print(f"\n  First+Last: {text[0]}({nums[0]}) + {text[-1]}({nums[-1]}) = {first_last_sum}")
        print(f"  First-Last concat: {first_last_concat}")

        if first_last_sum in targets:
            print(f"    >>> Sum MATCHES: {first_last_sum}")
        if first_last_concat in targets:
            print(f"    >>> Concat MATCHES: {first_last_concat}")

def extract_number_sequences():
    """Look for two-digit sequences across all gaps"""
    print("\n" + "="*80)
    print("LOOKING FOR TWO-DIGIT NUMBER SEQUENCES")
    print("="*80)

    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        print(f"\n{gap_name}: {text}")
        print(f"  Letter values: {nums}")

        # Form two-digit numbers
        two_digit_numbers = []
        for i in range(len(nums) - 1):
            two_digit = int(str(nums[i]) + str(nums[i+1]))
            two_digit_numbers.append(two_digit)

            if two_digit in [38, 6, 77, 6]:
                print(f"    >>> Position {i}-{i+1}: {text[i]}{text[i+1]} = {two_digit} *** MATCH ***")

        print(f"  All two-digit combinations: {two_digit_numbers}")

def main():
    print("\n" + "="*80)
    print("KRYPTOS COORDINATE EXTRACTION - SYSTEMATIC ANALYSIS")
    print("="*80)
    print("\nTarget coordinates: 38, 6, 77")
    print("\nGaps:")
    for name, text in gaps.items():
        print(f"  {name}: {text} (length={len(text)})")

    # Run all analyses
    extract_number_sequences()
    test_modulo_patterns()
    test_position_based()
    test_letter_pairs()
    test_first_last()
    test_reverse_patterns()
    test_ascii_sums()
    test_gap3_gap4_special()
    test_gap_combinations()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
