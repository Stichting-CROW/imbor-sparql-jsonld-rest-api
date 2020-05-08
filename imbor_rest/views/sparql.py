from ..imbor_rest import app, crow_ldp
from flask import render_template, request


@app.route("/endpoint/sparql", methods=["POST"])
def sparql():
    """
    Programmatically query with SPARQL (without hmac).
    """
    # TODO: Ondersteun meer dan alleen POST / SELECT
    # TODO: Voor het uploaden van datasets, ondersteun meer dan 1 MB

    if request.content_length > 1024 * 1024:  # 1 MB
        return "Payload too large (> 1MB)", 413

    res = crow_ldp.select(query=request.form["query"])
    return res, 200


@app.route("/query")
def yasgui():
    """
    Visually query with SPARQL (without hmac).
    """
    return render_template("yasgui.html", base_url=request.url_root)
