# Assemble kifus inside a json files to a sgf tree
import argparse
import os
import tqdm
from KifuAssembler.src.extractor import Extractor
from KifuAssembler.src.assembler import Assembler, dump_to
from KifuAssembler.src.utils import KifuParser
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Assemble kifus to a kifu tree.")

parser.add_argument('--json_src',
    type=str,
    help="The source 'json' path to extract kifu from.",
    default="dataInput/96x10_before_1008_8w.json"
)

parser.add_argument('--output_file',
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

parser.add_argument('--num_of_openings',
    type=int,
    default=0,
    help="Get common openings from the assembled tree and dump them to 'openings.txt'"
)


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

    blackMean =np.array([])
    whiteMean =np.array([])
    with tqdm.tqdm(total=len(kifus)) as pbar:
        number_of_skipped_moves = 0

        count =1
        blackNumber =0
        blackLen =0
        whiteNumber =0
        whiteLen =0
        for kifu, url, game_results in zip(kifus, urls, game_results):
            
            # Use Kifuparser to parse the raw string into sequence of move
            moves = KifuParser.parse(kifu)
            move_backup = moves.copy()
            if len(moves) < args.lower_bound:
                number_of_skipped_moves += 1
            else:
                assembler.assemble(moves, url, game_results)
           # print(move_backup)
            #black win
            if((str(move_backup[0])=="B[GG]" or str(move_backup[0])=="B[GF]" or str( move_backup[0])=="B[FG]" or str(move_backup[0])=="B[FF]")and len(move_backup)!=144):
                count +=1
                if(len(move_backup)%2 == 1):
                    blackNumber+=1
                    blackLen+=len(move_backup)
                else:
                    whiteNumber+=1
                    whiteLen+=len(move_backup)

            if(count %100 ==0):
                if(blackNumber ==0):
                    blackMean = np.append(blackMean,0)
                else:
                    print(blackLen/blackNumber)
                    blackMean = np.append(blackMean,blackLen/blackNumber)
                
                if(whiteNumber ==0):
                    whiteMean = np.append(whiteMean,0)
                else:
                    whiteMean = np.append(whiteMean,whiteLen/whiteNumber)
                
                count =0
                blackNumber =0
                blackLen =0
                whiteNumber =0
                whiteLen =0
                
            pbar.update(1)
        x1 = np.linspace(1,np.size(blackMean),np.size(blackMean))
        x2 = np.linspace(1,np.size(whiteMean),np.size(whiteMean))
        plt.plot(x1,blackMean,label="black_mean")
        plt.plot(x2,whiteMean,label="white_mean")
        plt.legend(loc='upper right')
        plt.show()

        print(f"'{number_of_skipped_moves}' kifus are skipped because it has too few moves.\n")

    if args.num_of_openings != 0:
        with open("openings.txt", "w") as f:
            f.write(str(assembler.top_n_moves(args.num_of_openings)))

    print(f"Writing to file '{args.output_file}'...>")
    with open(args.output_file, "w") as f:
        dump_to(assembler, f, editor_style=args.use_editor_style)

