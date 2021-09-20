#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@Time   : 2021/09/19 14:48
@author : hui
@file   : main.py
@desc   :  依据打印要求，分离PDF中的彩色和黑白页面
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
    pdf_document = fitz.open(path)
    color_page_list = []
    index = 0
    while index < len(pdf_document):
        for image in pdf_document.getPageImageList(index):
            xref = image[0]
            pix = fitz.Pixmap(pdf_document, xref)
            if pix.n > 1:  # 彩图
                if double_sided:
                    if index % 2 :
                        color_page_list.append(index-1)
                        color_page_list.append(index)
                    else:
                        color_page_list.append(index)
                        color_page_list.append(index+1)
                        index += 1
                else:
                    color_page_list.append(index)
                break
        index += 1
    print(color_page_list)

    pdf = PdfFileReader(path)
    color_pdf_writer = PdfFileWriter()
    gray_pdf_writer = PdfFileWriter()
    for index in range(pdf.getNumPages()):
        page = pdf.getPage(index)
        if index in color_page_list:
            color_pdf_writer.addPage(page)
        else:
            gray_pdf_writer.addPage(page)

    with open(out_color_path, "wb") as out:
        color_pdf_writer.write(out)
        print("created", out_color_path)
    
    with open(out_gray_path, "wb") as out:
        gray_pdf_writer.write(out)
        print("created", out_gray_path)


# 主函数
if __name__ == '__main__':
    s_time = datetime.datetime.now()
    print(s_time, '程序开始运行')
    run()
    e_time = datetime.datetime.now()
    print(e_time, '运行结束，耗时', e_time - s_time)
