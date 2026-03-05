import cv2
import threading
import time
from detector import ThreatDetector
from database import SessionLocal
from models import EventDB
from datetime import datetime
import numpy as np
import asyncio
from face_tools import train_recognizer, face_cascade

class VideoEngine:
    def __init__(self, source=0):
        self.source = source
        print("Initializing YOLO ThreatDetector. This may download weights...")
        self.detector = ThreatDetector()
        
        print("Training Face Recognition AI...")
        self.face_recognizer, self.label_map = train_recognizer()
        
        self.current_frame = None
        self.latest_alerts = []
        self.running = False
        self.heatmap_data = [] 
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        threading.Thread(target=self._update, daemon=True).start()

    def stop(self):
        self.running = False

    def _update(self):
        print("Starting video engine background thread...")
        
        # Load detector FIRST before locking the camera so downloads don't hold the lock
        db = SessionLocal()
        last_alert_time = {}
        
        # Initialize video
        if isinstance(self.source, int) or str(self.source).isdigit():
            print(f"Opening camera {self.source} with DSHOW backend...")
            cap = cv2.VideoCapture(int(self.source), cv2.CAP_DSHOW)
        else:
            print(f"Opening video source {self.source}...")
            cap = cv2.VideoCapture(self.source)
            
        print(f"Camera opened: {cap.isOpened()}")    
        
        try:
            while self.running:
                if not cap.isOpened():
                    print("Camera not open, retrying...")
                    time.sleep(1)
                    if isinstance(self.source, int) or str(self.source).isdigit():
                        cap = cv2.VideoCapture(int(self.source), cv2.CAP_DSHOW)
                    else:
                        cap = cv2.VideoCapture(self.source)
                    continue

                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame from camera")
                    if isinstance(self.source, str) and not self.source.startswith('rtsp'):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        time.sleep(1)
                    continue
                
                # Process threats
                try:
                    annotated_frame, threats, persons = self.detector.process_frame(frame)
                except Exception as e:
                    print(f"Error during YOLO processing: {e}")
                    continue
                
                # Apply Local Facial Recognition
                if self.face_recognizer is not None:
                    try:
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                        
                        for (x, y, w, h) in faces:
                            face_roi = gray_frame[y:y+h, x:x+w]
                            label_id, confidence = self.face_recognizer.predict(face_roi)
                            
                            # Confidence lower is better for LBPH (distance). < 80 is generally a good match.
                            if confidence < 85:
                                name = self.label_map.get(label_id, "Unknown")
                                text = f"{name} ({int(confidence)})"
                                color = (0, 255, 0) # Green for known
                            else:
                                name = "Unknown"
                                text = name
                                color = (0, 0, 255) # Red for unknown
                                
                            # Draw face bounding box and name on the frame
                            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
                            cv2.putText(annotated_frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    except Exception as e:
                        print(f"Error during Face Recognition: {e}")
                
                self.heatmap_data.extend(persons)
                self.heatmap_data = self.heatmap_data[-2000:] # Cap heatmap data size

                new_alerts = []
                current_time = time.time()
                
                for t in threats:
                    alert_key = t['object']
                    if alert_key not in last_alert_time or (current_time - last_alert_time[alert_key] > 5):
                        last_alert_time[alert_key] = current_time
                        
                        event = EventDB(
                            camera_source=str(self.source),
                            detected_object=t['object'],
                            threat_level=t['level'],
                            confidence=t['confidence'],
                            location_x=t['center'][0],
                            location_y=t['center'][1]
                        )
                        db.add(event)
                        db.commit()
                        db.refresh(event)
                        
                        new_alerts.append({
                            'id': event.id,
                            'timestamp': event.timestamp.isoformat(),
                            'object': event.detected_object,
                            'level': event.threat_level
                        })

                with self.lock:
                    self.current_frame = annotated_frame.copy()
                    if new_alerts:
                        self.latest_alerts = (new_alerts + self.latest_alerts)[:20]
                        
                # Yield processing power
                time.sleep(0.03)
        finally:
            cap.release()
            db.close()

    def get_frame_bytes(self):
        with self.lock:
            if self.current_frame is None:
                return None
            frame = self.current_frame
        
        ret, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()

    def generate_heatmap(self):
        with self.lock:
            if self.current_frame is None:
                return b''
            height, width = self.current_frame.shape[:2]
            
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        for x, y in self.heatmap_data:
            if 0 <= x < width and 0 <= y < height:
                heatmap[y, x] += 1
                
        heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
        if np.max(heatmap) > 0:
            heatmap = (heatmap / np.max(heatmap)) * 255
            
        heatmap = heatmap.astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        ret, buffer = cv2.imencode('.jpg', heatmap_colored)
        return buffer.tobytes()
