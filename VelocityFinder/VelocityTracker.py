import cv2
import matplotlib.pyplot as plt
import sys
import numpy as np

# --- Adjust these variables as needed for each video
measuring_length = 2.35  # meters
camera_fps = 30  # frames per second
releaseFrame = 160  # this is the frame where the obj is released and the timer starts
numPoints = 20  # number of times velocity will be calculated
video_path = "Wave Tank Vids\ANMR0029.mp4"

tracker_type = 'CSRT'
video = cv2.VideoCapture(video_path)

# --- Parameters for calculating delta if desired
FLUID_VISCOSITY = 8.927 * 10**-7  # kinematic viscosity m^2/s
FLUID_DENSITY = 997  # kg/m^3
SPHERE_RADIUS = .02  # meters
GRAVITY = 9.81  # m/s^2

if not video.isOpened():
    print("Video not opened")
    sys.exit()

i = 1
while (i <= releaseFrame):
    rete, frame = video.read()
    i += 1

if not rete:
    print('Cant read video file')
    sys.exit()

frame = cv2.resize(frame, (854, 480))
measuringBounds = cv2.selectROI(
    "Select tracking area", frame)  # Start area at top of ball
cv2.destroyAllWindows()
# pixel_length = measuringBounds[3]  # gets pixel height of selection VERTICAL
pixel_length = measuringBounds[2]  # HORIZONTAL
PIXELS_PER_METER = pixel_length / measuring_length
# trackingPoints, interval = np.linspace(measuringBounds[1],
#                                        measuringBounds[1] + measuringBounds[3], numPoints, retstep=True)  # returns various heights to get velocity at (VERTICAL)
trackingPoints, interval = np.linspace(measuringBounds[0],
                                       measuringBounds[0] + measuringBounds[2], numPoints, retstep=True)  # returns various points to get velocity at (HORIZONTAL)

params = cv2.SimpleBlobDetector_Params()
params.filterByCircularity = True
params.filterByColor = True
params.blobColor = 150
params.minCircularity = .8

if int(7) < 3:
    tracker = cv2.Tracker_create(tracker_type)
else:
    tracker = cv2.TrackerCSRT_create()


frame = cv2.resize(frame, (854, 480))
if not rete:
    print('Cant read video file')
    sys.exit()

objectBounds = cv2.selectROI("Select object", frame)
cv2.destroyAllWindows()
rete = tracker.init(frame, objectBounds)
p1, prev = None, None

frameCount, prevFrame, speed = releaseFrame, 0, 0
# trackingCount = numPoints # VERTICAL
trackingCount = 0  # HORIZONTAL
velocities, times = [], []

while video.isOpened():
    rete, frame = video.read()
    frameCount += 1

    if not rete:
        break

    frame = cv2.resize(frame, (854, 480))
    timer = cv2.getTickCount()
    rete, objectBounds = tracker.update(frame)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    if rete:
        if p1 != None:
            prev = p1
        p1 = (int(objectBounds[0]), int(objectBounds[1]))
        p2 = (int(objectBounds[0] + objectBounds[2]),
              int(objectBounds[1] + objectBounds[3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
    else:
        cv2.putText(frame, "Tracking failure detected", (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    if trackingCount <= numPoints - 1 and objectBounds[0] >= trackingPoints[trackingCount]:
        # if objectBounds[1] <= trackingPoints[trackingCount] and trackingCount >= 0: # VERTICAL
        timeInterval = (frameCount - prevFrame) / camera_fps
        length = interval / PIXELS_PER_METER
        speed = length / timeInterval
        velocities.append(speed)
        totalTime = (frameCount - releaseFrame) / camera_fps
        times.append(totalTime)
        prevFrame = frameCount
        # - for VERTICAL, + for HORIZONTAL, also change trackingCount to start at 0
        trackingCount += 1

    cv2.putText(frame, "Velocity : " + str(float(speed)), (100, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    cv2.putText(frame, tracker_type + " Tracker", (100, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

# This removes the points in the first half second
i = 0
t = 0
while t <= .5 and i < numPoints-1:
    t = times[i]
    i += 1
times = times[i:]
velocities = velocities[i:]

# Formatting plots
fig, ax = plt.subplots()
ax.plot(times, velocities, 'bo')
ax.set_xlabel('time (s)')
ax.set_ylabel('velocity (m/s)')
ax.set_title('Drifter velocity')
trendline = np.poly1d(np.polyfit(times, velocities, 1))
ax.plot(times, trendline(times), linestyle='dashed')
plt.show()

# Getting avg velocity and using it to calculate delta
vAvg = np.sum(velocities) / len(velocities)
print("\n\n")
str = "Average velocity: {} m/s"
print(str.format(vAvg))
# EQ_CONSTANT = (3/2)*((3 * FLUID_VISCOSITY * vAvg) /
#                      (SPHERE_RADIUS**2 * FLUID_DENSITY))
# a = 2*GRAVITY
# b = a - EQ_CONSTANT
# c = 2 * EQ_CONSTANT
# deltas = np.roots([a, -b, -c])
# str = "Delta value: {} \n\n"
# print(str.format(deltas[0]))
