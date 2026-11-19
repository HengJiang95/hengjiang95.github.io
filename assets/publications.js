"use strict";

const toolbar = document.querySelector(".filter-toolbar");
const buttons = [...toolbar.querySelectorAll("[data-filter]")];
const groups = [...document.querySelectorAll(".year-group")].map((element) => ({
  element,
  papers: [...element.querySelectorAll(".paper")].map((paper) => ({
    element: paper,
    topics: paper.dataset.topics.split(" "),
  })),
}));
const countLabel = toolbar.querySelector(".filter-count");

function showTopic(topic) {
  let visibleCount = 0;
  for (const group of groups) {
    let groupCount = 0;
    for (const paper of group.papers) {
      const visible = topic === "all" || paper.topics.includes(topic);
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
}

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

showTopic("all");
toolbar.hidden = false;
