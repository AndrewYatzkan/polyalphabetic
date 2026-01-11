#!/usr/bin/env python3
"""
Systematic brute force test of all 26^4 = 456,976 combinations
for K4 key positions 0-4 with fixed positions 5-24.
"""

import sys
import os
import re
from collections import Counter

# KRYPTOS alphabet
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def load_english_words():
    """Load comprehensive English word list (3+ letters)"""
    words = set()

    # Try multiple system dictionary paths
    dict_paths = [
        '/usr/share/dict/words',
        '/usr/dict/words',
        '/etc/dictionaries-common/words',
    ]

    for path in dict_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    for line in f:
                        word = line.strip().upper()
                        # Only keep 3+ letter words, alphabetic only
                        if len(word) >= 3 and word.isalpha():
                            words.add(word)
                print(f"[*] Loaded {len(words):,} words from {path}")
                return words
            except Exception as e:
                print(f"[!] Error reading {path}: {e}")
                continue

    print("[!] Could not load system dictionary, using minimal fallback")
    # Minimal fallback word list
    fallback = """THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT
    DAY GET HAS HIM HIS HOW MAN OLD SEE SHE TWO WAY WHO BOY DID ITS LET
    NEW NOW OWN SAY SHE TOO USE BACK CALL CAME DOWN EACH EVEN FIND GAVE
    GOOD HAND HIGH JUST KNOW LIKE LINE MAKE MANY MUST NAME NEED NEXT ONLY
    OVER SAID SAME SHOW TAKE TELL THAN THAT THEM THEN THEY THIS TIME TOLD
    TOOK USED WANT WELL WHAT WHEN WITH WORK YEAR AFTER AGAIN CARRY COULD
    EVERY FIRST FOUND GOING GROUP GREAT HEARD HOUSE LARGE LATER LEAVE LIGHT
    LITTLE MAYBE MIGHT MOVED NEVER NIGHT NEVER OFTEN OTHER PLACE RIGHT SINCE
    SMALL SOUND STATE STILL STORY THEIR THESE THOSE THREE UNDER UNTIL WATER
    WHERE WHICH WHILE WHITE WHOLE WORLD WOULD WRITE ABOUT BEING BEING BEING
    BLACK BLANK BRING BUILD CAUSE CLASS CLEAN CLOSE COMES DOING EARLY EARLY
    EIGHT EQUAL FALSE FIGHT FIRST FIXED FLOAT FORCE FORCE FOURTH FRONT FULLY
    GIVEN GOING GRAND GRASS GREAT GROWN HEART HEAVY HORSE HOUSE HUMAN LAUGH
    LEARN LEAST LEAVE LEGAL LIGHT LIMIT LOCAL LOOSE LOWER MAGIC MAJOR MEANS
    METAL MIGHT MINOR MIXED MORAL MOTOR MOUTH MOVED MUSIC NEEDS NEVER NORTH
    NURSE OCCUR ORDER OTHER OUTER OUGHT PEACE PHASE PHONE PIECE PLAIN PLANT
    POINT POUND POWER PRESS PRIME PRINT PRIOR PROOF PROUD PROVE QUEEN QUICK
    QUIET QUITE RADIO RAISE RAPID REACH REALM RELAX REPLY RESET RIDER RIGHT
    RISKY RIVAL RIVER ROMAN ROUGH ROUND ROUTE ROYAL RURAL SCALE SCARE SCENE
    SCORE SENSE SERVE SEVEN SHALL SHAPE SHARE SHARP SHEET SHELF SHELL SHIRT
    SHOCK SHOOT SHORT SHOWN SIGHT SILLY SINCE SIXTH SIZED SKILL SLEEP SMALL
    SMART SMILE SMOKE SNAKE SOLAR SOLID SOLVE SORRY SOUND SOUTH SPACE SPARE
    SPEAK SPEED SPEND SPENT SPINE SPLIT SPOKE SPORT STAFF STAGE STAKE STAND
    START STATE STEAM STEEL STERN STICK STILL STOCK STONE STOOD STORE STORM
    STORY STRIP STUCK STUDY STUFF STYLE SUGAR SWEET TABLE TAKEN TASTE TAXES
    TEACH TEMPO TEND TENSE TENTH TERMS TESTS THANK THANK THEFT THEIR THEME
    THERE THESE THICK THING THINK THIRD THIRTY THOSE THREE THREW THROW TIDAL
    TIGER TIGHT TIMER TIMES TITLE TODAY TOKEN TOPIC TOTAL TOUCH TOUGH TOWER
    TRACK TRADE TRAIL TRAIN TRASH TREAT TREND TRIAL TRIBE TRICK TRIED TRIES
    TRUCK TRULY TRUNK TRUST TRUTH TUBES TULIP TUMOR TWEED TWELVE TWICE TWINS
    TWIST ULTRA UNCLE UNDER UNFIT UNION UNITY UPSET URBAN URGED USAGE USERS
    USUAL UTTER VAGUE VALID VALVE VENUE VERSE VIDEO VIGOR VILLA VINYL VIOLA
    VIRAL VIRUS VISIT VITAL VOICE WASTE WATCH WATER WAVED WAVES WEARY WEAVE
    WEDGE WEEDS WEEKS WEIGH WEIRD WELSH WHEAT WHEEL WHEN WHERE WHICH WHIFF
    WHILE WHINE WHITE WHOLE WHOSE WIDEN WIDER WIELD WIFE WILLS WIMPY WINDS
    WINED WINGS WIPED WIPER WIRES WITCH WIVES WOKEN WOMAN WOMEN WOODS WORDS
    WORKS WORLD WORMS WORRY WORSE WORST WORTH WOULD WOUND WOVEN WRAPS WRATH
    WRECK WRIST WRITE WRONG YACHT YEARS YELLS YIELD YOUNG YOURS YOUTH ZONED
    ZONES"""

    for word in fallback.split():
        if len(word) >= 3:
            words.add(word.upper())

    print(f"[*] Using {len(words)} fallback words")
    return words

