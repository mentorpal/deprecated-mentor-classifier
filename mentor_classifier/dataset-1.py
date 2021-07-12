import csv
import re
import pandas as pd
def find_sentence(job_title: str, text: str):
    sentences = [s+ '.' for s in text.split('.') if job_title in s]
    if not sentences == []:
        index = sentences[0].find(job_title)
        end = index + len(job_title)
        return sentences[0], index, end
    return None, None, None
   
path = "/Users/erice/Downloads/monster_com-job_sample.csv"
with open(path) as f:
    csv_reader = csv.reader(f, delimiter=",")
    next(csv_reader)
    columns =  ["job_title", "sentence", "index", "end_index"]
    csv = pd.DataFrame(columns = columns)
    stop = 0
    for row in csv_reader:
        job_title = row[6]
        sentence, index, end = find_sentence(job_title, row[5])
        if sentence is None: 
            continue
        df_row = pd.DataFrame([[job_title, sentence, index, end]], columns = columns)
        csv = pd.concat([csv, df_row])
        stop = stop + 1
        if stop == 1000:
            break
csv.to_csv("/Users/erice/Downloads/jobs2.csv", index = False)
    


            

