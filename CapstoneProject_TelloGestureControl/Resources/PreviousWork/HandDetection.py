import cv2
from djitellopy import tello
from gestures.HandTrackingModule import HandDetector
from Face.FaceDetectModule import FaceDetector
from gestures.gestureBuffer import GestureBuffer
from gestures.gesturecontroller import GestureController
import time

#cap = cv2.VideoCapture(0)
detectorHands = HandDetector(maxHands=1, detectionCon=0.65)
detectorFace = FaceDetector()
gestureText = ""

drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamoff()
drone.streamon()
global gestureController
gestureController = GestureController(drone)

global gesture_buffer
gesture_buffer = GestureBuffer()
# 0 = keyboard, 1 = gesture, 2 = facet-racking
#mode = 0


while True:
    # _, img = cap.read()
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (640, 480))
    allHands, img = detectorHands.findHands(img)
    img, bboxs = detectorFace.findFaces(img, draw=True)

    # check if allHands is not emptyx
    if bboxs:
        if allHands:
            if allHands[0]['type'] == "Right" and drone.is_flying:
                fingers = detectorHands.fingersUp(allHands)
                if fingers == [0, 0, 0, 0, 0]:
                    gestureText = "Stop"
                    gesture_buffer.add_gesture(0)

                elif fingers == [1, 1, 1, 1, 1]:
                    gestureText = "Back"
                    gesture_buffer.add_gesture(1)

                elif fingers == [1, 1, 0, 0, 0]:
                    gestureText = "Forward"
                    gesture_buffer.add_gesture(2)

                elif fingers == [0, 1, 0, 0, 0]:
                    gestureText = "up"
                    gesture_buffer.add_gesture(3)

                elif fingers == [0, 1, 1, 0, 0]:
                    gestureText = "down"
                    gesture_buffer.add_gesture(4)

                elif fingers == [0, 0, 0, 0, 1]:
                    gestureText = "Right"
                    gesture_buffer.add_gesture(5)

                elif fingers == [1, 0, 0, 0, 0]:
                    gestureText = "Left"
                    gesture_buffer.add_gesture(6)

                elif fingers == [1, 1, 0, 0, 1]:
                    gestureText = "Flip"
                    gesture_buffer.add_gesture(7)

                elif fingers == [1, 0, 0, 0, 1]:
                    gestureText = "Rotate"
                    gesture_buffer.add_gesture(8)

                elif fingers == [0, 0, 1, 1, 1]:
                    gestureText = "land"
                    gesture_buffer.add_gesture(100)
                cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                gesture_id = gesture_buffer.get_gesture()
                gestureController.gesture_control(gesture_id)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    if cv2.waitKey(5) & 0xFF == ord('g'):
        drone.takeoff()
        drone.send_rc_control(0, 0, 25, 0)
        mode = 1
        time.sleep(2)

    # if cv2.waitKey(5) & 0xFF == ord('f'):
    #     mode = 2
    #
    if cv2.waitKey(5) & 0xFF == ord('q'):
        drone.land()
        #mode = 0
        break;

cv2.destroyAllWindows()

