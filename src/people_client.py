import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class PeopleClient:
    def __init__(self):
        # 初始化时获取当前日期
        self.today = datetime.now()

    def fetch_people_shiping(self):
        # 根据当前日期构建 URL
        url = f'http://paper.people.com.cn/rmrb/html/{self.today.year}-{self.today.month:02d}/{self.today.day:02d}/nbs.D110000renmrb_05.htm'
        
        # 发起 GET 请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 设置正确的编码
            response.encoding = 'utf-8'  # 设置为UTF-8以避免乱码
            
            # 解析 HTML 内容
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有文章项
            articles = soup.select('ul.news-list li a')  # 使用 CSS 选择器找到所有文章链接
            
            found = False
            for article in articles:
                title = article.get_text(strip=True)
                link = article['href']
            
                # 检查标题中是否包含“人民时评”
                if "人民时评" in title:
                    print(f"找到‘人民时评’文章: 标题: {title}, 链接: {link}")
                    found = True
                    print(link)
                    content = self.fetch_article_detail(link)  # 抓取详情内容
                    return content
            
            if not found:
                print("未能找到任何关于“人民时评”的文章。")
                return None
                
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None

    def fetch_article_detail(self, article_link):
        # 构造完整的文章 URL
        full_link = f"http://paper.people.com.cn/rmrb/html/{self.today.year}-{self.today.month:02d}/{self.today.day:02d}/{article_link}" if article_link.startswith('nw.') else article_link
        
        # 发起请求
        response = requests.get(full_link)
        if response.status_code == 200:
            response.encoding = 'utf-8'  # 确保使用UTF-8编码
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='main')  # 假设内容在 main div 中
            
            if content_div:
                paragraphs = content_div.find_all('p')
                print("\n文章内容:")
                article_content = "\n".join(para.get_text(strip=True) for para in paragraphs)  # 将段落合并为字符串
                return article_content  # 返回文章内容
            else:
                print("未能找到文章内容区域。")
                return None
        else:
            print(f"请求详情失败，状态码: {response.status_code}，链接: {full_link}")
            return None

    def export_people_article(self, date=None, hour=None):
        LOG.debug("准备导出Hacker News的热门新闻。")
        people_article = self.fetch_people_shiping()  # 获取新闻数据
        
        if not people_article:
            LOG.warning("未找到任何Hacker News的新闻。")
            return None
        
        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # 构建存储路径
        dir_path = os.path.join('people_article', date)
        os.makedirs(dir_path, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(dir_path, f'{date}.md')  # 定义文件路径
        with open(file_path, 'w',encoding="utf-8") as file:
            file.write(people_article)
        
        LOG.info(f"人民时评文件生成：{file_path}")
        return file_path
# 使用示例
if __name__ == "__main__":
    client = PeopleClient()
    client.fetch_people_shiping()