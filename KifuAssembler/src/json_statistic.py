# Assemble kifus inside a json files to a sgf tree
import argparse
import os
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from KifuAssembler.src.extractor import Extractor
from KifuAssembler.src.assembler import Assembler, dump_to
from KifuAssembler.src.utils import KifuParser

parser = argparse.ArgumentParser(description="Assemble kifus to a kifu tree.")

parser.add_argument('--json_src',
    type=str,
    help="The source 'json' path to extract kifu from."
    default="dataInput/96x10_before_1033_1w.json"
)

parser.add_argument('--output_file',
    type=str,
    help="The location to output the assembled tree.",
    default="results/result.sgf"
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
        
        total_len = 0
        whole_infro= np.zero([15,2])
        if()
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
                            print(str(moves[step].i)+" "+str(moves[step].j)) 
                            count+=1
                            break
                    first = False
                    board[moves[step].i][moves[step].j]=(step%2)+1
                if(not canPaint):
                   print(moves) 
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
