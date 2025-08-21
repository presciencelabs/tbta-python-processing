# Usage

This script takes the exported unlinked concepts from TBTA and groups them by category (Noun, Adjective, etc). It also groups proper nouns separately.
The concepts are sorted alphabetically and put into tables in a Word document which can be sent to the MTT to translate.

If no concepts for a particular category are found, that table is excluded.

Example sentences are drawn from the verse that includes the concept. If no sentence is found to contain that concept, the whole verse is shown and highlighted so that the user can attend to it before sending to the MTT.

The script is called from the command line with the following arguments:

```tbta_missing_concepts_to_word.py -n "text_file.txt"```

The text file path is required, and the -n flag is optional.
```-n``` will include a 'Notes' column on the right. By default it is excluded.

# Development

To run this script, the package python-docx must be installed, which can be done using ```pip install python-docx```. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

In order for TBTA to call this script, it has to be made into a single-file executable. ```pyinstaller``` can be used, which is itself installed with ```pip install pyinstaller```.

To create the executable, run ```pyinstaller --onefile --noconsole "tbta_missing_concepts_to_word.py"``` and take the resulting .exe file from the generated ```dist/``` folder.