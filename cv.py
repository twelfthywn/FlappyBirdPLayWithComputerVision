import cv2
import mediapipe as mp
import pydirectinput
from pynput.keyboard import Key, Controller
import time
from threading import Thread
import json

class cv():
    def __init__(self) -> None:    
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.kb = Controller()
        # Ảnh tĩnh
        self.IMAGE_FILES = []
    
    def run(self): 
        with self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5) as hands:
            for idx, file in enumerate(self.IMAGE_FILES):
                # Read an image, flip it around y-axis for correct handedness output (see
                # above).
                image = cv2.flip(cv2.imread(file), 1)
                # Convert the BGR image to RGB before processing.
                results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                # Điểm.
                print('Handedness:', results.multi_handedness)
                if not results.multi_hand_landmarks:
                    continue
                image_height, image_width, _ = image.shape
                annotated_image = image.copy()
                for hand_landmarks in results.multi_hand_landmarks:
                    print('hand_landmarks:', hand_landmarks)
                    print(
                        f'Index finger tip coordinates: (',
                        f'{hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
                        f'{hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
                    )
                    self.mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
                cv2.imwrite(
                    '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))
                #Vẽ điểm.
                if not results.multi_hand_world_landmarks:
                    continue
                for hand_world_landmarks in results.multi_hand_world_landmarks:
                    self.mp_drawing.plot_landmarks(
                    hand_world_landmarks, self.mp_hands.HAND_CONNECTIONS, azimuth=5)

        # webcam:
        cap = cv2.VideoCapture(0)
        with self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # chạy vd
                    continue

                #
                #
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                #
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Hiển thị tọa độ điểm landmark thứ 9
                        print(hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y)
                        # Khi có tọa độ thì di chuyển đến hoành độ tương ứng màn hình 1920 x1080
                        pydirectinput.moveTo(int((1 - hand_landmarks.landmark[9].x) * 1920), int(hand_landmarks.landmark[9].y * 1080))
                        if hand_landmarks.landmark[4].y > hand_landmarks.landmark[1].y:
                            # and hand_landmarks.landmark[12].y >  hand_landmarks.landmark[11].y and hand_landmarks.landmark[16].y > hand_landmarks.landmark[15].y:
                            # pydirectinput.mouseDown()
                            self.kb.press(Key.space)
                            self.kb.release(Key.space)
                        elif hand_landmarks.landmark[12].y > hand_landmarks.landmark[11].y and hand_landmarks.landmark[8].y > \
                                hand_landmarks.landmark[7].y:
                            # pydirectinput.mouseUp()
                            self.kb.press(Key.space)
                            self.kb.press(Key.space)
                        else:
                            self.kb.release(Key.space)
                        self.mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style())
                # Flip
                cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
        cap.release()