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

# histoire = [{"phrase": "Il était une fois un navigateur intrépide voguant sur des océans tumultueux.", "prompt": "Un navigateur courageux, à bord d'un fier navire, affronte les vagues déchaînées et les cieux sombres."}, {"phrase": "Au cours de son voyage, le navigateur découvrit une île mystérieuse cachée parmi les brumes.", "prompt": "Une île mystérieuse émergeant des brumes, entourée d'une végétation luxuriante."}, {"phrase": "En explorant l'île, le navigateur trouva une grotte profonde et mystique, illuminée par des cristaux étincelants.", "prompt": "Un navigateur découvre une grotte cachée, illuminée par des cristaux scintillants suspendus au plafond."}, {"phrase": "Dans cette grotte, le navigateur trouva un ancien livre rempli de secrets et de savoirs anciens.", "prompt": "Un livre ancien, couvert de poussière, est découvert dans un coin de la grotte mystérieuse."}, {"phrase": "En étudiant le livre, le navigateur comprit comment déchiffrer les énigmes de l'océan.", "prompt": "Un navigateur qui observe attentivement les pages du livre ancien, en essayant de comprendre les mystères de l'océan."}, {"phrase": "Avec son nouveau savoir, le navigateur parvint à traverser les tempêtes et à découvrir des terres inexplorées.", "prompt": "Un navigateur triomphant, son navire naviguant avec confiance à travers les tempêtes, découvre des terres lointaines et inexplorées."}, {"phrase": "Et ainsi, le navigateur continua son périple, prêt à affronter de nouvelles aventures et à écrire son nom dans les annales de l'Histoire.", "prompt": "Un navigateur solitaire se tient debout sur le pont de son navire, regardant l'horizon avec détermination et prêt à embarquer pour de nouvelles aventures."}]

# print(response)
print("----")
msgrep = response.choices[0].message.content
print(msgrep)

start_i = msgrep.find("[")
end_i = msgrep.find("]")
tableau_str = msgrep[start_i:end_i + 1]
# tableau_str = tableau_str.replace("'", "\"")  # Remplace les guillemets simples par des guillemets doubles
# tableau_str = tableau_str.replace("\\\"", "\"")
histoire = json.loads(tableau_str)
print("----")
print(histoire)

if histoire:
    i=0

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

        i = i+1
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
            print(file_name + "supprimé")

    print("video terminée avec succes")
else:
    print("problème : histoire non valide")




# img = openai.Image.create(
#   prompt="a white siamese cat",
#   n=1,
#   size="1024x1024"
# )
# image_url = img['data'][0]['url']
# print(img)

# url_audio = "http://www.simphonics.com/library/WaveFiles/Production%20Wavefiles/Aircraft/A320%20-%20321/RUMBLE1.wav"
# url_image = "https://www.wallpapers13.com/cool-and-beautiful-nature-desktop-wallpaper-image-1680x1050/"
#
# response_audio = requests.get(url_audio)
# response_audio.raise_for_status()
# audio_content = response_audio.content
#
# with open("audio.mp3", "wb") as audio_file:
#     audio_file.write(audio_content)
# print("Fichier audio téléchargé avec succès.")
#
# response_image = requests.get(url_image)
# response_image.raise_for_status()
# image_content = response_image.content
# with open("image.jpg", "wb") as image_file:
#     image_file.write(image_content)
# print("Fichier image téléchargé avec succès.")
#
# with open("audio.mp3", "rb") as audio_file, open("image.jpg", "rb") as image_file, open("output.mp4", "wb") as output_file:
#     output_file.write(audio_file.read())
#     output_file.write(image_file.read())
# print("Fichier MP4 créé avec succès.")
#
#
#
# # with open('image.jpg', 'wb') as f:
# #     f.write(response.content)



# audio_file = "audio.mp3"  # Remplacez par le chemin réel de votre fichier audio
# image_file = "image.png"  # Remplacez par le chemin réel de votre fichier image
# output_file = "output.mp4"  # Remplacez par le nom de fichier de sortie souhaité
#
# audio_clip = AudioFileClip(audio_file)
# image_clip = ImageClip(image_file)
#
# video = image_clip.set_audio(audio_clip)
# video.duration = audio_clip.duration
# video.fps = 15
#
# video.write_videofile("output.mp4")


[
  {
    "role": "user",
    "content": "Bonjour, je voudrais faire une histoire imagée d'environ 1 minute. Pour cela, j'ai besoin d'un tableau d'objets Python avec pour chaque phrase un nouvel objet comprenant la phrase en question et un prompt pour générer l'image. Peux-tu me le faire en français s'il te plaît ?"
  },
  {
    "role": "assistant",
    "content": "[{\"phrase\": \"Il était une fois, dans une forêt enchantée...\", \"prompt\": \"forêt enchantée\"}, {\"phrase\": \"Un petit lapin blanc sautait gaiement parmi les fleurs...\", \"prompt\": \"lapin blanc parmi les fleurs\"}, {\"phrase\": \"Soudain, un immense dragon surgit des profondeurs de la terre...\", \"prompt\": \"dragon surgissant de la terre\"}, {\"phrase\": \"Une princesse courageuse se dressa devant le dragon...\", \"prompt\": \"princesse devant un dragon\"}, {\"phrase\": \"Les étoiles brillaient intensément dans le ciel nocturne...\", \"prompt\": \"ciel nocturne avec des étoiles brillantes\"}]"
  },
  {
    "role": "user",
    "content": "Peux-tu m'en générer un nouveau similaire à celui-ci ?"
  }
]

