import json                          # décodage du message JSON
import sqlite3                       # base de données légère (alternative simple à Firebase/MySQL)
from matplotlib.pyplot import rc
import paho.mqtt.client as mqtt      # client MQTT

BROKER, PORT = "broker.hivemq.com", 1883
TOPIC = "iot/test/monnaie/detection"

# Fonction appelee apres connexion
def on_connect(client, userdata, flags, reason_code, properties):  
  def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connecte a HiveMQ Cloud !")
        client.subscribe(TOPIC)
        print("Abonne au topic :", TOPIC)
    else:
        print("Erreur de connexion :", reason_code)


# Fonction appelee a la reception
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print("Message recu :", message)

# Creer le client MQTT
client = mqtt.Client()        

# Configurer les fonctions
client.on_connect = on_connect
client.on_message = on_message

# Se connecter
print("Connexion a HiveMQ Cloud...")
client.connect(BROKER, PORT, 60)

# Ecouter les messages continuellement
client.loop_forever()
