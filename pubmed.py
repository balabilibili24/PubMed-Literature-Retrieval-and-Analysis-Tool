import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import re


def clean_affiliation(affiliation):
    """提取通讯单位中的简化名称，按照优先级检索 University, Hospital, Institute, College，并处理多部分单位名称。"""
    if not affiliation:
        return "Unknown Institution"

    # 清除附加内容（如电子邮件地址和特殊字符）
    cleaned_affiliation = re.sub(r"\b\w+@\w+\.\w+\b", "", affiliation)  # 去掉电子邮件
    cleaned_affiliation = re.sub(r"[.;]", "", cleaned_affiliation)  # 去掉句号和分号

    # 设定优先级的关键词列表
    keywords = ["University", "Hospital", "Institute", "College"]

    # 根据优先级顺序，依次查找关键词并提取相关单位名称
    for keyword in keywords:
        # 创建正则表达式：匹配关键词后面跟随单位名称，直到遇到逗号或文本末尾
        pattern = r"([A-Za-z\s]*?{}[A-Za-z\s]*?)(?=\s*,|\s*$)".format(re.escape(keyword))
        match = re.search(pattern, cleaned_affiliation, re.IGNORECASE)

        if match:
            extracted_name = match.group(0).strip()

            # 处理特殊情况：如果单位名包含多个部分，确保提取完整单位名
            institution_pattern = r"([A-Za-z\s]+(?:University|Institute|Hospital|College)[A-Za-z\s]*)"
            institution_match = re.search(institution_pattern, extracted_name)

            if institution_match:
                return institution_match.group(0).strip()

    # 如果没有找到匹配的单位名称，返回 Unknown Institution
    return "Unknown Institution"


def extract_country(affiliation):
    """
    从通讯单位中提取国家信息，优化处理多种复杂情况，去除电子邮件和杂乱信息。
    """
    if not affiliation:
        return "Unknown Country"

    # 先移除电子邮件地址
    email_match = re.search(r"\b\w+@\w+\.\w+\b", affiliation)
    email_address = None
    if email_match:
        email_address = email_match.group(0)  # 提取电子邮件地址
        affiliation = affiliation.replace(email_address, "")  # 移除电子邮件

    # 移除句号和分号（如地址中存在）
    affiliation = re.sub(r"[.;]", "", affiliation)

    # 去掉额外的空格
    affiliation = affiliation.strip()

    # 特殊国家映射表（针对特定写法）
    common_variants = {
        "Republic of Korea": "South Korea",
        "Korea": "South Korea",
        "South Korea": "South Korea",
        "P. R. China": "China",
        "P R China": "China",
        "CHN": "China",
        "Taiwan": "Chinese Taiwan",
        "China": "China",
        "PRC": "China",
        "People's Republic of China": "China",
        "USA": "United States",
        "United States of America": "United States",
        "UK": "United Kingdom",
        "England": "United Kingdom",
        "Saudi Arabia": "Saudi Arabia",
        "Spain": "Spain",
        "Australia": "Australia",
        "Japan": "Japan",
        "JPN": "Japan",
        "France": "France",
        "Germany": "Germany",
        "Poland": "Poland",
        "Bangladesh": "Bangladesh",
        "India": "India",
        "Italy": "Italy",
        "Thailand": "Thailand",
        "Denmark": "Denmark",
        "Belgium": "Belgium",
        "Sweden": "Sweden",
        "Iran": "Iran",
        "Canada": "Canada",
        "Egypt": "Egypt",
        "the Netherlands": "the Netherlands",
        "Brazil": "Brazil"


    }

    # 检查是否包含映射表中的关键词
    for variant, country in common_variants.items():
        if variant in affiliation:
            return country

    # 提取最后一个逗号之后的部分，直到最后一个句号为止
    # 这部分很可能是国家信息
    parts = affiliation.split(",")
    if len(parts) > 1:
        last_part = parts[-1].strip()

        # 如果最后一部分是已知的国家，则返回该部分
        if last_part in common_variants.values():
            return last_part

        # 否则返回最后一个词（即最后一个逗号到最后一个句号之间的词）
        return last_part

    # 如果没有匹配，返回Unknown
    return "Unknown Country"

