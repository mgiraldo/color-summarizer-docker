import time
import pandas as pd
import subprocess
import multiprocessing
import tqdm
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", default="/usr/src/app/files/files-urls.csv", type=str, help="path to CSV file")
parser.add_argument("-o", "--origin_folder", default="/usr/src/app/files", type=str, help="Folder where images are located")
parser.add_argument("-d", "--destination", default="/usr/src/app/files/colors_output", type=str, help="Folder where images are located")
parser.add_argument("-p", "--processes", default=None, type=int, help="how many processes (default: None which lets Python decide)")

args = parser.parse_args()

cpu = args.processes
file = args.file
origin_folder = args.origin_folder
destination = args.destination

count=0
starttime = time.time()

if (os.path.exists(file) == False):
  print("File %s does not exist." % file)
  exit()

if (os.path.exists(origin_folder) == False):
  print("Folder %s does not exist." % origin_folder)
  exit()

if (os.path.exists(destination) == False):
  print("Folder %s does not exist." % destination)
  exit()

url_df = pd.read_csv(file, index_col="access_pid")

count = len(url_df.file_key)

skipped = []

print("Summarizing %s files with %s processes" % (count, (multiprocessing.cpu_count() if cpu == None else cpu)))

def summarize_row(access_pid, row):
  try:
    file_key = row["file_key"].replace("\"","")
    access_pid = access_pid.replace("\"","")
    image = "%s/%s" % (origin_folder, file_key)
    json = "%s/%s.json" % (destination, access_pid)
    if (Path(json).exists() == False):
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