# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200"> <br/> Swagger UI for Python

This module is a part of the [Pip.Services](http://pipservices.org) polyglot microservices toolkit.

The swagger module provides a Swagger UI that can be added into microservices and seamlessly integrated with existing REST and Commandable HTTP services.

The module contains the following packages:
- **Build** - Swagger service factory
- **Services** - Swagger UI service

<a name="links"></a> Quick links:

* [API Reference](https://pip-services3-python.github.io/pip-services3-swagger-python)
* [Change Log](CHANGELOG.md)
* [Get Help](https://www.pipservices.org/community/help)
* [Contribute](https://www.pipservices.org/community/contribute)


## Use

Install the Python package as
```bash
pip install pip-services3-swagger
```

Develop a RESTful service component. For example, it may look the following way.
In the `register` method we load an Open API specification for the service.
You can also enable swagger by default in the constractor by setting `_swagger_enable` property.
```python
class MyRestService(RestService):
    def __init__(self):
        super();
        self._base_route = "myservice"
        self._swagger_enable = True

    def __greeting(self):
        name = bottle.request.query.get('name')
        response = "Hello, " + name + "!"
        return self.send_result(result)

    def register(self):
        self.register_route(
            'get', '/greeting',
            ObjectSchema(True)
                .with_required_property("name", TypeCode.String),
            self.__greeting
        )

        self.register_open_api_spec_from_file('./pip_services3_swagger/services/myservice.yml')
```

The Open API specification for the service shall be prepared either manually
or using [Swagger Editor](https://editor.swagger.io/)
```yaml
openapi: '3.0.2'
info:
  title: 'MyService'
  description: 'MyService REST API'
  version: '1'
paths:
  /myservice/greeting:
    get:
      tags:
        - myservice
      operationId: 'greeting'
      parameters:
      - name: correlation_id
        in: query
        description: Correlation ID
        required: false
        schema:
          type: string
      - name: name
        in: query
        description: Name of a person
        required: true
        schema:
          type: string
      responses:
        200:
          description: 'Successful response'
          content:
            application/json:
              schema:
                type: 'string'
```

Include Swagger service into `config.yml` file and enable swagger for your REST or Commandable HTTP services.
Also explicitely adding HttpEndpoint allows to share the same port betwee REST services and the Swagger service.
```yaml
---
...
# Shared HTTP Endpoint
- descriptor: "pip-services:endpoint:http:default:1.0"
  connection:
    protocol: http
    host: localhost
    port: 8080

# Swagger Service
- descriptor: "pip-services:swagger-service:http:default:1.0"

# My RESTful Service
- descriptor: "myservice:service:rest:default:1.0"
  swagger:
    enable: true
```

Finally, remember to add factories to your container, to allow it creating required components.
```python
from pip_services3_rpc.build.DefaultRpcFactory import DefaultRpcFactory
from pip_services3_swagger.build.DefaultSwaggerFactory import DefaultSwaggerFactory
# ...
class MyProcess(ProccesContainer):
    def __init__(self):
        super(MyProcess, self).__init__("myservice", "MyService microservice")

        self._factories.add(DefaultRpcFactory())
        self._factories.add(DefaultSwaggerFactory())
        self._factories.add(MyServiceFactory())
        # ...
```

Launch the microservice and open the browser to open the Open API specification at
[http://localhost:8080/greeting/swagger](http://localhost:8080/greeting/swagger)

Then open the Swagger UI using the link [http://localhost:8080/swagger](http://localhost:8080/swagger).
The result shall look similar to the picture below.

<img src="swagger-ui.png"/>

## Develop

For development you shall install the following prerequisites:
* Python 3.7+
* Visual Studio Code or another IDE of your choice
* Docker

Install dependencies:
```bash
pip install -r requirements.txt
```

Run automated tests:
```bash
python test.py
```

Generate API documentation:
```bash
./docgen.ps1
```

Before committing changes run dockerized build and test as:
```bash
./build.ps1
./test.ps1
./clear.ps1
```

## Contacts

The library is created and maintained by:
- **Sergey Seroukhov**
- **Danil Prisiazhnyi**
