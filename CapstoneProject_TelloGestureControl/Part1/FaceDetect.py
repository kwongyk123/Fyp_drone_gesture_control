from djitellopy import tello
import cv2
import cvzone
import time
from cvzone.FaceDetectionModule import FaceDetector

detector = FaceDetector(minDetectionCon=0.6)

hi, wi = 480, 640
# cap = cv2.VideoCapture(0)
# _, img = cap.read()
# hi, wi, _ = img.shape
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

global imgStacked


def faceTracking(img, bboxs):

    xVal = 0
    yVal = 0
    zVal = 0

    if bboxs and drone.is_flying:
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
        # imgStacked = cvzone.stackImages([img, imgPlotX_resized, imgPlotY_resized, imgPlotZ_resized], 2, 1)
        imgStacked = cvzone.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 1)
        cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    else:
        imgStacked = cvzone.stackImages([img], 1, 0.75)

    drone.send_rc_control(0, -zVal, -yVal, xVal)
    cv2.imshow("Image Stacked", imgStacked)


while True:
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (640, 480))
    # _, img = cap.read()
    img, bboxs = detector.findFaces(img, draw=True)
    faceTracking(img, bboxs)
    cv2.imshow("Image Stacked", imgStacked)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        drone.takeoff()

    if cv2.waitKey(1) & 0xFF == ord('u'):
        drone.send_rc_control(0, 0, 25, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break

cv2.destroyAllWindows()
