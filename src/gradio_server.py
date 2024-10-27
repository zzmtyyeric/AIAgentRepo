import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def generate_report(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
    return report, report_file_path  # 返回报告内容和报告文件路径

def display_user_input(user_input):
    # 处理用户输入
    subscription_manager.add_subscription(user_input)
    return f"您添加的项目是: {user_input}"  # 返回用户输入的文本

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("# GitHubSentinel")

    # 报告生成部分
    with gr.Group():
        gr.Markdown("## 生成报告")
        repo_dropdown = gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        )  # 下拉菜单选择订阅的GitHub项目
        days_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        report_output = gr.Markdown()  # 输出报告的Markdown
        report_file_output = gr.File(label="下载报告")  # 文件下载输出
        
        report_button = gr.Button("生成报告")  # 按钮触发报告生成
        report_button.click(generate_report, 
                             inputs=[repo_dropdown, days_slider], 
                             outputs=[report_output, report_file_output])  # 绑定函数与输入输出
    
    # 用户输入部分
    with gr.Group():
        gr.Markdown("## 添加新项目")
        user_input_box = gr.Textbox(label="用户输入", placeholder="请输入您想要添加的新项目")  # 文本输入框
        user_output = gr.Markdown(label="您的输入内容")  # 输出用户输入的内容
        
        input_button = gr.Button("提交输入")  # 按钮触发用户输入处理
        input_button.click(display_user_input, 
                           inputs=user_input_box, 
                           outputs=user_output)  # 绑定函数与输入输出
if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))