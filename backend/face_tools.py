import cv2
import os
import numpy as np

# Use an absolute path if necessary, but assuming relative works based on main execution context
USER_DIR = "../User"

# Pre-trained Haar Cascade classifier for frontal face detection
# OpenCV usually stores this internally, or we can use the cv2 data path
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

def train_recognizer(base_dir=USER_DIR):
    """
    Scans the given base_dir for user folders, loads images, detects faces,
    and returns a trained LBPHFaceRecognizer and a label_map.
    """
    if not os.path.exists(base_dir):
        print(f"Warning: User directory '{base_dir}' not found.")
        return None, {}

    faces = []
    labels = []
    label_map = {}
    current_label = 0

    print(f"Scanning target directory: {base_dir}")
    
    for user_name in os.listdir(base_dir):
        user_path = os.path.join(base_dir, user_name)
        if not os.path.isdir(user_path):
            continue
            
        label_map[current_label] = user_name
        print(f"Parsing faces for user: {user_name} (ID: {current_label})")
        
        for image_name in os.listdir(user_path):
            image_path = os.path.join(user_path, image_name)
            
            try:
                # Read image in grayscale explicitly
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                    
                # Detect faces in the image
                detected_faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                # If a face is found, crop and add to our training data
                for (x, y, w, h) in detected_faces:
                    faces.append(img[y:y+h, x:x+w])
                    labels.append(current_label)
                    # For training clarity, we just take the first detected face per reference image
                    break 
                    
            except Exception as e:
                print(f"Error parsing image {image_path}: {e}")
                
        current_label += 1

    if len(faces) > 0:
        print(f"Training Face Recognizer on {len(faces)} samples...")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        print("Training complete!")
        return recognizer, label_map
    else:
        print("No valid faces found to train on.")
        return None, {}

if __name__ == "__main__":
    # Test execution
    r, m = train_recognizer()
    print("Label Map:", m)
