# Daily Briefing · 每日简报

每天 07:30（澳大利亚墨尔本时间）自动生成的中文新闻简报，覆盖：

1. 世界主要事件
2. 中国政治（含「政策信号解读」）
3. 澳洲新闻
4. 墨尔本新闻
5. 科技与 AI
6. 世界经济

**在线地址：<https://news.maxzhuge.com/>**

（备用：<https://runtaozhuge.github.io/daily-news/>，会 301 跳转到自定义域名）

## 结构

```
.
├── CNAME               # 自定义域名 news.maxzhuge.com
├── index.html          # 首页（自动生成，展示最新一期）
├── archive.html        # 归档（自动生成）
├── feed.json           # 结构化数据（自动生成）
├── build.py            # 构建脚本，重新生成上面三个文件
├── assets/site.css     # 首页与归档页样式
├── YYYY-MM-DD.html     # 每期简报，自包含单文件
└── .nojekyll           # 关闭 GitHub Pages 的 Jekyll 处理
```

每期简报是**自包含 HTML**（CSS 内联、无外部依赖），可以单独下载、离线打开或打印。首页与归档页由 `build.py` 扫描日期文件自动生成。

## 新增一期

```bash
# 1. 放入新一期文件，命名必须是 YYYY-MM-DD.html
#    并在 <head> 中带上三行元数据：
#    <meta name="dn:date"    content="2026-11-09">
#    <meta name="dn:issue"   content="2">
#    <meta name="dn:summary" content="一句话导读">

# 2. 重建首页 / 归档 / feed
python3 build.py

# 3. 发布
git add -A && git commit -m "daily: 2026-11-09" && git push
```

`build.py` 会读取每期页面的 `<h1>`、`class="focus"` 列表和 `dn:*` 元数据，因此新增一期不需要改任何模板。

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 说明

内容基于公开报道整理，每条附原始来源链接；标注「传闻 / 未官宣」「待确认」的信息未经官方确认。中国政治板块的「政策信号解读」为分析判断，不代表官方立场。仅供信息参考，不构成投资建议。
