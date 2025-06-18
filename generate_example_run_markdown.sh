#!/bin/bash

# This file will generate a markdown page with all the png files from a comparitive test run.

# arg1 = $1 = output/markdown/filename.md
# arg2 = $2 = dir/of/input/graphs/

echo "" > $1
for file in $(ls $2/*.png | sort); do
  echo "![$file]($file)" >> $1
done