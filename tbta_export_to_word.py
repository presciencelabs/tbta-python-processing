# This script takes the exported text file from TBTA and arranges the verses
# into a Word document table that can then be sent to the MTT. It separates the
# English and the target language, making sure the corresponding verses and
# sentences are aligned properly.
#
# The txt file to import the verses from must be specified as the last argument.
# Including the argument -s will separate each sentence into its own line.
#   By default each whole verse gets its own row
# Including the argument -n will add a blank 'Notes' column on the right.
#   By default it is excluded.
#
# When splitting sentences, there may be some misalignment between the two
# langauges due to some sentences being combined in one language but not the other,
# or due to the presence of an implicit sentence. A blank line will alert the
# user that there is misalignment which will have to be dealt with manually.
# However, this misalignment will not extend beyond the verse in question.

import sys
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Cm, RGBColor


# Parameter Name constants
PARAM_INPUT_PATH = 'input_path'
PARAM_OUTPUT_PATH = 'output_path'
PARAM_FOOTNOTE = 'footnote'
PARAM_SPLIT_SENTENCES = 'split_sentences'
PARAM_NOTES_COLUMN = 'add_notes_column'
PARAM_PUB_REFS = 'publishable_refs'
PARAM_COMPARE = 'compare'
PARAM_LANGUAGE_INFO = 'languages'

# Language Info Fields
LANG_NAME = 'name'
LANG_BOOK_NAME = 'book_name'
LANG_IS_TARGET = 'is_target'

# Verse Fields
VERSE_REF = 'ref'
VERSE_TEXT = 'text'

def get_params():
    # usage is: tbta_export_to_word.exe -s -n -p -c "text_file.txt" "footnote:"
    # The text file path is required. The footnote word is required if there is no -c or -p
    do_compare = '-C' in sys.argv or '-c' in sys.argv
    do_pub_refs = '-P' in sys.argv or '-p' in sys.argv
    do_default = not do_compare and not do_pub_refs

    non_flag_args = [a for a in sys.argv if not a.startswith('-')]

    if do_default and len(non_flag_args) < 3:
        show_error('Please specify a .txt file to import and the Target word for Footnote')
        return None

    if (do_compare or do_pub_refs) and len(non_flag_args) < 2:
        show_error('Please specify a .txt file to import')
        return None

    file_name = non_flag_args[1]
    file_path = Path(file_name).with_suffix('.txt')
    if not file_path.exists():
        show_error(f'Specified File "{file_name}" does not exist...')
        return None

    return {
        PARAM_INPUT_PATH: file_path,
        PARAM_OUTPUT_PATH: file_path.with_name(f'{file_path.stem}.docx'),
        PARAM_FOOTNOTE: non_flag_args[2] if do_default else '',
        PARAM_SPLIT_SENTENCES: '-S' in sys.argv or '-s' in sys.argv,
        PARAM_NOTES_COLUMN: '-N' in sys.argv or '-n' in sys.argv,
        PARAM_PUB_REFS: do_pub_refs,
        PARAM_COMPARE: do_compare,
    }


def get_language_info(file_iter):
    # The first line has the language info.
    # This handles the following cases:
    #   Target-Churched Adults and English-Churched Adults and Third-Churched Adults
    #   Target and English-Churched Adults
    #   Target-Churched Adults
    #   Target
    line = next(file_iter)
    languages = [s.split('-')[0] for s in line.strip().split(' and ')]

    # The next non-empty line has the book name for each language separated by a hyphen
    line = next(file_iter)
    while not line.strip():
        line = next(file_iter)
    book_names = re.findall(r'\s*(.+?)\s*(?:$|-)', line)

    if not languages or len(languages) != len(book_names):
        print('Unexpected format of file contents')
        return None

    language_info = []
    def create_info(i, is_target):
        return { LANG_NAME: languages.pop(i), LANG_BOOK_NAME: book_names.pop(i), LANG_IS_TARGET: is_target }

    # In the file the order is Target (English) (Other)
    # Reorder so it's (English) Target (Other) which is the order the verses appear in
    if len(languages) > 1 and 'English' in languages:
        language_info.append(create_info(1, False))
    
    language_info.append(create_info(0, True))

    if len(languages) > 0:
        language_info.append(create_info(0, False))

    return language_info


