import sys
import re
import difflib
from typing import NamedTuple

class Token(NamedTuple):
    text: str
    char_indices: tuple[int, int]

class DiffData(NamedTuple):
    diff: str
    old_indices: tuple[int, int]
    new_indices: tuple[int, int]

class TextRange:
    def __init__(self, tokens: list[Token], char_indices: tuple[int, int]):
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

    def _slice(self, token_indices: tuple[int, int]):
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
        else:
            new_end_char = self.tokens[end-1].char_indices[1]
        
        return TextRange(self.tokens[start:end], (new_start_char, new_end_char))


PUNCTUATION = ',.?!:<>"“”‘’'
SPLIT_REGEX = re.compile(f'([ {PUNCTUATION}]+)')
PUNC_REGEX = re.compile(f'([{PUNCTUATION}]+)')
def split_tokens(text: str) -> TextRange:
    tokens = []
    token_start, token_end = 0, 0
    for token in SPLIT_REGEX.split(text):
        if not len(token):
            continue
        token_end = token_start + len(token)
        tokens.append(Token(token, (token_start, token_end)))
        token_start = token_end
    return TextRange(tokens, (0, len(text)))


SMART_QUOTE_REGEX = re.compile(r'[“”‘’]')
def find_differences(old: str, new: str, try_match_words: bool=False, separate_punctuation: bool=False) -> list[DiffData]:
    diffs = []

    def record_diff(old_range: TextRange, new_range: TextRange):
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
            # Refer to https://docs.python.org/3/library/difflib.html#difflib.get_close_matches
            close_matches = difflib.get_close_matches(old_token.text, new_str_list, cutoff=0.8)
            if len(close_matches):
                new_token_index = new_str_list.index(close_matches[0])
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
    old_diff_start_token = 0
    new_diff_start_token = 0

    if not old or not new:
        record_diff(old_tokens, new_tokens)
        return diffs

    # Refer to https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks
    for (a, b, n) in difflib.SequenceMatcher(lambda x: x == ' ', old_tokens.as_str_list(), new_tokens.as_str_list()).get_matching_blocks():
        old_diff = old_tokens[old_diff_start_token:a]
        new_diff = new_tokens[new_diff_start_token:b]
        old_diff_start_token = a + n
        new_diff_start_token = b + n

        if not len(old_diff) and not len(new_diff):
            # Don't add an entry if neither text has a diff
            continue

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


if __name__ == "__main__":
    texts = sys.stdin.read().splitlines()[:2]
    if len(texts) == 1:
        texts.append('')

    diffs = find_differences(texts[0], texts[1])
    old_indices, new_indices = zip(*[(diff.old_indices, diff.new_indices) for diff in diffs])
    old_str = ','.join((f'{start}-{end}' for start, end in old_indices))
    new_str = ','.join((f'{start}-{end}' for start, end in new_indices))
    full_str = f'{old_str};{new_str}'

    print(full_str)
    sys.exit(0)