import sys
import re
from pathlib import Path
from typing import NamedTuple
from tbta_find_differences import Indices, find_differences

# Parameter Name constants
PARAM_INPUT_PATH_OLD = 'input_path_old'
PARAM_INPUT_PATH_NEW = 'input_path_new'
PARAM_OUTPUT_PATH = 'output_path'


class VerseRef(NamedTuple):
    chapter: str
    verse: str

class DiffOccurrence(NamedTuple):
    ref: VerseRef
    old: Indices
    new: Indices


def get_params():
    # usage is: tbta_analyze_edits.exe "sfm_file_old.sfm" "sfm_file_new.sfm"

    if len(sys.argv) < 3:
        show_error('Please specify two .sfm files to compare')
        return None

    file_name_old = sys.argv[1]
    file_path_old = Path(file_name_old)
    if not file_path_old.exists():
        show_error(f'Specified File "{file_name_old}" does not exist...')
        return None
    
    file_name_new = sys.argv[2]
    file_path_new = Path(file_name_new)
    if not file_path_new.exists():
        show_error(f'Specified File "{file_name_new}" does not exist...')
        return None

    return {
        PARAM_INPUT_PATH_OLD: file_path_old,
        PARAM_INPUT_PATH_NEW: file_path_new,
        PARAM_OUTPUT_PATH: Path('AnalysisOfEdits.txt'),
    }


def import_file(input_path: Path):
    try:
        return import_verses_from_paratext(input_path)
    except IOError:
        return import_verses_from_paratext(input_path, encoding='utf-8-sig')


VERSE_REGEX = re.compile(r'\\v (\d+) (.*)')
FOOTNOTE_REPLACE_REGEX = re.compile(r'\\f \+ \\fr (\d*:\d*) \\ft|\\f\*')
def import_verses_from_paratext(input_path: Path, encoding='utf-8'):
    verses = {}

    print(f'Importing text from "{input_path}"')

    with input_path.open(encoding=encoding, newline='\n') as file:
        current_chapter = 0
        current_heading = None

        for line in file:
            # The line ending seems to be inconsistent, so strip all whitespace at the end before doing anything
            line = line.strip()

            if line.startswith('\\c '):
                current_chapter = int(line[3:])
                continue

            if line.startswith('\\s '):
                current_heading = line[3:]
                continue

            if line.startswith('\\f '):
                footnote_match = FOOTNOTE_REPLACE_REGEX.match(line)
                if footnote_match:
                    print(f'Footnote ref: "{footnote_match[1]}"')
                    ref_key = VerseRef(*(int(part) for part in footnote_match[1].split(':')))
                    verses[ref_key] = verses.setdefault(ref_key, '') + FOOTNOTE_REPLACE_REGEX.sub('', line)
            
            verse_match = VERSE_REGEX.fullmatch(line)
            if verse_match:
                ref_key = VerseRef(current_chapter, int(verse_match[1]))
                verses[ref_key] = FOOTNOTE_REPLACE_REGEX.sub('', verse_match[2])

                # TODO uncomment when titles are handled on the TBTA side
                # if current_heading is not None:
                #     verses[ref_key] = f'{current_heading} | {verse_match[2]}'
                #     current_heading = None
                # else:
                #     verses[ref_key] = verse_match[2]

    print(f'Retrieved {len(verses)} verses')
    return verses


def compare_verses(old: dict[VerseRef, str], new: dict[VerseRef, str]):
    diff_tracker: dict[str, list[DiffOccurrence]] = {}
    for ref, old_verse in old.items():
        if ref not in new:
            continue

        new_verse = new[ref]
        for diff, old_indices, new_indices in find_differences(old_verse, new_verse, try_match_words=True, separate_punctuation=True):
            diff_value = DiffOccurrence(ref, old_indices, new_indices)
            diff_tracker.setdefault(diff, []).append(diff_value)
    
    # sort the diffs by most frequent, then by the first verse reference
    sorted_diffs = sorted(diff_tracker.items(), key=lambda diff: (len(diff[1])*-1, diff[1][0].ref))
    return sorted_diffs


def export_file(diffs: list[tuple[str, list[DiffOccurrence]]], params: dict):
    with params[PARAM_OUTPUT_PATH].open('w', encoding='utf-8') as file:
        for diff, occurrences in diffs:
            file.write(f'{diff}\n')
            all_refs = ';'.join(f'{ref.chapter}:{ref.verse},{old.start}-{old.end},{new.start}-{new.end}' for ref, old, new in occurrences)
            file.write(f'{len(occurrences)};{all_refs}\n')


def show_error(text):
    print("Error: " + text)
    import ctypes  
    ctypes.windll.user32.MessageBoxW(0, text, "Error Creating Word Document", 0 + 16)


if __name__ == "__main__":
    params = get_params()
    if params:
        old_verses = import_file(params[PARAM_INPUT_PATH_OLD])
        new_verses = import_file(params[PARAM_INPUT_PATH_NEW])
        diffs = compare_verses(old_verses, new_verses)
        export_file(diffs, params)
