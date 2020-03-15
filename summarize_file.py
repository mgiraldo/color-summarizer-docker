#!/usr/bin/env python
import argparse
import uuid
import subprocess
import xmltodict
import os
import json

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

size=50
clusters=5
uuid_str = str(uuid.uuid4())
final_file_name = "./%s.png" % uuid_str
folder = "./colorsummarizer-0.77"

if (not os.path.exists(image)):
  if (not silent):
    print("Image %s does not exist." % image)
  exit()

if (not os.path.exists(os.path.dirname(destination))):
  if (not silent):
    print("Folder does not exist.")
  exit()

if (no_convert):
  subprocess.run(["convert", image, "-profile", "./profiles/ColorMatchRGB.icc", "-resize", ("%sx" % size), ("PNG24:%s" % final_file_name)])
else:
  final_file_name = image

cmd = ["perl", "-X", "%s/bin/colorsummarizer" % folder, "-conf", "summarizer.conf", "-clip", "transparent", "-image", final_file_name, "-width", str(size), "-xml", "-stats", "-histogram", "-clusters", str(clusters)]
process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, universal_newlines=True)
output = process.stdout

json_str = json.dumps(xmltodict.parse(output))

if (no_convert):
  os.remove(final_file_name)

file = open(destination,"w") 
file.write(json_str)
file.close() 
