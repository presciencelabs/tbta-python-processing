# Usage

This script takes a text file that was exported from TBTA and puts it in a Word document. This document is more easily sent to and understood by the MTT.

The format of the text file and format of the output Word document depends on the mode of usage, determined by command-line flag arguments.

There are three modes of using this script:
1. Normal
2. Publishable Refs
3. Compare

## Normal Mode

In normal mode, this script takes an exported text file from TBTA and arranges the verses into a Word document table that can then be sent to the MTT. It separates the target language from the other languages, making sure the corresponding verses and sentences are aligned properly. For this mode, the script is called from the command line with the following arguments:

```tbta_export_to_word.py (-s) (-n) "text_file.txt" "footnote:"```

- The text file path and 'footnote' word are required, and the flags are optional.
- ```-s``` will split each verse into sentences, each line getting its own row.
- ```-n``` will include a 'Notes' column on the right. By default it is excluded.
- The footnote word is the target-language word for the start of a footnote. TBTA puts the target-language footnotes on their own line, so this is used to recognize that line.

If no argument flags are set, and there is only one language within the file, the script exports a simple word document with no table.

When splitting sentences with ```-s```, there may be some misalignment between multiple languages due to some sentences being combined in one language but not the other, or due to the presence of an implicit sentence. A blank line will alert the user that there is misalignment which will have to be dealt with manually. However, this misalignment will not extend beyond the verse in question.

This script should handle any combination of languages within the text file, and any combination of arguments. 

## Publishable Refs

```tbta_export_to_word.py -p "text_file.txt"```

TBTA can export text using verse references that are more standard and thus 'publishable'. The text is taken as-is and put directly into a Word document without any additional formatting or handling.

## Compare

```tbta_export_to_word.py -c (-n) "text_file.txt"```

TBTA can export text differences between saved and old versions. The Old and New text within the text file are compared using [difflib.SequenceMatcher.get_matching_blocks()](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks), and the character-by-character differences become formatted in bold red text in the word document. Using this mode will put the text in a table. It can also includes a notes using the `-n` flag.

# Development

## Dependencies

To run this script, the package python-docx must be installed, which can be done using ```pip install python-docx```. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

## Testing

To run the tests, simply run ```tbta_export_to_word_test.py```.

## Distributing

In order for TBTA to call this script, it has to be made into a single-file executable. ```pyinstaller``` can be used, which is itself installed with ```pip install pyinstaller```.

To create the executable, run ```pyinstaller --onefile --noconsole "tbta_export_to_word.py"``` and take the resulting .exe file from the generated ```dist/``` folder.
