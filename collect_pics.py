#!/usr/bin/env python
#
# collect_pics.py creates an image concatenating all of the images in a directory for each directory given.
#
# Copyright K. Scarbro; 2025--

"""
    Takes as input a list of directories with .png files in them. Outputs a .png file in each input directory. The output .png file is
    an image of all of the images in each input directory, grouped in a grid.

Syntax:
    collect_pics.py directory [...]    
    - directory: the directory (or directories) containing the .png files

Output:
    A group_image.png file in each directory. The group_image.png file will be a single image containing all of the images in the directory
    grouped in a grid format.

Examples:
    collect_pics.py directory
    collect_pics.py run****

K. Scarbro 02.2025
"""

try:
    import sys, os
    import PIL.Image
    import math
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit(1)

#---------------------------------------------------
def collect_images(path, padding = 10):
    """
    grab all images in the directory and group them into one image
    """
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.png')]
    images = [PIL.Image.open(image_path) for image_path in image_paths]
    widths, heights = zip(*(image.size for image in images))
    
    total_width = 2 * max(widths) + padding
    # the total height is the sum of every other image (since we're pasting two in a row at a time)
    total_height = sum(heights[::2]) + padding * (len(images[::2]) - 1)
    output_image = PIL.Image.new('RGB', (total_width, total_height), color = 'white')
    y_offset = 0
    x_offset = 0
    for image in images:
        output_image.paste(image, (x_offset, y_offset))
        if x_offset == 0:
            x_offset += image.width + padding
        else:
            x_offset = 0
            y_offset += image.height + padding 
    
    output_image.save(path + '/group_image.png')

def main(args):
    """
    read command line arguments and process commands
    """
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        else:
            sys.stdout.write(f"Warning: unexpected argument {arg}\n")
            sys.exit()

    for p in paths:
        collect_images(p)

    return 0


#----------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
