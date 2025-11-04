# Getting started

## First thing to get started, please provide your Docker org name

::variableDefinition[orgname]{prompt="What is your Docker org name?"}

## 1. Morror a DHI node image repo

Go to the [Python DHI page](https://hub.docker.com/orgs/$$orgname$$/hardened-images/catalog/dhi/python) and click on the `Mirror to repository` button.

In the opened pop-up set the name of the destination repository to `dhi-python`  
![Morror Python DHI](.labspace/images/mirror-python.png)  

Click on Mirror. In a few minutes you'll see all available Node DHI tags in your `dhi-python` repository in the Docker Hub. Mirrored repositories work like any other repository in your Docker Hub organization

## 2. Login with docker 
In order to use Docker Scout to analyze the image during this lab, you will need to be logged in. Make sure that you are logged in with Docker:
```bash
docker login
```
You should see the following message:
```bash no-run-button no-copy-button
Login Succeeded
```
If not, follow the instructions to complete login. 

## 3. Configure Docker Scout organization 

If your account is part of an paid organization, you may have additional output that reflects policy alignment.
```bash
docker scout config organization $$orgname$$
```