# paybackapp

## Deployment

In order to build a docker image running the application with gunicorn execute:

    sudo docker build --tag paybackapp .

Then to start the container:

    sudo docker run -v "$(pwd):/app" -dp 6000:6000 paybackapp

If you start the container from outside the application directory, then use the path to the application directory instead of $(pwd).


## Telegram Bot Client
* used to work at last commit but needs updates now
* ask toni for access to the [code](https://github.com/gh-toni/payapp-bot)

## Android Client
* not yet talking to the server, only to other android devices with the same app
* but here's the [code](https://github.com/fstreun/Payapp)
