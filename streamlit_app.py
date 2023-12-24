# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import os, urllib
import io
from matplotlib_venn import venn3
import matplotlib.pyplot as plt

# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox("Choose the app mode",
        ["Show instructions", "Run the app", "Data clean", "User analysis", "Modeling","Show the source code"])
    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Show the source code":
        readme_text.empty()
        st.code(get_file_content_as_string("streamlit_app.py"))
    elif app_mode == "Run the app":
        readme_text.empty()
        run_the_app()
    elif app_mode == "Data clean":
        readme_text.empty()
        # TODO:添加数据清洗
    elif app_mode == "User analysis":
        readme_text.empty()
        user_classification()
    elif app_mode == "Modeling":
        readme_text.empty()
        # TODO:添加建模分析

# This is the main app app itself, which appears when the user selects "Run the app".
def run_the_app():
    # 全流程
    # TODO：添加全流程
    # 1. 数据预处理
    # 2. 用户分类
    user_classification()
    # 3. 建模分析

def user_classification():
    @st.cache_data
    def load_data(nrows=None):
        user = pd.read_csv('user_classify.csv', encoding='utf-8')
        if nrows:
            user = user.head(nrows)
        return user

    # 加载原始数据
    user_data = load_data()
    total_user = len(user_data)
    top_user = len(user_data[user_data['top_user'] == 1])
    high_quality = len(user_data[user_data['high_quality'] == 1])
    official = len(user_data[user_data['official'] == 1])

    st.header('用户分类')
    st.text(f'总共有{total_user}个账号，其中大V（10万粉以上）有{top_user}个，高活跃度账号有{high_quality}个，官方账号有{official}个。')
    st.text('据此可以将用户分为八类，对应编码为三种类别对应的二进制数：\n‘{是否高活跃度}’‘{是否官方}’‘{是否大V}’（分别取值0/1）。')
    user_classification_bar_chart(official, top_user, high_quality, total_user)
    user_classification_followers_analysis(user_data)
    user_classification_followers_analysis_per_class(user_data)
    user_classification_cross_analysis(user_data)


def user_classification_bar_chart(official, top_user, high_quality, total_user):
    # 三种分类的粉丝数柱状图
    st.subheader('三种分类的账号数量数柱状图')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.text(f'三种分类下账号的数量的比例都大约在{int(100*np.mean(official+top_user+high_quality)/total_user)}%。')

    # 柱状图的数据
    followers_count = np.array([official, top_user, high_quality])  # positive 柱子的高度
    x_labels = ['official', 'top_user', 'activity']  # 柱子的标签
    positive_labels = 'official/top_user/high_activity'
    negative_labels = 'non_official/non_top_user/low_activity'

    # 创建绘图区域和子图
    fig, ax = plt.subplots(figsize=(8, 4))
    width = 0.35  # 柱子的宽度

    bars1 = ax.bar(x_labels, followers_count,color='orange', width=width, label=positive_labels)
    bars2 = ax.bar(x_labels, total_user-followers_count, bottom=followers_count, color="green",width=width, label=negative_labels)
    for bar1,bar2 in zip(bars1,bars2):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax.text(bar1.get_x() + bar1.get_width() / 2, height1+height2, str(height2), ha='center', va='bottom')
        ax.text(bar1.get_x() + bar1.get_width() / 2, height1, str(height1), color="white", ha='center', va='bottom')
    ax.set_ylabel('Number of users')
    ax.set_title('Number of users by classification')
    ax.set_ylim(0, total_user+3000)

    ax.legend(loc='upper right')
    # 显示图形
    st.pyplot(fig)

def Number_outlier(data):
    Q1 = np.nanpercentile(data, 25)
    Q3 = np.nanpercentile(data, 75)
    IQR = Q3 - Q1
    motified_data = [k for k in data if k < Q3 + 1.5 * IQR and k > Q1 - 1.5 * IQR]
    return motified_data

