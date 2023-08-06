# Timeseer.AI

Timeseer is a Flask web application that can run data quality analyses on time series data.

![Timeseer components](diagrams/components.svg)

## Running

First, install Python and `npm`.

Then create a virtualenv for Python and install dependencies:

```bash
$ python -m venv venv
$ source venv/bin/activate
$ make deps
```

Then generate the NPM libraries:

```bash
$ make npm
```

Then start Timeseer:

```bash
$ make run
```

Timeseer is now listening on http://localhost:5000.

Timeseer Bus needs to be started separately:

```bash
$ make run-bus
```

Timeseer Bus is listening on http://localhost:8081.

## Configuration

Timeseer is configured in `Timeseer.toml`.

This path can be configured using the `--config-file` flag.

### Data storage

The path to the local data storage of Timeseer is configured by:

```toml
data_dir = "<path to data directory>"
```

`data_dir` is not required.
By default, data is stored in the current working directory.

### Includes

Timeseer can include other configuration files.
Configure this using an array of tables:

```toml
[[include]]
glob = "<file glob>"
```

The `glob` key is required.

Paths in includes files are resolved relative to the application working directory.
They are not relative to the included configuration file.

Conflicts are handled depending on the value type:

- `string`: the last included field overrides earlier values
- `list`: the items in the list are appended to the earlier list
- `mapping`: the earlier mapping is updated with the new mapping, overriding existing keys

Note that the main configuration file is processed before any includes.
This means it is not possible to override configuration set by an include in the main configuration file.

Example:

```toml
[[include]]
glob = "examples/*/*.toml"
```

This will include all TOML files in a direct subdirectory of `examples/`.

For example, `examples/csv/csv-examples.toml` could contain:

```toml
[source.row]
type = "csv"
path = "examples/csv/row.csv"
metadata = "examples/csv/row-metadata.csv"
```

### Analysis Configuration

An `[analysis]` section configures the analysis.

The start date of the time period analyzed by Timeseer is configured using:

```toml
[analysis]
start_date = "<RFC3339 timestamp>"
```

The default start date is `2019-01-01T00:00:00Z`.

The number of analysis workers is configured using:

```toml
[analysis]
workers = <number>
```

The default number of workers is the number of processor cores on the system.

### HTTP Configuration

A `[web]` section configures the HTTP webserver.

```toml
[web]
host = "127.0.0.1"
port = 8080
```

On Linux,
2 times the number of visible CPUs + 1 workers are started by default.

This is configurable:

```toml
[web]
workers = 2
```

Timeseer support SAML as a Service Provider.
SAML is configured in the `[web]` section as well.

```toml
[web]
saml.url = "https://demo.timeseer.ai"
saml.key = "saml/timeseer.key"
saml.certificate = "saml/timeseer.cert"
saml.metadata = "saml/idp-metadata.xml"
```

`saml.url` is the URL where the application is available at.

`saml.key` and `saml.certificate` can be generated using:

```bash
$ openssl req -x509 -newkey rsa:2048 -keyout saml/timeseer.key -out saml/timeseer.cert -days 365 -nodes -subj "/CN=demo.timeseer.ai"
```

`saml.metadata` is the metadata provided by the Identity Provider.

SAML metadata for Timeseer is available at `/saml/metadata`.

