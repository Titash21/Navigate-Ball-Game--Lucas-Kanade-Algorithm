import matplotlib.pyplot as p
import numpy as np
import argparse
import imutils
import cv2
import video
from common import anorm2, draw_str
from time import clock
from collections import deque
import math
import pyautogui
gp=[]
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())
lower_green = np.array([29,86,6])
upper_green = np.array([64,255,255])
pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        print "Successful"    

# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
                  minEigThreshold=1e-4)

feature_params = dict( maxCorners = 10,
                       qualityLevel = 0.3,
                       minDistance = 10,
                       blockSize = 25 )

class App:
    def __init__(self, camera):
        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.cam = video.create_capture()
        self.frame_idx = 0
        self.centers=[]
        self.graphpoints=[]

    def run(self):
        while True:
            ret,frame = self.cam.read()
            if args.get("video") and not ret:
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            vis = frame.copy()

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1000
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 0, 128),2)
                draw_str(vis, (200, 200), 'track count: %d' % len(self.tracks))

            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                mask = cv2.inRange(frame_hsv, lower_green, upper_green)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)

                # find contours in the mask and initialize the current
                # (x, y) center of the ball
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
                center = None
                # only proceed if at least one contour was found
                if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    if len(self.centers)==2:
                        print self.centers
                        xdiff=self.centers[1][0]-self.centers[0][0]
                        ydiff=self.centers[1][1]-self.centers[0][1]
                        if (xdiff>20 and math.fabs(xdiff)>math.fabs(ydiff)):
                            print "LEFT"
                            pyautogui.press('left')
                        elif(xdiff<-20 and math.fabs(xdiff)>math.fabs(ydiff)):
                            print "RIGHT"
                            pyautogui.press('right')
                        elif(ydiff>20 and math.fabs(xdiff)<math.fabs(ydiff)):
                            print "DOWN"
                            pyautogui.press('down')
                        elif(ydiff<-20 and math.fabs(xdiff)<math.fabs(ydiff)):
                            print "UP" 
                            pyautogui.press('up') 
                        self.centers=[]
                    self.centers.append(center)
                    xcenter=center[0]
                    ycenter=center[1]
                    self.graphpoints.append(center)


                    if len(self.tracks)==2:
                        self.tracks=[]
                    self.tracks.append([(center[0], center[1])])
                    # only proceed if the radius meets a minimum size
                    if radius > 10:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(vis, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                        cv2.circle(vis, center, 5, (0, 0, 255), -1)
                        cv2.putText(vis,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
                        cv2.putText(vis,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
                        
                # update the points queue
                pts.appendleft(center)
                # loop over the set of tracked points
                for i in xrange(1, len(pts)):
                    # if either of the tracked points are None, ignore
                    # them
                    if pts[i - 1] is None or pts[i] is None:
                        continue

                    # otherwise, compute the thickness of the line and
                    # draw the connecting lines
                    thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                    cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


                #Bitwise-AND mask and original image
                res = cv2.bitwise_and(frame,frame, mask= mask)
                cv2.polylines(res, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0),2)
                draw_str(res, (200, 200), 'track count: %d' % len(self.tracks))
                
               

            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv2.imshow('res',res)
            cv2.imshow('lk_track', vis)
            


            ch = 0xFF & cv2.waitKey(1)
            # if the 'q' key is pressed, stop the loop
            if ch == ord("q"):
                break

        f=open("textfile.txt","w")        
        for g in self.graphpoints:
            s=str(g[0]),str(g[1])
            f.write(" ".join(s))
            f.write('\n')   
        f.close()    
                  
        
           
                

App(camera).run()
camera.release()

cv2.destroyAllWindows()
