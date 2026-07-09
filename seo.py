from datetime import date
from html import escape

from flask import request, url_for


SITE_NAME = "Agropecuária Nossos Bichos"
SITE_TAGLINE = "Rações, pets e produtos agropecuários em Volta Redonda"
PUBLIC_BASE_URL = "https://agronossosbichos.com.br"
BUSINESS_CITY = "Volta Redonda"
BUSINESS_REGION = "RJ"
BUSINESS_COUNTRY = "BR"
WHATSAPP_PHONE = "552433467354"
DISPLAY_PHONE = "+55 24 3346-7354"
INSTAGRAM_URL = "https://www.instagram.com/agronbichos/"
MAPS_URL = "https://maps.app.goo.gl/mN2von8hsKx4cabq6"
LOGO_IMAGE = "logo-agropecuaria-nossos-bichos.jpg"
OG_IMAGE_ALT = (
    "Logo da Agropecuária Nossos Bichos, agropecuária em Volta Redonda, RJ"
)


def official_url(path="/"):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{PUBLIC_BASE_URL}{path if path.startswith('/') else f'/{path}'}"


def asset_url(filename):
    return official_url(url_for("assets", filename=filename))


def current_page_url():
    return official_url(request.path)


def build_meta(title, description, canonical_url, robots="index, follow"):
    image_url = asset_url(LOGO_IMAGE)
    return {
        "title": title,
        "description": description,
        "canonical_url": canonical_url,
        "robots": robots,
        "image_url": image_url,
        "image_alt": OG_IMAGE_ALT,
        "site_name": SITE_NAME,
        "locale": "pt_BR",
        "twitter_card": "summary_large_image",
        "schema": None,
    }


def build_default_seo():
    return build_meta(
        title=(
            "Agropecuária Nossos Bichos em Volta Redonda | "
            "Rações, Pets e Produtos Agropecuários"
        ),
        description=(
            "Agropecuária Nossos Bichos em Volta Redonda RJ. Encontre rações, "
            "produtos para pets, acessórios e itens agropecuários com atendimento "
            "especializado."
        ),
        canonical_url=current_page_url(),
    )


def build_product_image_alt(product_name):
    return (
        f"Foto do produto {product_name} disponível na {SITE_NAME} em "
        f"{BUSINESS_CITY}, {BUSINESS_REGION}"
    )


def build_home_seo(produtos):
    canonical_url = official_url(url_for("index"))
    title = (
        "Agropecuária Nossos Bichos em Volta Redonda | "
        "Rações, Pets e Produtos Agropecuários"
    )
    description = (
        "Agropecuária Nossos Bichos em Volta Redonda RJ. Encontre rações, "
        "produtos para pets, acessórios e itens agropecuários com atendimento "
        "especializado."
    )
    seo = build_meta(title, description, canonical_url)
    seo["schema"] = build_home_schema(produtos, canonical_url)
    return seo


def build_admin_seo(title):
    return build_meta(
        title=title,
        description=(
            "Área administrativa da Agropecuária Nossos Bichos para gestão "
            "interna de produtos."
        ),
        canonical_url=current_page_url(),
        robots="noindex, nofollow",
    )


def build_not_found_seo():
    return build_meta(
        title=f"Página não encontrada | {SITE_NAME}",
        description=(
            "A página solicitada não foi encontrada. Acesse a Agropecuária "
            "Nossos Bichos em Volta Redonda para ver produtos, localização "
            "e formas de contato."
        ),
        canonical_url=current_page_url(),
        robots="noindex, follow",
    )


def build_home_schema(produtos, canonical_url):
    business_id = f"{canonical_url}#localbusiness"
    website_id = f"{canonical_url}#website"
    logo_url = asset_url(LOGO_IMAGE)

    graph = [
        {
            "@type": "PetStore",
            "@id": business_id,
            "name": SITE_NAME,
            "description": (
                "Agropecuária e pet shop em Volta Redonda, RJ, com rações, "
                "acessórios pet, produtos para animais e atendimento local."
            ),
            "url": canonical_url,
            "image": logo_url,
            "logo": logo_url,
            "telephone": DISPLAY_PHONE,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": BUSINESS_CITY,
                "addressRegion": BUSINESS_REGION,
                "addressCountry": BUSINESS_COUNTRY,
            },
            "areaServed": [
                {
                    "@type": "City",
                    "name": BUSINESS_CITY,
                    "addressRegion": BUSINESS_REGION,
                },
                {
                    "@type": "AdministrativeArea",
                    "name": "Rio de Janeiro",
                },
            ],
            "hasMap": MAPS_URL,
            "sameAs": [INSTAGRAM_URL],
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": DISPLAY_PHONE,
                "contactType": "customer service",
                "areaServed": BUSINESS_COUNTRY,
                "availableLanguage": "pt-BR",
            },
        },
        {
            "@type": "WebSite",
            "@id": website_id,
            "name": SITE_NAME,
            "alternateName": SITE_TAGLINE,
            "url": canonical_url,
            "publisher": {"@id": business_id},
            "inLanguage": "pt-BR",
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{canonical_url}#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Início",
                    "item": canonical_url,
                }
            ],
        },
    ]

    product_items = []
    for position, produto in enumerate(produtos, start=1):
        product = {
            "@type": "Product",
            "name": produto["nome"],
            "brand": {"@id": business_id},
            "offers": {
                "@type": "Offer",
                "price": f"{produto['preco']:.2f}",
                "priceCurrency": "BRL",
                "availability": "https://schema.org/InStock",
                "url": f"{canonical_url}#produtos",
            },
        }
        if produto["foto"]:
            product["image"] = official_url(
                url_for(
                    "static",
                    filename=produto["foto"].replace("static/", "", 1),
                )
            )
        else:
            product["image"] = logo_url

        product_items.append(
            {
                "@type": "ListItem",
                "position": position,
                "item": product,
            }
        )

    if product_items:
        graph.append(
            {
                "@type": "ItemList",
                "@id": f"{canonical_url}#produtos-lista",
                "name": f"Produtos pet e agropecuários em {BUSINESS_CITY}",
                "itemListElement": product_items,
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}


def build_sitemap_xml():
    canonical_url = official_url(url_for("index"))
    today = date.today().isoformat()
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{escape(canonical_url)}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    )


def build_robots_txt():
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {official_url(url_for('sitemap_xml'))}",
            "",
        ]
    )
