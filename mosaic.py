#coding:utf-8

import os
import sys
import random
import argparse
import numpy as np
from PIL import Image

def getImages(file_dir):
    files = os.listdir(file_dir)
    images = []
    # cnt = 0
    for file in files:
        # cnt+=1
        filePath = os.path.abspath(os.path.join(file_dir,file))
        try:
            fp = open(filePath,"rb")
            image = Image.open(fp)
            images.append(image)
            image.load()
            fp.close()   #节约资源
        except:
            print ("Invail Images : %s" % (filePath))
    # print ("cnt= %d"%cnt)
    return images

def get_Average_RGB(images):
    image  = np.array(images)
    # print image
    w,h,d= image.shape
    return tuple(np.average(image.reshape(w * h,d) ,axis=0))

def splitImage(image,size):
    W = image.size[0]
    H = image.size[1]
    m , n = size
    w = int(W / n)
    h = int(H / m)
    images = []
    for i in range(m):
        for j in range(n):
            images.append(image.crop((j * w, i * h, (j + 1) * w,(i + 1) * h)))
    return images

def get_best_match(input_avg,avgs):
    avg = input_avg
    index = 0
    min_index = 0
    min_dis = float("inf")
    for val in avgs:
        dis = ((val[0] - avg[0]) ** 2 + (val[1] - avg[1]) ** 2 + (val[2] - val[2]) ** 2)
        if dis  < min_dis:
            min_dis = dis
            min_index = index
        index += 1

    return min_index

def creatImageGrid(images,dims):
    m,n = dims
    assert m * n == len(images)

    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])

    #创建输出图像
    grid_img = Image.new('RGB',(n * width, m * height))

    for index in range(len(images)):
        row = int(index / n)
        col = index - n * row
        grid_img.paste(images[index] , (col * width, row * height))

    return grid_img

def creat_mosaic(target_image, input_image, grid_size, reuse_image = True):
    print ("splitting image now...")
    target_image = splitImage(target_image,grid_size)
    print ("Finding image match...")
    output_image = []
    cnt = 0
    batch_size = int(len(target_image) / 10)
    avgs = []
    for img in input_image:
        avgs.append(get_Average_RGB(img))

    for img in target_image:
        avg = get_Average_RGB(img)
        mathch_index = get_best_match(avg,avgs)
        output_image.append(input_image[mathch_index])

        if cnt > 0 and batch_size > 10 and (cnt % batch_size) == 0 :
            print ("processing %d of %d ..." % (cnt,len(target_image)))
        cnt += 1
        if not reuse_image:
            input_image.remove(mathch_index)

    mosaic_image = creatImageGrid(output_image,grid_size)
    return mosaic_image


if __name__ == "__main__":
    args = 128,128
    # 载入目标图像
    target_image = Image.open("source.png")
    # 从目录下读入小块图像
    print('Reading input images...')
    input_images = getImages("DataSet")
    # 判断小块图像列表是否为空
    if input_images == []:
        print("No input images found in %s. Exiting")
        exit()
    random.shuffle(input_images) # 是否使用随机列表,来增加输出的多样性
    grid_size = 64,64 # 打码的小方块大小
    output_filename = 'mosaic.png' # 输出文件名
    reuse_images = True # 是否允许重用输入的图片
    resize_input = True  # 是否调整输入图片的大小来适应网格

    # 如果不能重复利用图片, 验证 m*n <= num_of_images 是否成立
    if not reuse_images:
        if grid_size[0] * grid_size[1] > len(input_images):
            print('grid size less than number of images')
            exit()
    # 重新调整输入图片的大小
    if resize_input:
        # 根据给定的网格大小，统计宽度和高度的最大值
        dims = (int(target_image.size[0] / grid_size[1]),
                int(target_image.size[1] / grid_size[0]))
        # 调整图片大小
        for img in input_images:
            img.thumbnail(dims)

    mosaic_image = creat_mosaic(target_image, input_images, grid_size, reuse_images)  # 创建照片马赛克
    mosaic_image.save(output_filename, 'PNG')# 保存 mosaic 到文件
    print('Done.')
