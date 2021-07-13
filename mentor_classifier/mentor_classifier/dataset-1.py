# import csv
# import re
# import pandas as pd
# import spacy 

# def find_sentence(job_title: str, text: str):
#     sentences = [sentence + '.' for sentence in text.split('.') if job_title in sentence]
#     if len(sentences)> 1:
#         index = sentences[1].find(job_title)
#         end = index + len(sentences[1])
#         return sentences[1], index, end
#     if not sentences == []:
#         index = sentences[0].find(job_title)
#         end = index + len(sentences[0])
#         return sentences[0], index, end
#     return None, None, None
   
# path = "/Users/erice/Downloads/dice_com-job_us_sample 2.csv"
# with open(path) as f:
#     csv_reader = csv.reader(f, delimiter=",")
#     next(csv_reader)
#     columns =  ["job_title", "sentence", "index", "end_index"]
#     csv = pd.DataFrame(columns = columns)
#     stop = 0
#     for row in csv_reader:
#         job_title = row[6]
#         sentence, index, end = find_sentence(job_title, row[3])
#         print(sentence, index, end)
#         if sentence is None: 
#             continue
#         df_row = pd.DataFrame([[job_title, sentence, index, end]], columns = columns)
#         print(df_row)
#         csv = pd.concat([csv, df_row])
#         stop = stop + 1
#         if stop == 2000:
#             break
# csv.to_csv("/Users/erice/Downloads/NEW_JOBS_2.csv", index = False)
   
import spacy
import csv
from spacy.tokens import DocBin
db = DocBin() # create a DocBin object
with open("/Users/erice/Downloads/NEW_JOBS.csv") as f:
    nlp = spacy.load("/Users/erice/Desktop/mentor-classifier/shared/installed/spacy-model/en_core_web_sm-3.0.0/en_core_web_sm/en_core_web_sm-3.0.0")
    csv_reader = csv.reader(f, delimiter=",")
    next(csv_reader)
    for row in csv_reader:
        job_title = row[0]
        print(job_title)
        start = int(row[2])
        print(start)
        end = int(row[3])
        print(end)
        sentence = row[1]
        print(sentence)
        doc = nlp.make_doc(sentence)
        ents = []
        span = doc.char_span(start, end, label = "JOB")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
        doc.ents = ents # label the text with the ents
        db.add(doc)   
db.to_disk("/Users/erice/Downloads/train.spacy") # save the docbin object      

