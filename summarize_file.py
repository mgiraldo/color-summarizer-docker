import argparse
import uuid
import subprocess
import xmltodict
import os
import json

parser = argparse.ArgumentParser()

parser.add_argument("image", type=str, help="Path to image to summarize")
parser.add_argument("destination", type=str, help="Path to destination JSON file")

args = parser.parse_args()

image = args.image
destination = args.destination

size=50
clusters=5
uuid_str = str(uuid.uuid4())
final_file_name = "./%s.png" % uuid_str
folder = "./colorsummarizer-0.77"

if (os.path.exists(image) == False):
  print("Image %s does not exist." % image)
  exit()

if (os.path.exists(os.path.dirname(destination)) == False):
  print("Folder %s does not exist." % os.path.dirname(destination))
  exit()

subprocess.run(["convert", image, "-profile", "./profiles/ColorMatchRGB.icc", "-resize", ("%sx" % size), ("PNG24:%s" % final_file_name)])

cmd = ["perl", "-X", "%s/bin/colorsummarizer" % folder, "-conf", "summarizer.conf", "-clip", "transparent", "-image", final_file_name, "-width", str(size), "-xml", "-stats", "-histogram", "-clusters", str(clusters)]
process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, universal_newlines=True)
output = process.stdout

json_str = json.dumps(xmltodict.parse(output))

os.remove(final_file_name)

file = open(destination,"w") 
file.write(json_str)
file.close() 
