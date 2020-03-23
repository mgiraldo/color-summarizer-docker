#!/usr/bin/env python
import uuid
import subprocess
import xmltodict
import os
import json

SUMMARIZER_FOLDER = "./colorsummarizer-0.77"

def summarize(image_path, convert=True, silent=False):
  """
  Takes an image file path (no urls for now) and returns a JSON with the full summary
  """
  size=50
  clusters=5
  uuid_str = str(uuid.uuid4())
  final_file_name = "./%s.png" % uuid_str
  folder = SUMMARIZER_FOLDER

  if (not os.path.exists(image_path)):
    if (not silent):
      print("Image %s does not exist." % image_path)
    exit()

  if (convert):
    if (not silent):
      print("Converting...")
    subprocess.run(["convert", image_path, "-profile", "./profiles/ColorMatchRGB.icc", "-resize", ("%sx" % size), ("PNG24:%s" % final_file_name)])
  else:
    final_file_name = image_path

  cmd = ["perl", "-X", "%s/bin/colorsummarizer" % folder, "-conf", "summarizer.conf", "-clip", "transparent", "-image", final_file_name, "-width", str(size), "-xml", "-stats", "-histogram", "-clusters", str(clusters)]
  process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, universal_newlines=True)
  output = process.stdout

  json_str = json.dumps(xmltodict.parse(output))

  if (convert):
    os.remove(final_file_name)

  return json_str
