# Run it locally

Before starting this guide:

- Follow the [local setup](./local-setup.md) documentation.

## Run

Once everything is properly set up, you can launch the project
with the following command at root level:

```bash
poetry run start
```

The application is now launched and running on port 8000 of the machine.

## Webhook setup

### Ngrok setup

As GitHub Actions Exporter depends on webhook coming from github to work properly.

Ngrok can help you setup a public URL to be used with GitHub webhooks.

You can install Ngrok on your Linux machine using the following command:

```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
```

For more information, you can visit the Ngrok [website](https://ngrok.com/download).

Once installed, you can run the following command to listen on port 8000
of the machine and assign a public URL to it.

```shell
ngrok http 8000
```

### Setting up the webhook

Setup a webhook at the organization level, should be on a link like the following:
`https://github.com/organizations/<your org>/settings/hooks`

- Click on Add Webhook
- In payload url, enter your ngrok url, like the following:
  `https://xxxxx.ngrok.io/webhook`
- Content type: application/json
- Click on `Let me select individual events.`
- Select: `Workflow jobs` and `Workflow runs`
- Save

## Setting up your testing repo

Create a new repository in the organization you have configured the runner manager.

And push a workflow in the repository, here is an example:

```yaml
# .github/workflows/test-gh-actions-exporter.yaml
---
name: test-gh-actions-exporter
on:
  push:
  workflow_dispatch:
jobs:
  greet:
    strategy:
      matrix:
        person:
          - foo
          - bar
    runs-on:
      - ubuntu
      - focal
      - large
      - gcloud
    steps:
      - name: sleep
        run: sleep 120
      - name: Send greeting
        run: echo "Hello ${{ matrix.person }}!"
```

Trigger builds and enjoy :beers:
