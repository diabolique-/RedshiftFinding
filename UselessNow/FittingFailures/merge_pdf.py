from PyPDF2 import PdfFileMerger
import os


def merge_pdf(directory="/Users/gbbtz7/GoogleDrive/Research/Plots/", filename="ColorMagPlots.pdf", identifier="MERGE"):
    """Take pdfs with a certain identifier and merges them into one pdf. Remove the individual pdfs when done.

    :param directory: Where the plots are, and where the combined one will be stored
    """
    merger = PdfFileMerger()
    for pdf in os.listdir(directory):
        if pdf.endswith(identifier + ".pdf"):
            # Open and append the f
            opened_pdf = open(directory + pdf, "rb")
            merger.append(opened_pdf)
            # remove the files we merged into one, to remove clutter, after closing
            opened_pdf.close()
            os.remove(directory + pdf)

    # Make sure the user specified the filename to have .pdf. If not, add it
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    # Now write the combined .pdf
    merger.write(directory + filename)