import sys
import re
from typing import NamedTuple

class Indices(NamedTuple):
    start: int
    end: int

class Token(NamedTuple):
    text: str
    char_indices: Indices

class DiffData(NamedTuple):
    diff: str
    old_indices: Indices
    new_indices: Indices

class TextRange:
    def __init__(self, tokens: list[Token], char_indices: Indices):
        self.tokens = tokens
        self.char_indices = char_indices

    def __repr__(self):
        return ''.join(self.as_str_list()).strip()

    def __len__(self):
        return len(self.tokens)
    
    def __getitem__(self, x: int|slice):
        if isinstance(x, slice):
            return self._slice((x.start or 0, x.stop if x.stop is not None else len(self.tokens)))
        else:
            return self.tokens[x]

    def as_str_list(self):
        return [t.text for t in self.tokens]

    def _slice(self, token_indices: Indices):
        start, end = token_indices

        if start == 0 and end == len(self):
            return self

        if not len(self):
            new_start_char = self.char_indices[0]
        elif start >= len(self):
            new_start_char = self.char_indices[1]
        else:
            new_start_char = self.tokens[start].char_indices[0]
            
        if not len(self):
            new_end_char = self.char_indices[1]
        elif end == 0:
            new_end_char = self.char_indices[0]
        elif end < 0:
            new_end_char = self.tokens[len(self)+end-1].char_indices[1]
        else:
            new_end_char = self.tokens[end-1].char_indices[1]
        
        return TextRange(self.tokens[start:end], Indices(new_start_char, new_end_char))


PUNCTUATION = ',.?!:<>"“”‘’'
SPLIT_REGEX = re.compile(f'([ {PUNCTUATION}])')
PUNC_REGEX = re.compile(f'([{PUNCTUATION}]+)')
def split_tokens(text: str) -> TextRange:
    tokens = []
    token_start, token_end = 0, 0
    for token in SPLIT_REGEX.split(text):
        if not len(token):
            continue
        token_end = token_start + len(token)
        tokens.append(Token(token, Indices(token_start, token_end)))
        token_start = token_end
    return TextRange(tokens, (0, len(text)))


