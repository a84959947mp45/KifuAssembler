import numpy as np
import json
import os
import argparse
import yaml

parser = argparse.ArgumentParser(description="transfer a kifu yml to a kifu json.")
'''
parser.add_argument('json_src',
    type=str,
    help="The source 'json' path to extract kifu from.",
    default="shao/1592212293837151_statistic.yml"
)

parser.add_argument('output_file',
    type=str,
    help="The location to output the assembled tree.",
    default="data.json"
)
'''
relectRow ={0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h",8:"i",9:"j",10:"k",11:"l"}

storeData = []
#print(os.listdir("KifuAssembler/shao"))

if __name__ == '__main__':
    args = parser.parse_args()
    data = "null"
    print("start read .yml")
    with open("KifuAssembler/shao/1592212293837151_statistic.yml", "r") as stream:
        data = yaml.load(stream, Loader=yaml.CLoader)
    print("success to read .yml")
    print("show")
    
    for i in range(len(data["BatchOfPositions"])):
        #print(data["BatchOfPositions"][i])
        kifu="(;"
        reStore ={}
        last=""
        for j in range (len(data["BatchOfPositions"][i])):
            nowPosiiton=";"
            if j%2==0:
               nowPosiiton+="B"
               last="BWin"
            else :
               nowPosiiton+="W"
               last="WWin"
            
            row = relectRow[int(data["BatchOfPositions"][i][j]/12)]
            col = str(int(data["BatchOfPositions"][i][j]%12))
            nowPosiiton+=row    
            nowPosiiton+=col 
            kifu+=nowPosiiton
        kifu+=")"
        reStore["kifu"]=kifu
        if len(data["BatchOfPositions"][i]) == 144:
         #   print("DRAW")
            reStore["game_result"]="Draw"
        else:
            reStore["game_result"]=last
        
        storeData.append(reStore)
    with open('data.json', 'w') as outfile:
        for i in storeData:
            json.dump(storeData, outfile)
        


