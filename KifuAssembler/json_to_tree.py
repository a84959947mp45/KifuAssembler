# Assemble kifus inside a json files to a sgf tree
import argparse
import os
import tqdm
import numpy as np
from KifuAssembler.src.extractor import Extractor
from KifuAssembler.src.assembler import Assembler, dump_to
from KifuAssembler.src.utils import KifuParser

parser = argparse.ArgumentParser(description="Assemble kifus to a kifu tree.")

parser.add_argument('json_src',
    type=str,
    help="The source 'json' path to extract kifu from."
)

parser.add_argument('output_file',
    type=str,
    help="The location to output the assembled tree.",
    default="results/result.sgf"
)

parser.add_argument('-s', '--enable_symmetrical_assembling',
    action='store_true',
    help="View symmetrical sgfs as the same."
)

parser.add_argument('-l', '--lower_bound',
    type=int,
    default=5,
    help="Ignore moves which has length smaller than this flag."
)

parser.add_argument('--use_editor_style',
    action='store_true',
    help="Use connect6 rule when dumping tree. (I.e., (W0, W1) and (W1, W0) are considered interchangeable.)"
)

parser.add_argument('-f','--use_filter',
    action='store_true',
    help="fiter 5x5 zone.)"
)

parser.add_argument('--num_of_openings',
    type=int,
    default=0,
    help="Get common openings from the assembled tree and dump them to 'openings.txt'"
)

nearPosition=[[0,1],[0,-1],[1,0],[-1,0],
              [1,1],[1,-1],[-1,1],[-1,-1],
              [0,2],[0,-2],[2, 0],[-2, 0],
              [2,2],[2,-2],[-2,2],[-2,-2],
              [2,1],[2,-1],[-2,1],[-2,-1],
              [1,2],[1,-2],[-1,2],[-1,-2]
                ]

if __name__ == '__main__':
    args = parser.parse_args()

    if not os.path.exists(args.json_src):
        print(f"Error! The json src file {args.json_src} does not exist!")
        exit(-1)

    kifus = Extractor().extract(args.json_src, "kifu")
    urls = Extractor().extract(args.json_src, "url")
    game_results = Extractor().extract(args.json_src, "game_result")

    print("Assembling to a tree...")
    assembler = Assembler(
        merge_symmetric_moves=args.enable_symmetrical_assembling,
    )

    with tqdm.tqdm(total=len(kifus)) as pbar:
        number_of_skipped_moves = 0
        count=0
        
        for kifu, url, game_results in zip(kifus, urls, game_results):
            # Use Kifuparser to parse the raw string into sequence of move
            moves = KifuParser.parse(kifu)

            board = np.zeros([15,15])
            first = True
            canPaint = False
            #if we need to filter
            if(args.use_filter):
                for step in range(len(moves)):
                    if(not first):
                        canPaint = False
                        for z in range(24):
                            goalPositionX = moves[step].i + nearPosition[z][0]
                            goalPositionY = moves[step].j + nearPosition[z][1]
                            if goalPositionX <0 or goalPositionX>11 or goalPositionY <0 or goalPositionY >11:
                                continue
                            else:
                                if board[goalPositionX][goalPositionY]!=0 :
                                    canPaint = True
                                    break
                        if(not canPaint):
                            #print("the episode droupout")
                            count+=1
                            break
                    first = False
                    board[moves[step].i][moves[step].j]=(step%2)+1
                if(not canPaint):
                   pbar.update(1)
                   continue




            if len(moves) < args.lower_bound:
                number_of_skipped_moves += 1
            else:
                assembler.assemble(moves, url, game_results)

            pbar.update(1)
        print("filter number: "+str(count))
        print(f"'{number_of_skipped_moves}' kifus are skipped because it has too few moves.\n")

    if args.num_of_openings != 0:
        with open("openings.txt", "w") as f:
            f.write(str(assembler.top_n_moves(args.num_of_openings)))

    print(f"Writing to file '{args.output_file}'...>")
    with open(args.output_file, "w") as f:
        dump_to(assembler, f, editor_style=args.use_editor_style)
