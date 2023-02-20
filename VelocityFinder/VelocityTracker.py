import cv2
import matplotlib.pyplot as plt
import sys

measuring_length = .4  # meters
camera_fps = 30  # frames per second
video_path = "ANMR0001.mp4"
video = cv2.VideoCapture(video_path)
tracker_type = 'MIL'

params = cv2.SimpleBlobDetector_Params()
params.filterByCircularity = True
params.minCircularity = 0.9

tracker = cv2.TrackerMIL_create()
i = 0
while i < 12:
    rete,frame = video.read()
    i += 1
rete, frame = video.read()
# frame = cv2.resize(frame, (854,480))
if not rete:
    print('Cant read video file')
    sys.exit()
objectBounds = cv2.selectROI(frame)
cv2.destroyAllWindows()
rete = tracker.init(frame, objectBounds)

while video.isOpened():
    rete, frame = video.read()
    if not rete:
        break
    # frame = cv2.resize(frame, (854,480))
    timer = cv2.getTickCount()
    rete, objectBounds = tracker.update(frame)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    if rete:
        p1 = (int(objectBounds[0]),int(objectBounds[1]))
        p2 = (int(objectBounds[0] + objectBounds[2]),int(objectBounds[1] + objectBounds[3]))
        cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    else:
        cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
    # cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
    cv2.imshow("Tracking",frame)