def import_file(params):
    # Read the text file and return either a list of lines or verse text
    # TODO handle utf-16-le again
    with params[PARAM_INPUT_PATH].open(encoding='utf-8-sig') as file:
        file_iter = iter(file)

        if params[PARAM_COMPARE]:
            table_verses = import_verses_for_compare(file_iter, params)
            return (None, table_verses)

        language_info = get_language_info(file_iter)
        params[PARAM_LANGUAGE_INFO] = language_info

        if language_info is None:
            return (None, None)
        if (params[PARAM_PUB_REFS] or 
                (len(language_info) == 1 and not params[PARAM_SPLIT_SENTENCES] and not params[PARAM_NOTES_COLUMN])):
            # Must bring all lines into memory since the file is closed when this function returns
            lines = [line for line in file_iter]
            return (lines, None)
        else:
            table_verses = import_verses_for_table(file_iter, params)
            if params[PARAM_SPLIT_SENTENCES]:
                table_verses = split_verse_sentences(table_verses)
            return (None, table_verses)


def import_verses_for_table(file_iter, params):
    footnote_word = params[PARAM_FOOTNOTE]
    num_languages = len(params[PARAM_LANGUAGE_INFO])

    def new_verse():
        return [{ VERSE_REF: '', VERSE_TEXT: '' } for _ in range(num_languages)]

    verses = []
    current_verse = new_verse()
    current_language = 0

    def line_is_for_current_language(line):
        return (not current_verse[current_language][VERSE_REF]
                or line.startswith(footnote_word))
    
    def append_text(text):
        if current_verse[current_language][VERSE_TEXT]:
            text = ' ' + text
        current_verse[current_language][VERSE_TEXT] += text
    
    VERSE_LINE_REGEX = re.compile(r'^(.+? \d+:\d+) ?(.*)?')

    for line in file_iter:
        # The line ending seems to be inconsistent, so strip all whitespace at the end before doing anything
        line = line.strip()
        if not line:
            continue

        if not line_is_for_current_language(line):
            # Go to the next language
            current_language += 1

            if current_language == num_languages:
                # Start the next verse
                verses.append(current_verse)
                current_verse = new_verse()
                current_language = 0
        
        # Parse the line
        verse_match = VERSE_LINE_REGEX.fullmatch(line)
        if verse_match:
            current_verse[current_language][VERSE_REF] = verse_match[1]
            append_text(verse_match[2])
        else:
            append_text(line)

    # There may be a last unpushed verse at the end
    if verses and verses[-1][0][VERSE_REF] != current_verse[0][VERSE_REF]:
        verses.append(current_verse)

    print(f'Retrieved {len(verses)} verses from "{params[PARAM_INPUT_PATH]}"')
    return verses


def import_verses_for_compare(file_iter, params):
    params[PARAM_LANGUAGE_INFO] = []

    def new_verse():
        # currently assumes 3 languages (English, Old Target, New Target)
        return [{ VERSE_REF: '', VERSE_TEXT: '' } for _ in range(3)]

    verses = []
    current_verse = new_verse()
    next_language = 0
    
    VERSE_REF_REGEX = re.compile(r'(.+? \d+:\d+)')
    VERSE_TEXT_REGEX = re.compile(r'(.+?):(.*)')

    for line in file_iter:
        # The line ending seems to be inconsistent, so strip all whitespace at the end before doing anything
        line = line.strip()
        if not line:
            # a blank line separates each verse
            verses.append(current_verse)
            current_verse = new_verse()
            next_language = 0
            continue
        
        ref_match = VERSE_REF_REGEX.fullmatch(line)
        text_match = VERSE_TEXT_REGEX.fullmatch(line)
        if ref_match:
            current_verse[0][VERSE_REF] = ref_match[1]

        elif text_match:
            lang_name = text_match[1]
            lang_text = text_match[2]
            current_verse[next_language][VERSE_TEXT] = lang_text.strip()
            next_language += 1

            if all([lang[LANG_NAME] != lang_name for lang in params[PARAM_LANGUAGE_INFO]]):
                params[PARAM_LANGUAGE_INFO].append({ LANG_NAME: lang_name })

    # There may be a last unpushed verse at the end
    if verses and verses[-1][0][VERSE_REF] != current_verse[0][VERSE_REF]:
        verses.append(current_verse)

    print(f'Retrieved {len(verses)} verses from "{params[PARAM_INPUT_PATH]}"')
    return verses


