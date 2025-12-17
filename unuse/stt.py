import whisper
import json
model = whisper.load_model("large-v2")

result = model.transcribe(audio = "audios/01_Introduction.mp3", 
                          language = "hi", 
                          task = "translate",
                          world_timestampes = False)

print(result["segments"])
chunks =[]
for segment in result["segments"]:
    chunks.append({"start": segment["start"], "end": segment["end"], "text": segment["text"]})
    
print(chunks) 

with open("output.json", "w") as f:
    json.dump(chunks ,f)