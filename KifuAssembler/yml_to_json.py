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

parser.add_argument('-d', '--enable_use_multiple_yml',
    action='store_true',
    help="transfer multiple yml to json"
)


relectRow = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h",8:"i",9:"j",10:"k",11:"l"}



def handle_yml_to_json_format(data,storeData):

    for i in range(len(data["BatchOfPositions"])):

        kifu="("
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
            col = str(int(data["BatchOfPositions"][i][j]%12)+1)
            nowPosiiton+=("["+row)    
            nowPosiiton+=(col +"]")
            kifu+=nowPosiiton
        kifu+=")"
        reStore["kifu"]=kifu
        if len(data["BatchOfPositions"][i]) == 144:
         #   print("DRAW")
            reStore["game_result"]="Draw"
        else:
            reStore["game_result"]=last
        
        reStore["url"]="."

        storeData.append(reStore)

    return storeData

if __name__ == '__main__':
    args = parser.parse_args()
    data = "null"
    print("start read .yml")
    
    output_data = []

    if(args.enable_use_multiple_yml):
        with open(args.json_src, "r") as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)
        
        output_data = handle_yml_to_json_format(data,output_data)

    else :
        print("load multi-yml files")
        for yml in pathlib.Path("demo").glob("*.yml"):
            print(yml)
            with yml.open('r') as f:
                data = yaml.load(f, Loader=yaml.CLoader)
        
            output_data = handle_yml_to_json_format(data,output_data)

    
        

    with open(args.output_file, 'w') as outfile:
        json.dump(output_data, outfile, indent=2)

    print("success to produce .json")  


