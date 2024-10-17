# mdnov_yw7

Converter between .mdnov and .yw7 file format.

This is a command line tool for migrating novel projects between 
[mdnovel](https://github.com/peter88213/mdnovel) and
[yWriter](https://spacejock.com/yWriter7.html).

## Requirements

- A Python installation (version 3.6 or newer).

## Download

Save the file [mdnov_yw7.py](https://raw.githubusercontent.com/peter88213/mdnov_yw7/main/dist/mdnov_yw7.py).

## Usage 

`mdnov_yw7.py sourcefile`

- *yWriter* project files with the extension *.yw7* are converted to *.mdnov* format.
- *mdnovel* project files with the extension *.mdnov* are converted to *.yw7* format.

**Note:** Since *yWriter* and *mdnovel* do not have the same set of features, 
information may be lost during the conversion process. 

- *mdnov_yw7* supports `**bold**` and `*italics*` highlighting in CommonMarks style. 
  Other formatting and HTML/TEX inline code is not converted. 
- *yWriter* project variables and global variables are not resolved.
- *mdnovel* plot lines are converted to *yWriter* "Todo" chapters.  
- *mdnovel* plot points are converted to *yWriter* "Todo" scenes.  
- *mdnovel* plot line notes are lost.  

## Feedback

Post a message in the [mdnovel discussions forum](https://github.com/peter88213/mdnovel/discussions/).

## License

This is Open Source software, and *mdnov_yw7* is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/mdnovel/blob/main/LICENSE) file.



