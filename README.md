# Webapp-Deployment-AWS-Lightsail

Deploy Streamlit app on AWS Lightsail with Nginx and Docker.

## Create AWS Lightsail Instance

Use Ubuntu, 20.04

## Install Docker and Docker Compose

[How To Install and Use Docker on Ubuntu 20.04 | DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

[How To Install and Use Docker Compose on Ubuntu 20.04 | DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)

## Install AWS CLI
For my case i have an endpoint of the frontend in AWS SageMaker Instance using boto3.

to install and configure AWS CLI : 

`sudo apt update`

`curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"`

`sudo apt install unzip`

`unzip awscliv2.zip`

`sudo ./aws/install`

`aws configure`

and then enter your access key, secret key and region

## Clone the repo of the app

Go to working directory, in my case `cd ~`  and git clone the repository

## Docker Compose

Go to the repo directory 

`sudo docker-compose up --build -d`



Now, you can access to the app using the public IP.

