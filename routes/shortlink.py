from flask import request, jsonify, redirect, render_template
from services.utils import generate_shortname, is_valid_url
from routes import routes_bp
import edgedb

# Initialize EdgeDB client
client = edgedb.create_client()

# Shortlink redirection route
@routes_bp.route("/s/<short_name>", methods=["GET"])
def redirect_shortname(short_name):
    result = client.query_single(
        """
            SELECT Shortlink { shortname, url }
            FILTER .shortname = <str>$shortname
            """,
        shortname=short_name,
    )
    if result:
        return redirect(result.url, code=302)
    else:
        return redirect("/")

# Check shortname route
@routes_bp.route("/checkshort")
def check_shortname():
    shortname = request.args.get("shortname")

    if not shortname:
        return jsonify({"error": "Shortname is required"}), 400

    result = client.query_single(
        """
        SELECT Shortlink { shortname }
        FILTER .shortname = <str>$shortname
        """,
        shortname=shortname,
    )

    return jsonify({"check": bool(result)})

# Create shortlink route
@routes_bp.route("/shortlink", methods=["POST"])
def shortlink():
    data = request.get_json()
    url = data.get("url")
    shortname = data.get("shortname", "").strip()

    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid URL format"}), 400

    if not shortname:
        shortname = generate_shortname()

    try:
        existing = client.query_single(
            """
            SELECT Shortlink { shortname }
            FILTER .shortname = <str>$shortname
            """,
            shortname=shortname,
        )

        if existing:
            return jsonify({"error": "Shortname already exists"}), 409

        client.query(
            """
            INSERT Shortlink {
                shortname := <str>$shortname,
                url := <str>$url
            }
            """,
            shortname=shortname,
            url=url,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    shortlink_url = f"/s/{shortname}"
    return jsonify({"shortlink": shortlink_url}), 200

# List all shortlinks route
@routes_bp.route('/links')
def list_links():
    entries = client.query("SELECT Shortlink { shortname, url };")
    return render_template('listshortlink.html', entries=entries)

# Delete a shortlink route
@routes_bp.route('/delete_link/<shortname>', methods=['DELETE'])
def delete_entry(shortname):
    try:
        client.execute("DELETE Shortlink FILTER .shortname = <str>$shortname;", shortname=shortname)
        return jsonify({"message": f"Shortlink '{shortname}' deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Delete all shortlinks route
@routes_bp.route('/delete_all_links', methods=['DELETE'])
def delete_all_entries():
    try:
        client.execute("DELETE Shortlink;")
        return jsonify({"message": "All Shortlink deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400