#!/bin/bash

poetry shell
python -m KifuAssembler.dir_to_json dataInput/955w_1600 dataInput/
python -m KifuAssembler.json_to_tree dataInput/result.json dataInput/result.sgf -s -f
todos dataInput/result.sgf
mv dataInput/result.sgf dataInput/955w_1600.sgf
mv dataInput/result.json dataInput/955w_1600.json


