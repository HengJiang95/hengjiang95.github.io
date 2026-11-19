"use strict";

const figurePreview = document.querySelector(".figure-preview");

if (typeof figurePreview?.showModal === "function") {
  const previewTitle = figurePreview.querySelector("#figure-preview-title");
  const previewImage = figurePreview.querySelector("img");
  const originalLink = figurePreview.querySelector("[data-figure-original]");

  for (const link of document.querySelectorAll("[data-figure-title]")) {
    link.setAttribute("aria-haspopup", "dialog");
    link.addEventListener("click", (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }

      event.preventDefault();
      previewTitle.textContent = link.dataset.figureTitle;
      previewImage.alt = link.querySelector("img").alt;
      previewImage.src = link.href;
      originalLink.href = link.href;
      figurePreview.showModal();
    });
  }

  figurePreview.addEventListener("click", (event) => {
    if (event.target === figurePreview) {
      figurePreview.close();
    }
  });
}
