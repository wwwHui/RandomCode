# 提取彩色PDF页面

## 环境
python>=3.7

PyMuPDF>=1.18.19

PyPDF2>=1.26.0


注意：安装PyMuPDF后，不用额外安装fitz，否则会提示“ModuleNotFoundError: No module named 'frontend'”


## 问题来源
想打印PDF文件，但是部分页面有需要彩色打印，这就要求将含有彩图的PDF页面单独提取出来。不想人工去一页一页查看，就用Python处理了一下


## 基本流程
从原始PDF提取图片，根据图像信息决定是否提取该页面，同时还要考虑是否双面打印的问题，最后将相关页面转化为PDF文件