# Usage

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

## Dependencies

To run this script, the package python-docx must be installed, which can be done using `pip install python-docx`. Go to https://python-docx.readthedocs.io/en/latest/index.html for the package documentation.

## Testing

To run the unit tests, simply run `tbta_analyze_edits_test.py`.

To test on a particular text file, make sure to add the `-t` flag if you don't want the text file to be deleted.

## Distributing

In order for TBTA to call these scripts, they each have to be made into a single-file executable. `pyinstaller` can be used, which is itself installed with `pip install pyinstaller`.

To create the executable, run:
```
pyinstaller --onefile --noconsole "tbta_analyze_edits.py"
```
Then take the resulting .exe file from the generated `dist/` folder.
