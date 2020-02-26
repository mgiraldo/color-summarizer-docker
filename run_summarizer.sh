#!/bin/bash
COUNT=0
STARTTIME=$(date +%s)
while IFS=, read -r file_key master_pid access_pid
do
  IMAGE=("/usr/src/app/files/${file_key//\"/}")
  FILE=("/usr/src/app/files/colors_output/${access_pid//\"/}.json")
  if [ $file_key != file_key ] && [ -f $IMAGE ] && [ ! -f $FILE ] && [ ! -z "$access_pid" ]
  then
    ruby summarize_file.rb -i ${IMAGE} -d ${FILE}
  fi
  let COUNT=COUNT+1
done < /usr/src/app/files/files-urls.csv
ENDTIME=$(date +%s)
echo "Processed ${COUNT} files in $(($ENDTIME - $STARTTIME)) seconds."
