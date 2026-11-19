"""Regenerate the English and Chinese GitHub Pages HTML from the JSON content."""

from html import escape
from itertools import groupby
from pathlib import Path
from string import Template
import json


ROOT = Path(__file__).resolve().parents[1]


def read_json(filename):
    return json.loads((ROOT / "content" / filename).read_text(encoding="utf-8"))


def render_papers(papers, topics, name, github, repository_label):
    sections = []
    ordered = sorted(papers, key=lambda paper: paper["year"], reverse=True)
    for year, entries in groupby(ordered, key=lambda paper: paper["year"]):
        articles = []
        for paper in entries:
            doi_url = escape(f"https://doi.org/{paper['doi']}")
            title = escape(paper["title"])
            author_line = ", ".join(
                f"<strong>{escape(author)}</strong>" if author == name else escape(author)
                for author in paper["authors"]
            )
            tag_line = "".join(
                f'<span class="paper-tag">{escape(topics[topic]["label"])}</span>'
                for topic in paper["topics"]
            )
            repo = paper.get("repository")
            repo_link = (
                f'<a href="{escape(f"{github}/{repo}")}">{escape(repository_label)}</a>'
                if repo else ""
            )
            articles.append(f'''
          <article class="paper" data-topics="{escape(" ".join(paper["topics"]))}">
            <div class="paper-main">
              <div class="paper-tags">{tag_line}</div>
              <h4 lang="en"><a href="{doi_url}">{title}</a></h4>
              <p class="authors" lang="en">{author_line}</p>
              <p class="journal" lang="en"><cite>{escape(paper["journal"])}</cite> · {escape(paper["details"])}</p>
            </div>
            <div class="paper-links">
              <a href="{doi_url}" aria-label="DOI · {title}">DOI</a>{repo_link}
            </div>
          </article>''')
        article_list = "".join(articles)
        sections.append(f'''
        <section class="year-group" aria-labelledby="year-{year}">
          <h3 id="year-{year}">{year}</h3>
          <div class="year-papers">{article_list}
          </div>
        </section>''')
    return "".join(sections)


def render_language_links(language, prefix):
    links = {
        "en": (prefix + "index.html", "EN"),
        "zh-CN": (prefix + "zh/index.html", "中文"),
    }
    return " ".join(
        f'<span lang="{code}" aria-current="page">{label}</span>'
        if code == language else
        f'<a href="{href}" lang="{code}" hreflang="{code}">{label}</a>'
        for code, (href, label) in links.items()
    )


def render_page(site, papers, template, language, variant):
    copy = variant["copy"]
    folder = variant["folder"]
    prefix = "../" if folder else ""
    name = site["name"]
    origin = site["origin"]
    topics = variant["topics"]
    profile_urls = site["profiles"]
    scholar = profile_urls["scholar"].replace("hl=en", f"hl={language}")
    orcid = profile_urls["orcid"]
    github = profile_urls["github"]
    canonical = f"{origin}/{folder}"

    research_cards = []
    for topic, item in topics.items():
        if "name" in item:
            research_cards.append(f'''
          <a class="research-card research-card--{escape(topic)}" href="#publications" data-filter-link="{escape(topic)}">
            <h3>{escape(item["name"])}</h3>
            <p>{escape(item["description"])}</p>
          </a>''')

    topic_buttons = [
        f'<button type="button" data-filter="all" aria-pressed="true">{escape(copy["allTopics"])}</button>'
    ]
    for topic, item in topics.items():
        topic_buttons.append(
            f'<button type="button" data-filter="{escape(topic)}" aria-pressed="false">{escape(item["label"])}</button>'
        )

    project_cards = []
    for project in site["projects"]:
        project_name = escape(project["name"])
        topic = escape(project["topic"])
        repository_url = escape(f"{github}/{project['repository']}")
        project_cards.append(f'''
          <article class="project-card project-card--{topic}">
            <h3 lang="en">{project_name}</h3>
            <p>{escape(project["description"][language])}</p>
            <a class="text-link" href="{repository_url}">{escape(copy["repository"])} · GitHub</a>
          </article>''')

    institution_parent = copy["institutionParent"]
    parent_line = f"<br>{escape(institution_parent)}" if institution_parent else ""
    profiles = (
        (escape(copy["scholarLabel"]), escape(scholar), ""),
        ("ORCID", escape(orcid), ' rel="me"'),
        ("GitHub", escape(github), ' rel="me"'),
    )
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": canonical,
        "sameAs": [scholar, orcid, github],
        "affiliation": {"@type": "Organization", "name": copy["institution"]},
    }
    return template.substitute(
        {key: escape(value) for key, value in copy.items()},
        lang=language,
        name=escape(name),
        canonical=escape(canonical),
        englishUrl=escape(f"{origin}/"),
        chineseUrl=escape(f"{origin}/zh/"),
        socialImage=escape(f"{origin}/assets/tomography.webp"),
        favicon=f"{prefix}assets/icon.png",
        stylesheet=f"{prefix}assets/site.css",
        script=f"{prefix}assets/publications.js",
        figureImage=f"{prefix}assets/tomography.webp",
        structuredData=json.dumps(structured_data, ensure_ascii=False).replace("<", "\\u003c"),
        parentInstitution=parent_line,
        profileLinks=" ".join(
            f'<a href="{url}"{relationship}>{label}</a>' for label, url, relationship in profiles
        ),
        languageLinks=render_language_links(language, prefix),
        scholarUrl=escape(scholar),
        orcidUrl=escape(orcid),
        githubUrl=escape(github),
        researchCards="".join(research_cards),
        topicButtons="\n            ".join(topic_buttons),
        papers=render_papers(papers, topics, name, github, copy["repository"]),
        projectCards="".join(project_cards),
    )


def main():
    site = read_json("site.json")
    papers = read_json("publications.json")
    template = Template((ROOT / "templates" / "home.html").read_text(encoding="utf-8"))
    for language, variant in site["languages"].items():
        destination = ROOT / variant["folder"] / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_page(site, papers, template, language, variant), encoding="utf-8", newline="\n")
        print(destination.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
