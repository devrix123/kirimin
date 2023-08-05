from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import cgi
import threading
import urllib.parse

# Lokasi direktori penyimpanan file yang dapat diunduh
file_storage_directory = ""

class FileUploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")  # Tambahkan charset=utf-8 di sini
            self.end_headers()
            html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Unggah File</title>
                </head>
                <body>
                    <h1>Unggah File</h1>
                    <form method="post" enctype="multipart/form-data" action="/unggah">
                        <input type="file" name="file" id="file">
                        <input type="submit" value="Unggah">
                    </form>
                    <br>
                    <a href="/files">Lihat File yang Tersimpan</a>
                </body>
                </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/files":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")  # Tambahkan charset=utf-8 di sini
            self.end_headers()
            html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Daftar File</title>
                </head>
                <body>
                    <h1>Daftar File</h1>
                    <a href="/unggah">Unggah File</a>
                    <br>
                    <br>
            """
            file_list = os.listdir(file_storage_directory)
            for filename in file_list:
                encoded_filename = urllib.parse.quote(filename)
                html += f"<a href='/download/{encoded_filename}'>{filename}</a><br>"
            html += """
                </body>
                </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif self.path.startswith("/download/"):
            filename = self.path.lstrip("/download/")
            filename = urllib.parse.unquote(filename)
            file_path = os.path.join(file_storage_directory, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.send_header("Content-Disposition", f"attachment; filename={filename}")
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == "/unggah":
            self._handle_upload_form()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/unggah":
            self._handle_upload_post()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_upload_form(self):
        # Tampilkan halaman unggah file
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")  # Tambahkan charset=utf-8 di sini
        self.end_headers()
        html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unggah File</title>
            </head>
            <body>
                <h1>Unggah File</h1>
                <form method="post" enctype="multipart/form-data" action="/unggah">
                    <input type="file" name="file" id="file">
                    <input type="submit" value="Unggah">
                </form>
                <br>
                <a href="/files">Lihat File yang Tersimpan</a>
            </body>
            </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def _handle_upload_post(self):
        form_data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        file_item = form_data['file']
        if file_item.file:
            filename = os.path.basename(file_item.filename)
            filename = urllib.parse.quote(filename)  # Enkode nama file
            file_path = os.path.join(file_storage_directory, filename)

            with open(file_path, 'wb') as f:
                f.write(file_item.file.read())

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")  # Tambahkan charset=utf-8 di sini
            self.end_headers()
            self.wfile.write(b"File berhasil diunggah!")
            self.wfile.write(b"<br>")
            self.wfile.write(b"<a href='/'>Unggah File Lagi</a>")
            self.wfile.write(b"<br>")
            self.wfile.write(b"<a href='/files'>Lihat File yang Tersimpan</a>")
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")  # Tambahkan charset=utf-8 di sini
            self.end_headers()
            self.wfile.write(b"Tidak ada file yang diunggah.")
            self.wfile.write(b"<br>")
            self.wfile.write(b"<a href='/'>Coba Unggah Lagi</a>")

def run_server():
    host = '0.0.0.0'
    port = 5001

    if not os.path.exists(file_storage_directory):
        os.makedirs(file_storage_directory)

    server_address = (host, port)
    httpd = HTTPServer(server_address, FileUploadHandler)
    print(f"Server berjalan di http://{host}:{port}")

    # Buat thread baru untuk menangani permintaan
    server_thread = threading.Thread(target=httpd.serve_forever)

    # Set daemon menjadi True agar thread berhenti ketika program berhenti
    server_thread.daemon = True

    # Jalankan thread
    server_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        httpd.shutdown()
        print("\nServer berhenti.")

if __name__ == '__main__':
    run_server()
