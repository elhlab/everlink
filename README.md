# everlink

Everlink is a simple application that runs on your machine.
It proxies downloads while keeping them alive if the session expires due to a long queue time, for example.

This application is meant to be run with a download manager such as IDM (Internet Download Manager).
These managers are great, but sometimes your queue fills up or an unstable download link keeps expiring.
Everlink solves this by transparently refreshing the download link.

## Installing

Install [uv](https://docs.astral.sh/uv/) and run:

```shell
uv sync
```

### Running

Once installed, start Everlink with:

```shell
uv run everlink
```

By default, Everlink listens on `0.0.0.0:8000`. You can change this and other settings using the environment variables below.

### Environment variables

| Variable               | Default           | Description                                               |
|------------------------|-------------------|-----------------------------------------------------------|
| `BIND_HOST`            | `0.0.0.0`         | Host address the server binds to.                         |
| `PORT`                 | `8000`            | Port the server listens on.                               |
| `DEVELOPMENT`          | `false`           | Enables development features such as automatic reloading. |
| `LOG_LEVEL`            | `INFO`            | Logging level, e.g. `DEBUG`, `INFO`, `WARNING`, `ERROR`.  |
| `CUSTOM_SERVICES_PATH` | `custom-services` | Path to the custom-services directory.                    |
| `LOG_FILE`             | —                 | Path to the log file. If unset, file logging is disabled. |

### Custom Services

You can add your own services by placing them in the `custom-services` directory, or by specifying a different directory with the `CUSTOM_SERVICES_PATH` environment variable.

See `_example.py` for an example of how to define a custom downloader. For built-in service implementations, see `src/everlink/services/`.

Custom services are discovered dynamically. Everlink imports each `.py` file in the configured directory and looks for a `definition` variable containing a `ServiceDefinition` instance (see `src/everlink/interfaces.py`). Files whose names start with `_` are ignored.

In development mode, files starting with `_` are imported as well. This allows files such as `_example.py` to be loaded for testing.

Each service must have a unique ID. If a custom service has the same ID as a built-in service, the custom service takes precedence and replaces the built-in service.

## Intercepting downloads

To use the transparent proxy, you can intercept downloads with a simple userscript for your browser that replaces the download link for the service.

Alternatively, you can manually copy the slug and add the download using:

`http://localhost:8000/<service>/<url-encoded-slug>`

The slug should be URL-encoded before being added to the URL.

For example, if the slug is `abc/123`:

`http://localhost:8000/example/abc%2F123`