def vigenere_decrypt(ciphertext, key, alphabet):
    """Decrypt using Vigenere cipher with custom alphabet"""
    plaintext = []
    key_index = 0

    for char in ciphertext:
        if char not in alphabet:
            plaintext.append(char)
            continue

        char_pos = alphabet.index(char)
        key_char = key[key_index % len(key)]
        key_pos = alphabet.index(key_char)

        # Vigenere decryption: (cipher_pos - key_pos) mod alphabet_size
        plain_pos = (char_pos - key_pos) % len(alphabet)
        plaintext.append(alphabet[plain_pos])

        key_index += 1

    return ''.join(plaintext)

def count_english_words(text, word_set):
    """Count English words (3+ letters) in decrypted text"""
    # Extract all sequences of letters
    words = re.findall(r'[A-Za-z]+', text)

    count = 0
    for word in words:
        word_upper = word.upper()
        if len(word_upper) >= 3 and word_upper in word_set:
            count += 1

    return count

def get_words_from_text(text, word_set):
    """Extract actual words found in text"""
    words = re.findall(r'[A-Za-z]+', text)
    found = []

    for word in words:
        word_upper = word.upper()
        if len(word_upper) >= 3 and word_upper in word_set:
            found.append(word_upper)

    return found

def main():
    # K4 ciphertext
    K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    # Fixed key parts
    fixed_5_15 = "ELYOIECBAQK"
    fixed_16_24 = "VAATCRDUM"

    print("=" * 110)
    print("KRYPTOS K4 - SYSTEMATIC BRUTE FORCE TEST")
    print("Testing all 26^4 = 456,976 combinations for positions 0-4")
    print("=" * 110)
    print(f"\nCiphertext ({len(K4)} chars): {K4}")
    print(f"Alphabet: {KRYPTOS_ALPHABET} ({len(KRYPTOS_ALPHABET)} letters)")
    print(f"Fixed key positions 5-15: {fixed_5_15}")
    print(f"Fixed key positions 16-24: {fixed_16_24}")
    print(f"Testing positions 0-4: all 26^4 combinations\n")

    # Load word list
    word_set = load_english_words()
    print(f"[*] Ready to test 456,976 combinations\n")

    # Test all combinations
    results = []
    total_combinations = 26 ** 4

    print("Testing combinations...")
    for i0 in range(26):
        for i1 in range(26):
            for i2 in range(26):
                for i3 in range(26):
                    for i4 in range(26):
                        # Build key for positions 0-4
                        key_part = (KRYPTOS_ALPHABET[i0] +
                                   KRYPTOS_ALPHABET[i1] +
                                   KRYPTOS_ALPHABET[i2] +
                                   KRYPTOS_ALPHABET[i3] +
                                   KRYPTOS_ALPHABET[i4])

                        # Full key
                        full_key = key_part + fixed_5_15 + fixed_16_24

                        # Decrypt K4
                        plaintext = vigenere_decrypt(K4, full_key, KRYPTOS_ALPHABET)

                        # Count English words
                        word_count = count_english_words(plaintext, word_set)

                        # Store result if any words found
                        if word_count > 0:
                            found_words = get_words_from_text(plaintext, word_set)
                            results.append({
                                'word_count': word_count,
                                'key_part': key_part,
                                'full_key': full_key,
                                'plaintext': plaintext,
                                'words': found_words
                            })

                        # Progress indicator
                        current = (i0 * 26**3 + i1 * 26**2 + i2 * 26 + i3) * 26 + i4 + 1
                        if current % 50000 == 0 or current in [456976]:
                            pct = 100.0 * current / total_combinations
                            print(f"  Progress: {current:>7,} / {total_combinations:,} ({pct:>5.1f}%)")

    print(f"\n[*] Testing complete!")
    print(f"[*] Found {len(results):,} combinations with at least 1 English word\n")

    # Sort by word count (descending)
    results.sort(reverse=True, key=lambda x: x['word_count'])

    # Print top 20
    print("=" * 110)
    print("TOP 20 RESULTS BY ENGLISH WORD COUNT")
    print("=" * 110)

    for rank, result in enumerate(results[:20], 1):
        print(f"\nRank {rank}: {result['word_count']} English words found")
        print(f"  Key positions 0-4: {result['key_part']}")
        print(f"  Full Key (0-24): {result['full_key']}")
        print(f"  Words found: {', '.join(result['words'][:15])}" +
              (f"... and {len(result['words']) - 15} more" if len(result['words']) > 15 else ""))
        print(f"  Plaintext:\n    {result['plaintext']}")
        print()

    # Also save to file
    output_file = '/home/user/polyalphabetic/k4_bruteforce_results_positions_0_4.txt'
    with open(output_file, 'w') as f:
        f.write("=" * 110 + "\n")
        f.write("KRYPTOS K4 - BRUTE FORCE RESULTS (Positions 0-4)\n")
        f.write("=" * 110 + "\n\n")
        f.write(f"Ciphertext: {K4}\n")
        f.write(f"Alphabet: {KRYPTOS_ALPHABET}\n")
        f.write(f"Fixed positions 5-15: {fixed_5_15}\n")
        f.write(f"Fixed positions 16-24: {fixed_16_24}\n")
        f.write(f"Total combinations tested: 456,976\n")
        f.write(f"Combinations with valid words: {len(results):,}\n\n")

        f.write("=" * 110 + "\n")
        f.write("TOP 20 RESULTS\n")
        f.write("=" * 110 + "\n\n")

        for rank, result in enumerate(results[:20], 1):
            f.write(f"Rank {rank}: {result['word_count']} English words\n")
            f.write(f"  Key positions 0-4: {result['key_part']}\n")
            f.write(f"  Full Key: {result['full_key']}\n")
            f.write(f"  Words: {', '.join(result['words'][:20])}\n")
            f.write(f"  Plaintext: {result['plaintext']}\n\n")

    print(f"[*] Results saved to {output_file}")

if __name__ == "__main__":
    main()
