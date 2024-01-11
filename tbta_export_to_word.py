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
from docx.shared import Cm


class VerseInfo:
    def __init__(self, num_languages):
        self.languages = [{ 'ref': '', 'text': '' } for _ in range(num_languages)]

    def set_ref(self, ref, lang_index):
        self.languages[lang_index]['ref'] = ref

    def get_ref(self, lang_index):
        return self.languages[lang_index]['ref']

    def append_text(self, text, lang_index):
        if self.languages[lang_index]['text']:
            text = ' ' + text
        self.languages[lang_index]['text'] += text

    def get_text(self, lang_index):
        return self.languages[lang_index]['text']

    
# Parameter Name constants
PARAM_INPUT_PATH = 'input_path'
PARAM_OUTPUT_PATH = 'output_path'
PARAM_FOOTNOTE = 'footnote'
PARAM_SPLIT_SENTENCES = 'split_sentences'
PARAM_NOTES_COLUMN = 'add_notes_column'
PARAM_PUB_REFS = 'publishable_refs'
PARAM_LANGUAGE_INFO = "languages"

# Language Info Fields
LANG_NAME = "name"
LANG_BOOK_NAME = "book_name"
LANG_IS_TARGET = "is_target"

def get_params():
    # usage is: tbta_export_to_word.exe -s -n -p "text_file.txt" "footnote:"
    # The text file path and footnote word are required
    if len([a for a in sys.argv if not a.startswith('-')]) < 3:
        show_error('Please specify a .txt file to import and the Target word for Footnote')
        return None

    file_name = sys.argv[-2]
    file_path = Path(file_name).with_suffix('.txt')
    if not file_path.exists():
        show_error(f'Specified File "{file_name}" does not exist...')
        return None

    return {
        PARAM_INPUT_PATH: file_path,
        PARAM_OUTPUT_PATH: file_path.with_name(f'{file_path.stem}.docx'),
        PARAM_FOOTNOTE: sys.argv[-1],
        PARAM_SPLIT_SENTENCES: '-S' in sys.argv or '-s' in sys.argv,
        PARAM_NOTES_COLUMN: '-N' in sys.argv or '-n' in sys.argv,
        PARAM_PUB_REFS: '-P' in sys.argv or '-p' in sys.argv,
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


def import_file(encoding, params):
    # Read the text file and return either a list of lines or verse text
    with params[PARAM_INPUT_PATH].open(encoding=encoding) as file:
        file_iter = iter(file)
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
            return (None, table_verses)


def import_verses_for_table(file_iter, params):
    footnote_word = params[PARAM_FOOTNOTE]
    num_languages = len(params[PARAM_LANGUAGE_INFO])

    verses = []
    current_verse = VerseInfo(num_languages)
    current_language = 0

    def line_is_for_current_language(line):
        return (not current_verse.get_ref(current_language)
                or line.startswith(footnote_word))
    
    VERSE_LINE_REGEX = re.compile(r'^(.+? \d+:\d+) ?(.+)?')

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
                current_verse = VerseInfo(num_languages)
                current_language = 0
        
        # Parse the line
        verse_match = VERSE_LINE_REGEX.fullmatch(line)
        if verse_match:
            current_verse.set_ref(verse_match[1], current_language)
            current_verse.append_text(verse_match[2], current_language)
        else:
            current_verse.append_text(line, current_language)

    # There may be a last unpushed verse at the end
    if verses and verses[-1].get_ref(0) != current_verse.get_ref(0):
        verses.append(current_verse)

    print(f'Retrieved {len(verses)} verses from "{params[PARAM_INPUT_PATH]}"')
    return verses


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

    for verse in verses:
        add_verse_rows(verse, table, params[PARAM_SPLIT_SENTENCES])

    # Set the column widths. Each cell needs to be set individually
    for idx, col in enumerate(table.columns):
        for cell in col.cells:
            cell.width = col_widths[idx]
            
    return save_document(doc, params[PARAM_OUTPUT_PATH])


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


SENTENCE_REGEX = re.compile(r'([^.?!]+[.?!]\S*) ?')
def add_verse_rows(verse, table, split_sentences):
    # Always include the whole verse as the first row
    main_row = table.add_row()
    main_row.cells[0].text = verse.get_ref(0)
    for i in range(len(verse.languages)):
        main_row.cells[i+1].text = verse.get_text(i)

    if split_sentences:
        lang_sentences = [SENTENCE_REGEX.findall(verse.get_text(i)) for i in range(len(verse.languages))]

        # Some sentences in either language may be combined so it may
        # not correspond exactly, but an empty line should notify the
        # user of the issue and not mess up the sentence alignment
        num_lines = max([len(s) for s in lang_sentences])
        for sentences in lang_sentences:
            sentences.extend([''] * (num_lines - len(sentences)))

        # Add a row for each sentence
        for i in range(num_lines):
            row = table.add_row()
            row.cells[0].text = f'{verse.get_ref(0).strip(".")}:{i+1}'
            for (j, lang) in enumerate(lang_sentences):
                row.cells[j+1].text = lang[i]


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
        (lines, verses) = import_file('utf-8-sig', params)
        if lines:
            if export_simple_document(lines, params):
                print(f'Successfully exported "{params[PARAM_OUTPUT_PATH]}"')
        elif verses:
            if export_table_document(verses, params):
                print(f'Successfully exported "{params[PARAM_OUTPUT_PATH]}"')
