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


def render_experience(entries, language, heading):
    if not entries:
        return ""

    rows = []
    for entry in entries:
        item = entry[language]
        rows.append(f'''
        <li>
          <p class="experience-period">{escape(item["period"])}</p>
          <div>
            <p class="experience-role">{escape(item["role"])}</p>
            <p class="experience-institution">{escape(item["institution"])}</p>
          </div>
        </li>''')
    return f'''<section class="experience container section" id="experience" aria-labelledby="experience-title">
      <div class="section-heading">
        <h2 id="experience-title">{escape(heading)}</h2>
      </div>
      <ul class="experience-list" role="list">{"".join(rows)}
      </ul>
    </section>'''


def render_projects(projects, groups, language, github, repository_label):
    cards = {key: [] for key in groups} if groups else {None: []}
    heading_tag = "h4" if groups else "h3"
    for project in projects:
        key = project["group"] if groups else None
        project_name = escape(project["name"])
        topic = escape(project["topic"])
        repository_url = escape(f"{github}/{project['repository']}")
        cards[key].append(f'''
          <article class="project-card project-card--{topic}">
            <{heading_tag} lang="en">{project_name}</{heading_tag}>
            <p>{escape(project["description"][language])}</p>
            <a class="text-link" href="{repository_url}">{escape(repository_label)} · GitHub</a>
          </article>''')

    if not groups:
        return f'<div class="project-grid">{"".join(cards[None])}</div>'

    sections = []
    for key, labels in groups.items():
        if cards[key]:
            sections.append(f'''
        <section class="project-group" aria-labelledby="project-group-{escape(key)}">
          <h3 id="project-group-{escape(key)}">{escape(labels[language])}</h3>
          <div class="project-grid">{"".join(cards[key])}
          </div>
        </section>''')
    return f'<div class="project-groups">{"".join(sections)}</div>'


def render_academic_sections(funding, journals, language, copy):
    sections = []
    if funding:
        rows = []
        for entry in funding:
            item = entry[language]
            metadata = " · ".join(filter(None, (entry.get("period"), item["status"])))
            rows.append(f'''
          <li>
            <p class="funding-title">{escape(item["title"])}</p>
            <p class="funding-meta">{escape(metadata)}</p>
          </li>''')
        sections.append(f'''
      <section class="section" id="funding" aria-labelledby="funding-title">
        <div class="section-heading">
          <h2 id="funding-title">{escape(copy["fundingHeading"])}</h2>
        </div>
        <ul class="funding-list" role="list">{"".join(rows)}
        </ul>
      </section>''')

    if journals:
        journal_rows = "".join(f"<li>{escape(journal)}</li>" for journal in journals)
        sections.append(f'''
      <section class="section" id="services" aria-labelledby="services-title">
        <div class="section-heading">
          <h2 id="services-title">{escape(copy["servicesHeading"])}</h2>
        </div>
        <h3 class="review-heading">{escape(copy["reviewHeading"])}</h3>
        <ul class="review-list" lang="en" role="list">{journal_rows}</ul>
      </section>''')

    return f'<div class="container academic-details">{"".join(sections)}</div>' if sections else ""


def render_contact(contact, language, copy):
    if not contact:
        return ""

    email = escape(contact["email"])
    address = "<br>".join(escape(line) for line in contact["address"][language])
    website = escape(contact["website"])
    return f'''<section class="contact section" id="contact" aria-labelledby="contact-title">
      <div class="container">
        <div class="section-heading">
          <h2 id="contact-title">{escape(copy["contactHeading"])}</h2>
          <a class="text-link" href="{website}">{escape(copy["schoolLink"])}</a>
        </div>
        <dl class="contact-details">
          <div>
            <dt>{escape(copy["emailLabel"])}</dt>
            <dd><a class="text-link contact-email" href="mailto:{email}">{email}</a></dd>
          </div>
          <div>
            <dt>{escape(copy["addressLabel"])}</dt>
            <dd><address>{address}</address></dd>
          </div>
        </dl>
      </div>
    </section>'''


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
    experience = site.get("experience", [])
    contact = site.get("contact")

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
        experienceNavLink=f'<a href="#experience">{escape(copy["experienceNav"])}</a>' if experience else "",
        contactNavLink=f'<a href="#contact">{escape(copy["contactHeading"])}</a>' if contact else "",
        experienceSection=render_experience(experience, language, copy.get("experienceHeading", "")),
        researchNote="" if experience else f'<p class="section-note">{escape(copy["education"])}</p>',
        researchCards="".join(research_cards),
        topicButtons="\n            ".join(topic_buttons),
        papers=render_papers(papers, topics, name, github, copy["repository"]),
        projectSections=render_projects(
            site["projects"], site.get("projectGroups", {}), language, github, copy["repository"]
        ),
        academicSections=render_academic_sections(
            site.get("funding", []), site.get("reviewJournals", []), language, copy
        ),
        contactSection=render_contact(contact, language, copy),
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
