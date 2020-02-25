import cv2
import sys
from hand_coded_lane_follower import HandCodedLaneFollower

def save_image_and_steering_angle(image_file):
    lane_follower = HandCodedLaneFollower()
    frame = cv2.imread(image_file + '.jpg')

    lane_follower.follow_lane(frame)
    cv2.imwrite("%s_%03d.png" % (image_file, lane_follower.curr_steering_angle), frame)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    for i in range(27):
        save_image_and_steering_angle('image'+str(i))