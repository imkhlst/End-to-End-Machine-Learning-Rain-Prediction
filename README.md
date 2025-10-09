# End-to-End-Machine-Learning-Rain-Prediction

### Early Setup
1. Create an repo on your github.
2. Clone the repo into your work directory.
3. Setup your conda environment, you can see steps below.
4. Open a VS Code, then run template.py on your terminal.

## How to create and run conda environment?

Set your conda name and python version. My conda name is rain and python version is 3.11.3.

```bash
conda create -n rain python=3.11.3 -y
```

Initializing your conda before activate. Type bash if you're using git bash.

```bash
conda init bash 
```

Then, activate your conda environment.

```bash
conda activate rain
```

finally, install  the requirements.txt

```bash
pip install -3 requirements.txt
```

## Workflow step
1. Update Constant
2. Update Artifact and Config Entity
3. Update Component
4. Update Pipeline
5. Update Main file

## How to export the environment variable?

```bash
export MONGODB_URL="mongodb+srv://<username>:<password>...."

export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>

export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
```

## AWS CICD Deployment with Github Action

### 1. Login to AWS Console

### 2. Create IAM user for deployment
```
# Specific access

1. EC2 access : It is virtual machine

2. ECR: Elastic Container registry to save your docker image in aws


# Description: About the deployment

1. Build docker image of the source code

2. Push your docker image to ECR

3. Launch Your EC2 

4. Pull Your image from ECR in EC2

5. Lauch your docker image in EC2

# Policy:

1. AmazonEC2ContainerRegistryFullAccess

2. AmazonEC2FullAccess
```

### 3. Create ECR repo to store/save docker image

```
Save your URI after create repository.
```

### 4. Create EC2 machine (Ubuntu)

### 5. Connect EC2 and install docker in EC2 machine
```
# Optional

sudo apt-get update -y

sudo apt-get upgrade

# Required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker
```

### 6. Configure EC2 as self-hosted runner
```
setting > actions > runner > new self hosted runner > choose os > then run command one by one
```

### 7. Setup Github secret
```
setting > Secrets and variables > New Repository secret > Upload repository name and secret one by one as mentioned below.

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- ECR_REPO
```