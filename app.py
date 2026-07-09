import os

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from jinja2 import ChoiceLoader, FileSystemLoader

from admin_produtos import admin_produtos_bp, get_db, init_app as init_produtos_app
from seo import (
    WHATSAPP_PHONE,
    build_default_seo,
    build_home_seo,
    build_not_found_seo,
    build_product_image_alt,
    build_robots_txt,
    build_sitemap_xml,
)


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-admin-secret")
    app.config["DATABASE"] = "admin_produtos_agronossosbichos.db"
    app.config["UPLOAD_FOLDER"] = "static/uploads/produtos"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.jinja_loader = ChoiceLoader(
        [
            app.jinja_loader,
            FileSystemLoader(app.root_path),
        ]
    )

    if config:
        app.config.update(config)

    init_produtos_app(app)
    app.register_blueprint(admin_produtos_bp)

    @app.after_request
    def allow_local_product_api(response):
        if request.path == "/api/produtos":
            response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @app.template_filter("brl")
    def format_brl(value):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.context_processor
    def inject_default_template_context():
        return {
            "seo": build_default_seo(),
            "whatsapp_phone": WHATSAPP_PHONE,
            "product_image_alt": build_product_image_alt,
        }

    @app.get("/")
    def index():
        produtos = get_db().execute(
            "SELECT id, nome, preco, foto FROM produtos ORDER BY id DESC"
        ).fetchall()

        return render_template(
            "index.html",
            produtos=produtos,
            seo=build_home_seo(produtos),
            whatsapp_phone=WHATSAPP_PHONE,
            product_image_alt=build_product_image_alt,
        )

    @app.get("/api/produtos")
    def api_produtos():
        produtos = get_db().execute(
            "SELECT id, nome, preco, foto FROM produtos ORDER BY id DESC"
        ).fetchall()

        return jsonify(
            [
                {
                    "id": produto["id"],
                    "nome": produto["nome"],
                    "preco": produto["preco"],
                    "preco_formatado": format_brl(produto["preco"]),
                    "foto_alt": build_product_image_alt(produto["nome"]),
                    "foto_url": url_for(
                        "static",
                        filename=produto["foto"].replace("static/", "", 1),
                    )
                    if produto["foto"]
                    else url_for("assets", filename="logo-agropecuaria-nossos-bichos.jpg"),
                }
                for produto in produtos
            ]
        )

    @app.get("/assets/<path:filename>")
    def assets(filename):
        return send_from_directory(os.path.join(app.root_path, "assets"), filename)

    @app.get("/fonts/<path:filename>")
    def fonts(filename):
        return send_from_directory(os.path.join(app.root_path, "fonts"), filename)

    @app.get("/sitemap.xml")
    def sitemap_xml():
        return Response(build_sitemap_xml(), mimetype="application/xml")

    @app.get("/robots.txt")
    def robots_txt():
        return Response(build_robots_txt(), mimetype="text/plain")

    @app.get("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "assets"),
            "logo-agropecuaria-nossos-bichos.jpg",
            mimetype="image/jpeg",
        )

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html", seo=build_not_found_seo()), 404

    @app.get("/<path:filename>")
    def root_files(filename):
        is_google_verification = (
            "/" not in filename
            and "\\" not in filename
            and filename.startswith("google")
            and filename.endswith(".html")
            and os.path.isfile(os.path.join(app.root_path, filename))
        )
        if filename in {"styles.css", "script.js"} or is_google_verification:
            return send_from_directory(app.root_path, filename)
        return ("Not found", 404)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
