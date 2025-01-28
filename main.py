import os
import socket
import ssl
import urllib
import urllib.parse
import html

class URL:
    def __init__(self, url) -> None:
        if url.startswith("view-source:"):
            self.is_view_source = True
            url = url[12:]
        else:
            self.is_view_source = False
        
        self.scheme, url = url.split("://", 1)

        assert self.scheme in ["http", "https", "file", "data"]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        elif self.scheme == "file":
            self.path = url
        elif self.scheme == "data":
            self.data = url

        if self.scheme in ["http", "https"]:
            if "/" not in url:
                url = url + '/'
                self.host, url = url.split('/', 1)
                self.path = '/' + url

            if ":" in self.host:
                self.host, port = self.host.split(':', 1)
                self.port = int(port)

        self.socket = None

    def __add_headers(self, req, headers):
        for i in headers:
            req += f"{i[0]}: {i[1]}\r\n"
        return req

    def request(self):
        if self.scheme == "file":
            return self.load_file()
        elif self.scheme == "http" or self.scheme == "https":
            return self.load_http()
        elif self.scheme == "data":
            return self.load_data()
        elif self.is_view_source:
            return self.load_source()
        
    def load_source(self):
        return self.load_http()

    def load_http(self):
        # s = socket.socket(family=socket.AF_INET, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM)
        # s.connect((self.host, self.port))


        if self.socket is None:
            self.socket = socket.create_connection((self.host, self.port))


        if self.scheme == "https":
            ctx = ssl.create_default_context()
            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.host)

        req = f"GET {self.path} HTTP/1.1\r\n"
        req += f"Host: {self.host}\r\n"
        
        final_req = self.__add_headers(req, [
            ("Connection", "keep-alive"),
            ("User-Agent", "Pratik's own browser/0.0.1 (github.com/pratik12350/my-own-browser)")
            ])
        final_req += "\r\n"

        self.socket.sendall(final_req.encode("utf8"))

        res = self.socket.makefile('rb', newline="\r\n")

        res_line = res.readline().decode("utf8").strip()
        version, status, explanation = res_line.split(" ", 2)

        res_headers = {}
        while True:
            line = res.readline().decode("utf8").strip()
            if line == "":
                break
            h, v = line.split(':', 1)
            res_headers[h.casefold()] = v.strip()

        if "content-length" in res_headers:
            content_len = int(res_headers["content-length"])
            content = res.read(content_len).decode("utf8")
        else:
            content = ""

        return content


        assert "transfer-encoding" not in res_headers
        assert "content-encoding" not in res_headers

        content = res.read()

        s.close()
        return content
    
    def load_file(self):
        file_path = os.path.abspath(self.path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        
        with open(file_path, "r", encoding="utf8") as f:
            return f.read()
        
    def load_data(self):
        if "," not in self.data:
            raise ValueError("Invalid data URL")
         
        mime_type, data = self.data.split(",", 1)
        mime_type = mime_type or "text/plain"  

        if mime_type.startswith("text/"):
            content = urllib.parse.unquote(data)
        else:
            raise ValueError("Unsupported MIME type provided")
        
        return content

def show_body(body):
    if body is None:
        print("No content to display.")
        return
    
    content = ''
    is_tag = False
    for char in body:
        if char == '<':
            is_tag = True
        elif char == '>':
            is_tag = False
        elif not is_tag:
            content += char

    content = html.unescape(content)
    print(content)


def load(url):
    body = url.request()
    if url.is_view_source:
        print(body)
    else:
        show_body(body)


if __name__ == "__main__":
    import sys
    default_file = "index.html"

    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL(f"file://{os.path.abspath(default_file)}")

    load(url)
