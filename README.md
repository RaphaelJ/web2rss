# Web2RSS

Web2RSS generates RSS feeds from regular webpages.

demo.mov

## Features

* Configure DOM selectors used to extract content
* Uses an LLM to automatically deduce the DOM selectors
* Visual aid tool to configure the DOM selectors

## Setup & running

Use the `Dockerfile` to build a Docker image:

```sh
    docker build -t web2rss .
```

The web app requires the following environment variables:

```sh
    export SERVER_NAME="your_domain.tld"
    export SECRET_KEY="some_long_secret_string"
    export MISTRAL_API_KEY="your_Mistral_AI_API_key"
```

Run the Docker image. The web app will be exposed on port 8080.

```sh
    docker run -p 8080:8080 --env SERVER_NAME --env SECRET_KEY --env MISTRAL_API_KEY web2rss
```