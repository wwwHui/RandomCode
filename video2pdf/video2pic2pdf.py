#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@Time   : 2021/01/13 10:20
@author : hui
@file   : main.py
@desc   : 视频中提取图片 图片去重 转PDF
          增加删除不合适图片
"""

import os
import cv2
import datetime
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import multiprocessing
import shutil
# from skimage.measure import compare_ssim
from skimage.metrics import structural_similarity
# 高版本（>=0.16）的 skimage 删掉了compare_ssim 其功能由 skimage.metrics 下的 structural_similarity 实现


# 从视频中提取帧
def get_frame(path, video_name, video_capture="./capture_image", time_rate=100, work_index=False):
    """从视频中提取帧

    :param path: 视频所在文件夹
    :param video_name: 视频文件名
    :param video_capture: 保存图片文件夹
    :param time_rate: 提取图片的时间间隔，单位是秒
    :param work_index: int 仅用于标识线程，无实际作用
    :return: True
    """
    video_path = os.path.join(path, video_name)
    file, extension = os.path.splitext(video_name)
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    pic_index = 0
    FPS = round(cap.get(5))  # 视频帧率 这个是小数，这里四舍五入
    FPS_rate = FPS * time_rate  # 需要提取的 FPS 间隔 time_rate 单位是秒
    print(datetime.datetime.now(), video_name, FPS)
    ret = True
    while ret:
        ret, frame = cap.read()
        frame_index += 1
        if frame_index % FPS_rate == 0:
            pic_index += 1
            if work_index:
                print(datetime.datetime.now(), "{}, work_index {:0>3d}, pic {:0>3d}, frame {}" .
                      format(video_name, work_index, pic_index, frame_index))
            else:
                print(datetime.datetime.now(), "{}, pic {:0>3d}, frame {}" .
                      format(video_name, pic_index, frame_index))
            # 这里就可以做一些操作了：显示截取的帧图片、保存截取帧到本地
            out_file = video_capture + '/{}-{:0>3d}-{}.jpg'.format(file, pic_index, frame_index)
            cv2.imwrite(out_file, frame)  # 这里是将截取的图像保存在本地

        cv2.waitKey(0)

    cap.release()
    print(datetime.datetime.now(), "{}, 共{}张图片" .format(video_name, pic_index))
    return True


# 读取某一类文件
def get_file_list(path, extension='.mp4'):
    """从文件夹中读取某一类文件

    :param path: 文件夹
    :param extension: 后缀
    :return:
    """
    file_lists = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_extension = os.path.splitext(file)[1]  # 文件后缀 （带点） 例 .mp4
            if file_extension == extension:
                file_lists.append(file)
    return file_lists


# 搜索图片边界
def get_edges(img):
    """搜索图片边界

    :param img: 图片
    :return: left, right, top, bottom
    """
    image = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
    img = cv2.medianBlur(image, 5)  # 中值滤波，去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)  # 调整裁剪效果
    binary_image = b[1]  # 二值图--具有三通道
    binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
    # print(binary_image.shape)  # 改为单通道

    x = binary_image.shape[0]
    # print("高度x=", x)
    y = binary_image.shape[1]
    # print("宽度y=", y)
    edges_x = []
    edges_y = []
    for i in range(x):
        for j in range(y):
            if binary_image[i][j] == 255:
                edges_x.append(i)
                edges_y.append(j)
    if edges_x:
        left = min(edges_x)  # 左边界
        right = max(edges_x)  # 右边界
    else:
        left = 0
        right = x
    width = right - left  # 宽度
    if edges_y:
        bottom = min(edges_y)  # 底部
        top = max(edges_y)  # 顶部
    else:
        bottom = 0
        top = y
    height = top - bottom  # 高度

    # pre1_picture = image[left:left + width, bottom:bottom + height]  # 图片截取
    return left, right, top, bottom  # 返回图片数据


# 剪切图片
def cut_img(img):
    """搜索图片边界并剪切

    :param img: 图片
    :return: img_new
    """
    left, right, top, bottom = get_edges(img)
    bottom += 1
    left += 1
    # img_new = img.crop((bottom, left, top, right))
    img_new = img[left:right, bottom:top]
    return img_new


# 图片转pdf
def pic_to_pdf(pic_file_lists, pic_folder, pdf_name):
    """图片转pdf

    :param pic_file_lists: list 图片名
    :param pic_folder: 图片所在文件夹
    :param pdf_name: 输出的pdf路径
    :return:
    """
    img_list = []
    i = 0
    # print(pic_file_lists)
    while i < len(pic_file_lists):
        if i + 1 < len(pic_file_lists):
            img_name_1 = pic_file_lists[i]
            img_name_2 = pic_file_lists[i + 1]
            if img_name_1[:3] == img_name_2[:3]:
                img_1 = Image.open(os.path.join(os.path.join(pic_folder, img_name_1)))
                img_2 = Image.open(os.path.join(os.path.join(pic_folder, img_name_2)))
                width_1, height_1 = img_1.size[0], img_1.size[1]
                width_2, height_2 = img_2.size[0], img_2.size[1]
                i = i + 2
            else:
                img_1 = Image.open(os.path.join(os.path.join(pic_folder, img_name_1)))
                width_1, height_1 = img_1.size[0], img_1.size[1]
                img_2 = Image.new('RGB', (width_1, height_1), "#FFFFFF")
                width_2 = width_1
                height_2 = height_1
                i = i + 1
        else:
            img_1 = Image.open(os.path.join(os.path.join(pic_folder, img_name_1)))
            width_1, height_1 = img_1.size[0], img_1.size[1]
            img_2 = Image.new('RGB', (width_1, height_1), "#FFFFFF")
            width_2 = width_1
            height_2 = height_1
            i = i + 1

        # 合并图片
        new_width = width_1 if width_1 > width_2 else width_2
        new_height = int(11 * (height_1 + height_2) / 10)
        joint = Image.new('RGB', (new_width, new_height), "#FFFFFF")
        joint.paste(img_1, (0, 0))
        joint.paste(img_2, (0, height_1))

        # 左下角增加文字
        joint = add_text(joint, img_name_1[4:12])

        img_list.append(joint)

    img0 = img_list.pop(0)
    img0.save(pdf_name, "PDF", resolution=100.0, save_all=True, append_images=img_list)
    print("输出文件名称：", pdf_name)


# 为图片添加文字
def add_text(img, text):
    """在图片左下角添加文字

    :param img: 图片
    :param text: 文字
    :return:图片
    """
    width = img.width
    height = img.height
    font_size = int(0.25 * height / 11)
    font = ImageFont.truetype("C:\Windows\Fonts\simsun.ttc", font_size)
    # 设置文字颜色
    position = (int(width / 10), height - 3*font_size)
    # 添加文字
    draw = ImageDraw.Draw(img)
    # 显示图片
    draw.text(position, text, fill='black', font=font, direction=None)
    return img


# 处理利用多线程提取视频帧
def multiprocessing_get_frame(video_folder, video_file_lists, video_capture, work_index):
    """

    :param video_folder: 视频所在文件夹
    :param video_file_lists: 视频名列表
    :param video_capture: 输出文件夹
    :param work_index: 编号
    :return:
    """
    for video_name in video_file_lists:
       get_frame(video_folder, video_name, video_capture, work_index=work_index)
    return video_file_lists


# 处理不合适图片 删除重复 删除全黑等
def get_right_pic(file_list, file_folder, out_folder, out_del_folder='del_pic'):
    """处理不合适图片

    :param file_list: 图片文件名list
    :param file_folder: 图片所在文件夹
    :param out_folder: 输出文件夹
    :param out_del_folder: 部分丢弃图片（不重复但不合适的图片）文件夹
    :return:
    """
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    else:
        shutil.rmtree(out_folder)
        os.makedirs(out_folder)

    if not os.path.exists(out_del_folder):
        os.makedirs(out_del_folder)
    else:
        shutil.rmtree(out_del_folder)
        os.makedirs(out_del_folder)

    diff_pic_list = []
    img_compare = cv2.imread(os.path.join(file_folder, file_list[0]))
    diff_pic_list.append(file_list[0])
    cv2.imwrite(os.path.join(out_folder, file_list[0]), cut_img(img_compare))
    # shutil.copy(os.path.join(file_folder, file_list[0]), out_folder)
    print(datetime.datetime.now(), file_list[0], '合适图片')
    for index in range(1, len(file_list)):
        similarity = False
        file = file_list[index]
        img_new = cv2.imread(os.path.join(file_folder, file))
        if img_compare.shape == img_new.shape:
            # ssim = compare_ssim(img_compare, img_new, multichannel=True)
            ssim = structural_similarity(img_compare, img_new, multichannel=True)
            if ssim > 0.9:  # 重复图片
                similarity = True

        if similarity:
            print(datetime.datetime.now(), file, '重复')
        else:  # 不重复图片
            save, img_cut = img_need_save(img_new, file)
            if save:
                diff_pic_list.append(file)
                img_compare = img_new
                cv2.imwrite(os.path.join(out_folder, file), img_cut)
                # shutil.copy(os.path.join(file_folder, file), out_folder)
                print(datetime.datetime.now(), file, '合适图片')
            else:
                print(datetime.datetime.now(), file, '不合适')
                # 不重复 也不合适的图片复制到 out_del_folder
                shutil.copy(os.path.join(file_folder, file), out_del_folder)

    return diff_pic_list


def img_need_save(img, file):
    """判断图片是否合适

    :param img:图片
    :param file:文件名，仅用于测试时的打印
    :return:True or Fasle, img_cut
    """
    img_cut = cut_img(img)
    (mean, stddv) = cv2.meanStdDev(img_cut)
    m0, m1, m2 = mean[:,0]
    if m0 < 20 and m1 < 20 and m2 < 20:  # 几乎全黑的图片
        return False, img_cut
    
    (mean, stddv) = cv2.meanStdDev(img)
    hist = cv2.calcHist([img], [0], None, [256], [0, 255])
    m0, m1, m2 = mean[:,0]
    s0, s1, s2 = stddv[:, 0]
    height = img.shape[0]
    width = img.shape[1]
    channel = img.shape[2]

    # if '2' in file:
    #     print(file, img.shape)
    #     if m0 < 200 and m1 < 200 and m2 < 200:
    #         print(m0, m1, m2,  max(hist[25:225,:]), '**************')
    #     else:
    #         print(m0, m1, m2, max(hist[25:225,:]))
    #     print(s0, s1, s2)
    #     if '2020' in file:
    #         # hist = hist[25:225,:]
    #         from matplotlib import pyplot as plt
    #         plt.plot(hist, color="r")
    #         plt.title(file)
    #         plt.show()

    if max(hist[25:225, 0]) > 9000 and m0 < 200 and m1 < 200 and m2 < 200 and s0+s1+s2<300:
        return False, img_cut
    return True, img_cut


# 视频处理
def video_process(video_folder, video_capture, num_workers=30, extension='.mp4'):
    """利用多线程从视频中提取图片

    :param video_folder:视频文件夹
    :param video_capture:图片文件夹
    :param num_workers:线程数，若为0，则为单线程
    :return:
    """

    if not os.path.exists(video_capture):
        os.makedirs(video_capture)
    else:
        shutil.rmtree(video_capture)
        os.makedirs(video_capture)

    if num_workers < 0:
        print('参数错误, num_workers', num_workers)
        return

    # 将视频文件夹下的视频文件名提取出来
    video_file_lists = get_file_list(video_folder, extension)
    print(video_file_lists)

    if num_workers == 0:  # 单线程
        get_frame(video_folder, video_file_lists, video_capture)
    else:  # 多线程
        video_batch_size = len(video_file_lists) // num_workers + 1
        pool = multiprocessing.Pool(processes=num_workers)
        res_list = []
        for i in range(0, num_workers):
            video_lists = []
            for j in range(video_batch_size):
                index = i + j * num_workers
                if index < len(video_file_lists):
                    video_lists.append(video_file_lists[index])
            res = pool.apply_async(multiprocessing_get_frame, (video_folder, video_lists, video_capture, i, ))
            res_list.append(res)
        pool.close()
        pool.join()

        for i, r in enumerate(res_list):
            print(datetime.datetime.now(), '进程池{}处理完成，处理的视频文件有：'.format(i))
            print(r.get())
        print('图片提取完成')


# 运行函数
def run():
    """
    优先显示函数内的多行注释
    """

    video_folder = '../videofile'  # 视频存放文件夹
    video_capture = 'capture_image'  # 截图所在文件夹
    pic_folder = 'diff_pic'  # 图片过滤后所在文件夹

    # 提取视频帧
    # video_process(video_folder, video_capture)

    # 读取图片
    pic_file_lists = get_file_list(video_capture, '.jpg')
    # 过滤图片
    get_right_pic(pic_file_lists, video_capture, pic_folder)
    # 图片转pdf
    pic_file_lists = get_file_list(pic_folder, '.jpg')
    pic_to_pdf(pic_file_lists, pic_folder, 'out2.pdf')

    # file = '043.20201013-009-27000.jpg'
    # img = cv2.imread(os.path.join(video_capture, file))
    # img_need_save(img, file)


# 主函数
if __name__ == '__main__':
    s_time = datetime.datetime.now()
    print(s_time, '程序开始运行')
    run()
    e_time = datetime.datetime.now()
    print(e_time, '运行结束，耗时', e_time - s_time)
