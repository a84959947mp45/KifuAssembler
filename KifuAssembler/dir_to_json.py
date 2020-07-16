# Helper script to grab multiple sgf files inside a directory and put them into a single json file.
# (so it can be "assembled" into a merged sgf)

# Note that the game outcome is determined by the filename if czf flag is set.
# I.e., If the filename ends with BlackWin, the generated json will mark it BWin.
#       If the filename ends with WhiteWin, the generated json will mark it WWin.

import pathlib
import argparse
import json
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("input_directory", help="The directory that stores sgf files.")
parser.add_argument("output_directory", help="The output directory that stores the json file.")
parser.add_argument("--czf", action='store_true', help="Input sgf files are generate by nctu6_compete")
parser.add_argument("--name", default="result.json", help="The json output.")

if __name__ == '__main__':
    args = parser.parse_args()
    if not pathlib.Path(args.input_directory).exists():
        print("The input directory does not exists!")

    result = []
    for sgf in pathlib.Path(args.input_directory).glob("*.sgf"):
        with sgf.open('r') as f:
            if args.czf:
                text = sgf.read_text()
                
                if sgf.stem[-8::] == "BlackWin":
                    result.append({"kifu": text, "url": "", "game_result": "BWin"})
                elif sgf.stem[-8::] == "WhiteWin":
                    result.append({"kifu": text, "url": "", "game_result": "WWin"})
                elif sgf.stem[-4::] == "Draw":
                    result.append({"kifu": text, "url": "", "game_result": "Draw"})
            else:

                infro =np.array( sgf.read_text().split(';') )
                win_side =infro[:][-1][0]
                if(len(sgf.read_text())>9400):
                    result.append({"kifu": sgf.read_text(), "url": "", "game_result": "Draw"})
                elif(win_side=='W'):
                    result.append({"kifu": sgf.read_text(), "url": "", "game_result": "WWin"})
                elif(win_side=='B'):
                    result.append({"kifu": sgf.read_text(), "url": "", "game_result": "BWin"})
 

    with (pathlib.Path(args.output_directory) / args.name).open("w") as json_file:
        json.dump(result, json_file, indent=4)
