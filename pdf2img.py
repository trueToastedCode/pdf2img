import sys
import os
import re
from typing import Iterable
from PIL import Image
import pymupdf


def page_to_img(page: pymupdf.Page, dpi: int = 300) -> Image.Image:
    """
    Converts a single PDF page to an image.

    Parameters:
    - page (pymupdf.Page): The PDF page object to convert.
    - dpi (int): The resolution in dots per inch (DPI) for the output image. Default is 300.

    Returns:
    - Image.Image: The converted page as a PIL Image object.
    """
    pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72))  # Convert the page to a pixmap at the desired DPI.
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)  # Create an image from the pixmap's raw data.


def doc_to_imgs(doc: pymupdf.Document) -> list[Image.Image]:
    """
    Converts a PDF document to a list of images, with each image representing a page.

    Parameters:
    - doc (pymupdf.Document): The PDF document object.

    Returns:
    - list[Image.Image]: A list of PIL Image objects for each page of the document.
    """
    return list(map(page_to_img, doc))  # Apply the page_to_img function to each page of the document.


def combine_imgs(imgs: Iterable[Image.Image], padding: int = 55) -> Image.Image:
    """
    Combines multiple images vertically into one image with optional padding between them.

    Parameters:
    - imgs (Iterable[Image.Image]): An iterable of PIL Image objects to combine.
    - padding (int): The amount of vertical space (in pixels) between the images. Default is 55.

    Returns:
    - Image.Image: A single combined image containing all input images.
    """
    combined_width = max(img.width for img in imgs)  # The combined image width is the maximum width of all images.
    combined_height = sum(img.height for img in imgs) + (len(imgs) - 1) * padding  # Sum heights with padding.
    combined_img = Image.new(
        'RGBA',
        (combined_width, combined_height)
    )  # Create a new blank image for the combined result.

    y_offset = 0
    for img in imgs:
        combined_img.paste(img, (0, y_offset))  # Paste each image into the combined image at the appropriate offset.
        y_offset += img.height + padding  # Update the vertical offset for the next image.

    return combined_img  # Return the combined image.


if __name__ == '__main__':
    """
    Main execution block. Reads command-line arguments to process a PDF document, extract its pages as images,
    optionally combine the images, and save the result.

    Command-line Arguments:
    - (Optional) Range of pages (start:stop) to process.
    - Path to the PDF document if no range is provided.
    - (Optional) Path to save the resulting image. If not provided, the result is saved in the same 
      directory as the PDF with a .png extension.

    Behavior:
    - If a range (start:stop) is provided as the first argument, it processes only those pages.
    - If only a PDF path is provided, it processes the entire document.
    - The result is saved as a PNG file.
    """
    if len(sys.argv) == 1:
        exit(1)  # Exit if no arguments are provided.

    is_first_arg_range = bool(re.match(r'^\d*:\d*$', sys.argv[1]))  # Check if the first argument is a range.

    if is_first_arg_range and len(sys.argv) == 2:
        exit(1)  # Exit if only the range is provided without a document path.

    # Extract start and stop page numbers from the range.
    i = sys.argv[1].find(':')
    try:
        start = int(sys.argv[1][:i])
    except ValueError:
        start = None  # If no start page is provided, set it to None.

    try:
        stop = int(sys.argv[1][i + 1:])
    except ValueError:
        stop = None  # If no stop page is provided, set it to None.

    # Open the PDF document.
    doc = pymupdf.open(sys.argv[1 + int(is_first_arg_range)])

    # Convert the specified range of pages (or all pages) to images.
    imgs = doc_to_imgs(doc[start:stop])

    # Combine the images vertically with padding.
    combined_img = combine_imgs(imgs)

    # Save the combined image to the specified output path or default to the input PDF's base name.
    combined_img.save(
        sys.argv[2 + int(is_first_arg_range)] if len(sys.argv) > 2 + int(is_first_arg_range)
        else f'{os.path.splitext(sys.argv[1 + int(is_first_arg_range)])[0]}.png'
    )
