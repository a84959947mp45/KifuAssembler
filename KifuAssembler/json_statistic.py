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
    help="The source 'json' path to extract kifu from.",
    default="dataInput/1033_1600.json"
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


nearPosition=[[0,1],[0,-1],[1,0],[-1,0],
              [1,1],[1,-1],[-1,1],[-1,-1],
              [0,2],[0,-2],[2, 0],[-2, 0],
              [2,2],[2,-2],[-2,2],[-2,-2],
              [2,1],[2,-1],[-2,1],[-2,-1],
              [1,2],[1,-2],[-1,2],[-1,-2]
                ]

def weird_division(n, d):
    return n / d if d else 0

if __name__ == '__main__':
    args = parser.parse_args()

    if not os.path.exists(args.json_src):
        print(f"Error! The json src file {args.json_src} does not exist!")
        exit(-1)

    kifus = Extractor().extract(args.json_src, "kifu")
    urls = Extractor().extract(args.json_src, "url")
    game_results = Extractor().extract(args.json_src, "game_result")

   
    count=0

    #define statistic variable
    step_info = np.zeros([6])
    whole_infro= np.zeros([15,3])
    draw_number =0

    #every game for-loop
    for kifu, url, game_results in zip(kifus, urls, game_results):
        # Use Kifuparser to parse the raw string into sequence of move
        moves = KifuParser.parse(kifu)
        
        board = np.zeros([15,5])
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
                        count+=1
                        break
                first = False
                board[moves[step].i][moves[step].j]=(step%2)+1
            if(not canPaint):
                pbar.update(1) 
                continue
        
        #start statistic

        #1.step statistic
        step_info[0]+=len(moves)  #total step len
        step_info[3]+=1 #total step number
        if(game_results != "Draw"):
            if(game_results == "BWin"):
                step_info[1]+=len(moves)  #total black step number
                step_info[4]+=1  #total black step number
            else:
                step_info[2]+=len(moves)  #total white step number
                step_info[5]+=1  #total white step number
        
        #2. individual statistic
        if(game_results != "Draw"):
            episode_len = len(moves)
            classification = int(episode_len/10)
            whole_infro[classification,0] += 1
            if(game_results == "BWin"):
                whole_infro[classification,1]+=1  # black step number
            else:
                whole_infro[classification,2]+=1  # white step number
        else:
            draw_number +=1
    
    print("mean step number: "+str(weird_division(step_info[0],step_info[3]))+" unit")
    print("mean black step number: "+str(weird_division(step_info[1],step_info[4]))+" unit")
    print("mean while step number: "+str(weird_division(step_info[2],step_info[5]))+" unit")
    print(np.round(weird_division(whole_infro,step_info[3])*100))




