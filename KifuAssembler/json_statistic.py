# Assemble kifus inside a json files to a sgf tree
import argparse
import os
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from KifuAssembler.src.extractor import Extractor
from KifuAssembler.src.assembler import Assembler, dump_to
from KifuAssembler.src.utils import KifuParser

import gzip
import plotly.graph_objects as go
import pathlib

parser = argparse.ArgumentParser(description="Assemble kifus to a kifu tree.")

parser.add_argument('--json_src_dir',
    type=str,
    help="The source 'json' path to extract kifu from.",
    default="/home/shao/Desktop/statistic_to_1110w"
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

def game_result(board):

    # 1. 判斷橫向五子
    for x in range(8):
        for y in range(12):
            if board[x][y] == 1 and board[x + 1][y] == 1 and board[x + 2][y] == 1 and board[x + 3][y] == 1 and board[x + 4][y] == 1:
                    return 1
            if board[x][y] == 2 and board[x + 1][y] == 2 and board[x + 2][y] == 2 and board[x + 3][y] == 2 and board[x + 4][y] == 2:
                    return 2

    # 2. 判斷縱向五子
    for x in range(12):
        for y in range(8):
            if board[x][y] == 1 and board[x][y + 1] == 1 and board[x][y + 2] == 1 and board[x][y + 3] == 1 and board[x][y + 4] == 1:
                return 1
            if board[x][y] == 2 and board[x][y + 1] == 2 and board[x][y + 2] == 2 and board[x][y + 3] == 2 and board[x][y + 4] == 2:
                return 2


    # 3. 判斷是否有左上-右下的連續五子
    for x in range(8):
        for y in range(8):
            if board[x][y] == 1 and board[x + 1][y + 1] == 1 and board[x + 2][y + 2] == 1 and board[x + 3][y + 3] == 1 and board[x + 4][y + 4] == 1:
               return 1
            if board[x][y] == 2 and board[x + 1][y + 1] == 2 and board[x + 2][y + 2] == 2 and board[x + 3][y + 3] == 2 and board[x + 4][y + 4] == 2:
               return 2

    # 4. 判斷是否有右上-左下的連續五子
    for x in range(8):
        for y in range(8):
            if board[x + 4][y] == 1 and board[x + 3][y + 1] == 1 and board[x + 2][y + 2] == 1 and board[x + 1][y + 3] == 1 and board[x][y + 4] == 1:
                return 1
            if board[x + 4][y] == 2 and board[x + 3][y + 1] == 2 and board[x + 2][y + 2] == 2 and board[x + 1][y + 3] == 2 and board[x][y + 4] == 2:
                return 2

    # 5. 判斷是否為draw
    for x in range(12):
        for y in range(12):
            if board[x][y] == 0:  # 棋盘中还有剩余的格子，不能判断为平局
                return 0

    return 4 #draw

#white =1
#black =2
def caculate_count(board):
    
    count = 0
    #compute col
    for j in range(11):
        if(board[0,j]>0):
            count+=1
        if(board[11,j]>0):
            count+=1
    #count row
    for i in range(11):
        if(board[i,0]>0):
            count+=1
        if(board[j,11]>0):
            count+=1

    return count
        

if __name__ == '__main__':

    args = parser.parse_args()

    game_count=0

    mean_total_length_for_each_ten_thousand_game=[]
    mean_black_length_for_each_ten_thousand_game=[]
    mean_white_length_for_each_ten_thousand_game=[]

    total_length_for_each_game=[]
    black_length_for_each_game=[]
    white_length_for_each_game=[]

    draw_game_number = []
    edge_game_number = []
    canWin_game_number = []

    re_count =0
    
    try:
        for json in sorted(pathlib.Path(args.json_src_dir).glob("*.json")):

            print("start: "+str(json))

            json_name = str(json)
            kifus = Extractor().extract(json_name, "kifu")
            urls = Extractor().extract(json_name, "url")
            game_results = Extractor().extract(json_name, "game_result")

            filter_count=0

            #define statistic variable
            step_info = np.zeros([6])
            whole_infro= np.zeros([15,3])
            draw_number = 0
            edge_number = 0
            lost_number =0

            #every game for-loop
            for kifu, url, game_results in zip(kifus, urls, game_results):
                # Use Kifuparser to parse the raw string into sequence of move
                moves = KifuParser.parse(kifu)
                
                board = np.zeros([12,12])
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
                                filter_count+=1
                                break
                        first = False
                        board[moves[step].i][moves[step].j]=(step%2)+1
                    if(not canPaint):
                        continue
                else:
                    for step in range(len(moves)):
                        
                        for i in range(12):
                            for j in range(12):
                                if(board[i][j]==0):
                                    board_copy = np.copy(board)
                                    board_copy[i][j]=(step%2)+1
                                    result = game_result(board_copy)
                                    if(result != 0 and result != 4 and  result!= board_copy[i][j]):
                                        lost_number+=1

                        board[moves[step].i][moves[step].j]=(step%2)+1

                canWin_game_number.append(lost_number)
                lost_number=0

                #start statistic
                step_info[0]+=len(moves)  #total step len
                step_info[3]+=1 #total step number
                #1.step statistic
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

                    total_length_for_each_game.append(episode_len)
                    
                    if(game_results == "BWin"):
                        whole_infro[classification,1]+=1  # black step number
                        black_length_for_each_game.append(episode_len)
                    else:
                        whole_infro[classification,2]+=1  # white step number
                        white_length_for_each_game.append(episode_len)

                else:
                    draw_number +=1

                #3 caculate edge number
                    edge_number += caculate_count(board)
                
                game_count+=1

                
                #caculate relation between number and interval
                if(game_count%500000==0):
                    #print(np.round(weird_division(whole_infro[:,0],step_info[3])*100))
                    whole_infro= np.zeros([15,3])

                    layout = go.Layout(barmode='overlay',
                    title='Analyze 12x12 GOMOKU',
                    xaxis=dict(title='step'),
                    yaxis=dict(title='Count'))
                    fig = go.Figure(layout=layout)
                    fig.add_trace(go.Histogram(x=total_length_for_each_game[-500000:], marker={'color': '#666666'}))
                    fig.write_html(f"game_length_histogram_{len(total_length_for_each_game) - 500000}-{len(total_length_for_each_game)}.html")

                #caculate number variation
                if(game_count%100000==0):

                    #print("mean step number: "+str(weird_division(step_info[0],step_info[3]))+" unit")
                    #print("mean black step number: "+str(weird_division(step_info[1],step_info[4]))+" unit")
                    #print("mean while step number: "+str(weird_division(step_info[2],step_info[5]))+" unit")
                    #print(np.round(weird_division(whole_infro[:,0],step_info[3])*100))

                    mean_total_length_for_each_ten_thousand_game.append(weird_division(step_info[0],step_info[3]))
                    mean_black_length_for_each_ten_thousand_game.append(weird_division(step_info[1],step_info[4]))
                    mean_white_length_for_each_ten_thousand_game.append(weird_division(step_info[2],step_info[5]))

                    draw_game_number.append(np.round(weird_division(draw_number,step_info[3])*100))
                    edge_game_number.append(np.round(weird_division(edge_number,step_info[3])))
                    draw_number =0
                    edge_number =0
                    #define statistic variable
                    step_info = np.zeros([6])
                   # re_count+=1

           # if(re_count==2):
           #     break



        #print(mean_total_length_for_each_ten_thousand_game)
        #print(mean_black_length_for_each_ten_thousand_game)
        #print(mean_white_length_for_each_ten_thousand_game)
        x = np.linspace(1,len(draw_game_number),len(draw_game_number))
        plt.plot(x,np.array(draw_game_number),label="draw_game_number")
        plt.legend(loc='upper right')
        plt.show()

        x = np.linspace(1,len(edge_game_number),len(edge_game_number))
        plt.plot(x,np.array(edge_game_number),label="edge_game_number")
        plt.legend(loc='upper right')
        plt.show()

        x = np.linspace(1,len(mean_total_length_for_each_ten_thousand_game),len(mean_total_length_for_each_ten_thousand_game))
        plt.plot(x,np.array(mean_total_length_for_each_ten_thousand_game),label="total_mean")
        plt.plot(x,np.array(mean_black_length_for_each_ten_thousand_game),label="black_mean")
        plt.plot(x,np.array(mean_white_length_for_each_ten_thousand_game),label="white_mean")
        plt.legend(loc='upper right')
        plt.show()
    
    finally:
        np.save('canWin_game_number', np.array(canWin_game_number))

    # np.save('mean_total_length_for_each_ten_thousand_game', np.array(mean_total_length_for_each_ten_thousand_game))
    # np.save('mean_black_length_for_each_ten_thousand_game', np.array(mean_black_length_for_each_ten_thousand_game))
    # np.save('mean_white_length_for_each_ten_thousand_game', np.array(mean_white_length_for_each_ten_thousand_game))
    # np.save('total_length_for_each_game', np.array(total_length_for_each_game))
    # np.save('draw_game_number', np.array(draw_game_number))
    