The data in Timeseer can be exposed to [TrendMiner](https://www.trendminer.com) by enabling
the [TrendMiner Connector API](https://developer.trendminer.com/connector-api/#_api_provider_get) implementation in Timeseer.
Configure a generated api key in Timeseer as the password for the connector in TrendMiner.
The username in TrendMiner needs to be set to then name of the api key.

```
[web.trendminer]
enable = true
```

### Timeseer Bus

The Timeseer serves time series data using [Arrow Flight](https://arrow.apache.org/docs/format/Flight.html).

A `[flight]` section configures the interface.

```toml
[flight]
enabled = false
host = "0.0.0.0"
port = 8081
authentication = true
```

Unless Timeseer has been started with the `--bus` flag,
the interface is only started when `enabled = true`.

Authentication can be turned off for local instances by setting authentication to `false`.
When authentication is turned on, an api key and api key name has to be supplied.

All configured Time Series Sources are made available.

### Sources

Timeseer supports multiple types of time series and metadata sources.
They are [documented separately](timeseer/source/docs/sources.asciidoc).

### Logging

By default, Timeseer logs to standard output.

To log to a daily rotating file, add a `[logging]` section to the Timeseer configuration:

```toml
[logging]
path = "timeseer.log"
```

7 days of logs will be kept.

## Client

See [Timeseer client](timeseer_client/README.md)

### Release

To release a new timeseer client package to PyPI, tag the appropriate commit with `client-<version_number>`.

example:
```bash
git tag -a client-0.0.1
```


## Windows

Timeseer can be packaged as a Windows `.exe` by running:

```
> python .\setup_windows.py bdist_msi
```

This generates an MSI Installer in `dist/`.

For quick testing during development,
a Windows Sandbox configuration is available in `windows/sandbox-timeseer.wsb`.

First configure Timeseer by providing a `Timeseer.toml` configuration file.
A `Timeseer-example.toml` file is provided to be copied.

To start Timeseer as a Windows service, first register it:

```
> New-Service -Name "Timeseer.AI" -BinaryPathName '"C:\Program Files\Timeseer.AI\timeseer-service.exe"'
```

The last parameter is required and can be freely chosen.

Start the actual service:

```
> Start-Service -Name 'Timeseer.AI'
```

To stop:

```
> Stop-Service -Name 'Timeseer.AI'
```

Note that by default, Timeseer is configured on Windows to launch only one worker.
This is a safe default for systems with limited memory.
If not enough memory is available, the Windows Event Viewer will show that the service crashed
with a DEP (Data Execution Prevention) exception.
This probably happens because a `malloc()` returns `NULL` and this is not checked,
causing a `0x0` pointer dereference.

## Development

Install all dependencies:

```bash
(venv) $ make deps dev-deps unix-deps
```

You might need to install additional dependencies for [xmlsec](https://pypi.org/project/xmlsec/).

Lint (and autoformat JS):

```bash
(venv) $ make lint
```

To lint only Python code:

```bash
(venv) $ make lint-python
```

To lint only JS code:

```bash
$ make lint-js
```

Test:

```bash
(venv) $ make test
```

Run the docker container locally:

```bash
$ make run-docker
```

This will start Timeseer at http://localhost:8080.

The examples and example configuration will be volume mapped in the container.

Run a Timeseer bus instance locally:

```bash
$ make run-docker-bus
```

This will start Timeseer Bus at http://localhost:8081.

The examples and example configuration will be volume mapped in the container.

While developing, the `timeseer` module will not be found in tests or modules in VS Code.
To solve this, install the package:

```
(venv) $ pip install -e .
```

Update the VS Code settings to add the current path to the `pylint` path:

```json
    "python.linting.pylintArgs": ["--init-hook 'import sys; sys.path.append(\".\")'"],
```

To enable 'hot' reload for the react files run:

```bash
(venv) $ make npm-dev
```

### Timeseer Client

To run and test a timeseer client locally

Create a new build of the timeseer client

``` bash
(venv) $ python3 timeseer_client/setup_client.py install
```

Create the distributions

``` bash
(venv) $ python3 timeseer_client/setup_client.py sdist bdist_wheel
```

Create a new empty venv to load in your distributions and test

```bash
$ python -m venv venv-new
$ source venv-new/bin/activate
```

Copy the unzipped `timeseer-0.0.0.tar.gz` files into the `venv-new/lib` to start testing.


### Windows

On Windows, the usual Unix tooling is not available.
Install Python and NPM (Node.js).

Install the npm packages:

```
PS > npm ci
PS > npm run build
```

Create the virtual environment:

```
PS > python -m venv venv
```

To be able to enter the virtual environment, allow running unsigned scripts.
This can be done for the current session only:

```
PS > Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
```

Alternatively, launch Powershell with the `-ExecutionPolicy Unrestricted` flag.
This can be configured in the Windows Terminal profile.

Enter the virtual environment:

```
PS > .\venv\Scripts\activate
(venv) PS >
```

Set the environment variables required by Flask to start:

```
(venv) PS > $Env:FLASK_APP = "timeseer.web"
(venv) PS > $Env:FLASK_ENV = "development"
```

Then start Timeseer:

```
(venv) PS > python -m flask run
```

### Configuration

The default configuration contains an include for `data/*.toml`.
Store the configuration for development sources in `data/`.
This prevents them to be overwritten by updates and does not require them to be stashed away when rebasing.

To start Timeseer (on http://localhost:8080) with only one customer configuration loaded, use:

```bash
(venv) $ python -m timeseer.server --config-file data/<customer>.toml
```

### Database Migrations

Timeseer uses [Yoyo](https://ollycope.com/software/yoyo/latest/) for database migrations.
There is one subdirectory of `timeseer/repository/migrations` per database.

Individual migrations follow the `<number>__<name>.(sql|py)` naming conventions.
Dependencies between migrations are not automatically inferred from the naming,
but need to be explicitly declared in the migrations itself.

For example, in `002__index.sql`:

```sql
-- depends: 001__create
```

Observe that there is no extension in the name of the migration.

### InfluxDB

To test the InfluxDB connectivity, a docker container can be built in `examples/influxdb`.

```
$ cd examples/influxdb
$ docker-compose up
$ curl --header 'Accept: application/csv' http://localhost:8086/query?db=NOAA_water_database --data-urlencode "q=SELECT time,\"water_level\" FROM h2o_feet where location = 'santa_monica' and time >= 1568750040000000000 and time < 1568752560000000000"
name,tags,time,water_level
h2o_feet,,1568750040000000000,5.522
h2o_feet,,1568750400000000000,5.627
h2o_feet,,1568750760000000000,5.62
h2o_feet,,1568751120000000000,5.459
h2o_feet,,1568751480000000000,5.551
h2o_feet,,1568751840000000000,5.502
h2o_feet,,1568752200000000000,5.604
```

To remove the database, use:

```
$ docker-compose down --volumes
```

### ODBC

To test the ODBC connectivity, a docker container can be built in `examples/odbc`.

```
$ cd examples/odbc
$ docker build -t timeseer-example-odbc .
$ docker run --rm -p 1433:1433 timeseer-example-odbc:latest
```

On Linux, install `freetds`, then configure Timeseer:

```toml
[source.sql]
type = "odbc"
connection_string = "Driver={/usr/lib/libtdsodbc.so};Server=localhost;Port=1433;Database=TestData;UID=sa;PWD=Timeseer!AI"
metadata_query = "select description, units from Metadata where name = ?"
metadata_columns = ["description", "unit"]
data_query = "select ts, value from Data where name = ? and ts between ? and ?"
```

To simulate a source that returns timestamps and values as strings, update the `data_query`:

```toml
data_query = "select str_ts, str_value from Data where name = ? and ts between ? and ?"
```

This example is configured in [`examples/odbc/odbc-examples.toml`](examples/odbc/odbc-examples.toml)

### Update NPM packages

Timeseer uses `npm` and webpack to manage NPM packages.
Webpack generates static include files in `timeseer/web/static/dist/` from 'libraries' in `src/`.

Update NPM packages in `package.json`.
Then run:

```bash
$ npm run build
```

### Update diagrams

Install [PlantUML](https://plantuml.com/), then run:

```bash
$ make docs
```

### Internal documentation

Internal documentation is written in [AsciiDoc](https://asciidoctor.org/docs/asciidoc-syntax-quick-reference/) in the [docs/](docs/) directory.

Build and run the container locally:

```bash
$ make run-dev-docs
```

The documentation will be available at http://localhost:8082.
