
# Importer OpenCV pour utiliser la webcam
import cv2
# Importer YOLO depuis Ultralytics
from ultralytics import YOLO


# 1. Charger le modèle YOLO
MODEL_PATH = "models/best.pt"
model = YOLO(MODEL_PATH)

# 2. Ouvrir la webcam principale
camera = cv2.VideoCapture(0)
# Verifier si la webcam fonctionne
if not camera.isOpened():
    print("Erreur : webcam inaccessible.")
    exit()

#3. Definir la largeur de la video
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# 4. Definir la hauteur de la video
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("TuniMoney : détection démarrée.")
print("Appuie sur a pour quitter.")
#DETECTION EN TEMPS REEL
# 5. Boucle principale
while True:

    # Lire une image depuis la webcam
    success, frame = camera.read()
    # Verifier si la capture est correcte
    if not success:
        print("Impossible de lire l'image.")
        break

    # 5. Effectuer la détection avec YOLO
    results = model.predict(
        source=frame,
        conf=0.35,
        imgsz=960,
        verbose=False
    )

    # 6. Dessiner les résultats sur l'image
    annotated_frame = results[0].plot()

    # 7. Afficher le nombre d'objets détectés
    number_of_objects = len(results[0].boxes)

    cv2.putText(
        annotated_frame,
        f"Objets detectes : {number_of_objects}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    # 8. Afficher la vidéo
    cv2.imshow("TuniMoney - YOLO Detection", annotated_frame)

    # 9. Quitter avec la touche A
    if cv2.waitKey(1) & 0xFF == ord("a"):
        break

# 10. Libérer les ressources
camera.release()
cv2.destroyAllWindows()

print("Détection arrêtée.")
