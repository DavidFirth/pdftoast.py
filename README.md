# pdftoast.py

This is a Python script to split all pages of a PDF file for viewing on landscape screens.  It was written with academics and other researchers in mind --- people who routinely work with research papers and other such documents formatted as portrait-oriented PDF documents.  But perhaps some other people might find it useful too.

## Some use cases

The two applications that have emerged in my own work are the following.


1.  Uploading a paper to a _reMarkable 2_ or similar tablet device for reading and/or annotation, with text displayed at a good size and with no scrolling needed.  In fact, writing this script was motivated by my having started to play with a _reMarkable 2_, whose e-ink display makes scrolling a severe annoyance due to its constant refreshing of the screen while scrolling.  I now find reading and annotating PDFs on the _reMarkable 2_ much easier --- fun, even! --- when the PDF has been processed by `pdftoast.py` and is viewed in landscape mode on the tablet.  On the _reMarkable 2_, that view of a document has the text at a size that's slightly bigger than it would be in a printed copy of the paper.  And the right margin gives enough space, still, for short annotations --- with space for longer annotations still available by scrolling.  (All testing on the _reMarkable 2_ has been done with that tablet's software version 3.16.)
2.  Discussing a paper with students or colleagues, using a landscape-oriented screen in presentation mode to display the paper (online, or on my desk, or with a projector).  The landscape-oriented PDF made by `pdftoast.py` makes decent use of the screen space, with no scrolling and with page numbers always visible.

## Using the script

If the dependencies are all installed (see below) and the `pdftoast.py` script has been placed in the user's path, then at the shell prompt:
```
pdftoast.py --help
```
outlines the script's usage and options.  A typical command is like this:
```
pdftoast.py --verbose mydocument.pdf -p 2-
```
which will make a new PDF document named `mydocument-toasted.pdf` (in the same folder as `mydocument.pdf`).  

The `--verbose` switch is optional; if used, it gives a running commentary on progress. 

The `-p` argument is optionally used to specify a page range to select from the PDF document, instead of processing the whole document.  (In this example, the value `'2-'` means that pages 2 onwards are selected.)  Only one such page range is allowed, with its start and end page numbers always separated by `-`.

If `pdftoast.py` is **not** in the user's path, they would need to call Python explicitly like this:
```
python /path/to/pdftoast.py --verbose mydocument.pdf
```

## System requirements

This script depends on having the following installed on your system:

1. **Python** (tested to work with Python version 3.11.2) 
2. A fairly recent version of the Python package **pypdf** (tested to work with pypdf version 5.1.0 --- and known _not_ to work with much earlier versions, nor with the now-deprecated package PyPDF2)
3. Other python modules **argparse**, **os**, **subprocess**, **tempfile** and **shutil** (which versions should not matter much if at all)
4. **Ghostscript** (tested to work with Ghostscript version 10.00.0, and likely to work with more recent versions)

The mechanism for installing these things is system-dependent, so no more will be said about that here.

## Example

One of my own recent papers is in my Downloads folder (downloaded from [https://arxiv.org/abs/2312.10548](https://arxiv.org/abs/2312.10548)) 
as `2312.10548v1.pdf`.  Selected pages 2--3 from that file are processed by `pdftoast.py` as follows:
```
pdftoast.py -v 2312.10548v1.pdf -p 2-3
```
(Note that `-v` is just a convenient shorthand for `--verbose`.)

The output then seen in the terminal is this:
```
/home/david/Downloads$ pdftoast.py -v 2312.10548v1.pdf
--- This is pdftoast.py version 0.1 ---
Adding marginal page-number annotations, top and bottom...
...DONE
Flattening the annotated PDF...
...DONE
Splitting the pages...
...DONE
Writing the half-pages to the output file...
...DONE
Your new PDF file is at /home/david/Downloads/2312.10548v1-toasted.pdf.
```
A copy of both the original and `-toasted` PDF files can be found in the `Example` folder of the `pdftoast.py` repository at [https://github.com/DavidFirth/pdftoast.py](https://github.com/DavidFirth/pdftoast.py).

## Acknowledgment

This script uses ideas from an earlier script published by Niall at
[https://github.com/nmoran/landscape-pdf](https://github.com/nmoran/landscape-pdf).  Niall's contribution (inspiration!) is acknowledged with gratitude.
