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


    # Check if the requested file exists in the path
    # If it exists, the return 200 OK and serve the file,
    # otherwise, return 404 Not Found.
    # If the path is not correct, such as http://127.0.0.1:8080/deep,
    # then use 301 Moved Permanently to redirect to http://127.0.0.1:8080/deep/
    def check_if_file_exists(self, request):

        # From Stack Overflow https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
        # Author is Czarek Tomczak: https://stackoverflow.com/users/623622/czarek-tomczak
        # Get the path in which the script resides
        current_directory = os.path.dirname(os.path.realpath(__file__))

    # Create the conetnt of text in the HTTP response 
    def create_messge(self, status_code, error_code, error_message):

        return "<html><head>\r\n<title>{}</title>\r\n</head>
        <body>\r\n<h1>{}</h1>\r\n<p>{}</p>\r\n</body>
        </html>".format(status_code, error_code, error_message)

    # Create HTTP response
    def create_http_response(self, status_code, mime_type, text):

        return "HTTP/1.1 {}\r\n
        Content-Length: {}\r\n
        Connection: Closed\r\n
        Content-Type: {}\r\n\r\n
        {}\r\n".format(status_code, str(len(text)) mime_type, text)

    # Send the HTTP response
    def send_http_response(self, http_response):
        self.request.sendall(http_response.encode())

    def return_405_method_not_allowed(self):
        status_code = "405 Method Not Allowed"
        error_code = "Method Not Allowed"
        error_message = "This method is not allowed"
        text = create_messge(status_code, error_code, error_message)
        mime_type = "text/html"
        http_response = create_http_response(status_code, mime_type, text)
        send_http_response(http_response)

    # Check if the 'GET' method is contained within the request
    # If it does, then find the requested file
    # Otherwise, return the status code 405 Method Not Allowed
    def determine_method(self, request):
        method = request[0]
        if method = "GET":
            self.check_if_file_exists()
        elif method = "POST" or method = "PUT" or method = "DELETE":
            return_405_method_not_allowed()
        else:
            print("Can't recognize the method")

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # Split the request into an array
        # And decode each item in the array into string
        request = []
        print(type(self.data.split))
        for item in self.data.split():
            request.append(item.decode('utf-8'))
        print(request)
        print(type(request))

        determine_method(request)

        self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
