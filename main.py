import socket
import ssl

class URL:
    def __init__(self, url) -> None:
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

       

        if "/" not in url:
            url = url + '/'
            self.host, url = url.split('/', 1)
            self.path = '/' + url

        if ":" in self.host:
            self.host, port = self.host.split(':', 1)
            self.port = int(port)


    def __add_headers(self, req, headers):
        for i in headers:
            req += f"{i[0]}: {i[1]}\r\n"

        return req


    def request(self):
        s = socket.socket(family=socket.AF_INET, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM)
        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        req = f"GET {self.path} HTTP/1.1\r\n"
        req += f"Host: {self.host}\r\n"
        
        final_req = self.__add_headers(req, [
            ("Connection", "Close"),
            ("User-Agent", "Pratik's own browser/0.0.1 (github.com/pratik12350/my-own-browser)")
            ])
        final_req += "\r\n"

        print(final_req)
        s.send(final_req.encode("utf8"))

        res = s.makefile('r', newline="\r\n", encoding="utf8")

        res_line = res.readline()
        version, status, explaination = res_line.split(" ", 2)

        res_headers = {}
        while True:
            line = res.readline()
            if line == "\r\n": break
            h, v = line.split(':', 1)
            res_headers[h.casefold()] = v.strip()

        assert "transfer-encoding" not in res_headers
        assert "content-encoding" not in res_headers

        content = res.read()

        s.close()
        return content


def show_body(body):
    is_tag = False
    for char in body:
        if char == '<':
            is_tag = True
        elif char == '>':
            is_tag = False
        elif not is_tag:
            print(char, end='')


def load(url):
    body = url.request()
    show_body(body)



if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
