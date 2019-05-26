# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 13:36:50 2019

Own "trial-and-error" version of CNN training
@author: NeilDG
"""

import numpy as np
import tensorflow as tf
import cv2
from model import read_depth as rd
from model import fcrn_model as fcrn
from model import tensorboard_writer as tb
from matplotlib import pyplot as plt
from model import tensor_util as tu

KITTI_REDUCED_H = 128; KITTI_REDUCED_W = 416;

#First train: Last layer - Using NYU-  No inpaint LR = 0.5
#Train #2: All layers - From scratch - No inpaint LR = 0.5
#Train #3: Last layer - Using NYU - With inpaint
#Train #4: All layers - From scratch - With inpaint
class CNN(object):
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.epoch = 500
        self.learning_rate = 0.01
        self.batch_size = 4
        
        
    def parse_function(self, filenameRGB, fileNameDepth):
        image_string = tf.read_file(filenameRGB)
    
        # Don't use tf.image.decode_image, or the output shape will be undefined
        image = tf.image.decode_png(image_string, channels=3)
        image = tf.image.convert_image_dtype(image, tf.uint8, saturate = True)
    
        resizedRGB = tf.image.resize_images(image, [KITTI_REDUCED_H, KITTI_REDUCED_W])
        
        image_string = tf.read_file(fileNameDepth)
        image = tf.image.decode_png(image_string, channels = 1)
        #image = tf.image.adjust_contrast(image, 5.0)
        #image = tf.image.adjust_saturation(image, 3.0)
        image = tf.image.convert_image_dtype(image, tf.uint8, saturate = True)
        #image = rd.depth_read_image(image)
        
        resizedDepth = tf.image.resize_images(image, [KITTI_REDUCED_H, KITTI_REDUCED_W])
        return resizedRGB, resizedDepth
    
    def create_feature(self, inputImage, depthImage = None):
        if depthImage == None:
            mask = tf.ones_like(inputImage)
            feature_image = tu.reduce_features(inputImage, mask)
        else:
            feature_image = tu.reduce_features(inputImage,depthImage)
                
        return feature_image
    
    def create_convNet(self, inputImage, depthImage = None): 
        
        with tf.variable_scope("cnn", reuse = tf.AUTO_REUSE):
            
            if depthImage == None:
                mask = tf.ones_like(inputImage)
            else:
                mask = tu.reduce_features(inputImage,depthImage)
                           
            #conv1 = fcrn.conv(input=feature_image,name='conv1',stride=2,kernel_size=(7,7),num_filters=64, trainable = False)
            #bn_conv1 = fcrn.batch_norm(input=conv1,name='bn_conv1',relu=True)
            #pool1 = tf.nn.max_pool(bn_conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME',name='pool1')
            
            conv1, _ = fcrn.sparse_conv(inputImage, mask, filters = 64, kernel_size = (7,7), strides = 2)
            bn_conv1 = fcrn.batch_norm(input=conv1,name='bn_conv1',relu=True)
            pool1 = tf.nn.max_pool(bn_conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME',name='pool1')
            
            res2a_relu = fcrn.build_res_block(input=pool1,block_name='2a',d1=64,d2=256,projection=True,down_size=False,trainable = True)
            res2b_relu = fcrn.build_res_block(input=res2a_relu,block_name='2b',d1=64,d2=256,trainable = True)
            res2c_relu = fcrn.build_res_block(input=res2b_relu,block_name='2c',d1=64,d2=256,trainable = True)
            
            res3a_relu = fcrn.build_res_block(input=res2c_relu,block_name='3a',d1=128,d2=512,projection=True,trainable = True)
            res3b_relu = fcrn.build_res_block(input=res3a_relu,block_name='3b',d1=128,d2=512,trainable = True)
            res3c_relu = fcrn.build_res_block(input=res3b_relu,block_name='3c',d1=128,d2=512,trainable = True)
            res3d_relu = fcrn.build_res_block(input=res3c_relu,block_name='3d',d1=128,d2=512,trainable = True)
            
            res4a_relu = fcrn.build_res_block(input=res3d_relu,block_name='4a',d1=256,d2=1024,projection=True,trainable = True)
            res4b_relu = fcrn.build_res_block(input=res4a_relu,block_name='4b',d1=256,d2=1024,trainable = True)
            
            res5a_relu = fcrn.build_res_block(input=res4b_relu,block_name='5a',d1=512,d2=2048,projection=True,trainable = True)
            res5b_relu = fcrn.build_res_block(input=res5a_relu,block_name='5b',d1=512,d2=2048,trainable = True)
            
            layer1 = fcrn.conv_new(input=res5b_relu,name='layer1',stride=1,kernel_size=(1,1),num_filters=1024,trainable = True)
            layer1_BN = fcrn.batch_norm(input=layer1,name='layer1_BN',relu=False)
            
            # UP-CONV
            up_2x = fcrn.build_up_conv_block(input=layer1_BN,block_name='2x',num_filters=512, trainable = True)
            up_4x = fcrn.build_up_conv_block(input=up_2x, block_name='4x', num_filters=256, trainable = True)
            up_8x = fcrn.build_up_conv_block(input=up_4x, block_name='8x', num_filters=128, trainable = True)
            up_16x = fcrn.build_up_conv_block(input=up_8x, block_name='16x', num_filters = 64, trainable = True)
            #results to 128 x 416 if 2x - 4x. 256 x 832 if 2x - 4x - 8x.  512 x 1664 for 2x - 4x - 8x - 16x
            
            drop = tf.nn.dropout(up_16x, keep_prob = 1., name='drop')
            #im_1 = fcrn.conv_new(input=drop,name='ConvIntermediate_1',stride=1,kernel_size=(3,3),num_filters=64, trainable = True)
            #im_2 = fcrn.conv_new(input=im_1,name='ConvIntermediate_2',stride=1,kernel_size=(3,3),num_filters=64, trainable = True)
            #im_3 = fcrn.conv_new(input=im_2,name='ConvIntermediate_3',stride=1,kernel_size=(3,3),num_filters=64, trainable = True)
            #im_4 = fcrn.conv_new(input=im_3,name='ConvIntermediate_4',stride=1,kernel_size=(3,3),num_filters=64, trainable = True)
            #im_5 = fcrn.conv_new(input=im_4,name='ConvIntermediate_5',stride=1,kernel_size=(3,3),num_filters=64, trainable = True)
            pred = fcrn.conv(input=drop,name='ConvPred',stride=1,kernel_size=(3,3),num_filters=1, trainable = True)
            pred = tf.image.resize_bicubic(pred, [KITTI_REDUCED_H, KITTI_REDUCED_W])
            print("Pred CNN shape: ", pred, "Pred type: ", type(pred))
        return pred
    
    def train(self):

        trainData = self.dataset.map(map_func = self.parse_function, num_parallel_calls=4)
        batchRun = trainData.batch(self.batch_size)
        trainData = batchRun.prefetch(2)
        
        iterator = trainData.make_initializable_iterator()
        initOp = iterator.initializer
        image_rgbs, image_depths = iterator.get_next()
        
        print("Finished pre-processing train data with iterator: ", iterator)

        trainPred = self.create_convNet(image_rgbs, image_depths)
        
        ground_truths = image_depths
        ground_truths = tf.cast(ground_truths, tf.float32)
        
        loss = tf.losses.huber_loss(labels = ground_truths, predictions = trainPred)
        #weights = tf.Variable(tf.truncated_normal([KITTI_REDUCED_H * KITTI_REDUCED_W, 10]))
        #regularizer = tf.nn.l2_loss(weights)
        #loss = tf.reduce_mean(loss + (0.01 * regularizer))
        
        optimizer = tf.train.AdamOptimizer(learning_rate = self.learning_rate, beta1=0.9, beta2=0.999, epsilon=1e-08).minimize(loss)
        #optimizer = tf.train.MomentumOptimizer(learning_rate = self.learning_rate, momentum = 0.5, use_nesterov = True).minimize(loss)
        globalVar = tf.global_variables_initializer()
        print("Successful optimizer setup")
        
        # Define the different metrics
        with tf.variable_scope("metrics"): 
            metrics = {"mean_squared_error" : tf.metrics.mean_squared_error(labels = ground_truths, predictions = trainPred),
                       "rmse" : tf.metrics.root_mean_squared_error(labels = ground_truths, predictions = trainPred)}
            tf.summary.scalar('cnn_scratch/mean_squared_error', tf.reduce_mean(metrics["mean_squared_error"]))
            tf.summary.scalar('cnn_scratch/rmse', tf.reduce_mean(metrics["rmse"]))

            #tb.logGradients(loss, "cnn/layer2x_Conv/kernel:0", "cnn/2x")
            #tb.logGradients(loss, "cnn/layer4x_Conv/kernel:0", "cnn/4x")
            #tb.logGradients(loss, "cnn/layer8x_Conv/kernel:0", "cnn/8x")
            #tb.logGradients(loss, "cnn/layer16x_Conv/kernel:0", "cnn_Up16x/16x")
            #tb.logGradients(loss,"cnn/ConvIntermediate_1/kernel:0", "cnn_Intermediate/ConvPred/intermediate")
            tb.logGradients(loss,"cnn/ConvPred/kernel:0", "cnn_scratch/ConvPred/last_layer")
        
        # Group the update ops for the tf.metrics, so that we can run only one op to update them all
        update_metrics_op = tf.group(*[op for _, op in metrics.values()])
        
        # Get the op to reset the local variables used in tf.metrics, for when we restart an epoch
        metric_variables = tf.get_collection(tf.GraphKeys.LOCAL_VARIABLES, scope="metrics")
        metricsInitOp = tf.variables_initializer(metric_variables)
        merged = tf.summary.merge_all()
        trainWriter = tf.summary.FileWriter('train/train_result', tf.Session().graph)
        
        #for testing
        testInput = tf.placeholder(dtype = tf.float32, shape = (self.batch_size, KITTI_REDUCED_H, KITTI_REDUCED_W, 3), name = "test_input")
        testPred = self.create_convNet(testInput)
        
        saver = tf.train.Saver()  
        
#        feature_images = self.create_feature(image_rgbs,image_depths)
#        with tf.Session() as sess:
#            sess.run(globalVar) #init weights, biases and other variables
#            sess.run(initOp)
#            
#            while True:
#                try:
#                    rgbImages = sess.run(image_rgbs)
#                    depthImages = sess.run(image_depths)
#                    result = sess.run(feature_images)
#                    for i in range(self.batch_size):
#                        print("RGB shape: ", np.shape(rgbImages[i]), " Depth shape: ", np.shape(depthImages[i]))
#                        plt.imshow(rgbImages[i].astype("uint8")); plt.show()
#                        plt.imshow(depthImages[i][:,:,0]); plt.show()
#                        plt.imshow(result[i][:,:,0]); plt.show()
#                
#                except tf.errors.OutOfRangeError:
#                    print("Finished all batch")
#                    break
#            
        sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
        with sess:
            sess.run(globalVar) #init weights, biases and other variables
            sess.run(initOp)
            sess.run(metricsInitOp)
            # Restore variables from disk.
            #saver.restore(sess, "tmp/model_0331_intermediate.ckpt") 
            
            for i in range(self.epoch):
                while True:
                  try:
                    opt = sess.run([optimizer, loss])
                    print("Optimizing! ", opt)
                    sess.run(update_metrics_op)
                  except tf.errors.OutOfRangeError:
                    print("End of sequence, looping to next epoch ", (i+1))
                    sess.run(initOp)
                    #test image
                    inputImages = sess.run(image_rgbs)
                    depthImages = sess.run(image_depths)
                    predDepth = sess.run(testPred, feed_dict = {testInput: inputImages})
                    print("Pred depth values: " ,predDepth[0][:,:,0])
                    print("Ground truth depth values: ", depthImages[0][:,:,0])
                    plt.imshow(inputImages[0].astype("uint8")); plt.show()
                    plt.imshow(predDepth[0][:,:,0].astype("uint16")); plt.show()
                    plt.imshow(depthImages[0][:,:,0].astype("uint16")); plt.show()
                    
                    sess.run(initOp) #re-initialize iterator again for next epoch
                    
                    #save data
                    #save_path = saver.save(sess, "tmp/model_0331_intermediate.ckpt")
                    #print("Weights saved in path: %s" %save_path)
                    break                   

                # Get the values of the metrics
                metrics_values = {k: v[0] for k, v in metrics.items()}
                metrics_val = sess.run(metrics_values)
                print("Metrics", metrics_val)
                
                summary = sess.run(merged)
                trainWriter.add_summary(summary)
                
        
    def inpaintDepth(self, depthImage, rgbImage):
        _,binaryInv = cv2.threshold(depthImage, 0, 1, cv2.THRESH_BINARY_INV)
        binaryInv = binaryInv.astype("uint8")
        plt.imshow(binaryInv); plt.show()
        inpaintImg = cv2.inpaint(depthImage, binaryInv, 32, cv2.INPAINT_TELEA)
        plt.imshow(inpaintImg); plt.show()
        #plt.imshow(rgbImage); plt.show()
        
        return inpaintImg
    
    def writeImg(self, rgbImg, depthImg, rgbImgName, depthImgName):
        BASE_RGB_DIR = "C:/Users/NeilDG/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/train_rgb_inpaint/"
        BASE_DEPTH_DIR = "C:/Users/NeilDG/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/train_depth_inpaint/"
        
        cv2.imwrite(BASE_RGB_DIR + rgbImgName + ".png", rgbImg)
        cv2.imwrite(BASE_DEPTH_DIR + depthImgName + ".png", depthImg)
        print("Image write successful", BASE_RGB_DIR, "  ", BASE_DEPTH_DIR)
                
                
                

            
        
        

