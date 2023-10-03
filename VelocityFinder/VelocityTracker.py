import cv2
import matplotlib.pyplot as plt
import sys
import numpy as np


def getAveragePixelPerMeterHorizontal(frame):
    frame = cv2.resize(frame, (854, 480))
    measuringBounds = cv2.selectROI(
        "Select reference 1", frame
    )  # Select reference near camera
    cv2.destroyAllWindows()
    refLength1 = float(input("What is the length of the selection in meters?\n"))
    pixelPerMeter1 = measuringBounds[2] / refLength1

    measuringBounds = cv2.selectROI(
        "Select reference 2", frame
    )  # Select reference far from camera
    cv2.destroyAllWindows()
    refLength2 = float(input("What is the length of the selection in meters?\n"))
    pixelPerMeter2 = measuringBounds[2] / refLength2
    avgPPM = 0.5 * (pixelPerMeter1 + pixelPerMeter2)
    print("Average pixels/m: {}\n".format(avgPPM))
    return avgPPM


def getAveragePixelPerMeterVertical(frame):
    frame = cv2.resize(frame, (854, 480))
    measuringBounds = cv2.selectROI(
        "Select reference 1", frame
    )  # Select reference near camera
    cv2.destroyAllWindows()
    refLength1 = float(input("What is the length of the selection in meters?\n"))
    pixelPerMeter1 = measuringBounds[3] / refLength1

    measuringBounds = cv2.selectROI(
        "Select reference 2", frame
    )  # Select reference far from camera
    cv2.destroyAllWindows()
    refLength2 = float(input("What is the length of the selection in meters?\n"))
    pixelPerMeter2 = measuringBounds[3] / refLength2
    avgPPM = 0.5 * (pixelPerMeter1 + pixelPerMeter2)
    print(avgPPM)
    return avgPPM


def calculateDelta(vAvg):
    # --- Parameters for calculating delta if desired
    FLUID_VISCOSITY = 8.927 * 10**-7  # kinematic viscosity m^2/s
    FLUID_DENSITY = 997  # kg/m^3
    SPHERE_RADIUS = 0.02  # meters
    GRAVITY = 9.81  # m/s^2
    EQ_CONSTANT = (3 / 2) * (
        (3 * FLUID_VISCOSITY * vAvg) / (SPHERE_RADIUS**2 * FLUID_DENSITY)
    )
    a = 2 * GRAVITY
    b = a - EQ_CONSTANT
    c = 2 * EQ_CONSTANT
    deltas = np.roots([a, -b, -c])
    str = "Delta value: {} \n\n"
    print(str.format(deltas[0]))


def writeToFileVel(outfile, delta, times, velocities, vAvg, slope, PPM):
    with open(outfile, "w") as filehandle:
        filehandle.write("Average velocity: {:.5f} m/s\n".format(vAvg))
        filehandle.write("Trendline slope: {:.5f} m/s^2\n".format(slope))
        filehandle.write("Pixels/m: {}\n".format(PPM))
        filehandle.write("N = {}\n".format(len(times)))
        if delta != -1:
            filehandle.write("Delta: {:.5f}\n".format(delta))
        filehandle.write("\nTimes:\n")
        i = 0
        for i in range(len(times)):
            filehandle.write("{}: {}\n".format(i + 1, times[i]))
        filehandle.write("\nVelocities:\n")
        i = 0
        for i in range(len(times)):
            filehandle.write("{}: {}\n".format(i + 1, velocities[i]))
    filehandle.close()


def writeToFilePos(outfile, times, pos, slope):
    with open(outfile, "w") as filehandle:
        filehandle.write("Trendline slope: {:.5f} m/s\n".format(slope))
        filehandle.write("N = {}\n".format(len(times)))
        filehandle.write("\nTimes (s):\n")
        i = 0
        for i in range(len(times)):
            filehandle.write("{}: {}\n".format(i + 1, times[i]))
        filehandle.write("\nPositions (m):\n")
        i = 0
        for i in range(len(times)):
            filehandle.write("{}: {}\n".format(i + 1, pos[i]))
        i = 0
        filehandle.write("\nPoints:\n")
        for i in range(len(times)):
            filehandle.write("{}: ({}, {})\n".format(i + 1, times[i], pos[i]))
    filehandle.close()


