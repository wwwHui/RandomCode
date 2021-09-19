#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@Time   : 2021/09/19 14:48
@author : hui
@file   : main.py
@desc   :  依据打印要求，提取PDF中的彩图页面
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
    out_path = "out.pdf"  # 输出PDF地址
    double_sided = True  # True:表示双面打印 False:表示单面打印
    pdf_document = fitz.open(path)
    page_list = []
    index = 0
    while index < len(pdf_document):
        for image in pdf_document.getPageImageList(index):
            xref = image[0]
            pix = fitz.Pixmap(pdf_document, xref)
            if pix.n > 1:  # 彩图
                if double_sided:
                    if index % 2 :
                        page_list.append(index-1)
                        page_list.append(index)
                    else:
                        page_list.append(index)
                        page_list.append(index+1)
                        index += 1
                else:
                    page_list.append(index)
                break
        index += 1
    print(page_list)

    pdf = PdfFileReader(path)
    pdf_writer = PdfFileWriter()
    for index in page_list:
        page = pdf.getPage(index)

        pdf_writer.addPage(page)

    with open(out_path, "wb") as out:
        pdf_writer.write(out)
        print("created", out_path)


# 主函数
if __name__ == '__main__':
    s_time = datetime.datetime.now()
    print(s_time, '程序开始运行')
    run()
    e_time = datetime.datetime.now()
    print(e_time, '运行结束，耗时', e_time - s_time)
