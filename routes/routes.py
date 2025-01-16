from flask import render_template, request, jsonify, redirect, abort
import edgedb
import re
import random
import string
from routes import routes_bp
from services.s3_service import upload_files_to_s3, list_files_in_s3, s3_client
from botocore.exceptions import ClientError
import os


@routes_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@routes_bp.route("/upload", methods=["POST", "GET"])
def upload_file():
    if request.method == "GET":
        return jsonify({"message": "Use POST to upload files."}), 200
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files part"}), 400

        files = request.files.getlist("files")
        uploaded_files = upload_files_to_s3(files)

        if not uploaded_files:
            return jsonify({"error": "No files uploaded"}), 400

        return (
            jsonify(
                {
                    "message": "Files uploaded successfully",
                    "uploaded_files": uploaded_files,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@routes_bp.route("/files", methods=["GET"])
def list_files():
    try:
        files = list_files_in_s3()
        return render_template("files.html", files=files)
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


BUCKET_NAME = os.getenv("BUCKET_NAME")


@routes_bp.route("/delete_file/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    try:
        # Delete the file from S3
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        return jsonify({"message": f"File '{file_name}' deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@routes_bp.route("/delete_all_files", methods=["DELETE"])
def delete_all_files():
    try:
        # List all files in the bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])
        return jsonify({"message": "All files deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


client = edgedb.create_client(
    os.getenv('EDGEDB_INSTANCE'),secret_key=os.getenv('EDGEDB_SECRET_KEY')
)


def generate_shortname():
    return "".join(random.choices(string.ascii_letters + string.digits, k=4)).lower()


def is_valid_url(url):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IPv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # IPv6
        r"(?::\d+)?"  # port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None


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


@routes_bp.route("/checkshort")
def check_shortname():
    shortname = request.args.get("shortname")

    if not shortname:
        return jsonify({"error": "Shortname is required"}), 400

    # Query the database to check if the shortname exists
    result = client.query_single(
        """
        SELECT Shortlink { shortname }
        FILTER .shortname = <str>$shortname
        """,
        shortname=shortname,
    )

    # Return whether the shortname exists
    return jsonify({"check": bool(result)})


@routes_bp.route("/shortlink", methods=["POST"])
def shortlink():
    data = request.get_json()
    url = data.get("url")
    shortname = data.get("shortname", "").strip()

    # Validate URL format
    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid URL format"}), 400

    # Generate a random shortname if none is provided
    if not shortname:
        shortname = generate_shortname()

    try:
        # Check if the shortname already exists
        existing = client.query_single(
            """
            SELECT Shortlink { shortname }
            FILTER .shortname = <str>$shortname
            """,
            shortname=shortname,
        )

        if existing:
            return jsonify({"error": "Shortname already exists"}), 409

        # Insert the new shortlink into the database
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

    # Return the shortlink
    shortlink_url = f"/s/{shortname}"
    return jsonify({"shortlink": shortlink_url}), 200

@routes_bp.route('/links')
def list_links():
    # Fetch all entries from EdgeDB
    query = """
        SELECT Shortlink {
            shortname,
            url
        };
    """
    entries = client.query(query)
    return render_template('shortnames.html', entries=entries)


@routes_bp.route('/delete_link/<shortname>', methods=['DELETE'])
def delete_entry(shortname):
    # Delete the entry with the given shortname
    try:
        query = """
            DELETE Shortlink
            FILTER .shortname = <str>$shortname;
        """
        client.execute(query, shortname=shortname)
        return jsonify({"message": f"Shortlink '{shortname}' deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@routes_bp.route('/delete_all_links', methods=['DELETE'])
def delete_all_entries():
    # Delete all entries from the database
    try:
        query = "DELETE Shortlink;"
        client.execute(query)
        return jsonify({"message": "All Shortlink deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400