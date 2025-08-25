import sys
import re
from pathlib import Path
import time

import doc_utils


# Parameter Name Constants
PARAM_INPUT_PATH = 'input_path'
PARAM_OUTPUT_PATH = 'output_path'
PARAM_NOTES_COLUMN = 'add_notes_column'
PARAM_PASSAGE = 'passage'
PARAM_TEST = 'test'

# Concept Info Fields
CONCEPT_WORD = 'word'
CONCEPT_GLOSS = 'gloss'
CONCEPT_VERSE_REF = 'verse_ref'
CONCEPT_VERSE_TEXT = 'verse_text'
CONCEPT_OCCURRENCES = 'verse_occurrences'
CONCEPT_SAMPLE = 'sample'

# Semantic Categories
CATEGORY_PROPER = 'Proper Name'
CATEGORY_NOUN = 'Noun'
CATEGORY_VERB = 'Verb'
CATEGORY_ADJECTIVE = 'Adjective'
CATEGORY_ADVERB = 'Adverb'
CATEGORY_ADPOSITION = 'Adposition'
CATEGORY_CONJUNCTION = 'Conjunction'
CATEGORY_PARTICLE = 'Particle'
CATEGORY_PHRASAL = 'Phrasal'

# Table Header Names
HEADER_GLOSS = 'Glosses'
HEADER_OCCURRENCE = 'Verses'
HEADER_SAMPLE = 'Target Sentences'
HEADER_TARGET_WORD = 'Target Words'
HEADER_TARGET_GLOSS = 'Target Glosses'
HEADER_NOTES = 'Notes'


def get_params():
    # usage is: tbta_missing_concepts_to_word.exe -n -t "text_file.txt"
    # The text file path is required
    if len(sys.argv) < 2:
        print('Please specify a .txt file to import')
        return None

    file_name = sys.argv[-1]
    if file_name.startswith('-'):
        print('File name must be the last argument')
        return None

    file_path = Path(file_name).with_suffix('.txt')
    if not file_path.exists():
        print('Specified File does not exist...')
        return None

    return {
        PARAM_INPUT_PATH: file_path,
        PARAM_OUTPUT_PATH: file_path.with_name(f'Lexicon - {file_path.stem}.docx'),
        PARAM_NOTES_COLUMN: '-N' in sys.argv or '-n' in sys.argv,
        PARAM_TEST: '-T' in sys.argv or '-t' in sys.argv,
    }


def import_concepts(params):
    CONCEPT_REGEX = re.compile(r'^Concept \((?P<category>[a-zA-Z]+)\): (?P<word>[.a-zA-Z0-9- ]+?-[A-Z])(?:  \'(?P<gloss>.+?)\')?$')
    VERSE_REGEX = re.compile(r'^Verse: (?P<ref>[.a-zA-Z0-9- ]+:\d+) ?(?P<text>.*)$')
    GLOSS_REPLACE_REGEX = re.compile(r'\((LDV|simple|inexplicable|proper name|universal primitive)\) ')
    categories = {}

    def add_concept_to_category(concept, category):
        if category == CATEGORY_NOUN and concept[CONCEPT_WORD][0].isupper():
            category = CATEGORY_PROPER
        if category not in categories:
            categories[category] = []
        categories[category].append(concept)
        return category

    path = params[PARAM_INPUT_PATH]
    with path.open() as f:
        concept = None
        category = ''
        for line_num, line in enumerate(f):
            if line.startswith('Concept'):
                concept_match = CONCEPT_REGEX.match(line)
                if not concept_match:
                    print('Unexpected format for Concept on line ' + str(line_num))
                    continue

                concept = {
                    CONCEPT_WORD: concept_match['word'],
                    CONCEPT_GLOSS: GLOSS_REPLACE_REGEX.sub('', concept_match['gloss']) if concept_match['gloss'] else ''
                }
                category = add_concept_to_category(concept, concept_match['category'])

            elif line.startswith('Sample Sentence'):
                concept[CONCEPT_SAMPLE] = line[len('Sample Sentence: '):].strip()

            elif line.startswith('Verse'):
                if category == CATEGORY_PROPER:
                    continue
                verse_match = VERSE_REGEX.match(line)
                concept[CONCEPT_VERSE_REF] = verse_match['ref']
                concept[CONCEPT_VERSE_TEXT] = verse_match['text']
                concept[CONCEPT_OCCURRENCES] = extract_verse_occurrences(concept[CONCEPT_WORD], verse_match['text'])

            elif line.startswith('Current Passage'):
                # This only appears once at the top of the text file
                params[PARAM_PASSAGE] = line[len('Current Passage: '):].strip()

    # Only for debug purposes
    # for k,v in categories.items():
    #     print(f'Retrieved {len(v)} {k} unlinked concepts from "{path}"')
    return categories


SENTENCE_REGEX = re.compile(r'([^.?!]+[.?!]\S*) ?')
def extract_verse_occurrences(word, text):
    # Remove the sense -X from the word
    dash_idx = word.rindex('-')
    word = word[:dash_idx]
    
    occurrences = []

    # The verse might have an unrecognizable form of the word, the word
    # might not be present at all due to restructuring. 
    word_regex = r'\b(' + re.escape(word) + r'(?:s|es|ed|d)?)\b'
    for sentence in SENTENCE_REGEX.findall(text):
        word_match = re.search(word_regex, sentence, re.IGNORECASE)
        if word_match:
            occurrences.append({
                'sentence': sentence,
                'location': word_match.span(1),
            })

    return occurrences