SMART_QUOTE_REGEX = re.compile(r'[“”‘’]')
def find_differences(old: str, new: str, try_match_words: bool=False, separate_punctuation: bool=False) -> list[DiffData]:
    diffs = []

    def record_diff(old_range: TextRange, new_range: TextRange):
        if len(old_range) and len(new_range) and old_range[0].text == ' ' and new_range[0].text == ' ':
            old_range = old_range[1:]
            new_range = new_range[1:]
        if len(old_range) and len(new_range) and old_range[-1].text == ' ' and new_range[-1].text == ' ':
            old_range = old_range[:-1]
            new_range = new_range[:-1]
        
        diff_key = SMART_QUOTE_REGEX.sub(lambda m: '"' if m[0] in '“”' else "'", f'{old_range}->{new_range}')
        if len(diff_key) > 2:
            # don't include any empty diffs
            diffs.append(DiffData(diff_key, old_range.char_indices, new_range.char_indices))
    
    def handle_punctuation_change(old_diff: TextRange, new_diff: TextRange):
        old_punc_match = PUNC_REGEX.match(old_diff[0].text) if len(old_diff) else None
        new_punc_match = PUNC_REGEX.match(new_diff[0].text) if len(new_diff) else None
        if old_punc_match and new_punc_match:
            # punctuation at the start is changed
            record_diff(old_diff[0:1], new_diff[0:1])
            return (old_diff[1:], new_diff[1:])
        elif old_punc_match and not new_punc_match:
            # punctuation at the start is deleted
            record_diff(old_diff[0:1], new_diff[0:0])
            return (old_diff[1:], new_diff)
        elif new_punc_match and not old_punc_match:
            # punctuation at the start is added
            record_diff(old_diff[0:0], new_diff[0:1])
            return (old_diff, new_diff[1:])
        else:
            return (old_diff, new_diff)
    
    def can_try_to_match_words(old_range: TextRange, new_range: TextRange):
        return len(old_range) and len(new_range) and abs(len(old_range) - len(new_range)) < 5 and (len(old_range) in range(3, 9) or len(new_range) in range(3, 9))
    
    def try_to_match_words(old_diff: TextRange, new_diff: TextRange):
        # Find any words that closely match between diffs, and pair them up
        old_matched_indices, new_matched_indices = [], []
        new_str_list = new_diff.as_str_list()

        for old_token_index, old_token in enumerate(old_diff.tokens):
            if old_token.text == ' ':
                continue
            closest = get_closest_match(old_token.text, new_str_list)
            if closest:
                new_token_index = new_str_list.index(closest)
                old_matched_indices.append((old_token_index, old_token_index + 1))
                new_matched_indices.append((new_token_index, new_token_index + 1))

        # If not words matched, simply return the full diffs
        if not len(old_matched_indices):
            return ([old_diff], [new_diff])
        
        # Fill in the gaps from the range with the words that didn't match
        old_range_split_indices, new_range_split_indices = [], []
        next_old_start, next_new_start = 0, 0
        for old_match_index, new_match_index in zip(old_matched_indices, sorted(new_matched_indices)):
            if old_match_index[0] > next_old_start or new_match_index[0] > next_new_start:
                old_range_split_indices.append((next_old_start, old_match_index[0]))
                new_range_split_indices.append((next_new_start, new_match_index[0]))
            next_old_start = old_match_index[1]
            next_new_start = new_match_index[1]
        
        old_range_split_indices.extend(old_matched_indices)
        new_range_split_indices.extend(new_matched_indices)

        # Include any range at the end
        max_old = max(x[1] for x in old_range_split_indices)
        max_new = max(x[1] for x in new_range_split_indices)
        if max_old != len(old_diff) or max_new != len(new_diff):
            old_range_split_indices.append((max_old, len(old_diff)))
            new_range_split_indices.append((max_new, len(new_diff)))

        return ([old_diff[start:end] for (start, end) in old_range_split_indices],
            [new_diff[start:end] for (start, end) in new_range_split_indices])

    old_tokens = split_tokens(old)
    new_tokens = split_tokens(new)

    if not old or not new:
        record_diff(old_tokens, new_tokens)
        return diffs

    for (a_range, b_range) in get_diff_ranges(old_tokens, new_tokens):
        a_start, a_end = a_range
        b_start, b_end = b_range
        old_diff = old_tokens[a_start:a_end]
        new_diff = new_tokens[b_start:b_end]

        if separate_punctuation:
            old_diff, new_diff = handle_punctuation_change(old_diff, new_diff)

        # Check for other alignment of words
        if try_match_words and can_try_to_match_words(old_diff, new_diff):
            old_ranges, new_ranges = try_to_match_words(old_diff, new_diff)
            for old_range, new_range in zip(old_ranges, new_ranges):
                record_diff(old_range, new_range)
        else:
            record_diff(old_diff, new_diff)

    return diffs


def get_closest_match(word, possibilities):
    # Simplified version of difflib.get_close_matches()
    # See https://github.com/python/cpython/blob/e0f7c1097e19b6f5c2399e19f283c9fb373c243f/Lib/difflib.py#L667
    # and see https://github.com/python/cpython/blob/e0f7c1097e19b6f5c2399e19f283c9fb373c243f/Lib/difflib.py#L40
    cutoff = 0.8
    a, la = word, len(word)

    close_matches = []
    for b in possibilities:
        if b == ' ':
            continue

        lb = len(b)
        lboth = la + lb
        if (2.0 * min(la, lb) / lboth) < cutoff:
            continue

        matches = find_overlaps(a, b)
        ratio = 2.0 * len(matches) / lboth
        if ratio >= cutoff:
            close_matches.append((ratio, b))
    
    if not close_matches:
        return None
    return max(close_matches, key=lambda x: x[0])[1]