def user_classification_followers_analysis(user_data):
    st.subheader('粉丝数分析')
    st.text('粉丝数的最大值为：' + str(user_data['followers_count'].max()))
    st.text('粉丝数的最小值为：' + str(user_data['followers_count'].min()))
    st.text('粉丝数的平均值为：' + str(int(user_data['followers_count'].mean())))
    st.text('粉丝数对应的散点图如下，可以看到存在一些离群值，需要进行处理')
    # 粉丝数对应的散点图
    st.set_option('deprecation.showPyplotGlobalUse', False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(range(len(user_data['followers_count'])), user_data['followers_count'])
    st.pyplot(fig)

    motified_data = Number_outlier(user_data['followers_count'])
    st.text('去除离群值后，粉丝数对应的散点图如下')
    st.text('最大值为：' + str(max(motified_data)))
    st.text('最小值为：' + str(min(motified_data)))
    st.text('平均值为：' + str(int(np.mean(motified_data))))
    # 粉丝数对应的散点图
    st.set_option('deprecation.showPyplotGlobalUse', False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(range(len(motified_data)), motified_data)
    st.pyplot(fig)

def user_classification_followers_analysis_per_class_process(non_top_user_fans, top_user_fans):
    non_top_user_fans = Number_outlier(non_top_user_fans)
    top_user_fans = Number_outlier(top_user_fans)
    data = {
        '最大值': [max(non_top_user_fans), max(top_user_fans)],
        '最小值': [min(non_top_user_fans), min(top_user_fans)],
        '平均值': [int(np.mean(non_top_user_fans)), int(np.mean(top_user_fans))],
        '中位数': [int(np.median(non_top_user_fans)), int(np.median(top_user_fans))]
    }
    # 绘制表格
    st.table(pd.DataFrame(data))

def user_classification_followers_analysis_per_class(user_data):
    st.subheader('每类的粉丝数分析')
    st.text('top_user')
    top_user_fans = user_data[user_data['top_user'] == 1]['followers_count']
    top_user_fans = Number_outlier(top_user_fans)

    non_top_user_fans = user_data[user_data['top_user'] == 0]['followers_count']
    non_top_user_fans = Number_outlier(non_top_user_fans)

    user_classification_followers_analysis_per_class_process(non_top_user_fans, top_user_fans)
    
    st.text('high_activity')
    high_quality_fans = user_data[user_data['high_quality'] == 1]['followers_count']
    high_quality_fans = Number_outlier(high_quality_fans)

    non_high_quality_fans = user_data[user_data['high_quality'] == 0]['followers_count']
    non_high_quality_fans = Number_outlier(non_high_quality_fans)

    user_classification_followers_analysis_per_class_process(non_high_quality_fans, high_quality_fans)

    st.text('official')
    official_fans = user_data[user_data['official'] == 1]['followers_count']
    official_fans = Number_outlier(official_fans)

    non_official_fans = user_data[user_data['official'] == 0]['followers_count']
    non_official_fans = Number_outlier(non_official_fans)

    user_classification_followers_analysis_per_class_process(non_official_fans, official_fans)


def user_classification_cross_analysis(user_data):
    st.subheader('三种分类的交叉分析')
    st.text('三种分类对应的venn图如下')
    set_high_quality = set(user_data[user_data['high_quality'] == 1]['user_id'])
    set_official = set(user_data[user_data['official'] == 1]['user_id'])
    set_top_user = set(user_data[user_data['top_user'] == 1]['user_id'])

    # 使用 matplotlib_venn 创建韦恩图
    venn = venn3([set_high_quality, set_official, set_top_user], set_labels=('high_activity', 'official', 'top_user'))

    # 在内存中保存图像数据
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')

    # 在 Streamlit 中显示图像
    buffer.seek(0)
    st.image(buffer)


def get_file_content_as_string(path):
    # url = 'https://raw.githubusercontent.com/streamlit/demo-self-driving/master/' + path
    # response = urllib.request.urlopen(url)
    # return response.read().decode("utf-8")
    # 目前是本地，考虑放到github上
    with open(path, "r", encoding='utf-8') as file:
        text = file.read()
    return text

if __name__ == "__main__":
    main()