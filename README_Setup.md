# Setup

This project should be built in Linux environment (or WSL2).

---

## AWS CLI + AWS CDK + Node.js

```
$ sudo apt update && sudo apt upgrade -y
```

```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
$ sudo apt install unzip -y
$ unzip awscliv2.zip
$ sudo ./aws/install
$ rm -rf ./aws
$ aws --version
aws-cli/2.31.18 Python/3.13.7 Linux/6.6.87.2-microsoft-standard-WSL2 exe/x86_64.ubuntu.22
```

```
$ curl https://get.volta.sh | bash
$ source ~/.bashrc
$ volta --version
2.0.2
$ volta install node@v22.0.0
$ volta list
⚡️ Currently active tools:

    Node: v22.0.0 (default)
    Tool binaries available: NONE
```

```
$ npm install -g aws-cdk
$ cdk --version
2.1030.0 (build e46adaf)
```

---

## initialize project

```
$ cd src
$ cdk init app --language=typescript
```

---

## tool

```
$ npm install --save-dev prettier
```

---

## Docker

* Creating ECR repository at first.
    ```
    $ aws ecr create-repository --repository-name upload-images-repo --region=ap-northeast-1 --profile=<your profile>
    $ aws ecr create-repository --repository-name inference-repo --region=ap-northeast-1 --profile=<your profile>
    ```
* login
    ```
    $ aws ecr get-login-password --region=ap-northeast-1 --profile=<your profile> | docker login --username=AWS --password-stdin <account_id>.dkr.ecr.ap-northeast-1.amazonaws.com
    ```
* Building docker image on CLI.
    ```
    $ docker build -t upload-images ./lambdas/upload-images
    $ docker build -t inference ./lambdas/inference
    ```
* Pushing docker image to repository
    ```
    $ docker tag upload-images:latest <account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/upload-images-repo:latest
    $ docker push <account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/upload-images-repo:latest
    $ docker tag inference:latest <account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/inference-repo:latest
    $ docker push <account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/inference-repo:latest
    ```
* Finally, cdk deploy. 


---
