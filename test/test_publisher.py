
# Fichier : publisher.py
# client MQTT
import paho.mqtt.client as mqtt
 # pour les pauses entre deux envois
import time


# ===== Parametres =====
# adresse du broker cloud public
BROKER = "broker.hivemq.com"  
# port MQTT standard 
PORT = 1883                                  
TOPIC = "iot/test/monnaie/detection"     


# Creer le client MQTT
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)
# Connexion a HiveMQ
print("Connexion a HiveMQ Cloud...")
client.connect(BROKER, PORT, 60)

# Demarrer la communication
client.loop_start()

# Attendre la connexion
time.sleep(2)

# Message a envoyer
message = "Bonjour HiveMQ ! Mon projet IoT fonctionne."

# Publier le message
result = client.publish(TOPIC, message, qos=1)

# Attendre la confirmation de publication
result.wait_for_publish()

print("Message publie :", message)

# Fermer la connexion
client.disconnect()
client.loop_stop()
