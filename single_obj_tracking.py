import os
from Tkinter import *
import Tkinter as tk
import tkMessageBox
import cv2
import tensorflow as tf
import numpy as np
import os.path
import random
import sys

from pathlib import Path

sys.path.append("./ROLO/utils")
import ROLO_utils as utils

LARGE_FONT = ("Verdana", 12)


class Single_Obj_Tracking(tk.Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)

        self.controller = controller
        self.pageTitle = Label(self, text="Single Object Tracking", font=LARGE_FONT)
        self.pageTitle.grid(row=0, column=0, columnspan=2)
	self.pageTitle2 = Label(self, text="Enter Training Iteration")
        self.pageTitle2.grid(row=1, column=0, columnspan=2)
	self.training_iter_entry = tk.Entry(self)
	self.training_iter_entry.grid(row=2, column=0)
	self.training_iter_button = tk.Button(self, text="Ok", command=self.get_training_iter)
	self.training_iter_button.grid(row=2, column=2, columnspan=2, sticky="we")

        self.browse_button1 = Button(self, text="Training", command=self.train)
        self.browse_button1.grid(row=3, column=0, sticky="we")
	self.browse_button2 = Button(self, text="Testing(yet to implement")
        self.browse_button2.grid(row=4, column=0, sticky="we")
        self.browse_button3 = Button(self, text="Tracking", command=self.demo)
        self.browse_button3.grid(row=5, column=0, sticky="we")
    
    def get_training_iter(self):
	global training_iters1        
	training_iters = self.training_iter_entry.get()
	training_iters1 =int(training_iters)
	
    
    def train(self):
        ROLO_TF()

    def demo(self):

        ''' PARAMETERS '''
        num_steps = 6
        wid = 500
        ht = 500
        basepath = Path("./ROLO/DATA/")
        total = 0
        rolo_avgloss = 0
        yolo_avgloss = 0

        for entry in basepath.iterdir():
            if entry.is_dir():
                folder_path = os.path.join('./ROLO/DATA',entry.name)
                img_fold_path = os.path.join('./ROLO/DATA', entry.name, 'img/')
                gt_file_path = os.path.join('./ROLO/DATA', entry.name, 'groundtruth_rect.txt')
                yolo_out_path = os.path.join('./ROLO/DATA', entry.name, 'yolo_out/')
                rolo_out_path = os.path.join('./ROLO/DATA', entry.name, 'rolo_out_train/')


                paths_imgs = utils.load_folder(img_fold_path)
                paths_rolo = utils.load_folder(rolo_out_path)
                lines = utils.load_dataset_gt(gt_file_path)

                # Define the codec and create VideoWriter object
                # fourcc= cv2.cv.CV_FOURCC(*'DIVX')
                fourcc = cv2.VideoWriter_fourcc(*'DIVX')
                video_name = 'test.avi'
                video_path = os.path.join('output/videos/', video_name)
                video = cv2.VideoWriter(video_path, fourcc, 20, (wid, ht))

                center_points_gt = []
                center_points_rolo = []

                for i in range(len(paths_rolo) - num_steps):
                    id = i + 1
                    test_id = id + num_steps - 2  # * num_steps + 1

                    path = paths_imgs[test_id]
                    img = utils.file_to_img(path)

                    if (img is None): break

                    yolo_location = utils.find_yolo_location(yolo_out_path, test_id)
                    yolo_location = utils.locations_normal(wid, ht, yolo_location)
                    print(yolo_location)

                    rolo_location = utils.find_rolo_location(rolo_out_path, test_id)
                    rolo_location = utils.locations_normal(wid, ht, rolo_location)
                    print(rolo_location)

                    gt_location = utils.find_gt_location(lines, test_id - 1)
                    # gt_location= locations_from_0_to_1(None, 480, 640, gt_location)
                    # gt_location = locations_normal(None, 480, 640, gt_location)
                    # print('gt: ' + str(test_id))
                    # print(gt_location)

                    # calculate centroid
                    # (x1 +x2)/2
                    # (y1 +22)/2
                    l_gt = gt_location
                    center_x = l_gt[0] + (l_gt[2] / 2)
                    center_y = l_gt[1] + (l_gt[3] / 2)
                    center_points_gt.append((center_x, center_y))

                    # todo, fix center calculation
                    l_rolo = rolo_location
                    #center_x = int(l_rolo[0] + (l_rolo[2] / 2))
                    #center_y = int(l_rolo[1] + (l_rolo[3] / 2))
		    center_x = int(l_rolo[0])
                    center_y = int(l_rolo[1])
                    center_points_rolo.append((center_x, center_y))

                    frame = utils.debug_3_locations(
                        img, gt_location, yolo_location, rolo_location,
                        center_points_gt,
                        center_points_rolo
                    )
                    video.write(frame)

                    utils.createFolder(os.path.join('./ROLO/output/frames/', entry.name))
                    frame_name = os.path.join('./ROLO/output/frames/', entry.name, str(test_id) + '.jpg')

                    print(frame_name)
                    cv2.imwrite(frame_name, frame)
                    # cv2.imshow('frame',frame)
                    # cv2.waitKey(100)

                    rolo_loss = utils.cal_rolo_IOU(rolo_location, gt_location)
                    rolo_avgloss += rolo_loss
                    yolo_loss = utils.cal_yolo_IOU(yolo_location, gt_location)
                    yolo_avgloss += yolo_loss
                    total += 1

        rolo_avgloss /= total
        yolo_avgloss /= total
        print("yolo_avg_iou = ", yolo_avgloss)
        print("rolo_avg_iou = ", rolo_avgloss)
        print("rolo_avg_iou = ", rolo_avgloss)
        print("rolo_avg_iou = ", rolo_avgloss)
        video.release()
        cv2.destroyAllWindows()

