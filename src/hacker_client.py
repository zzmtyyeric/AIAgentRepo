# src/github_client.py

import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class HackerClient:
    pass

    def fetch_hackernews_top_stories(self):
      url = 'https://news.ycombinator.com/'
      response = requests.get(url)
      response.raise_for_status()  # 检查请求是否成功

      soup = BeautifulSoup(response.text, 'html.parser')
      # 查找包含新闻的所有 <tr> 标签
      stories = soup.find_all('tr', class_='athing')

      top_stories = []
      for story in stories:
          title_tag = story.find('span', class_='titleline').find('a')
          if title_tag:
              title = title_tag.text
              link = title_tag['href']
              top_stories.append({'title': title, 'link': link})

      return top_stories

    def export_progress_by_date_range(self, days):
        today = date.today()  # 获取当前日期
        since = today - timedelta(days=days)  # 计算开始日期
        
        updates = self.fetch_hackernews_top_stories()  # 获取指定日期范围内的更新
        
        repo_dir = 'daily_progress'  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        # 更新文件名以包含日期范围
        date_str = f"{since}_to_{today}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for Hacker News ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for idx, story in enumerate(updates, start=1):
              file.write(f"{idx}. {story['title']} Link: {story['link']}")
        
        LOG.info(f"Hacker News 趋势报告文件生成： {file_path}")  # 记录日志
        return file_path
