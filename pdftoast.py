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

version = 0.6

import argparse
import os
import pypdf as pdf
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText
from pypdf.annotations import Line
import subprocess
import tempfile
from shutil import which

def number_and_split_pages(inputfile: str, pagespec : list,
                           ar : float, cl : float, mo : float,
                           pncol: str, verbose: bool, debug: bool):
    """
    The main work is done by this function.

    Parameters
    ----------
    inputfile : str
        the path to the PDF file that will be processed
    pagespec : list
        a list of two str values
    ar : float
        desired aspect ratio (width/height) of resulting landscape pages
    cl : float
        the amount to crop from the left margin of esch page
    mo : float
        minimum overlap between top and bottom halves of a page
    pncol : str
        a hexadecimal colour code for marginal page-numbering 
    verbose : bool
        provide commentary when run
    debug : bool
        keep temporary files and show their names; and also show
        Ghostscript errors and warnings
    """
    
    if verbose:
        print("Adding marginal page-number and overlap annotations...")
    pagenumbers_color = pncol
    reader = PdfReader(inputfile)
    writer = PdfWriter()
    number_pages = len(reader.pages)
    pages = reader.pages
    if pagespec[0] == '':
        pagespec[0] = '1'
    pagespec[0] = int(pagespec[0]) - 1
    if pagespec[1] == '':
        pagespec[1] = str(number_pages)
    pagespec[1] = int(pagespec[1])
    pagerange = range(pagespec[0], pagespec[1])                           
    bb = pages[0].cropbox  ## assumed same for all pages
    page_width = bb[2]
    page_height = bb[3]
    half_height = bb[3] / 2
    crop_left = cl
    ## No cropping is done on the right margin!
    cropped_width = page_width - crop_left
    half_overlap = mo / 2
    aspect_ratio = ar
    ## Determine the top-and-bottom cropping needed to get the required aspect ratio:
    crop_tb = half_height + half_overlap - (cropped_width / aspect_ratio)
    ## If less than zero vertical cropping is needed, increase the overlap:
    if crop_tb < 0:
        half_overlap = half_overlap - crop_tb
        crop_tb = 0
    for i in range(len(pagerange)):
        pn = pagerange[i]
        pagenumber_text = " " + str(int(1 + pn)) + "/" + str(number_pages)
        page = pages[pn]
        writer.add_page(page)
        annotation_width = 42
        if number_pages >= 100:
            annotation_width = 56
        annotation_top = FreeText(
            text = pagenumber_text,
            rect = (page_width - annotation_width + 1, page_height - crop_tb - 43,
                    page_width + 1, page_height - crop_tb - 25),
            border_color = pagenumbers_color,
            background_color = "ffffff"
        )
        annotation_top.flags = 4
        writer.add_annotation(page_number = i, annotation = annotation_top)
        annotation_bottom = FreeText(
            text = pagenumber_text,
            rect=(page_width - annotation_width, crop_tb + 22,
                  page_width + 1, crop_tb + 3),
            border_color = "ffffff",
            background_color = pagenumbers_color
        )
        annotation_bottom.flags = 4
        writer.add_annotation(page_number = i, annotation = annotation_bottom)
        annotation_overlap = Line(
            p1 = (page_width - 3, half_height + half_overlap),
            p2 = (page_width - 3, half_height - half_overlap),
            rect = (page_width - 3, half_height + half_overlap,
                    page_width - 3, half_height - half_overlap)
        )
        annotation_overlap.flags = 4
        writer.add_annotation(page_number = i, annotation = annotation_overlap)
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
    subprocess.call(['gs'] + ghostscript_options +
                    ['-sOutputFile=' + temp2.name, temp1.name])
    if verbose:
        print("...DONE")

    ## Next we split each page into top and bottom halves, with the required overlap: 
    if verbose:
        print("Splitting the pages...")
    reader_top = PdfReader(temp2.name)
    reader_bottom = PdfReader(temp2.name)
    writer2 = PdfWriter()
    for i in range(len(pagerange)):
        page_top = reader_top.pages[i]
        page_bottom = reader_bottom.pages[i]
        page_top.cropbox = pdf.generic.RectangleObject([crop_left,
                                                        half_height - half_overlap,
                                                        page_width,
                                                        page_height - crop_tb])
        writer2.add_page(page_top)
        page_bottom.cropbox = pdf.generic.RectangleObject([crop_left,
                                                           crop_tb,
                                                           page_width,
                                                           half_height + half_overlap])
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
                "Splits all pages of a PDF file for viewing on landscape screens.  " +
                "Output is to a new file: the input PDF file is left unchanged.")
    parser.add_argument("inputfile", type = str, help = "path to the input PDF file")
    parser.add_argument("-p", "--pagespec", type = str,
                        help = "a page range such as '2-5' or '2-' or '-5' (default: '1-')",
                        default = "1-")
    parser.add_argument("--ar", type = float,
                        help = "the aspect ratio (width/height) of the resulting " +
                               "PDF pages (default: 1.34)",
                        default = 1.34)
    parser.add_argument("--cl", type = float,
                        help = "the amount (in pt) to crop from the left margin of " +
                               "each page (default: 35)",
                        default = 35)
    parser.add_argument("--mo", type = float,
                        help = "the minimum required overlap (pt) between top and bottom " +
                               "parts of pages (default: 40)",
                        default = 40)
    parser.add_argument("--pncol", type = str,
                        help = "a 6-digit hexadecimal colour for the marginal " +
                        "page numbering (default: '006600')",
                        default = "006600")
    parser.add_argument("-v", "--verbose", action = 'store_true',
                        help = "provide brief commentary")
    parser.add_argument("-d", "--debug", action = 'store_true',
                        help = "keep temporary files and show their names; " + 
                               "and also show Ghostscript errors and warnings " + 
                               "in addition to brief commentary")
    args = parser.parse_args()
    verbose = args.verbose
    debug = args.debug
    if debug:
        verbose = True
    if verbose:
        print("--- This is pdftoast.py version " + str(version) + " ---")
    if which('gs') is None:
        print("Aborting, because Ghostscript is not available in your path.  " +
              "No output file written.")
        os._exit(1)
    pagespec = args.pagespec.split("-")
    if (len(pagespec) == 1) & pagespec[0].isdigit():
        possibly_meant = str(pagespec[0]) + "-" + str(pagespec[0])
        print("Invalid page range specified: did you mean -p " + possibly_meant +
              " (or equivalently --pp " + possibly_meant + ")?")
        os._exit(1)
    if len(pagespec) != 2:
        print("Invalid page range specification: aborting with no output file written.")
        os._exit(1)
    outputfile = number_and_split_pages(inputfile = os.path.abspath(args.inputfile),
                                        pagespec = pagespec,
                                        ar = args.ar,
                                        cl = args.cl,
                                        mo = args.mo,
                                        pncol = args.pncol,
                                        verbose = verbose,
                                        debug = debug)
    return(outputfile)
    

if __name__ == "__main__":
    main()        

