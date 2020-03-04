import os
import cv2
from base_camera import BaseCamera

import numpy as np
import logging
import math
import datetime
import sys
from imgaug import augmenters as img_aug
from tensorflow.keras.models import load_model
import tensorflow as tf

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class Camera(object):
    video_source = 0
    curr_steering_angle = 90
    objects=[]
    def __init__(self):
        self.navigation_model_path = 'training data/trained model/lane/lane_navigation_final.h5'
        self.navigation_model = load_model(self.navigation_model_path)
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')
        self.camera.set(3, 640)
        self.camera.set(4, 480)
        self.OBJECT_MODEL_NAME = 'SIGN DETECTION MODEL'
        self.PATH_TO_CKPT = './training data/trained model/fine_tuned_model/frozen_inference_graph.pb'
        self.PATH_TO_LABELS = './training data/trained model/fine_tuned_model/label_map.pbtxt'
        self.NUM_CLASSES = 10
        self.object_model = load_model(self.PATH_TO_CKPT)
        self.cat_index = label_map_util.create_category_index_from_labelmap(self.PATH_TO_LABELS, use_display_name=True)

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    def get_frame(self,laneDetection,objectDetection):
        ret, img = self.camera.read()
        if ret:
            
            if laneDetection:
                Laneimg,Camera.curr_steering_angle = follow_lane(img,self.navigation_model,laneDetection)
            if objectDetection:
                Laneimg, objects = show_object(self.object_model,img,Laneimg,self.cat_index)
            return cv2.imencode('.jpg',Laneimg)[1].tobytes(), Camera.curr_steering_angle,Camera.objects

def follow_lane(frame,navigation_model,detectLane):
    ##print("follow_lane")
    # Main entry point of the lane follower
    curr_steering_angle = 90
    if detectLane:
        curr_steering_angle = compute_steering_angle(frame, navigation_model)
        lane_lines, frame = detect_lane(frame)
        frame = display_heading_line(frame, curr_steering_angle)
    return frame,curr_steering_angle

def show_object(model, image, laneImg,category_index):
    # Actual detection.
    output_dict = run_inference_for_single_image(model, image)
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        laneImg,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=8)
    return image,output_dict


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis,...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key:value[0, :num_detections].numpy() 
                    for key,value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
    
    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                output_dict['detection_masks'], output_dict['detection_boxes'],
                image.shape[0], image.shape[1])      
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                        tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
        
    return output_dict
def preprocessImage(image):
    brightness = img_aug.Multiply(4.0)
    image = brightness.augment_image(image)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return image


def detect_lane(frame):
    ##print("detect_lane")
    frameProcessed = preprocessImage(frame)
    edges = detect_edges(frameProcessed)

    cropped_edges = region_of_interest(edges)

    line_segments = detect_line_segments(cropped_edges)
    line_segment_image = display_lines(frame, line_segments)

    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)

    return lane_lines, lane_lines_image


def average_slope_intercept(frame, line_segments):
    ##print("average_slope_intercept")
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    # left lane line segment should be on left 2/3 of the screen
    left_region_boundary = width * (1 - boundary)
    # right lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines


def make_points(frame, line):
    #print("make_point")
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


def detect_line_segments(cropped_edges):
    #print("detect_line_segments")
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=8,
                                    maxLineGap=4)
    return line_segments


def region_of_interest(canny):
    #print("region_of_interest")
    height, width = canny.shape
    mask = np.zeros_like(canny)

    # only focus bottom half of the screen

    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image


def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    #print("display_lines")
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2),
                         line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def detect_edges(frame):
    #print("detect_edges")
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([30, 40, 0])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges


def compute_steering_angle(frame, model):
    #print("compute_steering_angle")
    preprocessed = img_preprocess(frame)
    X = np.asarray([preprocessed])
    steering_angle = model.predict(X)[0]
    return int(steering_angle + 0.5)  # round the nearest integer


def adjust_brightness(image):
    #print("adjust_brightness")
    # increase or decrease brightness by 30%
    brightness = img_aug.Multiply(3.0)
    image = brightness.augment_image(image)
    return image


def img_preprocess(image):
    #print("img_preprocess")
    height, _, _ = image.shape
    image = adjust_brightness(image)
    # remove top half of the image, as it is not relevant for lane following
    image = image[int(height/2):, :, :]
    # Nvidia model said it is best to use YUV color space
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.GaussianBlur(image, (15, 15), 0)
    # input image size (200,66) Nvidia model
    image = cv2.resize(image, (200, 66))
    # normalizing, the processed image becomes black for some reason.  do we need this?
    image = image / 255
    return image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    #print("display_heading_line")
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
    return heading_image

############################
# Test Functions
############################


def test_photo(file):
    model = load_model(
        'training data/trained model/lane/lane_navigation_final.h5')
    frame = cv2.imread(file)
    combo_image = follow_lane(frame, model)
    cv2.imshow('final', combo_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_video(video_file):
    model = load_model(
        'training data/trained model/lane/lane_navigation_final.h5')
    cap = cv2.VideoCapture(video_file + '.avi')
    # skip first second of video.
    for i in range(3):
        _, frame = cap.read()

    try:
        while cap.isOpened():
            _, frame = cap.read()
            combo_image = follow_lane(frame, model)
            cv2.imshow("Deep Learning", combo_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    #test_video('../lane-detection/data/outpy')
    #test_photo('/home/pi/DeepPiCar/models/lane_navigation/data/images/video01_100_084.png')
    test_photo('./training data/lane/image11.jpg')
    # test_video(sys.argv[1])
