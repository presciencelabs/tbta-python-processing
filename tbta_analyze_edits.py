import sys
import re
from pathlib import Path
from tbta_find_differences import compare_text_words

# Parameter Name constants
PARAM_INPUT_PATH_OLD = 'input_path_old'
PARAM_INPUT_PATH_NEW = 'input_path_new'
PARAM_OUTPUT_PATH = 'output_path'


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
        current_chapter = ''
        current_heading = None

        for line in file:
            # The line ending seems to be inconsistent, so strip all whitespace at the end before doing anything
            line = line.strip()

            if line.startswith('\\c '):
                current_chapter = line[3:]
                continue

            if line.startswith('\\s '):
                current_heading = line[3:]
                continue

            if line.startswith('\\f '):
                footnote_match = FOOTNOTE_REPLACE_REGEX.match(line)
                if footnote_match:
                    ref_key = footnote_match[1]
                    verses[ref_key] = verses[ref_key] + FOOTNOTE_REPLACE_REGEX.sub('', line)
            
            verse_match = VERSE_REGEX.fullmatch(line)
            if verse_match:
                ref_key = f'{current_chapter}:{verse_match[1]}'
                verses[ref_key] = FOOTNOTE_REPLACE_REGEX.sub('', verse_match[2])

                # TODO uncomment when titles are handled on the TBTA side
                # if current_heading is not None:
                #     verses[ref_key] = f'{current_heading} | {verse_match[2]}'
                #     current_heading = None
                # else:
                #     verses[ref_key] = verse_match[2]

    print(f'Retrieved {len(verses)} verses')
    return verses


def compare_verses(old: dict, new: dict):
    diff_tracker = {}
    for ref, old_verse in old.items():
        if ref not in new:
            continue

        new_verse = new[ref]
        for diff in compare_text_words(old_verse, new_verse):
            old_start, old_end = diff.old_indices
            new_start, new_end = diff.new_indices
            diff_value = f'{ref},{old_start}-{old_end},{new_start}-{new_end}'
            diff_tracker.setdefault(diff.diff, []).append(diff_value)
    
    # sort the diffs by most frequent, then alphabetically
    sorted_diffs = sorted(diff_tracker.items(), key=lambda diff: (len(diff[1])*-1, diff[0]))
    return sorted_diffs


def export_file(diffs, params):
    with params[PARAM_OUTPUT_PATH].open('w', encoding='utf-8') as file:
        for diff, refs in diffs:
            file.write(f'{diff}\n')
            all_refs = ';'.join(refs)
            file.write(f'{len(refs)};{all_refs}\n')


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
