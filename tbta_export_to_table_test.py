import unittest
from pathlib import Path
from tbta_export_to_table import *

# TODO redo tests

def setup_params(file_name, split=False, notes=False, compare=False):
    file_path = Path('./test/' + file_name)
    return {
        PARAM_INPUT_PATH: file_path,
        PARAM_OUTPUT_PATH: file_path.with_name(f'{file_path.stem}.docx'),
        PARAM_SPLIT_SENTENCES: split,
        PARAM_NOTES_COLUMN: notes,
        PARAM_COMPARE: compare,   #TODO test compare functionality
    }


class VerseTestCase(unittest.TestCase):

    def findVerse(self, verses, ref):
        for verse in verses:
            if verse[VERSE_REF] == ref:
                return verse[VERSE_TEXT]

    # def assertRefEqual(self, verse, expected):
    #     self.assertEqual(expected, verse[VERSE_REF])

    def assertVerseEqual(self, text, ref, expected):
        self.assertEqual(expected, text, f'{ref} not as expected')

    def assertVerseEmpty(self, verse, lang_index):
        self.assertEqual('', verse[VERSE_TEXT][lang_index], f'{verse[VERSE_REF]} should be empty')

    def assertVerseNotEmpty(self, verse, lang_index):
        self.assertNotEqual('', verse[VERSE_TEXT][lang_index], f'{verse[VERSE_REF]} should not be empty')

    def assertVerseStartswith(self, verse, lang_index, expected):
        self.assertTrue(verse[VERSE_TEXT][lang_index].startswith(expected), f'{verse[VERSE_REF]} not as expected')

    def assertVerseEndswith(self, verse, lang_index, expected):
        self.assertTrue(verse[VERSE_TEXT][lang_index].endswith(expected), f'{verse[VERSE_REF]} not as expected')

    def assertContains(self, text, expected):
        self.assertTrue(expected in text)


class TestTwoLanguagesSimple(VerseTestCase):

    def test_all_english_all_target(self):
        params = setup_params('Ruth 1 w English.txt')
        (verses, language_names) = import_for_table(params)

        self.assertListEqual(['English', 'Gichuka'], language_names)

        self.assertIsNotNone(verses)
        self.assertEqual(22, len(verses))

        (_, target) = self.findVerse(verses, 'Ruth 1:1')
        self.assertStartswith(target, "Title: Erimereki na Naomi kuuma Bethireemu kũthiĩ Moabu. Rĩrĩa aciirithania ma-thaga Iciraeri")
        self.assertContains(target, 'Footnote')

        verse = self.findVerse(verses, 'Ruth 1:10')
        self.assertVerseEqual(verse, 0, "Then Naomi's daughters-in-law said to her, “We'll certainly go to your people with you.”")

    def test_all_english_some_target(self):
        params = setup_params('Genesis 1-2 Ibwe and English.txt')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(56, len(verses))

        (english, target) = self.findVerse(verses, 'Genesis 1:21')
        self.assertRefEqual(target, 'Genesis 1:21')
        self.assertVerseEmpty(target)
        self.assertVerseNotEmpty(english)

    def test_some_english_some_target(self):
        params = setup_params('Genesis 1-2 Ibwe and English both missing.txt')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(56, len(verses))

        # both missing in 1:22
        (english, target) = self.findVerse(verses, 'Genesis 1:22')
        self.assertRefEqual(target, 'Genesis 1:22')
        self.assertVerseEmpty(target)
        self.assertVerseEmpty(english)

        # only english missing in 2:5
        (english, target) = self.findVerse(verses, 'Genesis 2:5')
        self.assertRefEqual(target, 'Genesis 2:5')
        self.assertVerseStartswith(target, "Title: Adam wan Hawa bagana di Eden. Pada jaman nang")
        self.assertVerseEmpty(english)

        # both present again in 2:22
        (english, target) = self.findVerse(verses, 'Genesis 2:22')
        self.assertRefEqual(target, 'Genesis 2:22')
        self.assertVerseStartswith(target, "Lalu Allah Al Khalik maulah bibinian")
        self.assertVerseStartswith(english, "Then the LORD God made a woman")

    def test_some_target_some_other(self):
        params = setup_params('Esther 1 w Tagalog.txt')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(22, len(verses))

        # tagalog missing in 1:10
        (target, tagalog) = self.findVerse(verses, 'Eciteri 1:10')
        self.assertVerseNotEmpty(target)
        self.assertVerseEmpty(tagalog)

        # both missing in 1:12
        (target, tagalog) = self.findVerse(verses, 'Eciteri 1:12')
        self.assertVerseEmpty(target)
        self.assertVerseEmpty(tagalog)

        # target missing in 1:22
        (target, tagalog) = self.findVerse(verses, 'Eciteri 1:22')
        self.assertVerseEmpty(target)
        self.assertVerseNotEmpty(tagalog)

    def test_footnote_with_verse_ref(self):
        params = setup_params('Matthew 4 Tagalog and English.txt', footnote='Talababa:')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(25, len(verses))

        # footnote with verse reference is handled correctly
        (english, tagalog) = self.findVerse(verses, 'Matthew 4:6')
        self.assertVerseEndswith(tagalog, 'Talababa: Makita ninyong Mga Awit 91:11-12.')
        self.assertVerseEndswith(english, 'Footnote: See Psalms 91:11-12.')


