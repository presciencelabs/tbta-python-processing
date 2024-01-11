# Usage

This script takes an exported text file from TBTA and arranges the verses into a Word document table that can then be sent to the MTT. It separates the English and the target language, making sure the corresponding verses and sentences are aligned properly.

The script is called from the command line with the following arguments:

tbta_export_to_word.py -s -n -p "text_file.txt" "footnote:"

The text file path and footnote word are required

The txt file to import the verses from must be specified as the last argument.
Including the argument -s will separate each sentence into its own line.
By default each whole verse gets its own row.
Including the argument -n will add a blank 'Notes' column on the right.
By default it is excluded.

When splitting sentences, there may be some misalignment between the two
langauges due to some sentences being combined in one language but not the other, or due to the presence of an implicit sentence. A blank line will alert the user that there is misalignment which will have to be dealt with manually. However, this misalignment will not extend beyond the verse in question.

# Development

To run this script, the package python-docx must be installed, which can be done using ```pip install python-docx```. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

In order for TBTA to call this script, it has to be made into a single-file executable. ```pyinstaller``` can be used, which is itself installed with ```pip install pyinstaller```.

To create the executable, run ```pyinstaller --onefile --noconsole "tbta_export_to_word.py"``` and take the resulting .exe file from the generated ```dist/``` folder.