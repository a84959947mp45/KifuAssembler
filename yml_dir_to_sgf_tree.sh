#!/bin/bash

poetry shell
python -m KifuAssembler.yml_to_json -d -i --input_dir dataInput/96x10_before_1033_1w   --output_file dataInput/96x10_before_1033_1w.json
python -m KifuAssembler.json_to_tree -s -f dataInput/96x10_before_1033_1w.json dataInput/96x10_before_1033_1w.sgf
todos dataInput/96x10_before_1033_1w.sgf
