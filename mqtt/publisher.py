
# 1. IMPORTATION DES BIBLIOTHEQUES
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import cv2
import json
from datetime import datetime

# 2. CONFIGURATION MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "money_detection_tunisia/project01/detections"
KEEPALIVE = 60 ## Temps maximum d'attente pour la connexion.

# 3. CONFIGURATION YOLO
MODEL_PATH = "models/best.pt"
## confiance minimale (0 à 1) pour accepter une détection
SEUIL_CONFIANCE = 0.5

# 4. VALEUR DES MONNAIES EN MILLIMES
# 1dt= 1000 millimes
CURRENCY_VALUES = {
    "piece_50_millimes": 50,
    "piece_100_millimes": 100,
    "piece_200_millimes": 200,
    "piece_500_millimes": 500,
    "piece_1_dinars": 1000,
    "piece_2_dinars": 2000,
    "piece_5_dinars": 5000,
    "billet_5_dinars": 5000,
    "billet_10_dinars": 10000,
    "billet_20_dinars": 20000,
    "billet_50_dinars": 50000
}
# 5. FONCTION DE CALCUL DU TOTAL
## Entrée : results = résultat de model.predict() 
# Sortie : total en millimes, total en dinars (TND) 
# et liste détaillée des détections
def calculate_total(results):
    total_millimes = 0
    # liste qui contiendra une entrée par objet détecté
    detections = []
    # parcourt chaque boîte détectée dans l'image
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = results[0].names[class_id]
        confidence = float(box.conf[0])
        # on ne garde que les classes dont on connaît la valeur
        if class_name in CURRENCY_VALUES:
            value = CURRENCY_VALUES[class_name] ## valeur de l'objet en millimes
            total_millimes += value
            detections.append({
                "class": class_name,
                "value_millimes": value, ## valeur en millimes
                "confidence": round(confidence * 100, 2)

            })
    total_tnd = total_millimes / 1000
    return total_millimes, total_tnd, detections

# 6. CONNEXION MQTT
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connexion au broker HiveMQ reussie !")
    else:
        print("Erreur de connexion MQTT :", reason_code)
# creation de client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
print("Connexion a HiveMQ public...")
try:
    client.connect(BROKER, PORT, KEEPALIVE)
except Exception as erreur:
    print("Erreur de connexion :", erreur)
    exit()
client.loop_start()

# 7. CHARGEMENT DU MODELE YOLO
model = YOLO(MODEL_PATH)
print("Modele YOLO charge avec succes !")

# 8. OUVERTURE DE LA WEBCAM
 # ouvre la webcam par défaut
camera = cv2.VideoCapture(0) 
if not camera.isOpened():
    print("Erreur : impossible d'ouvrir la webcam")
    client.disconnect()
    client.loop_stop()
    exit()
print("Detection demarree !")
print("Appuie sur A pour quitter.")

# 9. DETECTION ET CALCUL EN TEMPS REEL
try:
    while True:
        # Lire une image depuis la webcam
        success, image = camera.read()
        if not success:
            print("Erreur : impossible de lire l'image")
            break
        # Detection YOLO
        results = model.predict( image,  conf=SEUIL_CONFIANCE, verbose=False )
        result = results[0]
        # Calculer le montant total
        total_millimes, total_tnd, detections = calculate_total(results)
        # Afficher les resultats YOLO
        image_detected = result.plot()
         # écrit le total en haut à gauche (x=20, y=40)
        cv2.putText(image_detected,f"Total : {total_tnd:.3f} TND",(20, 40),
             # police, taille, couleur verte (BGR), épaisseur
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # affiche l'image dans une fenêtre
        cv2.imshow( "Detection de monnaie tunisienne", image_detected)

        # 10. ENVOI DES DONNEES VERS HIVEMQ
        if detections:
            donnees = {
                "project": "money_detection_tunisia",
                "device": "PC_Webcam",
                "date_heure": datetime.now().astimezone().isoformat(timespec="seconds"),
                "currency": "TND",
                "detections": detections,
                "total_millimes": total_millimes,
                "total_amount": round(total_tnd, 3)
            }

            message = json.dumps(donnees, ensure_ascii=False)
            if client.is_connected():
                resultat = client.publish(TOPIC,message,qos=1 )

                if resultat.rc == mqtt.MQTT_ERR_SUCCESS:
                    print("\nMessage envoye vers HiveMQ :")
                    print(message)
                else:
                    print("Erreur de publication MQTT.")

        # Quitter avec A

        if cv2.waitKey(1) & 0xFF in [ord('A'), ord('a')]:
            print("Detection interrompue par l'utilisateur.")
            break

# 11. FERMETURE DES CONNEXIONS
finally:
    camera.release()
    cv2.destroyAllWindows()
    if client.is_connected():
        client.disconnect()
    client.loop_stop()
    print("Programme TuniMoney termine.")
