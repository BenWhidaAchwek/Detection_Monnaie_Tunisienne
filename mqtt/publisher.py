
# Importer YOLO
from ultralytics import YOLO
# Importer OpenCV
import cv2
# Importer MQTT
import paho.mqtt.client as mqtt
import json
import time


#  Informations HiveMQ Cloud
BROKER = "broker.hivemq.com"                 
PORT = 1883                                 
TOPIC = "iot/test/monnaie/detection" 


#  Connexion au broker
client = mqtt.Client()               
client.connect(BROKER, PORT, 60)     
client.loop_start()                  
print("Connecte a HiveMQ Cloud !")


# Charger le modele YOLO
model = YOLO("models/best.pt")


# Ouvrir la webcam
# ouvre la webcam (0 = caméra par défaut)
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erreur : impossible d'ouvrir la webcam")
    client.disconnect()
    client.loop_stop()
    exit()

print("Detection demarree ! Appuie sur Q pour quitter.")

# Eviter d'envoyer le meme resultat continuellement
dernier_message = ""
dernier_envoi = 0

#  Detection en temps reel


while True:

    success, image = camera.read()

    if success:

        # Detecter les billets et les pieces
        results = model(image)

        # Recuperer les detections
        detections = results[0].boxes

        # Afficher les resultats
        image_detected = results[0].plot()

        # Parcourir les objets detectes
        for box in detections:

            # Recuperer la classe
            class_id = int(box.cls[0])

            # Recuperer le nom de la classe
            nom = model.names[class_id]

            # Recuperer la confiance
            confiance = float(box.conf[0])

            # Creer le message
            donnees = {
                "objets": nom,
                "confiance": round(confiance * 100, 2)
            }

            message = json.dumps(donnees, ensure_ascii=False)

            # Envoyer si le resultat a change
            # ou si 3 secondes sont passees
            maintenant = time.time()

            if (message != dernier_message or
                    maintenant - dernier_envoi >= 3):

                client.publish(TOPIC, message, qos=1)

                print("Message envoye :", message)

                dernier_message = message
                dernier_envoi = maintenant

        # Afficher la camera
        cv2.imshow(
            "Detection de monnaie tunisienne",
            image_detected
        )

    # Quitter avec Q
    if cv2.waitKey(1) == ord("q"):
        break

#  Fermer les connexions


camera.release()
cv2.destroyAllWindows()

client.disconnect()
client.loop_stop()

print("Programme termine.")
