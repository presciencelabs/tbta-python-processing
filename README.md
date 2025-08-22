TBTA uses several python scripts for various text processing tasks and Word document creation. Below is a breakdown of each script.

# Script Usage

## tbta_export_to_word

This script takes a text file that was exported from TBTA and puts it in a Word document. This document is more easily sent to and understood by the MTT.

It takes the text line-by-line and simply transfers it to a Word document. The text file can have any format, since the script has *no expectations* at all. The only formatting it does is make any text surrounded by asterisks '*' as red text in the Word document. Upon a successful export, the text file will be deleted. 

`tbta_export_to_word.py (-t) "text_file.txt"`

- `-t` is 'test' mode. Currently this just means that the original text file will not be deleted.

## tbta_export_to_table

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

When splitting sentences with `-s`, each text is broken into sentences, and put in their own rows below the full text/verse, and attempts to line up the sentences of each text/language. There may be some misalignment between multiple languages due to some sentences being combined in one language but not the other, or due to the presence of an implicit sentence. A blank line will alert the user that there is misalignment which will have to be dealt with manually. However, this misalignment will not extend beyond the verse in question.

Note that this is not compatible with the -c mode.

### Compare

TBTA can export text differences between old and new versions. This script compares the last two texts within the text file (typically 'Old X' and 'New X') using [difflib.SequenceMatcher.get_matching_blocks()](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks). The word-by-word differences become formatted in bold red text in the word document.

Note that this is not compatible with the -s mode.

### Testing

To run the unit tests, simply run `tbta_export_to_table_test.py`.

To test on a particular text file, make sure to add the `-t` flag if you don't want the text file to be deleted.

## tbta_missing_concepts_to_word

This script takes the exported unlinked concepts from TBTA and groups them by category (Noun, Adjective, etc). It also groups proper nouns separately.
The concepts are sorted alphabetically and put into tables in a Word document which can be sent to the MTT to translate.

If no concepts for a particular category are found, that table is excluded.

Example sentences are drawn from the verse that includes the concept. If no sentence is found to contain that concept, the whole verse is shown and highlighted so that the user can attend to it before sending to the MTT.

The script is called from the command line with the following arguments:

```tbta_missing_concepts_to_word.py -n "text_file.txt"```

The text file path is required, and the -n flag is optional.
```-n``` will include a 'Notes' column on the right. By default it is excluded.

## tbta_analyze_edits

This script takes two Paratext-formatted sfm files and performs a diff of them, verse by verse. It compiles a list of each change, counting the number of occurrences and tracking the references. It then outputs a plain text file with this list in the format described below.

To compare the two versions, this script uses [difflib.SequenceMatcher.get_matching_blocks()](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks) to do a word-by-word comparison. It also does its best to separate punctuation changes from word changes.

### Output File Format

The changes are listed and sorted by number of occurrences, then alphabetically (based on the default python sorting algorithm).

```
nargi->nagri
12;1:5,10-14,16-20;1:5,32-36,48-52;1:11,21-25,28-32;...
Wan->
7;1:5,0-2,0-0;1:6,27-29,25-25;...
...
```

# Development

To run some of these scripts, the package python-docx must be installed, which can be done using ```pip install python-docx```. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

# Distributing

In order for TBTA to call these scripts, they each have to be made into a single-file executable. `pyinstaller` can be used, which is itself installed with `pip install pyinstaller`.

To create the executable, run:
```
pyinstaller --onefile --noconsole "{script}.py"
```
Then take the resulting .exe file from the generated `dist/` folder.