# everlink

Everlink is a simple application that runs on your machine and proxies downloads through a persistent URL.

It is designed to work with download managers such as IDM (Internet Download Manager). Download managers are great for managing large queues, but download URLs can sometimes expire before a queued download gets a chance to start, or while a download is in progress. Everlink solves this by transparently refreshing expired download URLs. Instead of giving your download manager a temporary URL directly, you give it an Everlink URL. Everlink resolves that URL in the background and refreshes it when necessary, allowing the download to continue even if the original URL expires.

See [Intercepting downloads](#intercepting-downloads) for instructions on how to use Everlink with your downloads.

> **Note:** This project is not actively maintained. Built-in services may stop working if providers change their APIs. Feel free to open an issue if something breaks, but there is no guarantee that it will be fixed.

## Installing

### uv

Install [uv](https://docs.astral.sh/uv/) and run:

```shell
# Set up the package
uv sync

# Start Everlink
uv run everlink
```

### Docker

A Docker setup is also included. Run:

```shell
docker compose up -d
```

Everlink will be available on `localhost:8000`.

### Environment variables

| Variable               | Default   | Description                                               |
|------------------------|-----------|-----------------------------------------------------------|
| `BIND_HOST`            | `0.0.0.0` | Host address the server binds to.                         |
| `PORT`                 | `8000`    | Port the server listens on.                               |
| `DEVELOPMENT`          | `false`   | Enables development features such as automatic reloading. |
| `LOG_LEVEL`            | `INFO`    | Logging level, e.g. `DEBUG`, `INFO`, `WARNING`, `ERROR`.  |
| `CUSTOM_SERVICES_PATH` | —         | Path to the custom-services directory.                    |
| `LOG_FILE`             | —         | Path to the log file. If unset, file logging is disabled. |


## Services

Services tell Everlink how to resolve download links for a particular provider. Each service defines a slug format that Everlink can use to identify a download and obtain its current download URL.

For example, the Google Drive service uses the file ID as its slug. This is the <file-id> part of a Google Drive URL such as `https://drive.google.com/file/d/<file-id>/view?usp=drive_link`, which can be passed to Everlink using the gdrive service.

### Google Drive

Currently supports anonymous requests. Authenticated requests will not work. Public files shared via a URL that anyone can access should work. If Google Drive reports that a quota or download limit has been reached, Everlink will periodically retry the download. This should theoretically work, but it has not been thoroughly tested.

See [`gdrive.py`](src/everlink/services/gdrive.py) for the implementation.


### Custom Services

Additional services can be added by setting the `CUSTOM_SERVICES_PATH` environment variable to a directory containing your custom services.

Custom services are discovered dynamically. Each `.py` file in the configured directory is imported and checked for a `definition` variable containing a `ServiceDefinition` instance. Files whose names start with `_` are ignored. In development mode, files starting with `_` are imported as well, allowing files such as `_example.py` to be loaded for testing.

See [`_example.py`](custom-services/_example.py) for an example of how to define a custom service. For the service interface, see [`interfaces.py`](src/everlink/interfaces.py). Built-in service implementations can be found in [`src/everlink/services/`](src/everlink/services/).

Each service must have a unique ID. If a custom service uses the same ID as a built-in service, the custom service takes precedence and replaces the built-in service.

## Intercepting downloads

To use the transparent proxy, you can intercept downloads with a simple userscript for your browser that replaces the download link for the service.

Alternatively, you can manually copy the slug and add the download using:

`http://localhost:8000/<service>/<url-encoded-slug>`

The slug should be URL-encoded before being added to the URL. For example, if the slug is `abc/123`:

`http://localhost:8000/example/abc%2F123`