class ROLO_TF(Single_Obj_Tracking):
    disp_console = False
    restore_weights = True  # False

    # YOLO parameters
    fromfile = None
    tofile_img = './ROLO/test/output.jpg'
    tofile_txt = './ROLO/test/output.txt'
    imshow = True
    filewrite_img = False
    filewrite_txt = False
    yolo_weights_file = './ROLO/YOLO_small.ckpt'
    alpha = 0.1
    threshold = 0.2
    iou_threshold = 0.5
    num_class = 20
    num_box = 2
    grid_size = 7
    classes = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
    w_img, h_img = [352, 240]

    # ROLO Network Parameters
    rolo_weights_file = './ROLO/output/ROLO_model/model_step1_exp2.ckpt'
    # rolo_weights_file = '/u03/Guanghan/dev/ROLO-dev/output/ROLO_model/model_step1_exp2.ckpt'
    lstm_depth = 3
    num_steps = 1  # number of frames as an input sequence
    num_feat = 4096
    num_predict = 6  # final output of LSTM 6 loc parameters
    num_gt = 4
    num_input = num_feat + num_predict  # data input: 4096+6= 5002

    # ROLO Training Parameters
    # learning_rate = 0.00001 #training
    learning_rate = 0.00001  # testing
    #print(training_iter)
    #training_iters = 1  # 100000
    #print(training_iters)
    batch_size = 1  # 128
    display_step = 1

    # tf Graph input
    x = tf.placeholder("float32", [None, num_steps, num_input])
    istate = tf.placeholder("float32", [None, 2 * num_input])  # state & cell => 2x num_input
    y = tf.placeholder("float32", [None, num_gt])

    # Define weights
    weights = {
        'out': tf.Variable(tf.random_normal([num_input, num_predict]))
    }
    biases = {
        'out': tf.Variable(tf.random_normal([num_predict]))
    }

    def __init__(self, argvs=[]):
		    
	print("ROLO INIT")
        self.ROLO(argvs)
    def get_training_iter(self):
        #Set default moves by calling method of parent class
        super(ROLO_TF, self).get_training_iter()
	

    def LSTM_single(self, name, _X, _istate, _weights, _biases):

        # input shape: (batch_size, n_steps, n_input)
        _X = tf.transpose(_X, [1, 0, 2])  # permute num_steps and batch_size
        # Reshape to prepare input to hidden activation
        _X = tf.reshape(_X, [self.num_steps * self.batch_size, self.num_input])  # (num_steps*batch_size, num_input)
        # Split data because rnn cell needs a list of inputs for the RNN inner loop
        _X = tf.split(0, self.num_steps, _X)  # n_steps * (batch_size, num_input)
        # print("_X: ", _X)

        cell = tf.nn.rnn_cell.LSTMCell(self.num_input, self.num_input)
        state = _istate
        for step in range(self.num_steps):
            outputs, state = tf.nn.rnn(cell, [_X[step]], state)
            tf.get_variable_scope().reuse_variables()

        # print("output: ", outputs)
        # print("state: ", state)
        return outputs

    # Experiment with dropout
    def dropout_features(self, feature, prob):
        if prob == 0:
            return feature
        else:
            num_drop = int(prob * 4096)
            drop_index = random.sample(xrange(4096), num_drop)
            for i in range(len(drop_index)):
                index = drop_index[i]
                feature[index] = 0
            return feature

        # Experiment with input box noise (translate, scale)

    def det_add_noise(self, det):
        translate_rate = random.uniform(0.98, 1.02)
        scale_rate = random.uniform(0.8, 1.2)

        det[0] *= translate_rate
        det[1] *= translate_rate
        det[2] *= scale_rate
        det[3] *= scale_rate

        return det

    '''---------------------------------------------------------------------------------------'''

    def build_networks(self):
        if self.disp_console: print "Building ROLO graph..."

        # Build rolo layers
        self.lstm_module = self.LSTM_single('lstm_test', self.x, self.istate, self.weights, self.biases)
        self.ious = tf.Variable(tf.zeros([self.batch_size]), name="ious")
        self.sess = tf.Session()
        self.sess.run(tf.initialize_all_variables())
        self.saver = tf.train.Saver()
        self.saver.restore(self.sess, self.rolo_weights_file)
        if self.disp_console: print "Loading complete!" + '\n'

    def training(self, x_path, y_path):
        total_loss = 0

        if self.disp_console: print("TRAINING ROLO...")
        # Use rolo_input for LSTM training
        pred = self.LSTM_single('lstm_train', self.x, self.istate, self.weights, self.biases)
        if self.disp_console: print("pred: ", pred)
        self.pred_location = pred[0][:, 4097:4101]
        if self.disp_console: print("pred_location: ", self.pred_location)
        if self.disp_console: print("self.y: ", self.y)

        self.correct_prediction = tf.square(self.pred_location - self.y)
        if self.disp_console: print("self.correct_prediction: ", self.correct_prediction)
        self.accuracy = tf.reduce_mean(self.correct_prediction) * 100
        if self.disp_console: print("self.accuracy: ", self.accuracy)
        optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.accuracy)  # Adam Optimizer

        # Initializing the variables
        init = tf.initialize_all_variables()

        # Launch the graph
        with tf.Session() as sess:

            if (self.restore_weights == True):
                sess.run(init)
                self.saver.restore(sess, self.rolo_weights_file)
                print "Loading complete!" + '\n'
            else:
                sess.run(init)

            id = 0

            # Keep training until reach max iterations
            while id * self.batch_size < training_iters1:
                # Load training data & ground truth
                batch_xs = self.rolo_utils.load_yolo_output(x_path, self.batch_size, self.num_steps,
                                                            id)  # [num_of_examples, num_input] (depth == 1)
                print('len(batch_xs)= ', len(batch_xs))
                # for item in range(len(batch_xs)):

                batch_ys = self.rolo_utils.load_rolo_gt(y_path, self.batch_size, self.num_steps, id)
                batch_ys = self.locations_from_0_to_1(self.w_img, self.h_img, batch_ys)

                # Reshape data to get 3 seq of 5002 elements
                batch_xs = np.reshape(batch_xs, [self.batch_size, self.num_steps, self.num_input])
                batch_ys = np.reshape(batch_ys, [self.batch_size, 4])
                if self.disp_console: print("Batch_ys: ", batch_ys)

                pred_location = sess.run(self.pred_location, feed_dict={self.x: batch_xs, self.y: batch_ys,
                                                                        self.istate: np.zeros(
                                                                            (self.batch_size, 2 * self.num_input))})
                if self.disp_console: print("ROLO Pred: ", pred_location)
                # print("len(pred) = ", len(pred_location))
                if self.disp_console: print(
                "ROLO Pred in pixel: ", pred_location[0][0] * self.w_img, pred_location[0][1] * self.h_img,
                pred_location[0][2] * self.w_img, pred_location[0][3] * self.h_img)
                # print("correct_prediction int: ", (pred_location + 0.1).astype(int))

                # Save pred_location to file
                utils.save_rolo_output(self.output_path, pred_location, id, self.num_steps, self.batch_size)

                sess.run(optimizer, feed_dict={self.x: batch_xs, self.y: batch_ys,
                                               self.istate: np.zeros((self.batch_size, 2 * self.num_input))})
                if id % self.display_step == 0:
                    # Calculate batch loss
                    loss = sess.run(self.accuracy, feed_dict={self.x: batch_xs, self.y: batch_ys, self.istate: np.zeros(
                        (self.batch_size, 2 * self.num_input))})
                    if self.disp_console: print "Iter " + str(
                        id * self.batch_size) + ", Minibatch Loss= " + "{:.6f}".format(
                        loss)  # + "{:.5f}".format(self.accuracy)
                    total_loss += loss
                id += 1
                if self.disp_console: print(id)

                # show 3 kinds of locations, compare!

            print "Optimization Finished!"
            avg_loss = total_loss / id
            print "Avg loss: " + str(avg_loss)
            save_path = self.saver.save(sess, self.rolo_weights_file)
            print("Model saved in file: %s" % save_path)

        return avg_loss

    def train_30_2(self):
        print("TRAINING ROLO...")
        log_file = open("./ROLO/output/training-step1-exp2.txt",
                        "a")  # open in append mode
        self.build_networks()

        pred = self.LSTM_single('lstm_train', self.x, self.istate, self.weights, self.biases)
        self.pred_location = pred[0][:, 4097:4101]
        self.correct_prediction = tf.square(self.pred_location - self.y)
        self.accuracy = tf.reduce_mean(self.correct_prediction) * 100
        self.learning_rate = 0.00001
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(
            self.accuracy)  # Adam Optimizer

        # Initializing the variables
        init = tf.initialize_all_variables()

        # for in in video_list:
        #    choose(i)

        # Launch the graph
        with tf.Session() as sess:
            if (self.restore_weights == True):
                sess.run(init)
                self.saver.restore(sess, self.rolo_weights_file)
                print "Loading complete!" + '\n'
            else:
                sess.run(init)


            folders = os.listdir("./ROLO/DATA/")
            for folder_name in folders:
                output_path = os.path.join('ROLO/DATA', folder_name, 'rolo_out_train/')
                y_path = os.path.join('ROLO/DATA', folder_name, 'groundtruth_rect.txt')
                x_path = os.path.join('ROLO/DATA', folder_name, 'yolo_out/')
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                self.output_path = output_path

              
                id = 1
                total_loss = 0

                # Keep training until reach max iterations
                while id < training_iters1 - self.num_steps:
                    # Load training data & ground truth
                    batch_xs = self.rolo_utils.load_yolo_output_test(x_path, self.batch_size, self.num_steps,
                                                                     id)  # [num_of_examples, num_input] (depth == 1)

                    # Apply dropout to batch_xs
                    # for item in range(len(batch_xs)):
                    #    batch_xs[item] = self.dropout_features(batch_xs[item], 0)

                    # print(id)
                    batch_ys = self.rolo_utils.load_rolo_gt_test(y_path, self.batch_size, self.num_steps, id)
                    batch_ys = utils.locations_from_0_to_1(self.w_img, self.h_img, batch_ys)

                    # Reshape data to get 3 seq of 5002 elements
                    batch_xs = np.reshape(batch_xs, [self.batch_size, self.num_steps, self.num_input])
                    batch_ys = np.reshape(batch_ys, [self.batch_size, 4])
                    if self.disp_console: print("Batch_ys: ", batch_ys)

                    pred_location = sess.run(self.pred_location, feed_dict={self.x: batch_xs, self.y: batch_ys,
                                                                            self.istate: np.zeros(
                                                                                (self.batch_size, 2 * self.num_input))})
                    if self.disp_console: print("ROLO Pred: ", pred_location)
                    # print("len(pred) = ", len(pred_location))
                    if self.disp_console: print(
                    "ROLO Pred in pixel: ", pred_location[0][0] * self.w_img, pred_location[0][1] * self.h_img,
                    pred_location[0][2] * self.w_img, pred_location[0][3] * self.h_img)
                    # print("correct_prediction int: ", (pred_location + 0.1).astype(int))

                    # Save pred_location to file
                    utils.save_rolo_output_test(self.output_path, pred_location, id, self.num_steps, self.batch_size)

                    sess.run(self.optimizer, feed_dict={self.x: batch_xs, self.y: batch_ys,
                                                        self.istate: np.zeros((self.batch_size, 2 * self.num_input))})
                    if id % self.display_step == 0:
                        # Calculate batch loss
                        loss = sess.run(self.accuracy, feed_dict={self.x: batch_xs, self.y: batch_ys, self.istate: np.zeros(
                            (self.batch_size, 2 * self.num_input))})
                        if self.disp_console: print "Iter " + str(
                            id * self.batch_size) + ", Minibatch Loss= " + "{:.6f}".format(
                            loss)  # + "{:.5f}".format(self.accuracy)
                        total_loss += loss
                    id += 1
                    if self.disp_console: print(id)

                # print "Optimization Finished!"
                avg_loss = total_loss / id
                #print "Avg loss: " + folder_name + ": " + str(avg_loss)

                log_file.write(str("{:.3f}".format(avg_loss)) + '  ')

                log_file.write('\n')
                save_path = self.saver.save(sess, self.rolo_weights_file)
                #print("Model saved in file: %s" % save_path)
		tkMessageBox.showinfo("Average Loss", "Avg loss: " + folder_name + ": " + str(avg_loss))
		tkMessageBox.showinfo("Success", "Model successfully \n Saved in " + save_path)
            # tkMessageBox.showinfo("ERROR", "File already exists")
        log_file.close()
        return

    def ROLO(self, argvs):

        self.rolo_utils = utils.ROLO_utils()
        self.rolo_utils.loadCfg()
        self.params = self.rolo_utils.params

        arguments = self.rolo_utils.argv_parser(argvs)

        if self.rolo_utils.flag_train is True:
            self.training(utils.x_path, utils.y_path)
        elif self.rolo_utils.flag_track is True:
            self.build_networks()
            self.track_from_file(utils.file_in_path)
        elif self.rolo_utils.flag_detect is True:
            self.build_networks()
            self.detect_from_file(utils.file_in_path)
        else:
            self.train_30_2()