class TestThreeLanguagesSimple(VerseTestCase):

    def test_all_three(self):
        params = setup_params('Esther 1 Triple.txt')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(22, len(verses))

        (english, target, third) = self.findVerse(verses, 'Esther 1:1')
        self.assertVerseStartswith(english, "Title: King Xerxes")
        self.assertRefEqual(target, 'Eciteri 1:1')
        self.assertVerseStartswith(target, "Title: Cakceci akĩthũra")
        self.assertRefEqual(third, 'Esther 1:1')
        self.assertVerseStartswith(third, "Pamagat: Nagalit")

        (_, target, third) = self.findVerse(verses, 'Esther 1:6')
        self.assertVerseContains(target, 'Footnote:')
        self.assertVerseStartswith(third, "Bago pumunta")

        (english, target, third) = self.findVerse(verses, 'Esther 1:22')
        self.assertVerseStartswith(english, "King Xerxes sent letters")
        self.assertVerseStartswith(target, "Cakceci a-tũmire barũa")
        self.assertVerseStartswith(third, "Nagpadala si Haring Xerxes")

    def test_all_three_missing_some(self):
        params = setup_params('Esther 1 Triple some missing.txt')
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        self.assertEqual(22, len(verses))

        # third language missing
        (english, target, third) = self.findVerse(verses, 'Esther 1:1')
        self.assertVerseStartswith(english, "Title: King Xerxes")
        self.assertVerseStartswith(target, "Title: Cakceci akĩthũra")
        self.assertVerseEmpty(third)

        # english missing
        (english, target, third) = self.findVerse(verses, 'Esther 1:4')
        self.assertVerseEmpty(english)
        self.assertVerseStartswith(target, "Kabinda ka ntukũ ĩgana")
        self.assertVerseStartswith(third, "Sa loob ng 180 araw")

        # target missing
        (english, target, third) = self.findVerse(verses, 'Esther 1:5')
        self.assertVerseStartswith(english, "After that feast ended")
        self.assertVerseEmpty(target)
        self.assertVerseStartswith(third, "Matapos ang pistang iyon")

        # target and third missing
        (english, target, third) = self.findVerse(verses, 'Esther 1:10')
        self.assertVerseStartswith(english, "After seven days")
        self.assertVerseEmpty(target)
        self.assertVerseEmpty(third)

        # all present again
        (english, target, third) = self.findVerse(verses, 'Esther 1:11')
        self.assertVerseStartswith(english, "Then King Xerxes")
        self.assertVerseStartswith(target, "Cakceci a-thire")
        self.assertVerseStartswith(third, "Pagkatapos")


class TestTwoLanguagesSplitSentences(VerseTestCase):

    def test_split_none_missing(self):
        params = setup_params('Ruth 1 w English.txt', split=True)
        (_, verses) = import_for_table(params)

        self.assertIsNotNone(verses)
        verses = list(verses)   # verses is returned as a generator but we need a list here
        self.assertEqual(101, len(verses))

        (_, target) = self.findVerse(verses, 'Ruth 1:1')
        self.assertVerseNotEmpty(target)
        self.assertVerseStartswith(target, "Title: Erimereki na Naomi kuuma Bethireemu kũthiĩ Moabu. Rĩrĩa aciirithania ma-thaga Iciraeri")

        (english, target) = self.findVerse(verses, 'Ruth 1:1:5')
        self.assertRefEqual(target, 'Ruthu 1:1:5')
        self.assertVerseStartswith(target, 'Footnote:')
        self.assertVerseEmpty(english)

        (english, _) = self.findVerse(verses, 'Ruth 1:21:5')
        self.assertVerseNotEmpty(english)

if __name__ == '__main__':
    unittest.main()