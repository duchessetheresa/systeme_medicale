import face_recognition
import cv2
import numpy as np
import os
from app.config import Config

class FaceRecognitionService:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.load_existing_faces()

    def load_existing_faces(self):
        if not os.path.exists(Config.FACE_DATA_PATH):
            os.makedirs(Config.FACE_DATA_PATH)
        for filename in os.listdir(Config.FACE_DATA_PATH):
            if filename.endswith(('.jpg', '.png', '.jpeg')):
                user_id = os.path.splitext(filename)[0]
                image_path = os.path.join(Config.FACE_DATA_PATH, filename)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_ids.append(user_id)

    def register_face(self, user_id, image_file):
        try:
            if not os.path.exists(Config.FACE_DATA_PATH):
                os.makedirs(Config.FACE_DATA_PATH)
            filename = f"{user_id}.jpg"
            image_path = os.path.join(Config.FACE_DATA_PATH, filename)
            image_file.save(image_path)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                self.known_face_encodings.append(encodings[0])
                self.known_face_ids.append(user_id)
                return True
            return False
        except Exception as e:
            print(f"Error registering face: {e}")
            return False

    def verify_face(self, image_file):
        try:
            image = face_recognition.load_image_file(image_file)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                return None
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0])
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encodings[0])
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return self.known_face_ids[best_match_index]
            return None
        except Exception as e:
            print(f"Error verifying face: {e}")
            return None