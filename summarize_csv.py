#!/usr/bin/env python
import time
import pandas as pd
import subprocess
import multiprocessing
import tqdm
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", default="/usr/src/app/files/files-urls.csv", type=str, help="path to CSV file (default: /usr/src/app/files/files-urls.csv)")
parser.add_argument("-o", "--origin_folder", default="/usr/src/app/files", type=str, help="Folder where images are located (default: /usr/src/app/files)")
parser.add_argument("-d", "--destination", default="/usr/src/app/files/colors_output", type=str, help="Folder where to save results (default: /usr/src/app/files/colors_output)")
parser.add_argument('--overwrite', action='store_true', help='Overwrite existing json if it exists')
parser.add_argument("-p", "--processes", default=None, type=int, help="How many processes (default: None which lets Python decide)")

args = parser.parse_args()

cpu = args.processes
file = args.file
origin_folder = args.origin_folder
destination = args.destination
overwrite = args.overwrite

count=0
starttime = time.time()

if (not os.path.exists(file)):
  print("File %s does not exist." % file)
  exit()

if (not os.path.exists(origin_folder)):
  print("Folder %s does not exist." % origin_folder)
  exit()

if (not os.path.exists(destination)):
  print("Folder %s does not exist." % destination)
  exit()

url_df = pd.read_csv(file, index_col="access_pid")

count = len(url_df.filename)

skipped = []

print("Summarizing %s files with %s processes" % (count, (multiprocessing.cpu_count() if cpu is None else cpu)))

def summarize_row(access_pid, row):
  try:
    filename = row["filename"]
    image = "%s/%s/%s" % (origin_folder, filename[0:4], filename)
    json = "%s/%s.json" % (destination, access_pid)
    if (Path(json).exists() is False or overwrite):
      subprocess.run(["python", "summarize_file.py", "-s", image, json])
  except:
    skipped.append(row)
    pass

with multiprocessing.Pool(processes=cpu) as pool:
  for access_pid, row in tqdm.tqdm(url_df.iterrows(), total=count):
    pool.apply(summarize_row, args=(access_pid, row))
  pool.close()
  pool.join()

print("Processed %s files in {} seconds".format(time.time() - starttime) % count)

if (len(skipped) > 0):
  print("Skipped %s files:", len(skipped))
  print(skipped)