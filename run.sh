#!/bin/bash

IFS=',' read -r -a line <<< "$1"
#ImageID,Subset,OriginalURL,OriginalLandingURL,License,AuthorProfileURL,Author,Title,OriginalSize,OriginalMD5,Thumbnail300KURL
url=${line[2]}
#echo "$url"
if echo "$url" | grep -q ".jpg";
then
    #echo "$1" 
    IFS='/' read -r -a filename <<< "$url"
    if ! grep -Fq "${filename[-1]}" openimg.txt;
    then 
        echo "${filename[-1]}"
        wget -O /openimg/2017_07/train/images/"${filename[-1]}" "$url"
        #echo "${line[-1]}" >> imlist_done.txt
    fi
fi
