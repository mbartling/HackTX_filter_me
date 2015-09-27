#!/usr/bin/python 

from PIL import Image
import sys
import re

max_size = (1024,1024)

image = Image.open(sys.argv[1])
out_image = re.sub("\.", "_transformed.", sys.argv[1])

image.thumbnail(max_size, Image.ANTIALIAS)
image.save(out_image)
