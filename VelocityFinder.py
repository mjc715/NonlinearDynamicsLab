import cv2
import matplotlib.pyplot as plt

measuring_length = .4  # meters
camera_fps = 30  # frames per second
video_path = "ANMR0002.mp4"


def get_frames(video_path):
    video = cv2.VideoCapture(video_path)
    while (video.isOpened()):
        rete, frame = video.read()
        if rete:
            yield frame
        else:
            break
        video.release()
        yield None


def get_frame(video_path, index):  # Just in case I want to look at a particular frame
    counter = 0
    video = cv2.VideoCapture(video_path)
    while video.isOpened():
        rete, frame = video.read()
        if rete:
            if counter == index:
                return frame
            counter += 1
        else:
            break
    video.release()
    return None


def get_ball_frame(video_path):  # Finds start and end frames
    counter = 0
    video = cv2.VideoCapture(video_path)
    while video.isOpened():
        rete, frame = video.read()
        if counter == 0:
            rect = cv2.selectROI(frame)
            cv2.destroyAllWindows()
        # Cropping img to check for presence of ball in set area
        frame_crop = frame[int(rect[1]):int(rect[1]+rect[3]),
                           int(rect[0]):int(rect[0]+rect[2])]
        gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)
        # OpenCV threshold to isolate white pixels (ping pong ball)
        ret, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
        pixels = cv2.countNonZero(thresh)
        print('Scanning frames...')
        if rete and ret:
            if pixels > 400:  # If enough white pixels, it means the ball is in the zone, return frame
                s = "Hit on frame {}"
                print(s.format(counter))
                return frame, counter
            counter += 1
        else:
            break
    video.release()
    return None


# Gets ball start frame and image
start_img, start_index = get_ball_frame(video_path)
# Gets ball end frame and image
end_img, end_index = get_ball_frame(video_path)
print(start_index)
print(end_index)
# Get velocity by using the measuring length, cam fps, and start/end frames
velocity = measuring_length / (1 / camera_fps * (end_index - start_index))
string = 'Average ball vertical velocity: {} m/s'
print(string.format(velocity))

# Showing start and end images to check for correctness
plt.imshow(start_img)
plt.show()
plt.imshow(end_img)
plt.show()
