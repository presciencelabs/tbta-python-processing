# Usage

These scripts take a text file that was exported from TBTA and puts it in a Word document. This document is more easily sent to and understood by the MTT.

There are currently two scripts:
1. Plain Export (`tbta_export_to_word.py`)
2. Table Export (`tbta_export_to_table.py`)

## Plain Export

This takes exactly what is in the text file and puts it into a Word document. The text file can have any format, since the script has *no expectations* at all. Upon a successful export, the text file will be deleted.

`tbta_export_to_word.py (-t) "text_file.txt"`

- `-t` is 'test' mode. Currently this just means that the original text file will not be deleted.

## Table Export

This takes a text file, and puts its text into a table within a Word document. The text file must be in the format described below.

`tbta_export_to_table.py (-n) (-s) (-c) (-t) "text_file.txt"`

- `-n` will include a 'Notes' column on the right. By default it is excluded.
- `-s` will split each verse into sentences, each line getting its own row. See 'Split Sentences' below.
- `-c` will compare the last two texts of each verse. See 'Compare' below.
- `-t` is 'test' mode. Currently this just means that the original text file will not be deleted.

This script should handle any combination of languages within the text file, and any combination of arguments.

### Text File Format

The text file is expected to be in the following general format:
```
{Verse1 reference}
{Column1 header}: {Column1 text}
...
{ColumnN header}: {ColumnN text}

{Verse2 reference}
{Column1 header}: {Column1 text}
...
{ColumnN header}: {ColumnN text}

...
```

Each verse reference goes into the left-most 'Verse' column of each row. It must be in the format `{book} {chapter}:{verse}(:{sentence})` where `chapter`, `verse`, and `sentence` are numbers, and `sentence` is optional. `book` has no restrictions.

The column headers (typically the language name) go in the header row of the table. They should not include a `:`.

The column text can be any text, but must be a single line (no line breaks).

For example:
```
Genesis 44:1
English: Title: Joseph's silver cup is in Benjamin's bag. Then Joseph spoke to the chief servant who worked in his house. Joseph told that servant, “Fill these men's bags with a lot of food so that they would be full. Then put each man's silver into his bag on that food.
Ibwe: Judul: Cangkir Yusup dari perak baada di kantong Benyamin. Lalu Yusup bapandir lawan kapala susuruhan nang bagawi di rumahnya. “Isi ja ikam kantong-kantong urang-urang nang ini lawan banyak makanan sakira kantong-kantong hibak. Buati perak sabarataan urang di kantongnya di makanan nang itu.

Genesis 44:2
English: Then put my silver cup into the youngest brother's bag with the silver that he paid for the grain with.” That servant did all of the things that Joseph said.
Ibwe: Lalu buati ja ikam cangkirku dari perak di kantong dangsanak lalakian nang paanumnya lawan perak nang dibayarnya gasan gandum,” Yusup mamadahiakan susuruhan nang itu. Susuruhan nang itu malakuakan samuaan parbuatan nang Yusup ucapakan.
```

### Split Sentences

When splitting sentences with `-s`, there may be some misalignment between multiple languages due to some sentences being combined in one language but not the other, or due to the presence of an implicit sentence. A blank line will alert the user that there is misalignment which will have to be dealt with manually. However, this misalignment will not extend beyond the verse in question.

### Compare

TBTA can export text differences between old and new versions. This script compares the last two texts within the text file (typically 'Old X' and 'New X') using [difflib.SequenceMatcher.get_matching_blocks()](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks). The character-by-character differences become formatted in bold red text in the word document.

# Development

## Dependencies

To run this script, the package python-docx must be installed, which can be done using `pip install python-docx`. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

## Testing

To run the unit tests, simply run `tbta_export_to_table_test.py`.

To test on a particular text file, make sure to add the `-t` flag if you don't want the text file to be deleted.

## Distributing

In order for TBTA to call these scripts, they each have to be made into a single-file executable. `pyinstaller` can be used, which is itself installed with `pip install pyinstaller`.

To create the executable, run:
```
pyinstaller --onefile --noconsole "tbta_export_to_word.py"
```
and/or
```
pyinstaller --onefile --noconsole "tbta_export_to_table.py"
```
Then take the resulting .exe file from the generated `dist/` folder.
