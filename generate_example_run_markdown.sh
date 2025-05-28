#!/bin/bash

for file in $(ls example_run | sort); do
  echo "![$file](example_run/$file)" >> example_run.md
done