def get_diff_ranges(a: TextRange, b: TextRange):
    """
    Returns a list of ((start_a, end_a), (start_b, end_b)) tuples, representing the minimal ranges of differences in a and b.
    For a deletion, start_b and end_b will be the same. For an insertion, start_a and end_a will be the same.
    Spaces are ignored.
    """

    a_full = a.as_str_list()
    b_full = b.as_str_list()

    # Ignore spaces by removing them from the list, tracking the mapping of indices
    a_index_map = []
    norm_a = []
    for i, t in enumerate(a_full):
        if t == ' ':
            continue
        norm_a.append(t)
        a_index_map.append(i)
    a_index_map.append(len(a_full))

    b_index_map = []
    norm_b = []
    for j, t in enumerate(b_full):
        if t == ' ':
            continue
        norm_b.append(t)
        b_index_map.append(j)
    b_index_map.append(len(b_full))

    matches = find_overlaps(norm_a, norm_b)

    # Generate diff ranges
    diffs = []
    prev_a = prev_b = 0
    for ma, mb in matches:
        if prev_a < ma or prev_b < mb:
            diffs.append(((prev_a, ma), (prev_b, mb)))
        prev_a = ma + 1
        prev_b = mb + 1

    # Any remaining tail differences
    if prev_a < len(norm_a) or prev_b < len(norm_b):
        diffs.append(((prev_a, len(norm_a)), (prev_b, len(norm_b))))

    # Adjust the indices back to include the space tokens as well
    true_diffs = []
    for a_range, b_range in diffs:
        a_start, a_end = tuple(a_index_map[i] for i in a_range)
        b_start, b_end = tuple(b_index_map[j] for j in b_range)

        a_is_range = a_start != a_end
        b_is_range = b_start != b_end

        # Adjust for when a space should be included in a diff
        a_prev_is_space = a_start > 0 and a_full[a_start-1] == ' '
        b_prev_is_space = b_start > 0 and b_full[b_start-1] == ' '
        if a_prev_is_space and not b_prev_is_space:
            a_start -= 1
            a_end -= 1 if not a_is_range else 0
        elif not a_prev_is_space and b_prev_is_space:
            b_start -= 1
            b_end -= 1 if not b_is_range else 0

        # At this point, any space at the beginning of a diff is meaningful

        # Remove unnecessary spaces at the ends of insertions or deletions
        if a_is_range and a_full[a_end-1] == ' ' and b_end < len(b_full) and not b_is_range and b_full[b_end] == ' ':
            a_end -= 1
        elif a_end < len(a_full) and not a_is_range and a_full[a_end] == ' ' and b_is_range and b_full[b_end-1] == ' ':
            b_end -= 1

        true_diffs.append(((a_start, a_end), (b_start, b_end)))

    return true_diffs

def find_overlaps(a, b):
    """
    Find maximum overlap between two iterables using LCS (Longest Common Sequence).
    This algorithm is courtesy of ChatGPT.
    """
    len_a, len_b = len(a), len(b)

    # Build LCS table
    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]
    for i in range(len_a):
        for j in range(len_b):
            if a[i] == b[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])

    # Backtrack to find matching indices
    i, j = len_a, len_b
    matches = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            matches.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    matches.reverse()  # from start to end

    return matches


if __name__ == "__main__":
    exit_signal = 'close-pipe'
    while True:
        old_text = sys.stdin.readline().strip()
        if old_text == exit_signal:
            break
        new_text = sys.stdin.readline().strip()
        if new_text == exit_signal:
            break

        diffs = find_differences(old_text, new_text)
        old_indices, new_indices = zip(*[(diff.old_indices, diff.new_indices) for diff in diffs]) if len(diffs) else ((), ())
        old_str = ','.join((f'{start}-{end}' for start, end in old_indices))
        new_str = ','.join((f'{start}-{end}' for start, end in new_indices))
        full_str = f'{old_str};{new_str}'

        try:
            print(full_str, flush=True)
        except OSError:
            # This occurs if TBTA crashes or closes the pipe unexpectedly, so we should just exit the program
            break

    sys.exit(0)