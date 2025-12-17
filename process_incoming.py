import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np 
import joblib 
import requests


def create_embedding(text_list):
    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })

    embedding = r.json()["embeddings"] 
    return embedding


df = joblib.load('embedding.joblib')


incoming_query = input("Ask a Question: ")
question_embedding = create_embedding([incoming_query])[0] 

# Find similarities of question_embedding with other embeddings
# print(np.vstack(df['embedding'].values))
# print(np.vstack(df['embedding']).shape)
similarities = cosine_similarity(np.vstack(df['embedding']), [question_embedding]).flatten()
# print(similarities)
top_results = 5
max_indx = similarities.argsort()[::-1][0:top_results]
# print(max_indx)
new_df = df.loc[max_indx] 
# print(new_df[["title", "number", "text"]])

prompt = f'''i im wahtching the numpy videos course. here here are video subtitle chunks containg videos title, video number, start time in second, end time in the seconds, the txt that time:

{new_df[["title","number","start","end","text"]].to_json()}  
------------------------------------------------
"{incoming_query}"
user ask the quation related to the vidos chunks, you have to the answar where and how mouch content is taught in witch video 
(in witch video and at what timestamp) and guide the user to go to the particular video. if user asks unrelated question, tell hm that you can only answer
question related to the course    
'''
with open("romt.txt", "w") as f:
    f.write(prompt)
# for index, item in new_df.iterrows():
    # print(index, item["title"], item["number"], item["text"], item["start"], item["end"])