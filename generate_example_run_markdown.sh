#!/bin/bash
echo "" > example_run.md
for file in $(ls example_run/*.png | sort); do
  echo "![$file]($file)" >> example_run.md
done