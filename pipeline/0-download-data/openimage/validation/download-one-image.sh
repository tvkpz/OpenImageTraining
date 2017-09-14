#!/bin/bash

OUTPUT_FOLDER=$2
LOG_FOLDER=$2

IFS=',' read -r -a line <<< "$1"
#ImageID,Subset,OriginalURL,OriginalLandingURL,License,AuthorProfileURL,Author,Title,OriginalSize,OriginalMD5,Thumbnail300KURL
URL=${line[2]}

IFS='/' read -r -a filename <<< "$URL"
filename=${filename[-1]}

echo URL       : $URL
echo File name : $filename

if echo $filename | grep -q ".jpg";
then
    if [ ! -e $OUTPUT_FOLDER/$filename ]; then
        {
            wget --no-check-certificate --quiet --tries 3 --max-redirect 0 $URL -O $OUTPUT_FOLDER/$filename
            echo "Downloaded successfully."
        } || {
            echo Can not download $filename
            echo $URL >> $LOG_FOLDER/download_image_errors_url.txt
        }
    else
        echo "Already existed, skip."
    fi
fi