def extract_keywords(abstract, top_n=5):
    """
    从摘要中提取关键词。如果摘要为空，返回 'No keywords available'。
    :param abstract: 文献摘要文本
    :param top_n: 提取的关键词数量
    :return: 关键词列表
    """
    if not abstract:
        return "No keywords available"

    # 去掉标点和特殊字符，按空格拆分单词
    words = re.findall(r'\b[a-zA-Z]{4,}\b', abstract.lower())  # 只提取长度 >= 4 的单词
    common_words = set(["the", "with", "from", "that", "this", "these", "those","which", "while", "where", "there",
                        "about", "have","machine learning","deep learning","AI","high","data","Machine learning","artificial intelligence",
                        "research","Machine learning"])
    filtered_words = [word for word in words if word not in common_words]

    # 使用 Counter 统计词频，返回最常见的 top_n 个词
    most_common = Counter(filtered_words).most_common(top_n)
    return ", ".join([word for word, _ in most_common])


def search_pubmed_all(keyword):
    all_articles = []
    retstart = 0
    retmax = 200  # 每次请求返回 200 篇文献

    while True:
        # 使用 esearch API 搜索关键词
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": f"{keyword} NOT Review[PT]",  # 排除综述文章
            "retmax": retmax,
            "retstart": retstart,
            "retmode": "xml"
        }
        search_response = requests.get(search_url, params=search_params)
        search_soup = BeautifulSoup(search_response.content, "xml")
        pmids = [id_tag.text for id_tag in search_soup.find_all("Id")]

        # 如果没有新的文献 ID，停止请求
        if not pmids:
            break

        print(f"Fetching articles from {retstart} to {retstart + retmax}...")

        # 使用 efetch API 获取详细的文献信息
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_soup = BeautifulSoup(fetch_response.content, "xml")

        # 解析返回的 XML 文档
        for i, article in enumerate(fetch_soup.find_all("PubmedArticle")):
            try:
                title = article.find("ArticleTitle").text if article.find("ArticleTitle") else "No title available"
                journal = article.find("Title").text if article.find("Title") else "No journal available"

                # 提取年度信息
                pub_date = article.find("PubDate")
                pub_year = "Unknown"
                if pub_date:
                    year = pub_date.find("Year")
                    if year:
                        pub_year = year.text

                # 获取作者信息
                authors = article.find_all("Author")
                first_author = f"{authors[0].find('LastName').text} {authors[0].find('ForeName').text}" if authors else "Unknown"
                corresponding_author = "Unknown"
                affiliations = []

                # 遍历作者，查找通讯作者信息
                for author in authors:
                    affiliation = author.find("AffiliationInfo")
                    if affiliation:
                        affiliations.append(affiliation.find("Affiliation").text)
                    if author.get("ValidYN") == "Y":
                        corresponding_author = f"{author.find('LastName').text} {author.find('ForeName').text}"

                # 获取通讯单位（取第一个通讯作者的单位）
                affiliation = affiliations[0] if affiliations else "No affiliation available"
                cleaned_affiliation = clean_affiliation(affiliation)
                country = extract_country(affiliation)

                # 获取摘要
                abstract = article.find("AbstractText").text if article.find(
                    "AbstractText") else "No abstract available"

                # 获取关键词（优先使用已有关键词，否则从摘要生成）
                keyword_list = article.find_all("Keyword")
                if keyword_list:
                    keywords = ", ".join([kw.text for kw in keyword_list])
                else:
                    keywords = extract_keywords(abstract)

                article_info = {
                    "Index": len(all_articles) + 1,
                    "Title": title,
                    "Publication Year": pub_year,
                    "Journal": journal,
                    "First Author": first_author,
                    "Corresponding Author": corresponding_author,
                    "Affiliation": affiliation,
                    "University": cleaned_affiliation,
                    "Country": country,
                    "Abstract": abstract,
                    "Keywords": keywords
                }
                all_articles.append(article_info)
            except Exception as e:
                print(f"Error parsing article {len(all_articles) + 1}: {e}")

        # 更新起始位置，准备请求下一页
        retstart += retmax

    return all_articles


def export_to_csv(articles,filename):
    # 将结果导出为 CSV
    df = pd.DataFrame(articles)
    filepath = r"C:\Users\ZMS\Desktop\pubmed/" + filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"Results exported to {filepath}")

# 示例使用


for year in range(1960, 2025):  # 设置循环的年度范围
    keyword = "(Machine Learning OR Artificial Intelligence) AND (bio-imaging OR Medical Imaging) AND {}[DP]".format(year)

    # 调用 PubMed 搜索函数，获取相应年份的所有文章
    articles = search_pubmed_all(keyword)

    # 如果找到了文献，导出为 CSV 文件
    if articles:
        filename = "Bio-imaging-{}-pubmed_research.csv".format(year)
        export_to_csv(articles, filename=filename)
        print(f"Exported articles for year {year}.")
    else:
        print(f"No articles found for year {year}.")