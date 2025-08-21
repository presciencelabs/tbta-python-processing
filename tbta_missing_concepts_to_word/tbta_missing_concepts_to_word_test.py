import unittest
from pathlib import Path
from tbta_missing_concepts_to_word import *

def setup_params(file_name, export_name=None, notes=False):
    file_path = Path('./test/' + file_name)
    return {
        PARAM_INPUT_PATH: file_path,
        PARAM_OUTPUT_PATH: file_path.with_name(f'Lexicon - {export_name or file_path.stem}.docx'),
        PARAM_NOTES_COLUMN: notes,
    }

def find_concept(word, category):
    for concept in category:
        if concept[CONCEPT_WORD] == word:
            return concept
    return None


class TestImportConcepts(unittest.TestCase):

    def test_import(self):
        params = setup_params('Esther 1 Issues.txt')
        concepts = import_concepts(params)

        self.assertIn(CATEGORY_NOUN, concepts)
        self.assertEqual(33, len(concepts[CATEGORY_NOUN]))

        self.assertIn(CATEGORY_VERB, concepts)
        self.assertEqual(31, len(concepts[CATEGORY_VERB]))

        self.assertNotIn(CATEGORY_PARTICLE, concepts)

        # Regular verb
        concept = find_concept('describe-A', concepts[CATEGORY_VERB])
        self.assertIsNotNone(concept)
        self.assertIn(CONCEPT_SAMPLE, concept)
        self.assertIn(CONCEPT_OCCURRENCES, concept)
        self.assertEqual(1, len(concept[CONCEPT_OCCURRENCES]))

        # Regular proper noun
        concept = find_concept('Media-A', concepts[CATEGORY_PROPER])
        self.assertIsNotNone(concept)
        self.assertNotEqual('', concept[CONCEPT_GLOSS])
        self.assertNotIn(CONCEPT_SAMPLE, concept)
        self.assertNotIn(CONCEPT_OCCURRENCES, concept)

        # missing gloss
        concept = find_concept('Karshena-A', concepts[CATEGORY_PROPER])
        self.assertIsNotNone(concept)
        self.assertEqual('', concept[CONCEPT_GLOSS])

        # missing verse text
        concept = find_concept('cup-A', concepts[CATEGORY_NOUN])
        self.assertIsNotNone(concept)
        self.assertEqual('', concept[CONCEPT_VERSE_TEXT])
        self.assertIn(CONCEPT_OCCURRENCES, concept)
        self.assertEqual(0, len(concept[CONCEPT_OCCURRENCES]))


    def test_export_no_notes(self):
        params = setup_params('Esther 1 Issues.txt')
        concepts = import_concepts(params)
        export_document(concepts, params)


    def test_export_with_notes(self):
        params = setup_params('Esther 1 Issues.txt', export_name='Esther 1 Issues w Notes', notes=True)
        concepts = import_concepts(params)
        export_document(concepts, params)


    def test_export_no_verbs(self):
        params = setup_params('Esther 1 Issues.txt', export_name='Esther 1 Issues no Verbs')
        concepts = import_concepts(params)
        concepts.pop(CATEGORY_VERB)
        export_document(concepts, params)


if __name__ == '__main__':
    unittest.main()