SENTENCE_REGEX = re.compile(r'([^.?!]+[.?!]\S*) ?')
def split_verse_sentences(verses):
    for full_verse in verses:
        yield full_verse
        sentences_by_lang = [SENTENCE_REGEX.findall(lang[VERSE_TEXT]) for lang in full_verse]

        # Some sentences in either language may be combined so it may
        # not correspond exactly, but an empty line should notify the
        # user of the issue and not mess up the sentence alignment
        num_lines = max([len(s) for s in sentences_by_lang])
        for lang_sentences in sentences_by_lang:
            lang_sentences.extend([''] * (num_lines - len(lang_sentences)))

        # Add a row for each sentence
        for line_num in range(num_lines):
            verse_sentence = []
            for (lang_index, lang_sentences) in enumerate(sentences_by_lang):
                verse_sentence.append({
                    VERSE_REF: f'{full_verse[lang_index][VERSE_REF]}:{line_num+1}',
                    VERSE_TEXT: lang_sentences[line_num]
                })
            yield verse_sentence


def export_table_document(verses, params):
    print('Creating Word document with table...')
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri (Body)'

    # Set orientation to landscape
    section = doc.sections[-1]
    old_width, old_height = section.page_width, section.page_height
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_height = old_width
    section.page_width = old_height

    # Set the margins
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)

    # Add the table
    (col_names, col_widths) = calculate_columns(params)
    table = doc.add_table(rows=1, cols=len(col_names), style='Table Grid')
    header_row = table.rows[0]
    for (i, col_name) in enumerate(col_names):
        header_row.cells[i].text = col_name
        header_row.cells[i].paragraphs[0].runs[0].font.bold = True

    # Add rows for each verse
    for verse in verses:
        main_row = table.add_row()
        main_row.cells[0].text = verse[0][VERSE_REF]
        for (i, lang) in enumerate(verse):
            format_verse_text(lang[VERSE_TEXT], main_row.cells[i+1])

    # Set the column widths. Each cell needs to be set individually
    for idx, col in enumerate(table.columns):
        for cell in col.cells:
            cell.width = col_widths[idx]
            
    return save_document(doc, params[PARAM_OUTPUT_PATH])

FORMATTING_REGEX = re.compile(r'\[ (.+) \]')
def format_verse_text(text, table_cell):
    # For now only expect one occurrence of the red-text format marker
    format_match = FORMATTING_REGEX.search(text)
    if not format_match:
        table_cell.text = text
        return

    format_start, format_end = format_match.span(0)
    text_to_format = format_match[1]

    paragraph = table_cell.paragraphs[0]
    paragraph.add_run(text=' ' + text[:format_start])

    formatted_run = paragraph.add_run(text=text_to_format)
    formatted_run.bold = True
    formatted_run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)

    paragraph.add_run(text=text[format_end:])


def calculate_columns(params):
    languages = params[PARAM_LANGUAGE_INFO]

    col_names = ['Verse']
    for lang in languages:
        col_names.append(lang[LANG_NAME])
    if params[PARAM_NOTES_COLUMN]:
        col_names.append('Notes')

    # Set column widths depending on how many columns there are
    col_widths = [Cm(3)]
    if len(col_names) == 2:
        col_widths.append(Cm(15))
    elif len(col_names) == 3:
        col_widths.extend([Cm(10), Cm(10)])
    elif len(col_names) == 4 and len(languages) == 3:
        col_widths.extend([Cm(7), Cm(7), Cm(7)])
    elif len(col_names) == 4 and len(languages) == 2:
        col_widths.extend([Cm(8.5), Cm(8.5), Cm(4)])
    elif len(col_names) == 5:
        col_widths = [Cm(2.5), Cm(6), Cm(6), Cm(6), Cm(3)]
        
    return (col_names, col_widths)


def export_simple_document(lines, params):
    print('Creating simple Word document...')
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri (Body)'

    # Add the title line
    target_info = next(lang for lang in params[PARAM_LANGUAGE_INFO] if lang[LANG_IS_TARGET])
    doc.add_paragraph(target_info[LANG_NAME] + ' - ' + target_info[LANG_BOOK_NAME])

    for line in lines:
        doc.add_paragraph(text=line.strip())

    return save_document(doc, params[PARAM_OUTPUT_PATH])


def save_document(doc, path:Path):
    try:
        doc.save(str(path))
        return True
    except PermissionError:
        show_error(f'"{path.name}" is currently open. Please close and try again.')
        return False


def show_error(text):
    print("Error: " + text)
    import ctypes  
    ctypes.windll.user32.MessageBoxW(0, text, "Error Creating Word Document", 0 + 16)


if __name__ == "__main__":
    params = get_params()
    if params:
        (lines, verses) = import_file(params)
        if lines:
            if export_simple_document(lines, params):
                print(f'Successfully exported "{params[PARAM_OUTPUT_PATH]}"')
        elif verses:
            if export_table_document(verses, params):
                print(f'Successfully exported "{params[PARAM_OUTPUT_PATH]}"')
