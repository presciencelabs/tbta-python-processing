# Usage

This script takes an exported text file from TBTA and arranges the verses into a Word document table that can then be sent to the MTT. It separates the English and the target language, making sure the corresponding verses and sentences are aligned properly.

The script is called from the command line with the following arguments:

```tbta_export_to_word.py -s -n -p -c "text_file.txt" "footnote:"```

- The text file path is required, and the flags are optional. The 'footnote' word not required with ```-p``` or ```-c```, but is required otherwise.
- ```-s``` will split each verse into sentences, each line getting its own row.
- ```-n``` will include a 'Notes' column on the right. By default it is excluded.
- ```-p``` will export a simple word document with no table. If this flag is set, any other flag argument is ignored.
- ```-c``` will export a word document with a table with the text differences highlighted in red.

If no argument flags are set, and there is only one language within the file, the script exports a simple word document with no table.

The footnote word is the target-language word for the start of a footnote. TBTA puts the target-language footnotes on their own line, so this is used to recognize that line.

When splitting sentences with ```-s```, there may be some misalignment between multiple languages due to some sentences being combined in one language but not the other, or due to the presence of an implicit sentence. A blank line will alert the user that there is misalignment which will have to be dealt with manually. However, this misalignment will not extend beyond the verse in question.

When doing the comparison using ```-c```, this expects a text file where each verse has 'English', 'Old X' and 'New X' text. The Old and New text are expected to have their differences marked with ```[ ]```, which then gets formatted in bold red text in the word document. See ```test/Ibwe Differences.txt```.

This script should handle any combination of languages within the text file, and any combination of arguments. 

# Development

## Dependencies

To run this script, the package python-docx must be installed, which can be done using ```pip install python-docx```. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

## Testing

To run the tests, simply run ```tbta_export_to_word_test.py```.

## Distributing

In order for TBTA to call this script, it has to be made into a single-file executable. ```pyinstaller``` can be used, which is itself installed with ```pip install pyinstaller```.

To create the executable, run ```pyinstaller --onefile --noconsole "tbta_export_to_word.py"``` and take the resulting .exe file from the generated ```dist/``` folder.