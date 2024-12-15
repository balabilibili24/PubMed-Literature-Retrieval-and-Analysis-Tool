import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import numpy as np
import os

def create_folder(folder_path):
    """创建文件夹，如果文件夹已经存在，则不做任何操作"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def histogram(data,path):
    # **直方图：对 Publication Year 进行分布统计**
    data["Publication Year"] = pd.to_numeric(data["Publication Year"], errors='coerce')

    # **直方图：对 Publication Year 进行分布统计**
    plt.figure(figsize=(16, 6))

    # 绘制直方图
    data["Publication Year"].hist(bins=20, color='skyblue', edgecolor='black')

    # 设置标题和标签
    plt.title("Publication Year Distribution")
    plt.xlabel("Year")
    plt.ylabel("Number of Publications")

    # 设置x轴的显示范围，确保x轴从最早年份到2024
    plt.xlim(data["Publication Year"].min() - 1, 2024 + 1)

    # 调整x轴的标签，防止重叠
    plt.xticks(range(int(data["Publication Year"].min()), 2025), rotation=45)

    plt.grid(False)
    # 自动调整布局，避免标签被裁剪
    plt.tight_layout()

    # 保存并展示图像
    plt.savefig(path + "/publication_year_histogram_optimized.png", dpi=300)
    # plt.show()

# **气泡图绘制函数**
def plot_wordcloud_for_phrases(data,column_name, title, save_name):
    # 获取列中每个完整短语的频率
    word_counts = Counter(data[column_name].dropna().tolist())

    # 创建词云
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=200
    ).generate_from_frequencies(word_counts)

    # 绘制词云图
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(title, fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_name)
    # plt.show()

# **绘制词云图：关键词需要分词**
def clean_keywords(keywords_list):
    """
    清洗关键词列表：去掉指定词汇和无用词。
    """
    # 无用的关键词（不区分大小写）
    stopwords = {
        "artificial intelligence", "machine learning", "cell", "cells", "neural networks",
        "abstract","deep learning","such","based","nanoparticles","nanotechnology","available",
        "nanomedicine","nanoparticle","analysis","nanomedicines","learning",
        "artificial neural networks","artificial neural network","using","will","prediction",
        "were","support vector machine","time","future","effect","properties","care","model",
        "standards","machine","values","hospital","university","deep","neural network","motion",
        "algorithm","models","human","been","risk","images","proposed","walking","self","biomaterial",
        "biomaterials","features","feature","different","studies","gait","computer visions"

    }

    # 转小写并过滤无用词
    cleaned_keywords = [
        keyword.strip()
        for keyword in keywords_list
        if keyword.strip().lower() not in stopwords and keyword.strip()  # 非空且不在无用词中
    ]

    return cleaned_keywords

# **绘制词云图：关键词需要分词并清洗**
def filter_unknown_data(df):
    """
    过滤掉含有 "Unknown" 或 "Hospital" 或 "University" 的数据。
    """
    filtered_df = df[
        ~df["Country"].str.contains("Unknown", na=False) &
        ~df["University"].str.contains("Unknown", na=False) &
        ~df["Affiliation"].str.contains("Unknown", na=False) &
        ~df["First Author"].str.contains("Unknown", na=False) &
        ~df["Corresponding Author"].str.contains("Unknown", na=False) &
        ~df["University"].str.contains("Hospital|University|s College London", na=False)  # 去掉只包含 Hospital 或 University 的行
    ]
    return filtered_df


# **绘制词云图**
def plot_wordcloud(data_column, title, save_name, split_keywords=False, random_state=42):
    """
    根据列绘制词云图，支持对关键词进行分割和清洗。
    """
    if split_keywords:  # 如果是关键词列
        all_keywords = data_column.dropna().str.cat(sep=',').split(',')
        cleaned_keywords = clean_keywords(all_keywords)
        word_counts = Counter(cleaned_keywords)
    else:  # 其他列直接统计
        word_counts = Counter(data_column.dropna().tolist())
    font_path = r'C:\\Windows\\Fonts\\arial.ttf'
    # 创建词云，固定随机种子确保一致性
    wordcloud = WordCloud(
        width=1000,
        height=1000,
        background_color='white',
        colormap= "tab10" ,               # 'Accent', #Dark2 Paired tab10
        max_words=80,
        random_state=random_state,  # 固定随机种子
        min_font_size=20,  # 设置最小字体大小
        max_font_size=120,  # 设置最大字体大小
        font_path=font_path,  # 指定字体路径
        relative_scaling = 0.0 # 禁用相对缩放，所有词汇都使用统一的字体大小比例

    ).generate_from_frequencies(word_counts)

    # 绘制词云图
    plt.figure(figsize=(8, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    # plt.title(title, fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_name)
    # plt.show()

def data_imaging(path):
    for item in os.listdir(path):
        data_path = os.path.join(path, item)
        if data_path.split(".")[1] == "csv":
            data = pd.read_csv(data_path)
            filtered_data = filter_unknown_data(data)
            histogram(filtered_data, path)

            # **绘制词云图：非关键词列**
            columns_to_plot = {
                "First Author": "First Author",
                "Corresponding Author": "Corresponding Author",
                "University": "Affiliation",
                "Country": "Country",
            }

            for col, title in columns_to_plot.items():
                save_name = path + f"/{col.lower().replace(' ', '_')}_wordcloud.png"
                plot_wordcloud(filtered_data[col], title, save_name)
                plot_wordcloud(filtered_data["Keywords"], "Keywords WordCloud",
                               path + "/cleaned_keywords_wordcloud.png",
                               split_keywords=True)


if __name__ == "__main__":
    path = r"C:\Users\ZMS\Desktop\pubmed"
    for item in os.listdir(path):
        data_imaging(os.path.join(path,item))




