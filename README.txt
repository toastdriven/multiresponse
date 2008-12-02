MultiResponse
=============

A Python class for Django to provide mime type aware responses. This allows a client to receive different responses based on the HTTP "Accept" header they send. This is used in place of ``render_to_response`` or a manual ``HttpResponse``.


Requirements
------------

  * Python 2.5+ (lower versions may work but are untested.)
  * Django 1.0+ (again, lower versions may work but are untested.)
  * mimeparse 0.1.2+ - http://code.google.com/p/mimeparse/


Sample Usage:
-------------

  from django.conf import settings
  from django.shortcuts import render_to_response
  from multiresponse import MultiResponse

  def index(request, extension):
      sample_people = [
          {'name': 'Daniel', 'age': 26},
          {'name': 'John', 'age': 26},
          {'name': 'Jane', 'age': 20},
          {'name': 'Bob', 'age': 35},
      ]

      mr = MultiResponse(request)
      mr.register('html', 'index.html')
      mr.register('xml', 'people.xml')
      mr.register('json', 'people.json')
      mr.register('txt', 'people.txt')
      return mr.render({
          'people': sample_people,
      })


Output
------

A HTTP GET to http://localhost:8000/ with a web browser would yield something like:

  HTTP/1.0 200 OK
  Date: Tue, 02 Dec 2008 05:39:53 GMT
  Server: WSGIServer/0.1 Python/2.5.1
  Content-Type: text/html; charset=utf-8
  
  <html>
      <head>
          <title>People</title>
      </head>
      
      <body>
          <h1>People</h1>
          
          <ul>
              
                  <li>Daniel</li>
              
                  <li>John</li>
              
                  <li>Jane</li>
              
                  <li>Bob</li>
              
          </ul>
      </body>
  </html>

However, a HTTP GET to http://localhost:8000/ via "curl -i -H 'Accept: application/xml' http://localhost:8000/" would yield:

  HTTP/1.0 200 OK
  Date: Tue, 02 Dec 2008 05:42:14 GMT
  Server: WSGIServer/0.1 Python/2.5.1
  Content-Type: application/xml; charset=utf-8

  <?xml version="1.0"?>
  <people>

          <person>
              <name>Daniel</name>
              <age>26</age>
          </person>

          <person>
              <name>John</name>
              <age>26</age>
          </person>

          <person>
              <name>Jane</name>
              <age>20</age>
          </person>

          <person>
              <name>Bob</name>
              <age>35</age>
          </person>

  </people>

And a HTTP GET to http://localhost:8000/ via Javascript might look like:

  HTTP/1.0 200 OK
  Date: Tue, 02 Dec 2008 05:42:47 GMT
  Server: WSGIServer/0.1 Python/2.5.1
  Content-Type: application/json; charset=utf-8

  {
      'people': [

              {'name': 'Daniel', 'age': '26'},

              {'name': 'John', 'age': '26'},

              {'name': 'Jane', 'age': '20'},

              {'name': 'Bob', 'age': '35'},

      ]
  }
