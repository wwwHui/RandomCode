#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023-09-21 20:30:33
@File    :   invoice.py
@Author  :   hui
@Version :   V0.1
@Desc    :   说明
'''

import os
import cv2
import fitz
import datetime
import easyocr
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


def get_all_files(file_dir):
    res = {}
    count = 0
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.upper() not in ['.PDF']: continue
            path = os.path.join(root, file)
            key = root.removeprefix(file_dir)
            key = key.replace('\\', '-').strip('-')
            if key in res.keys():
                res[key].append(path)
            else:
                res[key] = [path]
            # print(key, path)
            count += 1
    print(datetime.datetime.now(), '共{}个文件.'.format(count))
    return res

def get_images_of_pages(path):
    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat    = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
    doc = fitz.open(path)
    # images = [page.get_pixmap(matrix=mat) for page in doc] # render page to an image
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        text = page.get_text()
        print(text)
    return images

 

def get_info(files, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cache_dir = '.cache'
    os.makedirs(cache_dir, exist_ok=True)
    reader = easyocr.Reader(['ch_sim','en'], gpu = False) # need to run only once to load model into memory
    res = []
    mat = fitz.Matrix(5, 5)  # 数字越大 图片越清晰
    qrCodeDetector = cv2.QRCodeDetector()
    for key, file_list in files.items():
        for file in file_list:
            name, ext = os.path.splitext(os.path.basename(file))
            # print(name)
            parts = name.split('_')
            info = {
                '类型': key,
                '就诊日期': parts[0][:-2],
                '票据代码': parts[1],
                '票据号码': parts[2]
            }
            doc = fitz.open(file)
            # text = doc[0].get_text()
            pix = doc[0].get_pixmap(matrix=mat)
            # print(doc[0].get_text())
            # print(pix.width, pix.height, pix.h, pix.w)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
            # print(type(img), img.shape)
            image = Image.fromarray(img)
            image.save("output_image.png")
            # tmp_path = os.path.join(cache_dir, 'tmp.png')
            # pix.save(tmp_path)
            # # print(text)
            
            qr_text, bbox, straight_qrcode = qrCodeDetector.detectAndDecode(img)
            # print(qr_text)
            parts = qr_text.split(',')
            if len(parts) == 7:
                info['qr_text'] = qr_text
                info['qr-票据代码'] = parts[2]
                info['qr-票据号码'] = parts[3]
                info['qr-验证码'] = parts[4]
                info['qr-日期'] = parts[5]
                info['qr-金额'] = parts[6]

            # info = parse_info(reader, img, info)
            # result = reader.readtext(tmp_path)
            res.append(info)
    out_path = os.path.join(out_dir, 'invoice-info-utf8.csv') 
    pd.DataFrame(res).to_csv(out_path, index_label='index', encoding='utf-8')
    out_path = os.path.join(out_dir, 'invoice-info-gbk.csv') 
    pd.DataFrame(res).to_csv(out_path, index_label='index', encoding='gbk')


def parse_info(reader, img, info):
    results = reader.readtext(img)
    for result in results:
        print(type(result), len(result))
        print(result[0], result[1], result[2])
    exit(0)
    return info


def merge_invoice_pdf(files, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    pdf_merger = fitz.open()
    toc = []
    for key, file_list in files.items():
        out_path = os.path.join(out_dir, 'key.csv') 
        toc.append([1, key, pdf_merger.page_count])
        for file in file_list:
            doc = fitz.open(file)
            pdf_merger.insert_pdf(doc, from_page=0, to_page=0)
            name, ext = os.path.splitext(os.path.basename(file))
            toc.append([2, name, pdf_merger.page_count])
            doc.close()
    # print(toc)
    pdf_merger.set_toc(toc)
    out_path = os.path.join(out_dir, 'merge.pdf')
    pdf_merger.save(out_path)
    pdf_merger.close()

def function_run():
    file_dir = '../发票'
    out_dir = 'out'
    files = get_all_files(file_dir)
    get_info(files, out_dir)

    merge_invoice_pdf(files, out_dir)


if __name__ == '__main__':
    t0 = datetime.datetime.now()
    print(t0, 'start')
    function_run()
    t1 = datetime.datetime.now()
    print(t1, 'over, time:', t1-t0)