import json
import time
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import subprocess
import sys
import os

STATUS_FILE = "status.txt"

app = Flask(__name__)
CORS(app)


# serve the static html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# serve script.js and styles.css and other image files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# make a clean object from status file, so that frontend can easily parse it and display the progress
def parse_status_file():
    if not os.path.exists(STATUS_FILE):
        return {
            "status": "waiting",
            "total_pages": 0,
            "completed_count": 0,
            "raw_latest_page": "",
            "restored_latest_page": "",
            "latest_page": ""
        }

    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return {
                "status": "waiting",
                "total_pages": 0,
                "completed_count": 0,
                "raw_latest_page": "",
                "restored_latest_page": "",
                "latest_page": ""
            }

        total_pages = 0
        raw_pages = []
        restored_pages = []
        success = False
        failed = False

        if "Total Pages:" in lines[0]:
            parts = lines[0].split("Total Pages:")
            if len(parts) > 1:
                total_pages = int(parts[1].lower().replace("pages.", "").strip())

        for line in lines[1:]:
            page_name = ""

            if line.startswith("RAW:") or "Successfully fetched and saved page:" in line:
                start = line.find("'") + 1
                end = line.rfind("'")
                if start > 0 and end > start:
                    page_name = os.path.basename(line[start:end].strip())
                    if page_name and page_name not in raw_pages:
                        raw_pages.append(page_name)

            elif line.startswith("RESTORED:"):
                start = line.find("'") + 1
                end = line.rfind("'")
                if start > 0 and end > start:
                    page_name = os.path.basename(line[start:end].strip())
                    if page_name and page_name not in restored_pages:
                        restored_pages.append(page_name)
            elif line.startswith("SUCCESS:"):
                success = True
            elif line.startswith("FAILED:"):
                failed = True

        raw_latest_page = raw_pages[-1] if raw_pages else ""
        restored_latest_page = restored_pages[-1] if restored_pages else ""
        completed_count = len(restored_pages) if restored_pages else len(raw_pages)
        latest_page = restored_latest_page or raw_latest_page
        all_pages_complete = total_pages > 0 and len(restored_pages) >= total_pages

        if all_pages_complete:
            return {
                "status": "completed" if success and not failed else "pdf_creation_failed" if failed and not success else "processing",
                "total_pages": total_pages,
                "completed_count": completed_count,
                "raw_latest_page": raw_latest_page,
                "restored_latest_page": restored_latest_page,
                "latest_page": latest_page,
                "message": "PDF downloaded successfully." if success and not failed else "Failed to create PDF." if failed and not success else ""
            }

        return {
            "status": "processing",
            "total_pages": total_pages,
            "completed_count": completed_count,
            "raw_latest_page": raw_latest_page,
            "restored_latest_page": restored_latest_page,
            "latest_page": latest_page,
            "message": ""
        }

    except Exception:
        return {
            "status": "processing",
            "total_pages": 0,
            "completed_count": 0,
            "raw_latest_page": "",
            "restored_latest_page": "",
            "latest_page": ""
        }


def status_snapshot_response():
    return jsonify(parse_status_file())



# serve the index.html file for the download functionality

@app.route('/download', methods=['POST'])
def start_download():
    data = request.get_json()
    book_slug = data.get('slug')
    
    if not book_slug:
        return jsonify({"status": "error", "message": "No book name provided!"}), 400
    
    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
        except Exception:
            pass

    try:
        print(f"Launching background process main.py for book: {book_slug}...")
        # using detached process to run main.py in the background
        # so i can stream the status updates to the frontend without blocking
        subprocess.Popen([sys.executable, 'main.py', book_slug])
        return jsonify({
            "status": "success", 
            "message": f"Download initiated for {book_slug}!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# serve the status updates to the frontend, Just using for the first update
@app.route('/status', methods=['GET'])
def get_status():
    return status_snapshot_response()


# live streaming via server-sent events (SSE) to the frontend, so that the progress bar can be updated in real-time, using yield to send the data in chunks, and the frontend can listen to the events and update the progress bar accordingly.
@app.route('/status-stream', methods=['GET'])
def status_stream():
    @stream_with_context
    def generate():
        sentinel = object()
        last_snapshot = sentinel
        last_mtime = sentinel

        while True:
            try:
                current_mtime = os.path.getmtime(STATUS_FILE) if os.path.exists(STATUS_FILE) else None
            except OSError:
                current_mtime = None

            if current_mtime != last_mtime or last_snapshot is sentinel:
                last_mtime = current_mtime
                snapshot = parse_status_file()

                if snapshot != last_snapshot:
                    last_snapshot = snapshot
                    yield f"event: status\ndata: {json.dumps(snapshot)}\n\n"

            time.sleep(0.1)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)