def verticalTracking(
    releaseFrame,
    numPoints,
    video_path,
    tracker_type,
    video,
    positionVSTime,
    out,
    outfile,
    calcDelta,
    measuringBounds,
    PIXELS_PER_METER,
):
    if not video.isOpened():
        print("Video not opened")
        sys.exit()

    i = 1
    while i <= releaseFrame:
        rete, frame = video.read()
        i += 1

    if not rete:
        print("Cant read video file")
        sys.exit()
    trackingPoints = []
    if not positionVSTime:
        frame = cv2.resize(frame, (854, 480))
        measuringBounds = cv2.selectROI(
            "Select tracking area", frame
        )  # Select plane that drifter moves thru
        cv2.destroyAllWindows()
        trackingPoints, interval = np.linspace(
            measuringBounds[1],
            measuringBounds[1] + measuringBounds[3],
            numPoints,
            retstep=True,
        )  # returns various heights to get velocity at (VERTICAL)

    params = cv2.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.filterByColor = True
    params.blobColor = 150
    params.minCircularity = 0.8

    tracker = cv2.TrackerKCF_create()
    frame = cv2.resize(frame, (854, 480))

    objectBounds = cv2.selectROI("Select object", frame)
    cv2.destroyAllWindows()
    initialPos = objectBounds[1]
    rete = tracker.init(frame, objectBounds)
    p1, prev = None, None
    frameCount, prevFrame, speed = releaseFrame, 0, 0
    trackingCount = numPoints  # VERTICAL
    velocities, times, pos = [], [], []

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
            p2 = (
                int(objectBounds[0] + objectBounds[2]),
                int(objectBounds[1] + objectBounds[3]),
            )
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            cv2.putText(
                frame,
                "Tracking failure detected",
                (100, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 0, 255),
                2,
            )
        totalTime = (frameCount - releaseFrame) / camera_fps
        currentPosition = objectBounds[1]
        if positionVSTime and totalTime % 0.25 == 0:
            times.append(totalTime)
            pos.append(initialPos - currentPosition)
        if (
            not positionVSTime
            and trackingCount >= 0
            and objectBounds[1] <= trackingPoints[trackingCount]
        ):
            timeInterval = (frameCount - prevFrame) / camera_fps
            length = interval / PIXELS_PER_METER
            speed = length / timeInterval
            velocities.append(speed)
            times.append(totalTime)
            prevFrame = frameCount
            trackingCount -= 1

        cv2.putText(
            frame,
            "Velocity : {}".format(float(speed)),
            (100, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.putText(
            frame,
            tracker_type + " Tracker",
            (100, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.putText(
            frame,
            "FPS : {}".format(int(fps)),
            (100, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.imshow("Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()

    # This removes the points in the first half second, they are unstable
    i = 0
    t = 0
    if not positionVSTime:
        while t <= 0.5 and i < numPoints - 1:
            t = times[i]
            i += 1
        times = times[i:]
        velocities = velocities[i:]

    # Getting avg velocity and using it to calculate delta
    if not positionVSTime:
        delta = -1
        vAvg = np.sum(velocities) / len(velocities)
        str = "\nAverage velocity: {} m/s"
        print(str.format(vAvg))
        if calcDelta == 1:
            delta = calculateDelta(vAvg)

    # Formatting plots
    fig, ax = plt.subplots()
    if positionVSTime:
        pos = [x / PIXELS_PER_METER for x in pos]
        trendline = np.poly1d(np.polyfit(times, pos, 1))
        slope = (trendline(times[1]) - trendline(times[0])) / (times[1] - times[0])
        print("trendline slope = {:.5f} m/s".format(slope))
        ax.plot(times, pos, "bo")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("position (m)")
    else:
        trendline = np.poly1d(np.polyfit(times, velocities, 1))
        slope = (trendline(times[1]) - trendline(times[0])) / (times[1] - times[0])
        print("trendline slope = {:.5f} m/s^2".format(slope))
        fig.text(0, 1, "m = {}".format(slope))
        ax.plot(times, velocities, "bo")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("velocity (m/s)")
    ax.set_title(video_path.split("\\")[-1])
    ax.plot(times, trendline(times), linestyle="dashed")
    fig.text(0, 1, "m = {}".format(slope))
    if out and positionVSTime:
        writeToFilePos(outfile, times, pos, slope)
        plt.savefig(outfile.split(".")[0] + ".png")
    elif out:
        writeToFileVel(outfile, delta, times, velocities, vAvg, slope, PIXELS_PER_METER)
        plt.savefig(outfile.split(".")[0] + ".png")
    plt.show()
    return None


def horizontalTracking(
    releaseFrame,
    numPoints,
    video_path,
    tracker_type,
    video,
    positionVSTime,
    out,
    outfile,
    calcDelta,
    measuringBounds,
    PIXELS_PER_METER,
):
    if not video.isOpened():
        print("Video not opened")
        sys.exit()

    i = 1
    while i <= releaseFrame:
        rete, frame = video.read()
        i += 1

    if not rete:
        print("Cant read video file")
        sys.exit()

    trackingPoints = []
    if not positionVSTime:
        frame = cv2.resize(frame, (854, 480))
        measuringBounds = cv2.selectROI(
            "Select tracking area", frame
        )  # Select plane that drifter moves thru
        cv2.destroyAllWindows()
        trackingPoints, interval = np.linspace(
            measuringBounds[0],
            measuringBounds[0] + measuringBounds[2],
            numPoints,
            retstep=True,
        )  # returns various points to get velocity at

    params = cv2.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.filterByColor = True
    params.blobColor = 150
    params.minCircularity = 0.8

    tracker = cv2.TrackerCSRT_create()
    frame = cv2.resize(frame, (854, 480))

    objectBounds = cv2.selectROI("Select object", frame)
    cv2.destroyAllWindows()
    initalPos = objectBounds[0] + objectBounds[2]
    rete = tracker.init(frame, objectBounds)
    p1, prev = None, None
    frameCount, prevFrame, speed = releaseFrame, 0, 0
    trackingCount = 0  # HORIZONTAL
    velocities, times, pos = [], [], []

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
            p2 = (
                int(objectBounds[0] + objectBounds[2]),
                int(objectBounds[1] + objectBounds[3]),
            )
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            cv2.putText(
                frame,
                "Tracking failure detected",
                (100, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 0, 255),
                2,
            )
        totalTime = (frameCount - releaseFrame) / camera_fps
        currentPosition = objectBounds[0] + objectBounds[2]

        if positionVSTime and totalTime % 0.25 == 0:
            times.append(totalTime)
            pos.append(currentPosition - initalPos)
        if (
            not positionVSTime
            and trackingCount <= numPoints - 1
            and objectBounds[0] >= trackingPoints[trackingCount]
        ):
            # This is to graph positions
            timeInterval = (frameCount - prevFrame) / camera_fps
            length = interval / PIXELS_PER_METER
            speed = length / timeInterval
            velocities.append(speed)
            times.append(totalTime)
            prevFrame = frameCount
            trackingCount += 1

        cv2.putText(
            frame,
            "Velocity : {}".format(float(speed)),
            (100, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.putText(
            frame,
            tracker_type + " Tracker",
            (100, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.putText(
            frame,
            "FPS : {}".format(int(fps)),
            (100, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2,
        )
        cv2.imshow("Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()

    # This removes the points in the first half second
    i = 0
    t = 0
    if not positionVSTime:
        while t <= 0.5 and i < numPoints - 1:
            t = times[i]
            i += 1
        times = times[i:]
        velocities = velocities[i:]

    # Getting avg velocity and using it to calculate delta
    if not positionVSTime:
        delta = -1
        vAvg = np.sum(velocities) / len(velocities)
        str = "\nAverage velocity: {} m/s"
        print(str.format(vAvg))
        if calcDelta == 1:
            delta = calculateDelta(vAvg)

    # Formatting plots
    fig, ax = plt.subplots()
    if positionVSTime:
        pos = [x / PIXELS_PER_METER for x in pos]
        trendline = np.poly1d(np.polyfit(times, pos, 1))
        slope = (trendline(times[1]) - trendline(times[0])) / (times[1] - times[0])
        print("trendline slope = {:.5f} pixels/s".format(slope))
        ax.plot(times, pos, "bo")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("position (m)")
    else:
        trendline = np.poly1d(np.polyfit(times, velocities, 1))
        slope = (trendline(times[1]) - trendline(times[0])) / (times[1] - times[0])
        print("trendline slope = {:.5f} m/s^2".format(slope))
        ax.plot(times, velocities, "bo")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("velocity (m/s)")
    fig.text(0, 1, "m = {}".format(slope))
    ax.set_title(video_path.split("\\")[-1])
    ax.plot(times, trendline(times), linestyle="dashed")
    if out and positionVSTime:
        writeToFilePos(outfile, times, pos, slope)
        plt.savefig(outfile.split(".")[0] + ".png")
    elif out:
        writeToFileVel(outfile, delta, times, velocities, vAvg, slope, PIXELS_PER_METER)
        plt.savefig(outfile.split(".")[0] + ".png")
    plt.show()
    return None


# ---- MAIN CODE ---- #
# --- PARAMETERS
horizontal = True  # Horizontal or vertical movement
positionVSTime = True  # Position vs time or velocity vs time
out = True  # True = output data to file
calcDelta = False  # Calculates delta coefficient
PIXELS_PER_METER = 262  # Pixels per meter in video, leave at 0 to calculate in program
video_path = "Wave Tank Vids\Group_25hz\ANMR0178.mp4"
measuring_length = 2.35  # in meters
releaseFrame = 330  # this is the frame where we start measuring motion
numPoints = 16  # number of times velocity will be calculated (vel vs time only)
camera_fps = 30  # frames per second
tracker_type = "CSRT"

if out:
    outfile = input("Enter name of text file to output to:")
else:
    outfile = ""

video = cv2.VideoCapture(video_path)
rete, frame = video.read()

if PIXELS_PER_METER == 0 and horizontal:
    PIXELS_PER_METER = getAveragePixelPerMeterHorizontal(frame)
elif PIXELS_PER_METER == 0 and not horizontal:
    PIXELS_PER_METER = getAveragePixelPerMeterVertical(frame)

if not positionVSTime:
    measuringBounds = cv2.selectROI(
        "Select tracking area", frame
    )  # Select plane that drifter moves thru
    cv2.destroyAllWindows()
else:
    measuringBounds = []

if horizontal:
    horizontalTracking(
        releaseFrame,
        numPoints,
        video_path,
        tracker_type,
        video,
        positionVSTime,
        out,
        outfile,
        calcDelta,
        measuringBounds,
        PIXELS_PER_METER,
    )
else:
    verticalTracking(
        releaseFrame,
        numPoints,
        video_path,
        tracker_type,
        video,
        positionVSTime,
        out,
        outfile,
        calcDelta,
        measuringBounds,
        PIXELS_PER_METER,
    )  # Use if tracking vertical velocity
