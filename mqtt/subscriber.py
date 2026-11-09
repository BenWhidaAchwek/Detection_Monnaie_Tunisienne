
# 1. IMPORTATION DES BIBLIOTHEQUES
import json
import paho.mqtt.client as mqtt

# 2. CONFIGURATION MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "money_detection_tunisia/project01/detections"
KEEPALIVE = 60

# 3. FONCTION DE CONNEXION AU BROKER
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connexion au broker HiveMQ reussie !")
        # S'abonner au topic pour recevoir les messages.
        client.subscribe(TOPIC, qos=1)
        print("Abonnement au topic MQTT reussi !")
        print("En attente des donnees de detection...\n")
    else:
        print("Erreur de connexion MQTT :", reason_code)

# 4. FONCTION DE RECEPTION DES MESSAGES
# Cette fonction est appelee automatiquement
# chaque fois qu'un nouveau message MQTT est recu.
def on_message(client, userdata, msg):
    # Recuperer le message recu depuis HiveMQ.
    # Le message est initialement sous forme binaire.
    texte = msg.payload.decode("utf-8")
    try:
        # Convertir le texte JSON en dictionnaire Python.
        donnees = json.loads(texte)
    except json.JSONDecodeError:
        print("Message non JSON recu :", texte)
        return
    
 #####AFFICHER LES INFORMATIONS GENERALES
    print("\n========================================")
    print("       NOUVELLE DETECTION RECUE")
    print("========================================")
    print("Projet :", donnees["project"])
    print("Appareil :", donnees["device"])
    print("Date et heure :", donnees["date_heure"])
    print("Devise :", donnees["currency"])
##### AFFICHER LES MONNAIES DETECTEES
    print("\n--- Monnaies detectees ---")
    # Parcourir la liste des monnaies detectees.
    for detection in donnees["detections"]:
        # Afficher le nom de la monnaie.
        print("\nMonnaie :", detection["class"])
        # Afficher sa valeur en millimes.
        print("Valeur :", detection["value_millimes"], "millimes")
        # Afficher le niveau de confiance de YOLO.
        print("Confiance :", detection["confidence"], "%")
#### AFFICHER LE MONTANT TOTAL 
    print("\n--- Montant total ---")
    print( "Total en millimes :",donnees["total_millimes"],"millimes")
    print( "Total en dinars :",donnees["total_amount"], "TND" )
    print("========================================\n")

# 5. CREATION DU CLIENT MQTT
# Creer le client MQTT.
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# Associer la fonction de connexion au client.
client.on_connect = on_connect
# Associer la fonction de reception des messages au client.
client.on_message = on_message
# 6. CONNEXION ET RECEPTION DES DONNEES
print("Connexion au broker...")
try:
    # Se connecter au broker MQTT.
    client.connect(BROKER, PORT, KEEPALIVE)
except Exception as erreur:
    print("Impossible de joindre le broker :", erreur)
    exit()
# 7. DEMARRAGE DU SUBSCRIBER
try:
    # Demarrer la boucle MQTT.
    # Elle permet de recevoir continuellement les messages.
    client.loop_forever()
except KeyboardInterrupt:
    print("\nArret par l'utilisateur. (Ctrl+C).")
finally:
    # Fermer la connexion MQTT.
    client.disconnect()
    print("Programme termine.")
