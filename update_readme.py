import json
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# 加载环境变量
load_dotenv()

# 从环境变量中获取 GitHub 个人访问令牌
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def read_keywords():
    """读取 keywords.json 文件"""
    with open("keywords.json", "r") as file:
        return json.load(file)


def search_awesome_projects(keyword):
    """使用 GitHub API 搜索 awesome-* 项目"""
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"q": f"{keyword} awesome in:name", "sort": "stars", "order": "desc"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["items"]


def generate_projects_list(projects):
    """生成项目列表的 Markdown 格式"""
    return "\n".join(
        f"- **[{project['name']}]({project['html_url']})**\n  - ⭐ {project['stargazers_count']}\n  - {project['description']}"
        for project in projects
    )


def update_readme(content):
    """更新 README.md 文件"""
    with open("README.md", "w") as file:
        file.write(content)


if __name__ == "__main__":
    keywords = read_keywords()
    all_projects = []
    for keyword in keywords:
        projects = search_awesome_projects(keyword)
        all_projects.extend(projects)

    # 去重并按 stars 排序
    unique_projects = {project["html_url"]: project for project in all_projects}
    sorted_projects = sorted(
        unique_projects.values(), key=lambda x: x["stargazers_count"], reverse=True
    )

    # 过滤 stars 大于 200 的项目
    filtered_projects = [
        project for project in sorted_projects if project["stargazers_count"] > 200
    ]

    # 生成项目列表
    projects_list = generate_projects_list(filtered_projects)

    # 读取模板并替换内容
    with open("README.template", "r") as template_file:
        template_content = template_file.read()

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 替换占位符
    readme_content = template_content.replace("{{ projects_list }}", projects_list)
    readme_content = readme_content.replace("{{ last_updated }}", current_date)

    # 更新 README.md
    update_readme(readme_content)
