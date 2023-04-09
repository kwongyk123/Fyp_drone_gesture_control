import cv2
import numpy as np
import time
import math
import copy


class LivePlot:
    def __init__(self, w=640, h=480, yLimit=[0, 100],
                 interval=0.001, invert=False, char=' '):

        self.yLimit = yLimit
        self.w = w
        self.h = h
        self.invert = invert
        self.interval = interval
        self.char = char[0]
        self.imgPlot = np.zeros((self.h, self.w, 3), np.uint8)
        self.imgPlot[:] = 225, 225, 225

        cv2.rectangle(self.imgPlot, (0, 0),
                      (self.w, self.h),
                      (0, 0, 0), cv2.FILLED)
        self.xP = 0
        self.yP = 0

        self.yList = []

        self.xList = [x for x in range(0, 100)]
        self.ptime = 0

    def update(self, y, color=(255, 0, 255)):

        if time.time() - self.ptime > self.interval:

            # Refresh
            self.imgPlot[:] = 225, 225, 225
            # Draw Static Parts
            self.drawBackground()
            # Draw the text value
            cv2.putText(self.imgPlot, str(y),
                        (self.w - (125), 50), cv2.FONT_HERSHEY_PLAIN,
                        3, (150, 150, 150), 3)
            if self.invert:
                self.yP = int(np.interp(y, self.yLimit,
                                        [self.h, 0]))
            else:
                self.yP = int(np.interp(y, self.yLimit,
                                        [0, self.h]))
            self.yList.append(self.yP)
            if len(self.yList) == 100:
                self.yList.pop(0)

            for i in range(0, len(self.yList)):
                if i < 2:
                    pass
                else:
                    cv2.line(self.imgPlot, (int((self.xList[i - 1] * (self.w // 100))) - (self.w // 10),
                                            self.yList[i - 1]),
                             (int((self.xList[i] * (self.w // 100)) - (self.w // 10)),
                              self.yList[i]), color, 2)
            self.ptime = time.time()

        return self.imgPlot

    def drawBackground(self):
        # Draw Background Canvas
        cv2.rectangle(self.imgPlot, (0, 0),
                      (self.w, self.h),
                      (0, 0, 0), cv2.FILLED)
        # Center Line
        cv2.line(self.imgPlot, (0, self.h // 2), (self.w, self.h // 2), (150, 150, 150), 2)
        # Draw Grid Lines
        for x in range(0, self.w, 50):
            cv2.line(self.imgPlot, (x, 0), (x, self.h),
                     (50, 50, 50), 1)
        for y in range(0, self.h, 50):
            cv2.line(self.imgPlot, (0, y), (self.w, y),
                     (50, 50, 50), 1)
            #  Y Label
            cv2.putText(self.imgPlot,
                        f'{int(self.yLimit[1] - ((y / 50) * ((self.yLimit[1] - self.yLimit[0]) / (self.h / 50))))}',
                        (10, y), cv2.FONT_HERSHEY_PLAIN,
                        1, (150, 150, 150), 1)
        cv2.putText(self.imgPlot, self.char,
                    (self.w - 100, self.h - 25), cv2.FONT_HERSHEY_PLAIN,
                    5, (150, 150, 150), 5)

    def stackImages(_imgList, cols, scale):
        """
        Stack Images together to display in a single window
        _imgList: list of images to stack
        cols: the num of img in a row
        scale: bigger~1+ ans smaller~1-
        return: Stacked Image
        """
        imgList = copy.deepcopy(_imgList)

        # make the array full by adding blank img, otherwise the openCV can't work
        totalImages = len(imgList)
        rows = totalImages // cols if totalImages // cols * cols == totalImages else totalImages // cols + 1
        blankImages = cols * rows - totalImages

        width = imgList[0].shape[1]
        height = imgList[0].shape[0]
        imgBlank = np.zeros((height, width, 3), np.uint8)
        imgList.extend([imgBlank] * blankImages)

        # resize the images
        for i in range(cols * rows):
            imgList[i] = cv2.resize(imgList[i], (0, 0), None, scale, scale)
            if len(imgList[i].shape) == 2:
                imgList[i] = cv2.cvtColor(imgList[i], cv2.COLOR_GRAY2BGR)

        # put the images in a board
        hor = [imgBlank] * rows
        for y in range(rows):
            line = []
            for x in range(cols):
                line.append(imgList[y * cols + x])
            hor[y] = np.hstack(line)
        ver = np.vstack(hor)
        return ver


def main():
    xPlot = LivePlot(w=1200, yLimit=[-100, 100], interval=0.01)
    x = 0
    while True:

        x += 1
        if x == 360: x = 0
        imgPlot = xPlot.update(int(math.sin(math.radians(x)) * 100))

        cv2.imshow("Image", imgPlot)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
