import cv2
import cvzone
from djitellopy import tello
from gestures.HandTrackingModule import HandDetector
from Face.FaceDetectModule import FaceDetector
from gestures.gestureBuffer import GestureBuffer
from gestures.gesturecontroller import GestureController
import time

detectorHands = HandDetector(maxHands=1, detectionCon=0.7)
detectorFace = FaceDetector()

hi, wi = 480, 640

#                  P  I  D
xPID = cvzone.PID([0.27, 0, 0.1], wi // 2)
yPID = cvzone.PID([0.25, 0, 0.1], hi // 2, axis=1)
zPID = cvzone.PID([0.005, 0, 0.001], 12000, limit=[-20, 20])

myPlotX = cvzone.LivePlot(yLimit=[-100, 100], char="X")
myPlotY = cvzone.LivePlot(yLimit=[-100, 100], char="Y")
myPlotZ = cvzone.LivePlot(yLimit=[-100, 100], char="Z")

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

mode = 1
gestureText = ""
modeText = "Gesture"

def gestureControl(img, bboxs,allHands):
    gestureText = ""
    # check if allHands is not empty
    if bboxs:
        if allHands and drone.is_flying:
            if allHands[0]['type'] == "Right":
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
                    gestureText = "Rotate360"
                    gesture_buffer.add_gesture(8)

                elif fingers == [0, 0, 1, 1, 1]:
                    gestureText = "land"
                    gesture_buffer.add_gesture(100)
                cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                gesture_id = gesture_buffer.get_gesture()
                gestureController.gesture_control(gesture_id)

            elif allHands[0]['type'] == "Left":
                fingers = detectorHands.fingersUp(allHands)
                if fingers == [0, 0, 0, 0, 0]:
                    gestureText = "Stop"
                    gesture_buffer.add_gesture(0)
                elif fingers == [0, 0, 0, 0, 1]:
                    gestureText = "RotateRight"
                    gesture_buffer.add_gesture(9)
                elif fingers == [1, 0, 0, 0, 0]:
                    gestureText = "RotateLeft"
                    gesture_buffer.add_gesture(10)

                gesture_id = gesture_buffer.get_gesture()
                gestureController.gesture_control(gesture_id)

        cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

def faceTracking(img, bboxs, allHands):
    xVal = 0
    yVal = 0
    zVal = 0

    if bboxs and drone.is_flying:
        if allHands:
            if allHands[0]['type'] == "Right" and drone.is_flying:
                fingers = detectorHands.fingersUp(allHands)
                if fingers == [0, 0, 1, 1, 1]:
                    gestureText = "land"
                    gesture_buffer.add_gesture(100)
                    cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                    gesture_id = gesture_buffer.get_gesture()
                    gestureController.gesture_control(gesture_id)
                else:
                    gestureText = ""

        cx, cy = bboxs[0]['center']
        x, y, w, h = bboxs[0]['bbox']
        area = w * h

        xVal = int(xPID.update(cx))
        yVal = int(yPID.update(cy))
        zVal = int(zPID.update(area))
        print(area)

        imgPlotX = myPlotX.update(xVal)

        imgPlotY = myPlotY.update(-yVal)

        imgPlotZ = myPlotZ.update(-zVal)

        img = xPID.draw(img, [cx, cy])
        img = yPID.draw(img, [cx, cy])
        imgStacked = cvzone.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 1)
        cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    else:
        imgStacked = cvzone.stackImages([img], 1, 0.75)
    drone.send_rc_control(0, -zVal, -yVal, xVal)
    return imgStacked



while True:
    # _, img = cap.read()
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (640, 480))
    allHands, img = detectorHands.findHands(img)
    img, bboxs = detectorFace.findFaces(img, draw=True)

    if mode == 1:
        gestureControl(img, bboxs, allHands)
        modeText = "Gesture"
    elif mode == 2:
        img = faceTracking(img, bboxs, allHands)
        modeText = "FaceTracking"


    cv2.putText(img, f'{modeText}', (20, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    cv2.imshow("Image", img)


    if cv2.waitKey(5) & 0xFF == ord('g') and drone.is_flying:
        mode = 1

    if cv2.waitKey(5) & 0xFF == ord('f') and drone.is_flying:
        mode = 2

    if cv2.waitKey(5) & 0xFF == ord('e') and not drone.is_flying:
        drone.takeoff()
        time.sleep(1.5)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
drone.land()