def export_document(categories, params):
    doc = doc_utils.create_doc(landscape=True, mx=2.54)

    # Add the passage as a heading
    doc_utils.add_paragraph(doc, { 'text': params[PARAM_PASSAGE] , 'bold': True, 'size': 14 })

    # Create the tables
    table_order = [
        CATEGORY_PROPER,
        CATEGORY_NOUN,
        CATEGORY_VERB,
        CATEGORY_ADJECTIVE,
        CATEGORY_ADVERB,
        CATEGORY_ADPOSITION,
        CATEGORY_CONJUNCTION,
        CATEGORY_PARTICLE,
        CATEGORY_PHRASAL,
    ]
    ordered_categories = sorted(categories.items(), key=lambda kv: table_order.index(kv[0]))
    for idx, (category, concepts) in enumerate(ordered_categories):
        create_table(category, concepts, idx+1, doc, params[PARAM_NOTES_COLUMN])

    try:
        doc.save(str(params[PARAM_OUTPUT_PATH]))
        return True
    except PermissionError:
        err_text = f'"{params[PARAM_OUTPUT_PATH].name}" is currently open. Please close and try again.'
        print("Error: " + err_text)
        import ctypes  
        ctypes.windll.user32.MessageBoxW(0, err_text, "Error Creating Word Document", 0 + 16)
        return False


def create_table(category, concepts, table_num, doc, add_notes_column):
    # Figure out the column names and widths
    if category == CATEGORY_PROPER:
        col_names = [f'Nouns: {category}s', HEADER_GLOSS, HEADER_TARGET_WORD]
        col_widths = [5] * 3
    elif add_notes_column:
        col_names = [category + 's', HEADER_GLOSS, HEADER_OCCURRENCE, HEADER_SAMPLE, HEADER_TARGET_WORD, HEADER_TARGET_GLOSS, HEADER_NOTES]
        col_widths = [2.5, 3, 6, 3, 3, 3, 3]
    else:
        col_names = [category + 's', HEADER_GLOSS, HEADER_OCCURRENCE, HEADER_SAMPLE, HEADER_TARGET_WORD, HEADER_TARGET_GLOSS]
        col_widths = [2.7, 3.2, 6.3, 4, 3.4, 3.4]

    if table_num > 1:
        doc_utils.add_paragraph(doc, formatting={ 'space_after': 0 })

    table_data = [
        # the header row
        [{ 'text': name, 'highlight': name == HEADER_TARGET_WORD } for name in col_names],
    ]
    table_data.extend(get_concept_rows(category, concepts))

    doc_utils.add_table(doc, table_data, col_widths, caption=f'Table {table_num}. {category}s')


def get_concept_rows(category, concepts):
    # TODO do we need to alphabetize the concepts?
    if category == CATEGORY_PROPER:
        return [[concept[CONCEPT_WORD], concept[CONCEPT_GLOSS]] for concept in concepts]
    else:
        return [[concept[CONCEPT_WORD], concept[CONCEPT_GLOSS], add_verse_sentences(concept), add_sample_sentences(concept)] for concept in concepts]


def add_verse_sentences(concept):
    if CONCEPT_OCCURRENCES not in concept or not concept[CONCEPT_OCCURRENCES]:
        # Show the whole verse and highlight the text so the user knows to attend to it
        return { 'text': concept[CONCEPT_VERSE_REF] + ' ' + concept[CONCEPT_VERSE_TEXT], 'highlight': True, 'size': 10 }

    runs = [{ 'text': concept[CONCEPT_VERSE_REF] }]
    # Show each occurrence of the word in bold
    for occurrence in concept[CONCEPT_OCCURRENCES]:
        sentence = occurrence['sentence']
        start, end = occurrence['location']
        runs.extend([
            { 'text': ' ' + sentence[:start] },
            { 'text': sentence[start:end], 'bold': True },
            { 'text': sentence[end:] },
        ])
    for run in runs:
        run['size'] = 10
    return runs


def add_sample_sentences(concept):
    if CONCEPT_SAMPLE not in concept:
        return ''

    # Start with the sample sentence itself with the separating bar
    return [
        { 'text': concept[CONCEPT_SAMPLE] + ' | ', 'size': 10 },
        { 'text': 'Translation here.', 'highlight': True, 'size': 10 },
    ]


if __name__ == "__main__":
    params = get_params()
    if params:
        concepts = import_concepts(params)
        start = time.time()
        success = export_document(concepts, params)
        end = time.time()
        print('time elapsed:', end-start)
        if success:
        # if export_document(concepts, params):
            if not params[PARAM_TEST]:
                print(f'Deleting {params[PARAM_INPUT_PATH]}')
                params[PARAM_INPUT_PATH].unlink()   # delete the original text file
            print(f'Successfully exported "{params[PARAM_OUTPUT_PATH]}"')
