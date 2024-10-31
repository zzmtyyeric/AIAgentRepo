import schedule # 导入 schedule 实现定时任务执行器
import time  # 导入time库，用于控制时间间隔
import signal  # 导入signal库，用于信号处理
import sys  # 导入sys库，用于执行系统相关的操作

from config import Config  # 导入配置管理类
from hacker_client import HackerClient  # 导入GitHub客户端类，处理GitHub API请求
from hacker_notifier import HackerNotifier  # 导入通知器类，用于发送通知
from hacker_report_generator import HackerReportGenerator  # 导入报告生成器类
from llm import LLM  # 导入语言模型类，可能用于生成报告内容
from logger import LOG  # 导入日志记录器


def graceful_shutdown(signum, frame):
    # 优雅关闭程序的函数，处理信号时调用
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)  # 安全退出程序

def hacker_job(hacker_client, report_generator, notifier, days):
    LOG.info("[开始执行定时任务,订阅Hacker News 网站]")
    
    # 遍历每个订阅的仓库，执行以下操作
    markdown_file_path = hacker_client.export_progress_by_date_range(days)
    # 从Markdown文件自动生成进展简报
    report, report_file_path = report_generator.generate_report_by_date_range(markdown_file_path, days)
    notifier.notify(report)
    LOG.info(f"[定时任务执行完毕]")


def main():
    # 设置信号处理器
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()  # 创建配置实例
    hacker_client = HackerClient()  # 创建GitHub客户端实例
    notifier = HackerNotifier(config.email)  # 创建通知器实例
    llm = LLM(config)  # 创建语言模型实例
    report_generator = HackerReportGenerator(llm)  # 创建报告生成器实例

    # 启动时立即执行（如不需要可注释）
    hacker_job(hacker_client, report_generator, notifier, config.freq_days)

    # 安排每天的定时任务
    schedule.every(config.freq_days).days.at(
        config.exec_time
    ).do(hacker_job, hacker_client, report_generator, notifier, config.freq_days)

    try:
        # 在守护进程中持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)  # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")
        sys.exit(1)



if __name__ == '__main__':
    main()
