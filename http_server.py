import socket
import sys
import os
import mimetypes

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->
        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    return b"\r\n".join([
                b"HTTP/1.1 200 OK",
                b"Content-Type: " + mimetype,
                b"",
                body,
            ])

def parse_request(request):

    method, uri, version = request.split("\r\n")[0].split(" ")

    if method != "GET":
        raise NotImplementedError

    return uri


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""
    return b"\r\n".join([
                b"HTTP/1.1 405 Method Not Allowed",
                b"",
                b"You can't do that on this server!",
            ])


def response_not_found():
    """Returns a 404 Not Found response"""

    # TODO: Construct and return a 404 "not found" response
    # You can re-use most of the code from the 405 Method Not
    # Allowed response.
    return b"\r\n".join([
                b"HTTP/1.1 404 Not Found",
                b"",
                b"That page wasn't found on this server!",
            ])
    

def resolve_uri(uri):
    """
    This method should return appropriate content and a mime type.

    If the requested URI is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the URI is a file, it should return the contents of that file
    and its correct mimetype.

    If the URI does not map to a real location, it should raise a
    NameError that the server can catch to return a 404 response.

    Ex:
        resolve_uri('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        resolve_uri('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        resolve_uri('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        resolve_uri('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    # TODO: Fill content and mime_type according to the function description
    # above. If the provided URI does not correspond to a real file or
    # directory, then raise a NameError.

    # Hint: When opening a file, use open(filename, "rb") to open and read the
    # file as a stream of bytes.
    content = b"not implemented"
    mime_type = b"not implemented"
    relative_uri = "webroot" + uri

    if os.path.isdir(relative_uri):

        mime_type = "text/plan".encode('utf8')
        # have to do something to print out contents of directory
        # I know how to ls from the command line, but not "here"
        dir_contents = os.listdir(relative_uri)
        str_dir_contents = " \n".join(dir_contents)
        str_dir_contents = str_dir_contents.encode('utf8')
        return str_dir_contents, mime_type


    else:
        mime_type = mimetypes.guess_type(uri)[0].encode('utf8')

        # type_base, sub_type = mime_type.split("/")
        # if type_base == "text":
        with open(relative_uri, 'rb') as file:
            content = file.read()

        # else:
        #     with open("webroot" + uri, 'r') as file:
        #         content = file.read()

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('0.0.0.0', int(os.environ.get('PORT', 10000)))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if len(data) < 1024:
                        break
                    if b'\r\n\r\n' in data:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    # TODO: resolve_uri will raise a NameError if the file
                    # specified by uri can't be found. If it does raise a
                    # NameError, then let response get response_not_found()
                    # instead of response_ok()
                    try:
                        body, mimetype = resolve_uri(uri)
                        response = response_ok(body=body, mimetype=mimetype)
                    except FileNotFoundError:
                        response = response_not_found()
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
