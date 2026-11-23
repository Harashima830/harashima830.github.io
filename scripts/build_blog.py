from pathlib import Path
from html import escape
from collections import defaultdict
import unicodedata
import markdown

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / 'posts'
BLOG = ROOT / 'blog'
CATEGORIES = ROOT / 'categories'
TEMPLATE = (ROOT / 'templates' / 'article.html').read_text(encoding='utf-8')
BLOG.mkdir(exist_ok=True)
CATEGORIES.mkdir(exist_ok=True)

def read_post(path):
    text = path.read_text(encoding='utf-8-sig').lstrip()
    metadata = {}
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")
            text = parts[2].strip()
    return (metadata.get('title', path.stem),
            metadata.get('date', '2026-11-11'),
            metadata.get('category', '未分類'), text)

def page(title, content, prefix=''):
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} | ナオのHP</title>
    <link rel="stylesheet" href="{prefix}css/style.css">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} | ナオのHP</title>
    <link rel="stylesheet" href="{prefix}css/style.css">
</head>
<body>
<header>
    <h1>ナオのHP</h1>
    <p>日常・研究・趣味の記録</p>
    <nav>
        <a href="{prefix}index.html">ホーム</a>
        <a href="{prefix}profile.html">プロフィール</a>
        <a href="{prefix}research.html">研究</a>
        <a href="{prefix}blog.html">ブログ</a>
    </nav>
</header>
<main class="blog-article">
{content}
</main>
<footer><p>© 2026 ナオのHP</p></footer>
</body>
</html>'''

def article_card(post, prefix='', filterable=False):
    category_attr = f' data-category="{escape(post["category"], quote=True)}"' if filterable else ''
    return f'''<article{category_attr}>
    <h2>{escape(post['title'])}</h2>
    <p class="blog-date">{escape(post['date'])}</p>
    <p>カテゴリー：{escape(post['category'])}</p>
    <a href="{prefix}blog/{escape(post['filename'], quote=True)}">続きを読む</a>
</article>'''

posts = []
for md_file in sorted(POSTS.glob('*.md')):
    title, date, category, body = read_post(md_file)
    rendered = markdown.markdown(body, extensions=['extra', 'tables', 'fenced_code'])
    output = BLOG / (md_file.stem + '.html')
   
    # 記事ごとのコメント・返信機能（giscus）
    comments_html = '''
<h2>コメント・感想</h2>
<p>記事へのご意見・ご感想をお待ちしています！</p>

<script src="https://giscus.app/client.js"
        data-repo="Harashima830/harashima830.github.io"
        data-repo-id="R_kgD0TLTCMQ"
        data-category="Announcements"
        data-category-id="DIC_kwD0TLTCMc4DLxDN"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="ja"
        crossorigin="anonymous"
        async>
</script>
'''

    # 記事本文の下にコメント欄を追加
    article_html = (TEMPLATE.replace('{{TITLE}}', escape(title))
                    .replace('{{DATE}}', escape(date))
                    .replace('{{CONTENT}}', rendered + comments_html))

    output.write_text(article_html, encoding='utf-8')
    posts.append({'title': title, 'date': date, 'category': category, 'filename': output.name})

posts.sort(key=lambda p: (p['date'], p['filename']))
by_category = defaultdict(list)
for post in posts:
    by_category[post['category']].append(post)

def category_filename(category):
    normalized = unicodedata.normalize('NFC', category)
    return 'cat-' + normalized.encode('utf-8').hex() + '.html'

links = ['<a href="#all-posts">すべての記事</a>']
for category in sorted(by_category):
    filename = category_filename(category)
    links.append(f'<a href="categories/{filename}">{escape(category)}（{len(by_category[category])}件）</a>')

buttons = ['<button type="button" data-filter="__all__">すべて</button>']
for category in sorted(by_category):
    buttons.append(f'<button type="button" data-filter="{escape(category, quote=True)}">{escape(category)}</button>')

content = ('<h1>ブログ一覧</h1>\n'
           '<h2>カテゴリー別ページ</h2>\n<p>' + ' | '.join(links) + '</p>\n'
           '<h2 id="all-posts">記事を絞り込む</h2>\n'
           '<div id="category-filters">' + ' '.join(buttons) + '</div>\n'
           '<p id="filter-count" aria-live="polite"></p>\n'
           '<div id="all-articles">\n' + '\n'.join(article_card(p, filterable=True) for p in posts) + '\n</div>\n')
content += '''<script>
(function () {
    const buttons = document.querySelectorAll('#category-filters button');
    const articles = document.querySelectorAll('#all-articles article');
    const counter = document.getElementById('filter-count');
    function filter(category) {
        let count = 0;
        articles.forEach(article => {
            const show = category === '__all__' || article.dataset.category === category;
            article.hidden = !show;
            if (show) count++;
        });
        buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
        counter.textContent = count + '件の記事';
    }
    buttons.forEach(button => button.addEventListener('click', () => filter(button.dataset.filter)));
    filter('__all__');
})();
</script>
<style>
#category-filters { display:flex; flex-wrap:wrap; gap:0.5rem; margin:1rem 0; }
#category-filters button { padding:0.45rem 0.8rem; cursor:pointer; border:1px solid #1679b9; border-radius:6px; background:white; color:#064274; }
#category-filters button[aria-pressed="true"] { background:#064274; color:white; }
#all-articles article[hidden] { display:none !important; }
</style>'''
(ROOT / 'blog.html').write_text(page('ブログ一覧', content), encoding='utf-8')

for category, group in by_category.items():
    filename = category_filename(category)
    cat_content = (f'<h1>{escape(category)}の記事一覧</h1>\n'
                   '<p><a href="../blog.html">← ブログ一覧へ戻る</a></p>\n'
                   + '\n'.join(article_card(p, prefix='../') for p in group))
    (CATEGORIES / filename).write_text(page(category, cat_content, prefix='../'), encoding='utf-8')

print(f'ブログ記事を{len(posts)}件、カテゴリー別ページを{len(by_category)}件生成しました。')

