#!/bin/bash

# ---------------------------------------------------------------------------- #
# Kattmann, 02.07.2019
# This script combines a number of .su2 meshes given over the command line.
# ---------------------------------------------------------------------------- #

display_usage() {
  echo "usage: combine -f <mesh1.su2> -f <mesh2.su2> -f ... -o <output filename> -d <dimension 2|3>"
  exit 0
}

# If no argument is given, display help
if [ $# == 0 ]; then
  display_usage; exit 0
fi

# ---------------------------------------------------------------------------- #

# Read in files via command line
while getopts hf:o:d: option; do
  case $option
  in
    h) display_usage;;
    f) FILES+=(${OPTARG});;
    o) OUTPUT=${OPTARG};;
    d) DIMENSION=${OPTARG};;
    \?) echo "Wrong usage."; display_usage
        exit 1;;
  esac
done

# ---------------------------------------------------------------------------- #
# Error checks for the input 

# min 2 FILES required which have to exist
if [ ${#FILES[@]} -le 1 ]; then
  echo "Provide at least 2 input files."; display_usage; exit 1
else
  for i in `seq 1 ${#FILES[@]}`; do
    if [ ! -e ${FILES[$i-1]} ]; then
      echo "Input file '${FILES[$i-1]}' does not exists."; display_usage; exit 1
    fi
  done
fi

# OUTPUT mustn't exists in the directory but has to prescribed
if [ -z $OUTPUT ]; then
  echo "Prescribe an outputfilename."; display_usage; exit 1
elif [ -e $OUTPUT ]; then
  echo "Output file '$OUTPUT' already exists."; display_usage; exit 1
fi

# DIMENSION has to be prescribed and be either <2|3>
if [ -z "$DIMENSION" ]; then
  echo "Dimension has to be given."; display_usage; exit 1
elif [ ! "$DIMENSION" -eq 2 ] && [ ! "$DIMENSION" -eq 3 ]; then
  echo "Dimension has to 2 or 3."; display_usage; exit 1
fi

# ---------------------------------------------------------------------------- #
touch $OUTPUT

# Write .su2 header once
echo "NDIME= $DIMENSION" >> $OUTPUT
echo -e "NZONE= ${#FILES[@]}" >> $OUTPUT

# Loop through FILES and paste them into to OUTPUT
for i in `seq 1 ${#FILES[@]}`; do
  echo -e "\nIZONE= $i\n" >> $OUTPUT
  cat ${FILES[$i-1]} >> $OUTPUT
done

# ---------------------------------------------------------------------------- #

# Get rid of all ^M characters if single-zone mesh file were written under windows.
# This is useful if file is displayed in vim under linux.
sed -i -e "s///" $OUTPUT

