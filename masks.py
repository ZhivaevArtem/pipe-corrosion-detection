import json
import os

def read_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    filename_without_extension = os.path.splitext(os.path.basename(json_filepath))[0]
    return data, filename_without_extension

folder = 'corrosion_data/mask'

datas = [read_json(os.path.join(folder, f)) for f in os.listdir(folder) if f.endswith('.json')]

for data, name in datas:
    for shape in data['shapes']:
        print(shape['label'])
