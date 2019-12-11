# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 19:37:01 2019

Constants files
@author: delgallegon
"""

"""
DIRECTORY FOR PC
"""
SAVE_PATH_RGB = 'C:/NN_Dataset/warp_rgb_orig/'
SAVE_PATH_WARP = 'C:/NN_Dataset/warp_rgb_mod/'
SAVE_PATH_RGB_CROPPED = 'C:/NN_Dataset/warp_rgb_cropped/'

SAVE_PATH_RGB_VAL = 'C:/NN_Dataset/warp_rgb_orig_val/'
SAVE_PATH_WARP_VAL = 'C:/NN_Dataset/warp_rgb_mod_val/'
SAVE_PATH_RGB_CROPPED_VAL = 'C:/NN_Dataset/warp_rgb_cropped_val/'

SAVE_PATH_UNSEEN_DATA = 'C:/NN_Dataset/unseen_data_orig/'
SAVE_PATH_UNSEEN_DATA_RGB = 'C:/NN_Dataset/unseen_data_rgb/'
SAVE_PATH_UNSEEN_DATA_WARP = 'C:/NN_Dataset/unseen_data_warp/'

SAVE_PATH_PREDICT = 'D:/Users/delgallegon/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/warp_rgb_predict/'
IMAGE_PATH_PREDICT = 'D:/Users/delgallegon/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/warp_img_predictions/'
IMAGE_PATH_EDGES = 'D:/Users/delgallegon/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/img_edges/'

IMAGE_RGB_DIR = "D:/Users/delgallegon/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/train_rgb/"

"""
DIRECTORY FOR LAPTOP
"""
#SAVE_PATH_RGB = 'D:/NN_Dataset/warp_rgb_orig/'
#SAVE_PATH_WARP = 'D:/NN_Dataset/warp_rgb_mod/'
#SAVE_PATH_RGB_CROPPED = 'D:/NN_Dataset/warp_rgb_cropped/'

#
#SAVE_PATH_RGB_VAL = 'D:/NN_Dataset/warp_rgb_orig_val/'
#SAVE_PATH_WARP_VAL = 'D:/NN_Dataset/warp_rgb_mod_val/'
#SAVE_PATH_UNSEEN_DATA = 'D:/NN_Dataset/unseen_data_orig/'
#SAVE_PATH_UNSEEN_DATA_RGB = 'D:/NN_Dataset/unseen_data_rgb/'
#SAVE_PATH_UNSEEN_DATA_WARP = 'D:/NN_Dataset/unseen_data_warp/'

#SAVE_PATH_PREDICT = 'D:/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/warp_rgb_predict/'
#IMAGE_PATH_PREDICT = 'D:/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/warp_img_predictions/'

#IMAGE_RGB_DIR = "D:/Documents/GithubProjects/NeuralNets-ImageDepthExperiment/dataset/train_rgb/" #LAPTOP dir

IMAGE_W = 1242; IMAGE_H = 375
WARP_W = 1442; WARP_H = 575

PADDING_CONSTANT = 100

if __name__=="__main__": #FIX for broken pipe num_workers issue.
    print()
