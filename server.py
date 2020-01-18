#  coding: utf-8
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    # Create the HTML form
    def create_html(self, status_code, error_code, error_message):

        # Credit to https://www.tutorialspoint.com/http/http_responses.htm
        return ('<html><head>\r\n<title>{0}</title>\r\n</head>'
        '<body>\r\n<h1>{1}</h1>\r\n<p>{2}</p>\r\n</body>'
        '</html>').format(status_code, error_code, error_message)

    # Create HTTP response
    def create_http_response(self, status_code, mime_type, content):

        return ('HTTP/1.1 {0}\r\n'
        'Content-Length: {1}\r\n'
        'Connection: Closed\r\n'
        'Content-Type: {2}\r\n\r\n'
        '{3}\r\n').format(status_code, str(len(content)), mime_type, content)

    # Send the HTTP response
    def send_http_response(self, http_response):
        self.request.sendall(http_response.encode())

    def return_200_ok(self, file_path):

        status_code = "200 OK"
        if file_path.endswith("html"):
            mime_type = "text/html"
        elif file_path.endswith("css"):
            mime_type = "text/css"

        # Credit to https://docs.python.org/2/tutorial/errors.html
        try:
            with open(file_path, 'r') as sent_file:
                # Get the content of the file
                html = sent_file.read()
            http_response = self.create_http_response(status_code, mime_type, html)
            self.send_http_response(http_response)

        except Exception as e:
            # If the file is not readable or the file doesn't exist,
            # Then return the 404 status code
            self.return_404_not_found()

    # Create and send back the 301 Moved Permanently html
    # Then redirect to the correct path
    def return_301_moved_permantently(self, correct_path):
        status_code = "301 Moved Permanently"
        error_code = "Moved Permanently"
        error_message = "The document has moved."
        html = ('<html><head>\r\n<title>{0}</title>\r\n</head>'
        '<body>\r\n<h1>{1}</h1>\r\n<p>{2}</p>\r\n<A HREF={3}">Redirect to the correct path</A>\r\n</body>'
        '</html>').format(status_code, error_code, error_message, correct_path)
        mime_type = "text/html"
        http_response = ('HTTP/1.1 {0}\r\n'
        'Location: {1}\r\n'
        'Content-Length: {2}\r\n'
        'Connection: Closed\r\n'
        'Content-Type: {3}\r\n\r\n'
        '{4}\r\n').format(status_code, correct_path, str(len(html)), mime_type, html)
        self.send_http_response(http_response)

    # Create and send back the 404 Not Found html
    def return_404_not_found(self):
        status_code = "404 Not Found"
        error_code = "Not Found"
        error_message = "The requested URL was not found in the path."
        html = self.create_html(status_code, error_code, error_message)
        mime_type = "text/html"
        http_response = self.create_http_response(status_code, mime_type, html)
        self.send_http_response(http_response)

    # Create and send back the 405 Method Not Allowed html
    def return_405_method_not_allowed(self):
        status_code = "405 Method Not Allowed"
        error_code = "Method Not Allowed"
        error_message = "This method is not allowed."
        html = self.create_html(status_code, error_code, error_message)
        mime_type = "text/html"
        http_response = self.create_http_response(status_code, mime_type, html)
        self.send_http_response(http_response)

    # Check if the requested file exists in the path
    # If it exists, the return 200 OK and serve the file,
    # otherwise, return 404 Not Found.
    # If the path is not correct, such as http://127.0.0.1:8080/deep,
    # then use 301 Moved Permanently to redirect to http://127.0.0.1:8080/deep/
    def look_for_file(self, request):

        # From Stack Overflow https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
        # Author is Czarek Tomczak: https://stackoverflow.com/users/623622/czarek-tomczak
        # Get the path in which the script resides
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_name = request[1]
        file_path = ('{0}/www{1}').format(current_directory, file_name)

        # Check if the file exists,
        # And determine if it is a file or directory
        # Credit to https://linuxize.com/post/python-check-if-file-exists/
        if not os.path.exists(file_path):
            self.return_404_not_found()

        else:
            if os.path.isdir(file_path):
                if not file_path.endswith('/'):
                    # file_path = file_path + "/"
                    # Get the folder's name, and redirect to the correct path
                    folder_withoutslash = os.path.split(file_path)[-1]
                    self.return_301_moved_permantently(folder_withoutslash+ "/")

                else:
                    file_path = file_path + "index.html"
                    self.return_200_ok(file_path)

            elif os.path.isfile(file_path):
                self.return_200_ok(file_path)

    # Check if the 'GET' method is contained within the request
    # If it does, then find the requested file
    # Otherwise, return the status code 405 Method Not Allowed
    def determine_method(self, request):
        method = request[0]
        if method == "GET":
            self.look_for_file(request)
        elif method in ("POST", "PUT", "DELETE"):
            self.return_405_method_not_allowed()

    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)

        # Split the request into an array
        # And decode each item in the array into string
        request = []
        for item in self.data.split():
            request.append(item.decode('utf-8'))

        self.determine_method(request)

        # self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
