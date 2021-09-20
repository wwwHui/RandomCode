#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@Time   : 2021/09/19 14:48
@author : hui
@file   : main.py
@desc   : 依据打印要求，分离PDF中的彩色和黑白页面
            参考连接  https://www.cnblogs.com/neuedu/p/14188218.html
"""

import datetime
import fitz
from PyPDF2 import PdfFileReader, PdfFileWriter


# 提取PDF页面
def run():
    """
    提取PDF页面
    """
    path = 'file.pdf'  # 原始PDF地址
    out_color_path = "out-color.pdf"  # 彩色PDF保存地址
    out_gray_path = "out-gray.pdf"  # 黑白PDF保存地址
    double_sided = True  # True:表示双面打印 False:表示单面打印
    save_img = True  # 是否保存PDF中的图片
    pdf_document = fitz.open(path)
    color_pages = set()
    for index, page in enumerate(pdf_document.pages()):
        images = pdf_document.get_page_images(index)
        for image in images:
            xref = image[0]
            pix = fitz.Pixmap(pdf_document, xref)
            img_path = "pic/p{:0>4d}-{}-{}-{}.png".format(index, xref, pix.n, pix.colorspace.name)
            if pix.colorspace.name == 'DeviceGray':  # 黑白图
                if save_img:
                    pix.save(img_path)
                continue
            else:   # 彩色图
                if double_sided:
                    if index % 2 :
                        color_pages.add(index-1)
                        color_pages.add(index)
                    else:
                        color_pages.add(index)
                        color_pages.add(index+1)
                        index += 1
                else:
                    color_pages.add(index)
                if save_img:
                    if pix.colorspace.name == 'DeviceCMYK':
                        pix = fitz.Pixmap(fitz.csRGB, pix)   # CMYK 需要转为 RGB 才可以保存到 PNG
                    pix.save(img_path)
                else:
                    break
        index += 1
    # print(color_page_list)

    pdf = PdfFileReader(path)
    color_pdf_writer = PdfFileWriter()
    gray_pdf_writer = PdfFileWriter()
    for index in range(pdf.getNumPages()):
        page = pdf.getPage(index)
        if index in color_pages:
            color_pdf_writer.addPage(page)
        else:
            gray_pdf_writer.addPage(page)

    with open(out_color_path, "wb") as out:
        color_pdf_writer.write(out)
        print(datetime.datetime.now(), "created", out_color_path)
    
    with open(out_gray_path, "wb") as out:
        gray_pdf_writer.write(out)
        print(datetime.datetime.now(), "created", out_gray_path)



# 主函数
if __name__ == '__main__':
    s_time = datetime.datetime.now()
    print(s_time, '程序开始运行')
    run()
    e_time = datetime.datetime.now()
    print(e_time, '运行结束，耗时', e_time - s_time)
