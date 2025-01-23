from edgedb import ClientError
from routes import routes_bp
from flask import render_template, jsonify, request, redirect
# from services.s3_service import s3_client, BUCKET_NAME

@routes_bp.route('/example')
def example():
    return render_template("example.html")


# def upload_files_to_s3(file):
#     file_name = file.filename
#     s3_client.upload_fileobj(
#         Fileobj=file.stream,
#         Bucket=BUCKET_NAME,
#         Key=file_name,
#         ExtraArgs={'ContentType': file.content_type}
#         )
#     return 'Complate'
CHUNK_SIZE = 2 * 1024 * 1024  # 2MB
@routes_bp.route('/upex', methods=['POST'])
def upex():
    try:
        file = request.files['file']
        print(file.stream.read(CHUNK_SIZE))
        return redirect('/example')
    except Exception as e:
        return {'error': str(e)}