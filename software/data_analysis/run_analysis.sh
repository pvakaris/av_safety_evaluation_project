#!/bin/bash

name=$1


if [ -z "$name" ]; then
    echo "If you want to run data analysis, the name for the analysis has to be specified."
    echo "Example use: ./run_analysis.sh name"
    exit 1
fi

cd ../../data/analysed_data/data/

if [ -d "$name" ]; then
  echo "Directory $name already exists. Please choose another name. Aborting."
  exit 1
fi

mkdir $name
mkdir ./$name/points

cd ../../../software/data_analysis
python analysis.py -s $name