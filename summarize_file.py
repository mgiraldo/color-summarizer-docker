#!/usr/bin/env python
import argparse
import os
from image_utils import summary

parser = argparse.ArgumentParser()

parser.add_argument("image", type=str, help="Path to image to summarize")
parser.add_argument("destination", type=str, help="Path to destination JSON file")
parser.add_argument('-n', '--no_convert', action='store_false', help='skip converting step (add if not providing grayscale images)')
parser.add_argument('-s', '--silent', action='store_true')

args = parser.parse_args()

image = args.image
silent = args.silent
destination = args.destination
no_convert = args.no_convert

if (not os.path.exists(image)):
  if (not silent):
    print("Image %s does not exist." % image)
  exit()

if (not os.path.exists(os.path.dirname(destination))):
  if (not silent):
    print("Folder does not exist.")
  exit()

json_str = summary.summarize(image, convert=no_convert, silent=silent)

file = open(destination,"w") 
file.write(json_str)
file.close() 
