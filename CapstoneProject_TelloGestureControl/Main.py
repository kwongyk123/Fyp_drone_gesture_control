import logging
import cv2
import time
from FaceTracking.PID import PID
from FaceTracking.PlotModule import LivePlot
from djitellopy import tello
from gestures.HandTrackingModule import HandDetector
from Face.FaceDetectModule import FaceDetector
from gestures.gestureBuffer import GestureBuffer
from gestures.gesturecontroller import GestureController


detectorHands = HandDetector(maxHands=1, detectionCon=0.7)
detectorFace = FaceDetector(minDetectionCon=0.6)

hi, wi = 480, 640

#                  P  I  D
xPID = PID([0.27, 0, 0.1], wi // 2)
yPID = PID([0.25, 0, 0.1], hi // 2, axis=1)
zPID = PID([0.005, 0, 0.001], 12000, limit=[-25, 20])

myPlotX = LivePlot(yLimit=[-100, 100], char="X")
myPlotY = LivePlot(yLimit=[-100, 100], char="Y")
myPlotZ = LivePlot(yLimit=[-100, 100], char="Z")

drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamoff()
drone.streamon()
global gestureController
gestureController = GestureController(drone)

global gesture_buffer
gesture_buffer = GestureBuffer(buffer_len=10)

# 1 = gesture, 2 = facet-racking
global mode
mode = 1
gestureText = ""
modeText = "Gesture"


def gestureControl(img, bboxs, allHands):
    global mode
    # global keepRecording
    # global recorder
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

                elif fingers == [1, 1, 1, 0, 0]:
                    gestureText = "switch Mode"
                    gesture_buffer.add_gesture(200)

                # elif fingers == [0, 1, 1, 1, 1]:
                #     gestureText = "RecordStart"
                #     gesture_buffer.add_gesture(80)

                cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                gesture_id = gesture_buffer.get_gesture()

                if gesture_id == 200:
                    mode = 2
                    gestureController.drone_stop()

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

                # elif fingers == [0, 1, 1, 1, 1]:
                #     gestureText ·、= "RecordStop"
                #     gesture_buffer.add_gesture(81)

                cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0,  0), 2)
                gesture_id = gesture_buffer.get_gesture()

                gestureController.gesture_control(gesture_id)




def faceTracking(img, bboxs, allHands):
    xVal = 0
    yVal = 0
    zVal = 0
    lVal = 0
    imgStacked = ""
    global mode
    if bboxs and drone.is_flying:
        if allHands:
            if allHands[0]['type'] == "Right" and drone.is_flying:
                fingers = detectorHands.fingersUp(allHands)
                if fingers == [0, 0, 1, 1, 1]:
                    gestureText = "land"
                    gesture_buffer.add_gesture(100)
                elif fingers == [1, 1, 1, 0, 0]:
                    gestureText = "switch Mode"
                    gesture_buffer.add_gesture(201)
                elif fingers == [0, 0, 0, 0, 1]:
                    gestureText = "right"
                    lVal = -25
                elif fingers == [1, 0, 0, 0, 0]:
                    gestureText = "left"
                    lVal = 25
                else:
                    gestureText = ""
                cv2.putText(img, f'{gestureText}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                gesture_id = gesture_buffer.get_gesture()
                if gesture_id == 201:
                    mode = 1
                    gestureController.drone_stop()
                gestureController.gesture_control(gesture_id)

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
        imgStacked = LivePlot.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 1)
        cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    else:
        imgStacked = LivePlot.stackImages([img], 1, 0.75)
    drone.send_rc_control(lVal, -zVal, -yVal, xVal)
    return imgStacked


# def videoRecorder(frame_read, filename):
#     # create a VideoWrite object, recoring to ./video.avi
#     height, width, _ = frame_read.shape
#     video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'MJPG'), 30, (width, height))
#
#     while keepRecording:
#         video.write(frame_read)
#         time.sleep(1 / 30)
#
#     video.release()


try:
    while True:
        # _, img = cap.read()
        img = drone.get_frame_read().frame
        # filename = f'Resources/video/video_{counter}.avi'
        # recorder = Thread(target=videoRecorder, args=(img, filename))
        # recorder.start()
        # if keepRecording:
        #     counter += 1
        img = cv2.resize(img, (640, 480))
        allHands, img = detectorHands.findHands(img)
        img, bboxs = detectorFace.findFaces(img, draw=True)

        cv2.putText(img, f'{modeText}', (20, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        # if keepRecording:
        #     cv2.putText(img, "Recording", (460, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        if mode == 1:
            gestureControl(img, bboxs, allHands)
            modeText = "Gesture"
        elif mode == 2:
            img = faceTracking(img, bboxs, allHands)
            modeText = "FaceTracking"

        cv2.imshow("Image", img)

        if cv2.waitKey(5) & 0xFF == ord('g') and drone.is_flying:
            mode = 1

        if cv2.waitKey(5) & 0xFF == ord('f') and drone.is_flying:
            mode = 2

        if cv2.waitKey(5) & 0xFF == ord('e') and not drone.is_flying:
            gestureController.drone_stop()
            drone.takeoff()
            time.sleep(1)


        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    if drone.is_flying:
        drone.send_rc_control(0, 0, 0, 0)
        drone.land()

    cv2.destroyAllWindows()

except:
    logging.exception("message")
    drone.end()

