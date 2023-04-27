import cv2
import matplotlib.pyplot as plt
import sys
import numpy as np

# --- PARAMETERS --- #
measuring_length = 2.35  # meters
camera_fps = 30  # frames per second
releaseFrame = 160  # this is the frame where the obj is released and the timer starts
numPoints = 16  # number of times velocity will be calculated
video_path = "Wave Tank Vids\ANMR0013.mp4"
tracker_type = 'CSRT'
video = cv2.VideoCapture(video_path)


def getAveragePixelPerMeterHorizontal(frame):
    frame = cv2.resize(frame, (854, 480))
    measuringBounds = cv2.selectROI(
        "Select reference 1", frame)  # Select reference near camera
    cv2.destroyAllWindows()
    refLength1 = float(
        input("What is the length of the selection in meters?\n"))
    pixelPerMeter1 = measuringBounds[2] / refLength1

    measuringBounds = cv2.selectROI(
        "Select reference 2", frame)  # Select reference far from camera
    cv2.destroyAllWindows()
    refLength2 = float(
        input("What is the length of the selection in meters?\n"))
    pixelPerMeter2 = measuringBounds[2] / refLength2
    avgPPM = .5 * (pixelPerMeter1 + pixelPerMeter2)
    print('Average pixels/m: {}\n'.format(avgPPM))
    return avgPPM


def getAveragePixelPerMeterVertical(frame):
    frame = cv2.resize(frame, (854, 480))
    measuringBounds = cv2.selectROI(
        "Select reference 1", frame)  # Select reference near camera
    cv2.destroyAllWindows()
    refLength1 = float(
        input("What is the length of the selection in meters?\n"))
    pixelPerMeter1 = measuringBounds[3] / refLength1

    measuringBounds = cv2.selectROI(
        "Select reference 2", frame)  # Select reference far from camera
    cv2.destroyAllWindows()
    refLength2 = float(
        input("What is the length of the selection in meters?\n"))
    pixelPerMeter2 = measuringBounds[3] / refLength2
    avgPPM = .5 * (pixelPerMeter1 + pixelPerMeter2)
    print(avgPPM)
    return avgPPM


def calculateDelta():
    # --- Parameters for calculating delta if desired
    FLUID_VISCOSITY = 8.927 * 10**-7  # kinematic viscosity m^2/s
    FLUID_DENSITY = 997  # kg/m^3
    SPHERE_RADIUS = .02  # meters
    GRAVITY = 9.81  # m/s^2
    EQ_CONSTANT = (3/2)*((3 * FLUID_VISCOSITY * vAvg) /
                         (SPHERE_RADIUS**2 * FLUID_DENSITY))
    a = 2*GRAVITY
    b = a - EQ_CONSTANT
    c = 2 * EQ_CONSTANT
    deltas = np.roots([a, -b, -c])
    str = "Delta value: {} \n\n"
    print(str.format(deltas[0]))


def writeToFile(outfile, delta, times, velocities, vAvg, slope, PPM):
    with open(outfile, 'w') as filehandle:
        filehandle.write("Average velocity: {:.5f} m/s\n".format(vAvg))
        filehandle.write("Trendline slope: {:.5f} m/s^2\n".format(slope))
        filehandle.write("Pixels/m: {}\n".format(PPM))
        filehandle.write('N = {}\n'.format(len(times)))
        if delta != -1:
            filehandle.write("Delta: {:.5f}\n".format(delta))
        filehandle.write("\nTimes:\n")
        i = 0
        for i in range(len(times)):
            filehandle.write('{}: {}\n'.format(i+1, times[i]))
        filehandle.write("\nVelocities:\n")
        i = 0
        for i in range(len(times)):
            filehandle.write('{}: {}\n'.format(i+1, velocities[i]))
    filehandle.close()


# ---- MAIN CODE ---- #
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

ppmCalculated = int(
    input("Do you have avg pixels/m already calculated? (1=yes,0=no)\n"))
if ppmCalculated == 1:
    PIXELS_PER_METER = float(input("Input pixels/m: "))
else:
    PIXELS_PER_METER = getAveragePixelPerMeterHorizontal(frame)   # HORIZONTAL
    # PIXELS_PER_METER = getAveragePixelPerMeterVertical(frame)   # VERTICAL
calcDelta = int(input("Calculate delta? (1=yes,0=no)\n"))
out = int(input("Write data to file? (1=yes,0=no)\n"))
if out == 1:
    outfile = input("Enter name of txt file to write to: ")

frame = cv2.resize(frame, (854, 480))
measuringBounds = cv2.selectROI(
    "Select tracking area", frame)  # Select plane that drifter moves thru
cv2.destroyAllWindows()

# pixel_length = measuringBounds[3]  # gets pixel height of selection VERTICAL
pixel_length = measuringBounds[2]  # HORIZONTAL
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

# Getting avg velocity and using it to calculate delta
delta = -1
vAvg = np.sum(velocities) / len(velocities)
str = "\nAverage velocity: {} m/s"
print(str.format(vAvg))
if calcDelta == 1:
    delta = calculateDelta(vAvg)

# Formatting plots
trendline = np.poly1d(np.polyfit(times, velocities, 1))
slope = (trendline(times[1]) - trendline(times[0])) / (times[1]-times[0])
print('trendline slope = {:.5f} m/s^2'.format(slope))
fig, ax = plt.subplots()
fig.text(0, 1, 'm = {}'.format(slope))
ax.plot(times, velocities, 'bo')
ax.set_xlabel('time (s)')
ax.set_ylabel('velocity (m/s)')
ax.set_title(video_path.split('\\')[-1])
ax.plot(times, trendline(times), linestyle='dashed')
if out == 1:
    writeToFile(outfile, delta, times, velocities,
                vAvg, slope, PIXELS_PER_METER)
    plt.savefig(outfile.split('.')[0]+'.png')
plt.show()
