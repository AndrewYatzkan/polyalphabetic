#!/usr/bin/env python3
"""
Targeted analysis to find 77 (longitude degrees)
"""

gaps = {
    'Gap1': 'QAPBZDBKZEL',
    'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'Gap3': 'RSPVJWQUL',
    'Gap4': 'ZOLRKCAYF',
}

def letter_to_num(letter):
    """Convert letter to 1-26 (A=1, Z=26)"""
    return ord(letter.upper()) - ord('A') + 1

def find_77():
    """Find 77 using various methods"""
    print("\n" + "="*80)
    print("SEARCHING FOR 77 (Longitude Degrees)")
    print("="*80)

    # Method 1: Three consecutive values that sum to 77
    print("\n--- THREE CONSECUTIVE LETTERS SUMMING TO 77 ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        for i in range(len(nums) - 2):
            triple_sum = nums[i] + nums[i+1] + nums[i+2]
            if triple_sum == 77:
                print(f"\n{gap_name}: {text[i]}{text[i+1]}{text[i+2]} = {nums[i]}+{nums[i+1]}+{nums[i+2]} = {triple_sum} *** MATCH ***")

    # Method 2: Two pairs from same gap
    print("\n--- TWO LETTER PAIRS FROM SAME GAP ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        # Try concatenating pairs
        for i in range(len(nums) - 3):
            pair1_sum = nums[i] + nums[i+1]
            pair2_sum = nums[i+2] + nums[i+3]
            if pair1_sum + pair2_sum == 77:
                print(f"\n{gap_name}: ({text[i]}{text[i+1]}: {pair1_sum}) + ({text[i+2]}{text[i+3]}: {pair2_sum}) = {pair1_sum + pair2_sum} *** MATCH ***")

    # Method 3: Alternating sum (odd positions vs even positions)
    print("\n--- ALTERNATING POSITION SUMS ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        odd_sum = sum(nums[i] for i in range(0, len(nums), 2))
        even_sum = sum(nums[i] for i in range(1, len(nums), 2))

        print(f"\n{gap_name}:")
        print(f"  Odd positions (0,2,4...): {odd_sum}")
        print(f"  Even positions (1,3,5...): {even_sum}")
        print(f"  Difference: {abs(odd_sum - even_sum)}")

        if odd_sum == 77:
            print(f"    >>> ODD POSITIONS SUM = 77 ***")
        if even_sum == 77:
            print(f"    >>> EVEN POSITIONS SUM = 77 ***")

    # Method 4: Consecutive triplet products
    print("\n--- THREE CONSECUTIVE LETTERS PRODUCING 77 VIA OPERATIONS ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        for i in range(len(nums) - 2):
            a, b, c = nums[i], nums[i+1], nums[i+2]
            operations = [
                ('sum', a + b + c),
                ('a+b*c', a + b*c),
                ('a*b+c', a*b + c),
                ('(a+b)*c', (a+b)*c),
                ('max-min', max(a,b,c) - min(a,b,c) if max(a,b,c) != min(a,b,c) else 0),
            ]
            for op_name, result in operations:
                if result == 77:
                    print(f"\n{gap_name}: {text[i]}{text[i+1]}{text[i+2]} ({a},{b},{c})")
                    print(f"  Operation '{op_name}' = {result} *** MATCH ***")

    # Method 5: Cross-gap analysis - find pairs
    print("\n--- CROSS-GAP PAIR SUMS ---")
    gap_names = list(gaps.keys())
    for i in range(len(gap_names)):
        for j in range(i+1, len(gap_names)):
            gap1_name = gap_names[i]
            gap2_name = gap_names[j]
            gap1 = gaps[gap1_name]
            gap2 = gaps[gap2_name]

            nums1 = [letter_to_num(c) for c in gap1]
            nums2 = [letter_to_num(c) for c in gap2]

            # First letter of each gap
            sum_first = nums1[0] + nums2[0]
            if sum_first == 77:
                print(f"\n{gap1_name}[0] + {gap2_name}[0]: {gap1[0]}({nums1[0]}) + {gap2[0]}({nums2[0]}) = {sum_first} *** MATCH ***")

            # Last letter of each gap
            sum_last = nums1[-1] + nums2[-1]
            if sum_last == 77:
                print(f"\n{gap1_name}[-1] + {gap2_name}[-1]: {gap1[-1]}({nums1[-1]}) + {gap2[-1]}({nums2[-1]}) = {sum_last} *** MATCH ***")

    # Method 6: Sequential letters across gaps
    print("\n--- SEQUENTIAL LETTERS ACROSS GAPS ---")
    all_text = ''.join(gaps[g] for g in ['Gap1', 'Gap2', 'Gap3', 'Gap4'])
    all_nums = [letter_to_num(c) for c in all_text]

    for i in range(len(all_nums) - 1):
        pair_sum = all_nums[i] + all_nums[i+1]
        if pair_sum == 77:
            # Find which gap
            pos = 0
            for gap_name in ['Gap1', 'Gap2', 'Gap3', 'Gap4']:
                gap_len = len(gaps[gap_name])
                if i < pos + gap_len and i + 1 < pos + gap_len:
                    # Both in same gap
                    gap_idx1 = i - pos
                    gap_idx2 = i + 1 - pos
                    print(f"\nWithin {gap_name}: {gaps[gap_name][gap_idx1]}{gaps[gap_name][gap_idx2]} = {all_nums[i]}+{all_nums[i+1]} = {pair_sum} *** MATCH ***")
                    break
                elif i < pos + gap_len and i + 1 >= pos + gap_len:
                    # Crosses gap boundary
                    gap1_idx = i - pos
                    gap1_name = gap_name
                    # Find second gap
                    for gap2_idx, gap2_name in enumerate(['Gap1', 'Gap2', 'Gap3', 'Gap4']):
                        gap2_start = sum(len(gaps[['Gap1', 'Gap2', 'Gap3', 'Gap4'][k]]) for k in range(gap2_idx))
                        if i + 1 >= gap2_start and i + 1 < gap2_start + len(gaps[gap2_name]):
                            gap2_pos = i + 1 - gap2_start
                            print(f"\nCross-gap: {gap1_name}[{gap1_idx}] + {gap2_name}[{gap2_pos}]: {gaps[gap1_name][gap1_idx]}{gaps[gap2_name][gap2_pos]} = {all_nums[i]}+{all_nums[i+1]} = {pair_sum} *** MATCH ***")
                            break
                    break
                pos += gap_len

    # Method 7: Four consecutive numbers
    print("\n--- FOUR CONSECUTIVE LETTERS SUMMING TO 77 ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        for i in range(len(nums) - 3):
            quad_sum = nums[i] + nums[i+1] + nums[i+2] + nums[i+3]
            if quad_sum == 77:
                print(f"\n{gap_name}: {text[i:i+4]} = {nums[i]}+{nums[i+1]}+{nums[i+2]}+{nums[i+3]} = {quad_sum} *** MATCH ***")

    # Method 8: Check middle letters
    print("\n--- MIDDLE POSITION ANALYSIS ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        mid = len(nums) // 2
        if len(nums) > 0:
            print(f"\n{gap_name} (length {len(nums)}):")
            if len(nums) > 1:
                print(f"  Middle two: {text[mid-1]}{text[mid]} = {nums[mid-1]}+{nums[mid]} = {nums[mid-1] + nums[mid]}")
            if len(nums) > 2:
                print(f"  Middle three: {text[mid-1]}{text[mid]}{text[mid+1]} = {nums[mid-1]}+{nums[mid]}+{nums[mid+1]} = {nums[mid-1] + nums[mid] + nums[mid+1]}")

    # Method 9: Sum of specific positions
    print("\n--- POSITION PATTERN 77 ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]

        # Try first + second + third...
        for length in range(2, min(6, len(nums) + 1)):
            for start in range(len(nums) - length + 1):
                segment_sum = sum(nums[start:start+length])
                if segment_sum == 77:
                    segment_text = text[start:start+length]
                    print(f"\n{gap_name}[{start}:{start+length}]: {segment_text} = {segment_sum} *** MATCH ***")

    # Method 10: Letter differences
    print("\n--- LETTER VALUE DIFFERENCES PRODUCING 77 ---")
    for gap_name, text in gaps.items():
        nums = [letter_to_num(c) for c in text]
        for i in range(len(nums) - 1):
            diff = nums[i] - nums[i+1]
            # If we need difference operations
            cumulative_diffs = []
            for j in range(i, min(i+4, len(nums))):
                if j > i:
                    cumulative_diffs.append(nums[j])

def main():
    find_77()

if __name__ == '__main__':
    main()
