#!/bin/bash

# arg1 = $1 = output/markdown/filename
# arg2 = $2 = dir/of/input/graphs/grap1.pn

echo "" > $1
for file in $(ls $2/*.png | sort); do
  echo "![$file]($file)" >> $1
done