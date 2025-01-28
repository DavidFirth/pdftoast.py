#!/usr/bin/env python
"""
Split All Pages of a PDF File for Viewing on Landscape Screens

This script allows the user to split each page of a portrait-oriented
PDF document into two landscape-oriented half pages, with a useful
overlap across the two halves. The result is a new PDF document that is
well suited to reading and/or annotation on a screen that has landscape
orientation.  Page numbers are added in the right margin of the output
document.

The assumption is that the input document has one of the two most
standard page sizes for academic papers, i.e. ISO A4 or "US letter";
and that the margins are all 1 inch or wider.  The output might not be
so useful when these assumptions fail.

Required software that must be separately installed on the system:
- Python 3.x
- The `pypdf` module for Python
- Ghostscript 
The script has been tested to work with Python 3.11.2 and pypdf version
5.1.0.  It is known not to work with much earlier versions of pypdf, nor
with the now-deprecated package PyPDF2.  The version of Ghostscript used
when testing the script was 10.00.0.

Usage:
Run the script from the command line with a PDF file path.  The name of
the PDF file to be processed must end in `.pdf`.
Examples:
1. Process `myfile.pdf` to new file `myfile-toasted.pdf`,
with verbose output:
    `python pdftoast.py -v myfile.pdf`
   Alternatively, if `pdftoast.py` is in your path:
    `pdftoast.py -v myfile.pdf`
2. Get help on usage:
    `python pdftoast.py -h`
   Or, if `pdftoast.py` is in your path,
    `pdftoast.py -h`

Script written by David Firth, maintained at
https://github.com/DavidFirth/pdftoast.py

Inspired by an earlier script published by Niall at
https://github.com/nmoran/landscape-pdf

License: MIT License
NO WARRANTY OF FITNESS FOR ANY PURPOSE  
"""

version = 0.1

import argparse
import os
import pypdf as pdf  ## tested to work with pypdf 5.1.0
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText
import subprocess
import tempfile

def number_and_split_pages(inputfile: str, verbose: bool, debug: bool):
    """
    The main work is done by this function.

    Parameters
    ----------
    inputfile : str
        the path to the PDF file that will be processed
    verbose : bool
        provide commentary when run
    debug : bool
        keep temporary files and show their names; and also show
        Ghostscript errors and warnings
    """
    if verbose:
        print("Adding marginal page-number annotations, top and bottom...")
    pagenumbers_colour = "009900"
    reader = PdfReader(inputfile)
    writer = PdfWriter()
    number_pages = len(reader.pages)
    pages = reader.pages
    bb = pages[0].cropbox  ## assumed same for all pages
    for pn in range(number_pages):
        pagenumber_text = " " + str(int(1 + pn)) + "/" + str(number_pages)
        page = pages[pn]
        writer.add_page(page)
        annotation_top = FreeText(
            text = pagenumber_text,
            rect = (bb[2]-39, bb[3]-78, bb[2]+1, bb[3]-60),
            border_color = pagenumbers_colour,
            background_color = "ffffff"
        )
        annotation_top.flags = 4  ## for "printable" annotation
        writer.add_annotation(page_number = pn, annotation = annotation_top)
        annotation_bottom = FreeText(
            text = pagenumber_text,
            rect=(bb[2]-40, 49, bb[2]+1, 30),
            border_color = "ffffff",
            background_color = pagenumbers_colour
        )
        annotation_bottom.flags = 4
        writer.add_annotation(page_number = pn, annotation = annotation_bottom)
    ## We will write out the resultant PDF to a temporary file:
    temp1 = tempfile.NamedTemporaryFile(suffix = '.pdf', delete = not debug)
    if debug:
        print("(the first temporary file will be written at " + temp1.name + ")")
    ##
    ## First remove duplicate/orphan objects to reduce PDF file size:
    writer.compress_identical_objects(remove_identicals = True, remove_orphans = True)
    ## Then write the file:
    with open(temp1.name, "wb") as io:
        writer.write(io)
    if verbose:
        print("...DONE")

    ## Next we "flatten" the PDF so that the page-number annotations will be visible
    ## when viewed on the _reMarkable_ and similar devices:
    if verbose:
        print("Flattening the annotated PDF...")
    temp2 = tempfile.NamedTemporaryFile(suffix = '.pdf', delete = not debug)
    if debug:
        print("(the second temporary file will be written at " + temp2.name + ")")
    ghostscript_options = ['-sDEVICE=pdfwrite', '-dSAFER', '-dPDFSETTINGS=/printer',
                           '-dNOPAUSE', '-dBATCH', '-dPreserveAnnots=false']
    if not debug:
        ghostscript_options.insert(0, '-dQUIET')
    subprocess.call(['gs'] + ghostscript_options + ['-sOutputFile='+temp2.name, temp1.name])
    if verbose:
        print("...DONE")

    ## Next we split each page into top and bottom halves, with a useful overlap: 
    if verbose:
        print("Splitting the pages...")
    reader_top = PdfReader(temp2.name)
    reader_bottom = PdfReader(temp2.name)
    writer2 = PdfWriter()
    for pn in range(number_pages):
        page_top = reader_top.pages[pn]
        page_bottom = reader_bottom.pages[pn]
        page_top.cropbox = pdf.generic.RectangleObject([35, (bb[3]/2)-25, bb[2], bb[3]-35])
        writer2.add_page(page_top)
        page_bottom.cropbox = pdf.generic.RectangleObject([35, 25, bb[2], (bb[3]/2)+15])
        writer2.add_page(page_bottom)
    if verbose:
        print("...DONE")

    ## Finally, write the result to the output PDF file:
    if verbose:
        print("Writing the half-pages to the output file...")
    writer2.compress_identical_objects(remove_identicals = True, remove_orphans = True)
    outputfile = inputfile.rsplit('.', 1)[0] + '-toasted.pdf'
    with open(outputfile, "wb") as io:
        writer2.write(io)
    if verbose:
        print("...DONE")
        print("Your new PDF file is at " + outputfile + ".")
    return(outputfile)

def main():
    """
    Main function to parse command-line arguments and call the PDF processing function.
    """
    parser = argparse.ArgumentParser(description = \
                "Splits all pages of a PDF file for viewing on landscape screens.  " + \
                "Output is to a new file: the input PDF file is left unchanged.")
    parser.add_argument("inputfile", type = str, help = "path to the input PDF file")
    parser.add_argument("-v", "--verbose", action = 'store_true',
                        help = "provide brief commentary")
    parser.add_argument("-d", "--debug", action = 'store_true',
                        help = "keep temporary files and show their names; " + \
                               "and also show Ghostscript errors and warnings " + \
                               "in addition to brief commentary")
    args = parser.parse_args()
    verbose = args.verbose
    debug = args.debug
    if debug:
        verbose = True
    if verbose:
        print("--- This is pdftoast.py version " + str(version) + " ---")
    outputfile = number_and_split_pages(inputfile = os.path.abspath(args.inputfile),
                                        verbose = verbose,
                                        debug = debug)
    return(outputfile)
    

if __name__ == "__main__":
    main()        



