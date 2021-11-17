from algo.masks import MASKS_BLACK, MASKS_WHITE, Patterns, PatternsValue

patterns = [0, 0, 0, 0, 0, 0, 0, 0, 19683, 45927, 2187, 58320, 223074, 19683, 59049, 177147, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 756, 81, 104490, 24786, 10935, 4374, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27, 0, 81, 729, 243, 1458, 5103, 4374, 43740, 29889, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6561, 39366, 183708, 39366, 54675, 266814, 1458, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
PATTERN_SIZES = [19] * 38 + \
    (list(range(1, 20, 1)) + list(range(18, 0, -1))) * 2

# for (mask_size, masks_white), (_, masks_black) in zip(MASKS_WHITE.items(), MASKS_BLACK.items()):
#     print(mask_size)
#     print(masks_white)
#     print(masks_black)
#     print("========")

def get_small_patterns(mask_size):
    small_patterns = {}
    for pattern_index, pattern in enumerate(patterns):
        pattern_size = PATTERN_SIZES[pattern_index]
        while pattern != 0:
            if pattern_size < mask_size:
                break
            small_pattern = pattern % 3**mask_size
            if small_pattern != 0:
                small_patterns[small_pattern] = 1 if small_pattern not in small_patterns else small_patterns[small_pattern] + 1
            pattern //= 3
            pattern_size -= 1
    return small_patterns

is_five_in_a_row = False
score = 0
for mask_size in MASKS_WHITE.keys():
    small_patterns = get_small_patterns(mask_size)
    for pattern_code in MASKS_WHITE[mask_size].keys():
        for mask_white, mask_black in zip(MASKS_WHITE[mask_size][pattern_code],
                                          MASKS_BLACK[mask_size][pattern_code]):
            mask_occurrences_w = small_patterns[mask_white] if mask_white in small_patterns else 0
            mask_occurrences_b = small_patterns[mask_black] if mask_black in small_patterns else 0
            if pattern_code == Patterns.FIVE_IN_A_ROW and (mask_occurrences_w > 0 or mask_occurrences_b > 0):
                is_five_in_a_row = True
            score += PatternsValue[pattern_code] * (mask_occurrences_w - mask_occurrences_b)
print(score)
print(is_five_in_a_row)