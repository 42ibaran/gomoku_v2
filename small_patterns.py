patterns = [0, 0, 0, 0, 0, 0, 0, 0, 19683, 45927, 2187, 58320, 223074, 19683, 59049, 177147, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 756, 81, 104490, 24786, 10935, 4374, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27, 0, 81, 729, 243, 1458, 5103, 4374, 43740, 29889, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6561, 39366, 183708, 39366, 54675, 266814, 1458, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
PATTERN_SIZES = [19] * 38 + \
    (list(range(1, 20, 1)) + list(range(18, 0, -1))) * 2

def get_small_patterns(patterns, mask_size):
    small_patterns = {}
    for pattern_index, pattern in enumerate(patterns):
        pattern_size = PATTERN_SIZES[pattern_index]
        while pattern != 0:
            small_pattern = pattern % 3**mask_size
            if small_pattern != 0:
                small_patterns[small_pattern] = 1 if small_pattern not in small_patterns else small_patterns[small_pattern] + 1
            pattern //= 3
            pattern_size -= 1
    return small_patterns

if __name__ == '__main__':
    small_patterns_5 = get_small_patterns(patterns, 4)
    print(small_patterns_5)
