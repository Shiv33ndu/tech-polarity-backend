from fastapi import APIRouter
from fastapi.responses import Response
from app.db import mongo

router = APIRouter(tags=["Sitemap"])

SITE_URL = "https://www.techpolarity.com"

STATIC_PAGES = [
    {"loc": "/", "changefreq": "daily", "priority": "1.0"},
    {"loc": "/about", "changefreq": "monthly", "priority": "0.5"},
    {"loc": "/contact", "changefreq": "monthly", "priority": "0.5"},
]


@router.get("/sitemap.xml", response_class=Response)
async def sitemap():
    urls = []

    for page in STATIC_PAGES:
        urls.append(
            f"""  <url>
    <loc>{SITE_URL}{page['loc']}</loc>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
  </url>"""
        )

    # Active categories
    categories = await mongo.database["categories"].find(
        {"is_active": True}, {"slug": 1, "updated_at": 1}
    ).to_list(length=None)

    for cat in categories:
        lastmod = ""
        if cat.get("updated_at"):
            lastmod = f"\n    <lastmod>{cat['updated_at'].strftime('%Y-%m-%d')}</lastmod>"
        urls.append(
            f"""  <url>
    <loc>{SITE_URL}/category/{cat['slug']}</loc>{lastmod}
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>"""
        )

    # Published articles
    articles = await mongo.database["articles"].find(
        {"status": "published"}, {"slug": 1, "published_at": 1, "updated_at": 1}
    ).sort("published_at", -1).to_list(length=None)

    for article in articles:
        date = article.get("updated_at") or article.get("published_at")
        lastmod = f"\n    <lastmod>{date.strftime('%Y-%m-%d')}</lastmod>" if date else ""
        urls.append(
            f"""  <url>
    <loc>{SITE_URL}/article/{article['slug']}</loc>{lastmod}
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "\n".join(urls)
    xml += "\n</urlset>"

    return Response(content=xml, media_type="application/xml")
