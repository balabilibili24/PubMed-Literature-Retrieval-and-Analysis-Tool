
PubMed 文献检索与分析工具 / PubMed Literature Retrieval and Analysis Tool
项目简介 / Project Overview
本项目通过关键词从 PubMed 检索文献，提取标题、作者、通讯单位、国家、关键词等关键信息，并生成可视化结果（直方图、词云图），帮助分析文献数据趋势。
This project retrieves literature from PubMed using keywords, extracts key information such as titles, authors, affiliations, countries, and keywords, and generates visualizations (histograms and word clouds) to analyze trends in the data.

功能特点 / Features
关键词检索 / Keyword Search：高效获取 PubMed 文献，排除综述文章。
Efficiently retrieves PubMed articles, excluding review papers.

数据提取 / Data Extraction：自动清洗并提取作者、通讯单位、国家、关键词等信息。
Automatically cleans and extracts data such as authors, affiliations, countries, and keywords.

可视化分析 / Visualization：生成词云图和直方图，直观展示文献分布和高频关键词。
Creates word clouds and histograms to intuitively display publication trends and high-frequency keywords.

数据导出 / Data Export：支持 CSV 格式保存结果，便于后续分析。
Supports exporting results in CSV format for further analysis.

使用说明 / Instructions
环境配置 / Setup：
配置 Python 环境并安装所需依赖（requests、pandas、matplotlib 等）。
Configure the Python environment and install dependencies (requests, pandas, matplotlib, etc.).

运行步骤 / How to Run：

运行 bio-imaging.py 检索文献数据。
Run bio-imaging.py to retrieve PubMed data.
运行 burble.py 生成可视化图表。
Run burble.py to generate visualizations.
结果存储 / Results Storage：
数据和可视化结果默认保存在 C:\Users\ZMS\Desktop\pubmed 目录。
Data and visualizations are saved by default in the directory C:\Users\ZMS\Desktop\pubmed.

示例 / Example
关键词 / Keywords：(Machine Learning OR Artificial Intelligence) AND nanomedicine
生成结果 / Outputs：
文献年份分布的直方图 / A histogram of publication year distribution
关键词、作者和通讯单位的词云图 / Word clouds for keywords, authors, and affiliations
简洁高效，助力文献分析与科研洞察！
Efficient and concise, empowering literature analysis and scientific insights!
