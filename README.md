# Heng Jiang · 个人学术主页

中英双语的静态学术网站。英文首页位于 `/`，中文首页位于 `/zh/`。

- [Google 学术](https://scholar.google.com/citations?user=1Rei_ToAAAAJ&hl=zh-CN)
- [ORCID](https://orcid.org/0000-0002-9344-4836)
- [GitHub](https://github.com/HengJiang95)

## 更新内容

在 `content/site.json` 修改简介、研究方向和项目，在 `content/publications.json` 更新论文。保留 DOI 和作者顺序以便查证。

用 Python 3.10 或以上版本运行 `python scripts/build.py`，即可生成英文和中文页面。将内容文件和重新生成的两个 `index.html` 一起提交。

本地预览可在仓库根目录运行 `python -m http.server 8000`，随后打开 [http://localhost:8000](http://localhost:8000)。

## GitHub Pages

在仓库的 **Settings → Pages** 中选择 **Deploy from a branch**，发布源设为 **`main`** 和 **`/(root)`**。站点入口为 [hengjiang95.github.io](https://hengjiang95.github.io/)。 [GitHub Pages 文档](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

## 内容与素材

论文信息依据公开的 ORCID 记录、Crossref 和出版商页面。首页图像由数值体模的平行束投影和滤波反投影生成。Inter 与 Instrument Serif 使用 SIL Open Font License，许可证见 `assets/fonts/`。

