import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords

# 下载 NLTK 停用词表
nltk.download("stopwords")
nltk.download("punkt")

def clean_affiliation(affiliation):
    """提取通讯单位中的简化名称（例如 Hunan University of Chinese Medicine）。"""
    if not affiliation:
        return "Unknown Institution"
    # 使用正则表达式提取最简化的大学或学院名称
    match = re.search(r"\b(?:University|Hospital)\b.*?(?=,)", affiliation, re.IGNORECASE)
    return match.group(0).strip() if match else affiliation

def extract_country(affiliation):
    """
    从通讯单位中提取国家信息，处理复杂情况，包括多个单位、电子邮件地址等。
    """
    if not affiliation:
        return "Unknown Country"

    # 移除电子邮件地址和其他无关字符
    cleaned_affiliation = re.sub(r"[.;]", "", affiliation)  # 移除句号和分号
    cleaned_affiliation = re.sub(r"\b\w+@\w+\.\w+\b", "", cleaned_affiliation)  # 删除电子邮件地址
    cleaned_affiliation = cleaned_affiliation.strip()

    # 特殊国家映射表（针对特定写法）
    common_variants = {
        "Republic of Korea": "South Korea",
        "Korea": "South Korea",
        "South Korea": "South Korea",
        "P. R. China": "China",
        "PRC": "China",
        "People's Republic of China": "China",
        "USA": "United States",
        "United States of America": "United States",
        "UK": "United Kingdom",
        "England": "United Kingdom",
        "Saudi Arabia": "Saudi Arabia",
        "Spain": "Spain",
        "Australia": "Australia"
    }

    # 检查是否包含映射表中的关键词
    for variant, country in common_variants.items():
        if variant in cleaned_affiliation:
            return country

    # 匹配最后的国家或地址部分
    country_match = re.search(r",\s*([a-zA-Z\s']+)$", cleaned_affiliation)
    if country_match:
        potential_country = country_match.group(1).strip()
        if potential_country in common_variants.values():  # 如果已知是国家
            return potential_country

    # 检查可能的缩写国家代码或复杂情况下的最后一个单位
    words = cleaned_affiliation.split(",")
    for word in reversed(words):
        word = word.strip()
        if word in common_variants.values():  # 检查是否是国家
            return word

    # 默认返回未知国家
    return "Unknown Country"

def generate_keywords(abstract):
    """根据摘要内容生成关键词。"""
    if not abstract or abstract == "No abstract available":
        return "No keywords available"
    # 使用 NLTK 提取高频名词作为关键词
    words = nltk.word_tokenize(abstract)
    words = [word.lower() for word in words if word.isalpha()]  # 仅保留字母
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    word_counts = Counter(filtered_words)
    # 提取前 5 个高频词作为关键词
    keywords = [word for word, count in word_counts.most_common(5)]
    return ", ".join(keywords)

def search_pubmed_all(keyword):
    all_articles = []
    retstart = 0
    retmax = 200  # 每次请求返回 200 篇文献

    while True:
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

        if not pmids:
            break

        print(f"Fetching articles from {retstart} to {retstart + retmax}...")

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_soup = BeautifulSoup(fetch_response.content, "xml")

        for i, article in enumerate(fetch_soup.find_all("PubmedArticle")):
            try:
                title = article.find("ArticleTitle").text if article.find("ArticleTitle") else "No title available"
                pub_date = article.find("PubDate").text if article.find("PubDate") else "Unknown"

                authors = article.find_all("Author")
                first_author = f"{authors[0].find('LastName').text} {authors[0].find('ForeName').text}" if authors else "Unknown"
                corresponding_author = "Unknown"
                affiliations = []

                for author in authors:
                    affiliation = author.find("AffiliationInfo")
                    if affiliation:
                        affiliations.append(affiliation.find("Affiliation").text)
                    if author.get("ValidYN") == "Y":
                        corresponding_author = f"{author.find('LastName').text} {author.find('ForeName').text}"

                # 获取通讯单位和国家
                affiliation = affiliations[0] if affiliations else "No affiliation available"
                cleaned_affiliation = clean_affiliation(affiliation)
                country = extract_country(affiliation)

                # 获取摘要
                abstract = article.find("AbstractText").text if article.find("AbstractText") else "No abstract available"

                # 提取或生成关键词
                keywords = generate_keywords(abstract)

                article_info = {
                    "Index": len(all_articles) + 1,
                    "Title": title,
                    "Publication Date": pub_date,
                    "First Author": first_author,
                    "Corresponding Author": corresponding_author,
                    "Affiliation": cleaned_affiliation,
                    "Country": country,
                    "Abstract": abstract,
                    "Keywords": keywords
                }
                all_articles.append(article_info)
            except Exception as e:
                print(f"Error parsing article {len(all_articles) + 1}: {e}")

        retstart += retmax

    return all_articles

def export_to_csv(articles):
    # 将结果导出为 CSV
    df = pd.DataFrame(articles)
    filename = r"C:\Users\ZMS\Desktop\pubmed/11-pubmed_research.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Results exported to {filename}")

# 示例使用
keyword = "(Machine Learning OR Artificial Intelligence) AND nanomedicine"
articles = search_pubmed_all(keyword)

if articles:
    export_to_csv(articles)
else:
    print("No articles found.")