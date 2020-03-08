import os
import cv2
import numpy as np
import tensorflow as tf
import argparse
import sys
import tensorflow as tf
from tensorflow.keras.models import load_model

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class Camera(object):
    def __init__(self):
        self.curr_steering_angle = 90
        self.objects = None
        self.setup_lane()
        self.setup_object()
        self.camera_setup()

    def camera_setup(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')
        self.camera.set(3,640)
        self.camera.set(4,480)

    def setup_lane(self):
        navigation_model_path = 'training data/trained model/lane/lane_navigation_final.h5'
        self.navigation_model = load_model(navigation_model_path)

    def setup_object(self):
        PATH_TO_CKPT = './trainingData/trained model/sign/fine_tuned_model/frozen_inference_graph.pb'
        PATH_TO_LABELS = './trainingData/trained model/sign/fine_tuned_model/object-detection.pbtxt'
        NUM_CLASSES = 10
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')
 
    def show_lane(self,frame):
        self.curr_steering_angle = compute_steering_angle(frame, self.navigation_model)
        lane_lines, frame = detect_lane(frame)
        frame = display_heading_line(frame, self.curr_steering_angle)
        return frame

    def show_object(self,frame,Laneframe=None):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_expanded = np.expand_dims(frame_rgb, axis=0)

            # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: frame_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        if not Laneframe:
            Laneframe = frame

        vis_util.visualize_boxes_and_labels_on_image_array(
            Laneframe,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.85)
        self.objects = get_objects(classes,self.category_index,scores)
        return Laneframe
    
    def get_frame(self,isLaneDetect,isObjectDetect):
        ret, img = self.camera.read()
        if ret:
            if isLaneDetect:
                laneImg = self.show_lane(img)
                if isObjectDetect:
                    img = self.show_object(img,laneImg)
                else:
                    img = laneImg
            else:
                if isObjectDetect:
                    img = self.show_object(img)
                 
            return cv2.imencode('.jpg',img)[1].tobytes(),self.curr_steering_angle,self.objects


#detect and Display Lane
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

def adjust_brightness(image):
    #print("adjust_brightness")
    # increase or decrease brightness by 30%
    brightness = img_aug.Multiply(3.0)
    image = brightness.augment_image(image)
    return image

#Stearing Angle Computation

def compute_steering_angle(frame, model):
    #print("compute_steering_angle")
    preprocessed = img_preprocess(frame)
    X = np.asarray([preprocessed])
    steering_angle = model.predict(X)[0]
    return int(steering_angle + 0.5)  # round the nearest integer

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


#find objects
def get_objects(classes,category_index,scores):
    o = []
    threshold = 0.98 # in order to get higher percentages you need to lower this number; usually at 0.01 you get 100% predicted objects
    for index, value in enumerate(classes[0]):
        object_dict = {}
        if scores[0, index] > threshold:
            object_dict[(category_index.get(value)).get('name').encode('utf8')] = \
                        scores[0, index]
            o.append(object_dict.keys())
    return o