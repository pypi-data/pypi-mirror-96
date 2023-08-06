# -*- coding: utf-8 -*-

"""
Author     : ZhangYafei
Description: zyf_timer
"""

import setuptools


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()


setuptools.setup(
    name='zyf',  # 模块名称
    version="0.3",  # 当前版本
    author="zhangyafei",  # 作者
    author_email="zhangyafeii@foxmail.com",  # 作者邮箱
    description="万能工具包",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    # url="https://github.com/zhangyafeii/timer",  # 模块github地址
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=['prettytable', 'pandas'],
    python_requires='>=3.6',
)