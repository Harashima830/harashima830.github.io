from pathlib import Path
from datetime import datetime
from html import escape
import re
import markdown

# フォルダの設定
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
BLOG = ROOT / "blog"
CSS = "css/style.css"

BLOG.mkdir(exist_ok=True)
# 記事用HTMLテンプレートを読み込む
ARTICLE_TEMPLATE = (
    ROOT / "templates" / "article.html"
).read_text(encoding="utf-8")

def read_post(path):
    text = path.read_text(encoding="utf-8-sig").lstrip()

    # Markdownの先頭にある記事情報を読み取る
    metadata = {}

    if text.startswith("---"):
        parts = text.split("---", 2)

        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")

            text = parts[2].strip()

    title = metadata.get("title", path.stem)
    date = metadata.get("date", "2026-11-11")

    return title, date, text


def page(title, content, css_path):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} | ナオのHP</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
<header>
    <h1>ナオのHP</h1>
    <p>日常・研究・趣味の記録</p>
    <nav>
        <a href="{ '../' if css_path.startswith('../') else '' }index.html">ホーム</a>
        <a href="{ '../' if css_path.startswith('../') else '' }profile.html">プロフィール</a>
        <a href="{ '../' if css_path.startswith('../') else '' }research.html">研究</a>
        <a href="{ '../' if css_path.startswith('../') else '' }blog.html">ブログ</a>
    </nav>
</header>
<main class="blog-article">
{content}
</main>
<footer>
    <p>© 2026 ナオのHP</p>
</footer>
</body>
</html>"""


articles = []

for md_file in POSTS.glob("*.md"):
    title, date, body = read_post(md_file)

    html_body = markdown.markdown(
        body,
        extensions=["extra", "tables", "fenced_code"]
    )

    output = BLOG / f"{md_file.stem}.html"

    # HTMLテンプレートに記事を挿入
    article_html = (
        ARTICLE_TEMPLATE
        .replace("{{TITLE}}", escape(title))
        .replace("{{DATE}}", escape(date))
        .replace("{{CONTENT}}", html_body)
    )

    # HTMLファイルを書き出す
    output.write_text(
        article_html,
        encoding="utf-8"
    )

    articles.append((date, title, output.name))

# 日付の新しい順に並べる
articles.sort(reverse=True)

list_content = "<h1>ブログ一覧</h1>"

for date, title, filename in articles:
    list_content += f"""
<article>
    <h2>{escape(title)}</h2>
    <p class="blog-date">{escape(date)}</p>
    <a href="blog/{filename}">続きを読む</a>
</article>
"""

(ROOT / "blog.html").write_text(
    page("ブログ一覧", list_content, CSS),
    encoding="utf-8"
)

print(f"ブログ記事を{len(articles)}件生成しました。")
