"use strict";

const toolbar = document.querySelector(".filter-toolbar");
const buttons = [...toolbar.querySelectorAll("[data-filter]")];
const search = toolbar.querySelector("#paper-search");
const year = toolbar.querySelector("#paper-year");
const countLabel = toolbar.querySelector(".filter-count");
const emptyMessage = document.querySelector(".publication-empty");
const groups = [...document.querySelectorAll(".year-group")].map((element) => ({
  element,
  year: element.dataset.year,
  papers: [...element.querySelectorAll(".paper")].map((paper) => ({
    element: paper,
    topics: paper.dataset.topics.split(" "),
    text: normalizeText(`${paper.querySelector(".paper-main").textContent} ${paper.dataset.doi}`),
  })),
}));
let topic = "all";

function normalizeText(value) {
  return value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
}

function updatePublications() {
  const keywords = normalizeText(search.value).trim().split(/\s+/).filter(Boolean);
  let visibleCount = 0;
  for (const group of groups) {
    let groupCount = 0;
    const matchesYear = year.value === "" || year.value === group.year;
    for (const paper of group.papers) {
      const visible = matchesYear
        && (topic === "all" || paper.topics.includes(topic))
        && keywords.every((keyword) => paper.text.includes(keyword));
      paper.element.hidden = !visible;
      groupCount += Number(visible);
    }
    group.element.hidden = groupCount === 0;
    visibleCount += groupCount;
  }

  for (const button of buttons) {
    button.setAttribute("aria-pressed", String(button.dataset.filter === topic));
  }
  const pattern = visibleCount === 1 ? countLabel.dataset.countSingle : countLabel.dataset.countPattern;
  countLabel.textContent = pattern.replace("%n", visibleCount);
  emptyMessage.hidden = visibleCount !== 0;
}

function showTopic(selectedTopic) {
  topic = selectedTopic;
  updatePublications();
}

search.addEventListener("input", updatePublications);
year.addEventListener("change", updatePublications);
for (const button of buttons) {
  button.addEventListener("click", () => showTopic(button.dataset.filter));
}
for (const link of document.querySelectorAll("[data-filter-link]")) {
  link.addEventListener("click", (event) => {
    if (event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) {
      showTopic(link.dataset.filterLink);
    }
  });
}

updatePublications();
toolbar.hidden = false;
