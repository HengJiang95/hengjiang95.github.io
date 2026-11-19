"use strict";

const owner = "HengJiang95";
const repository = `${owner}/hengjiang95.github.io`;
const repoAPI = `/repos/${repository}`;
const sitePath = "content/site.json";
const papersPath = "content/publications.json";
const contentPaths = [sitePath, papersPath];
const login = document.querySelector("#login");
const tokenField = document.querySelector("#token");
const loginStatus = document.querySelector("#login-status");
const editor = document.querySelector("#editor");
const fields = document.querySelector("#entries");
const publishButton = editor.querySelector("[type=submit]");
const logout = document.querySelector("#sign-out");
const publishStatus = document.querySelector("#publish-status");
const commitLink = document.querySelector("#last-commit");
const bioEn = document.querySelector("#bio-en");
const bioZh = document.querySelector("#bio-zh");
const lists = {
  paper: document.querySelector("#paper-list"),
  project: document.querySelector("#project-list"),
};
const originalRecords = new WeakMap();
let session;

async function github(path, token, method = "GET", data) {
  const response = await fetch(`https://api.github.com${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "X-GitHub-Api-Version": "2026-03-10",
    },
    body: data === undefined ? undefined : JSON.stringify(data),
    cache: "no-store",
    credentials: "omit",
    redirect: "error",
    signal: AbortSignal.timeout(25000),
  });
  if (!response.ok) {
    const error = new Error(`GitHub 请求失败（${response.status}）。`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

async function readHead(token) {
  const ref = await github(`${repoAPI}/git/ref/heads/main`, token);
  return ref.object.sha;
}

async function readFile(path, token, revision) {
  const file = await github(`${repoAPI}/contents/${path}?ref=${revision}`, token);
  const bytes = Uint8Array.from(atob(file.content.replace(/\s/g, "")), (character) => character.charCodeAt(0));
  return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
}

async function readContent(token, revision) {
  return Object.fromEntries(await Promise.all(contentPaths.map(async (path) => [
    path,
    await readFile(path, token, revision),
  ])));
}

function setStatus(element, message, error = false) {
  element.textContent = message;
  element.classList.toggle("error", error);
}

function topics() {
  return Object.entries(session.site.languages["zh-CN"].topics)
    .map(([key, topic]) => [key, topic.label]);
}

function addOptions(select, options, value) {
  select.append(new Option("请选择", ""));
  for (const [key, label] of options) select.append(new Option(label, key));
  select.value = value ?? "";
}

function addEntry(kind, record = {}) {
  const entry = document.querySelector(`#${kind}-template`).content.firstElementChild.cloneNode(true);
  const control = (name) => entry.querySelector(`[name="${name}"]`);
  const title = control(kind === "paper" ? "title" : "name");
  const summary = entry.querySelector("summary");
  originalRecords.set(entry, record);
  title.value = record.title ?? record.name ?? "";
  control("repository").value = record.repository ?? "";

  if (kind === "paper") {
    for (const name of ["year", "journal", "details", "doi"]) {
      control(name).value = record[name] ?? "";
    }
    control("authors").value = record.authors?.join("\n") ?? "";
    const choices = entry.querySelector("[data-topics]");
    for (const [key, label] of topics()) {
      const wrapper = document.createElement("label");
      const box = document.createElement("input");
      box.type = "checkbox";
      box.value = key;
      box.checked = record.topics?.includes(key) ?? false;
      wrapper.append(box, label);
      choices.append(wrapper);
    }
  } else {
    const groups = Object.entries(session.site.projectGroups)
      .map(([key, labels]) => [key, labels["zh-CN"]]);
    addOptions(control("group"), groups, record.group);
    addOptions(control("topic"), topics(), record.topic);
    control("descriptionEn").value = record.description?.en ?? "";
    control("descriptionZh").value = record.description?.["zh-CN"] ?? "";
  }

  function updateSummary() {
    const year = control("year")?.value;
    const label = kind === "paper" ? "新论文" : "新项目";
    summary.textContent = year ? `${year} · ${title.value.trim() || label}` : title.value.trim() || label;
  }
  updateSummary();
  entry.addEventListener("input", updateSummary);
  entry.querySelector("[data-remove]").addEventListener("click", () => entry.remove());
  lists[kind].append(entry);
  if (!Object.keys(record).length) {
    entry.open = true;
    title.focus();
  }
}

function fillEditor() {
  bioEn.value = session.site.languages.en.copy.bio;
  bioZh.value = session.site.languages["zh-CN"].copy.bio;
  for (const kind of Object.keys(lists)) lists[kind].replaceChildren();
  for (const paper of session.papers) addEntry("paper", paper);
  for (const project of session.site.projects) addEntry("project", project);
}

function readEntries(kind) {
  return Array.from(lists[kind].children, (entry) => {
    const value = (name) => entry.querySelector(`[name="${name}"]`).value.trim();
    const record = { ...originalRecords.get(entry) };
    if (kind === "project") {
      return {
        ...record,
        name: value("name"),
        group: value("group"),
        topic: value("topic"),
        repository: value("repository"),
        description: { ...record.description, en: value("descriptionEn"), "zh-CN": value("descriptionZh") },
      };
    }

    const authors = value("authors").split(/\r?\n/).map((author) => author.trim()).filter(Boolean);
    const selected = Array.from(entry.querySelectorAll("[data-topics] :checked"), (box) => box.value);
    const oldTopics = record.topics?.filter((topic) => selected.includes(topic)) ?? [];
    const doi = value("doi").replace(/^https?:\/\/(dx\.)?doi\.org\//i, "");
    if (doi && !/^10\.\d{4,9}\/\S+$/.test(doi)) {
      throw new Error(`请检查论文《${value("title")}》的 DOI 格式。`);
    }
    Object.assign(record, {
      title: value("title"),
      year: Number(value("year")),
      journal: value("journal"),
      authors,
      details: value("details"),
      topics: [...new Set([...oldTopics, ...selected])],
    });
    for (const [key, content] of [["repository", value("repository")], ["doi", doi]]) {
      if (content) record[key] = content;
      else delete record[key];
    }
    return record;
  });
}

function collectDraft() {
  const site = structuredClone(session.site);
  site.languages.en.copy.bio = bioEn.value.trim();
  site.languages["zh-CN"].copy.bio = bioZh.value.trim();
  site.projects = readEntries("project");
  return { [sitePath]: site, [papersPath]: readEntries("paper") };
}

function validateFields() {
  for (const control of fields.querySelectorAll("input, select, textarea")) {
    control.setCustomValidity(control.required && !control.value.trim() ? "请填写此项。" : "");
    if (!control.checkValidity()) {
      const entry = control.closest("details");
      if (entry) entry.open = true;
      control.reportValidity();
      return false;
    }
  }
  return true;
}

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

async function publish(draft) {
  const { token, revision, site, papers } = session;
  const original = { [sitePath]: site, [papersPath]: papers };
  const changed = Object.keys(draft).filter((path) => !same(draft[path], original[path]));
  if (!changed.length) return null;

  const head = await readHead(token);
  let baseFiles = original;
  if (head !== revision) {
    baseFiles = await readContent(token, head);
    if (changed.every((path) => same(draft[path], baseFiles[path]))) {
      return { revision: head, files: baseFiles };
    }
    if (changed.some((path) => !same(original[path], baseFiles[path]))) {
      throw new Error("仓库内容已更新。当前页保留了草稿，请另开管理页读取新版后合并修改。");
    }
  }

  const base = await github(`${repoAPI}/git/commits/${head}`, token);
  const tree = await github(`${repoAPI}/git/trees`, token, "POST", {
    base_tree: base.tree.sha,
    tree: changed.map((path) => ({
      path,
      mode: "100644",
      type: "blob",
      content: JSON.stringify(draft[path], null, 2) + "\n",
    })),
  });
  const commit = await github(`${repoAPI}/git/commits`, token, "POST", {
    message: "Update academic website content",
    tree: tree.sha,
    parents: [head],
  });
  try {
    await github(`${repoAPI}/git/refs/heads/main`, token, "PATCH", { sha: commit.sha, force: false });
  } catch (error) {
    if (error.status === 422 || error.status === 409) {
      throw new Error("提交发生冲突。当前页保留了草稿，可以重试。");
    }
    throw error;
  }
  for (const path of changed) baseFiles[path] = draft[path];
  return { revision: commit.sha, files: baseFiles };
}

function messageFor(error) {
  if (error.status === 401) return "GitHub 令牌无效或已过期。";
  if (error.status === 403 || error.status === 404) {
    return "GitHub 无法访问仓库。请检查令牌是否选中本站仓库并授予 Contents 读写权限。";
  }
  if (error instanceof TypeError || error.name === "TimeoutError") {
    return "连接 GitHub 失败。请检查网络后重试。";
  }
  return error.message;
}

login.addEventListener("submit", async (event) => {
  event.preventDefault();
  const token = tokenField.value.trim();
  tokenField.value = "";
  if (!token.startsWith("github_pat_")) {
    setStatus(loginStatus, "请输入 GitHub 细粒度访问令牌。", true);
    tokenField.focus();
    return;
  }

  const loginFields = login.querySelector("fieldset");
  loginFields.disabled = true;
  setStatus(loginStatus, "正在验证 GitHub 账号并读取内容…");
  try {
    const account = await github("/user", token);
    if (account.login.toLowerCase() !== owner.toLowerCase()) {
      throw new Error("请使用网站所有者的 GitHub 账号创建令牌。");
    }
    const revision = await readHead(token);
    const files = await readContent(token, revision);
    session = { token, revision, site: files[sitePath], papers: files[papersPath] };
    fillEditor();
    login.hidden = true;
    setStatus(loginStatus, "");
    editor.hidden = false;
    bioZh.focus();
  } catch (error) {
    session = undefined;
    setStatus(loginStatus, messageFor(error), true);
  } finally {
    loginFields.disabled = false;
  }
});

for (const button of editor.querySelectorAll("[data-add]")) {
  button.addEventListener("click", () => addEntry(button.dataset.add));
}

editor.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!session || publishButton.disabled || !validateFields()) return;
  fields.disabled = publishButton.disabled = logout.disabled = true;
  commitLink.hidden = true;
  setStatus(publishStatus, "正在提交到 GitHub…");
  try {
    const draft = collectDraft();
    const saved = await publish(draft);
    if (saved) {
      session.revision = saved.revision;
      session.site = saved.files[sitePath];
      session.papers = saved.files[papersPath];
      fillEditor();
      commitLink.href = `https://github.com/${repository}/commit/${saved.revision}`;
      commitLink.hidden = false;
      setStatus(publishStatus, "已提交。GitHub Actions 正在处理网站发布。");
    } else {
      setStatus(publishStatus, "没有需要提交的更改。");
    }
  } catch (error) {
    setStatus(publishStatus, messageFor(error), true);
  } finally {
    fields.disabled = publishButton.disabled = logout.disabled = false;
  }
});

logout.addEventListener("click", () => {
  session = undefined;
  editor.reset();
  for (const list of Object.values(lists)) list.replaceChildren();
  commitLink.removeAttribute("href");
  commitLink.hidden = true;
  setStatus(publishStatus, "");
  editor.hidden = true;
  login.hidden = false;
  tokenField.focus();
});
