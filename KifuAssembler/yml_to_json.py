import numpy as np
import json
import os
import argparse
import yaml
import pathlib

parser = argparse.ArgumentParser(description="transfer a kifu yml to a kifu json.")

parser.add_argument('--json_src',
    type=str,
    help="The source 'json' path to extract kifu from.",
    default="KifuAssembler/shao/1592212293837151_statistic.yml"
)

parser.add_argument('--output_file',
    type=str,
    help="The location to output the assembled tree.",
    default="data.json"
)
parser.add_argument('--input_dir',
    type=str,
    help="The location to output the assembled tree.",
    default="demo"
)

parser.add_argument('-d', '--enable_use_multiple_yml',
    action='store_true',
    help="transfer multiple yml to json"
)
parser.add_argument('-i', '--individual',
    action='store_true',
    help="transfer individual"
)



relectRow = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h",8:"i",9:"j",10:"k",11:"l",12:"m",13:"n",14:"o",15:"q"}
nearPosition=[[0,1],[0,-1],[1,0],[-1,0],
              [1,1],[1,-1],[-1,1],[-1,-1],
              [0,2],[0,-2],[2, 0],[-2, 0],
              [2,2],[2,-2],[-2,2],[-2,-2],
              [2,1],[2,-1],[-2,1],[-2,-1],
              [1,2],[1,-2],[-1,2],[-1,-2]
                ]


def handle_yml_to_json_format(data,storeData):

 
    #100 training game
    count=0
    for i in range(len(data["BatchOfPositions"])):

        kifu="("
        reStore ={}
        last=""

        board = np.zeros([15,15])
        first    = True
        canPaint = False
        #every game positions 
        for j in range (len(data["BatchOfPositions"][i])):

            nowPosiiton=";"
            rowPoint = 0
            colPoint = 0
            goalPositionX = 0
            goalPositionY = 0
            
            if j%2==0:
               nowPosiiton+="B"
               last="BWin"
            else :
               nowPosiiton+="W"
               last="WWin"

            rowPoint = int(data["BatchOfPositions"][i][j]/12)
            colPoint = int(data["BatchOfPositions"][i][j]%12)
            
            board[rowPoint][colPoint]=(j%2)+1

            row = relectRow[rowPoint]
            col = str(colPoint+1)
            nowPosiiton+=("["+row)    
            nowPosiiton+=(col +"]")
            kifu+=nowPosiiton
        '''
        if(not canPaint):
            continue
        '''
        kifu+=")"
        reStore["kifu"]=kifu
        if len(data["BatchOfPositions"][i]) == 144:
         #   print("DRAW")
            reStore["game_result"]="Draw"
        else:
            reStore["game_result"]=last
        
        reStore["url"]="."
        
        storeData.append(reStore)
   # print("total drouput number: "+str(count))

    return storeData

if __name__ == '__main__':
    args = parser.parse_args()
    data = "null"

    print("start read .yml")
    
    output_data = []
    use_multi = False
    use_multi = args.enable_use_multiple_yml
    if(not use_multi):
        print("load singal files")
        with open(args.json_src, "r") as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)
        
        output_data = handle_yml_to_json_format(data,output_data)

    else :
        print("load multi-yml files")
        for yml in pathlib.Path(args.input_dir).glob("*.yml"):
            print(yml)
            with yml.open('r') as f:
                data = yaml.load(f, Loader=yaml.CLoader)
        
            output_data = handle_yml_to_json_format(data,output_data)
            if(args.individual):
                fileName = str(yml)[0:-4]+".json"
                print(fileName)
                with open(fileName, 'w') as outfile:
                    json.dump(output_data, outfile, indent=2)
                output_data = []
        
    if(not args.individual):
        with open(args.output_file, 'w') as outfile:
            json.dump(output_data, outfile, indent=2)

    print("success to produce .json")  


