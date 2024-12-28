import json
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

GITHUB_TOKEN = os.getenv("GH_TOKEN")
print(GITHUB_TOKEN)


def read_keywords():
    with open("keywords.json", "r") as file:
        return json.load(file)


def search_awesome_projects(keyword):
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"q": f"{keyword} awesome in:name", "sort": "stars", "order": "desc"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["items"]


def generate_projects_list(projects):
    return "\n".join(
        f"- **[{project['name']}]({project['html_url']})**\n  - ⭐ {project['stargazers_count']}\n  - {project['description']}"
        for project in projects
    )


def update_readme(content):
    with open("README.md", "w") as file:
        file.write(content)


if __name__ == "__main__":
    keywords = read_keywords()
    all_projects = []
    for keyword in keywords:
        projects = search_awesome_projects(keyword)
        all_projects.extend(projects)

    unique_projects = {project["html_url"]: project for project in all_projects}
    sorted_projects = sorted(
        unique_projects.values(), key=lambda x: x["stargazers_count"], reverse=True
    )

    filtered_projects = [
        project for project in sorted_projects if project["stargazers_count"] > 200
    ]

    projects_list = generate_projects_list(filtered_projects)

    with open("README.template", "r") as template_file:
        template_content = template_file.read()

    current_date = datetime.now().strftime("%Y-%m-%d")

    readme_content = template_content.replace("{{ projects_list }}", projects_list)
    readme_content = readme_content.replace("{{ last_updated }}", current_date)

    update_readme(readme_content)
