from moviepy.editor import *
import openai
import requests
import os
import json

config = open('config.json')
configjson = json.load(config.json)

openai.api_key = configjson.openai
CHUNK_SIZE = 1024
url = configjson.elevenlabs

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "289719f06a3d086f239b72b740696118"
}

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "Tu est un célèbre écrivain d'histoire"},
{
    "role": "user",
    "content": "Bonjour, je voudrais faire une histoire imagée d'environ 1 minute. Pour cela, j'ai besoin d'un tableau d'objets Python avec pour chaque phrase un nouvel objet comprenant la phrase en question et un prompt pour générer l'image, il faut que le prompt soit précis. Le prompt ne doit pas faire référence aux autres parties du text/prompts, comme ceci : \"un chateau blanc dans un ciel bleu avec quelques nuages\" et non pas \"Le chateau blanc dans un ciel bleu avec quelques nuages\" . Peux-tu me le faire en français s'il te plaît ? Assure toi que l'histoire ait un sens, qu'elle ne raconte pas nimporte quoi et ne se finnisse pas brusquement"
  },
  {
    "role": "assistant",
    "content": "[{\"phrase\": \"Il était une fois un château majestueux perché sur une colline verdoyante.\", \"prompt\": \"Un château imposant en pierre blanche, situé au sommet d'une colline verdoyante entourée de fleurs sauvages. Le soleil brille intensément dans un ciel d'un bleu vif.\"}, {\"phrase\": \"À l'intérieur du château, vivait une princesse douce et bienveillante.\", \"prompt\": \"Une princesse élégante aux longs cheveux, vêtue d'une robe qui se tient gracieusement dans une salle ornée de lustres en cristal et de tapisseries.\"}, {\"phrase\": \"Un jour, la princesse découvrit un passage secret dissimulé derrière une bibliothèque ancienne.\", \"prompt\": \"Une princesse déplace une vieille bibliothèque en bois et découvre un passage secret.\"}, {\"phrase\": \"En explorant le passage, la princesse arriva dans un jardin enchanté rempli de fleurs multicolores.\", \"prompt\": \"Un passage secret qui mène à un jardin secret, éclatant de couleurs avec des fleurs aux pétales flamboyants\"}, {\"phrase\": \"Au milieu du jardin, la princesse découvrit une fontaine qui versait de l'eau scintillante.\", \"prompt\": \"Une fontaine trône au centre du jardin.\"}, {\"phrase\": \"La princesse s'approcha de la fontaine et vit son propre reflet, mais quelque chose chez elle était différent.\", \"prompt\": \"Une princesse regarde son reflet dans de l'eau scintillante d'une fontaine.\"}, {\"phrase\": \"La princesse réalisa qu'en traversant le jardin enchanté, elle avait grandi en sagesse et en courage.\", \"prompt\": \"Une princesse sourit avec fierté.\"}, {\"phrase\": \"Et ainsi, la princesse continua son voyage, prête à découvrir les merveilles du monde qui l'attendaient.\", \"prompt\": \"Une princesse qui quitte un jardin enchanté avec devant elle un horizon \"}]"  },
  {
    "role": "user",
    "content": "Peux-tu m'en générer un nouveau similaire à celui-ci ?"
  }

],
)

msgrep = response.choices[0].message.content
tableau_str = msgrep[msgrep.find("["):msgrep.find("]") + 1]
histoire = json.loads(tableau_str)

if histoire:
    i = 0

    for obj in histoire:
        phrase = obj["phrase"]
        prompt = obj["prompt"]
        print("Phrase :", phrase)
        print("Prompt :", prompt)
        try:
            img = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            previous_image_url = img
        except Exception as e:
            print("erreur dans la création de l'image:"+str(e))
            if previous_image_url:
                img = previous_image_url
        print(img)
        print("---------")

        data = {
            "text": phrase,
            "model_id": "eleven_multilingual_v1",
            "language": "french",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        reponse = requests.post(url, json=data, headers=headers)

        with open("audio" + str(i) + ".mp3", "wb") as f:
            for chunk in reponse.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        audio_file = "audio" + str(i) + ".mp3"  # Remplacez par le chemin réel de votre fichier audio
        image_file = img.data[0].url  # Remplacez par le chemin réel de votre fichier image
        output_file = "output" + str(i) + ".mp4"  # Remplacez par le nom de fichier de sortie souhaité

        audio_clip = AudioFileClip(audio_file)
        image_clip = ImageClip(image_file)

        video = image_clip.set_audio(audio_clip)
        video.duration = audio_clip.duration
        video.fps = 15

        video.write_videofile("output" + str(i) + ".mp4")

        i = i + 1
        print(i)

    video_clips = []

    for i in range(0, len(histoire)):
       try:
        file_name = "output" + str(i) + ".mp4"
        video_clip = VideoFileClip(file_name)
        video_clips.append(video_clip)
        print(video_clips)

        final_clip = concatenate_videoclips(video_clips)

        final_output_file = "output_final.mp4"
        final_clip.write_videofile(final_output_file, codec="libx264", audio_codec="aac")
       except Exception as e:
           print("erreur : " + e)

    for i in range(0, len(histoire)):
        file_name = "output" + str(i) + ".mp4"
        if os.path.exists(file_name):
            os.remove(file_name)
            print(file_name + " bien supprimé")

    print("video terminée avec succes")
else:
    print("problème : histoire non valide, essayez de relancer le proggrame")