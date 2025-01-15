<img src='images/smiling_teddy_bear.png'> 

# REINVENT4 <!-- omit from toc -->

[![License MIT](https://img.shields.io/github/license/acceleratedscience/openad_service_utils)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docs](https://img.shields.io/badge/website-live-brightgreen)](https://acceleratedscience.github.io/openad-docs/) <br>
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## About: <!-- omit from toc -->
<About Text needed>

REINVENT is a molecular design tool for de novo design, scaffold hopping,
R-group replacement, linker design, molecule optimization, and other small
molecule design tasks.  REINVENT uses a Reinforcement Learning
(RL) algorithm to generate optimized molecules compliant with a user defined
property profile defined as a multi-component score.  Transfer Learning (TL)
can be used to create or pre-train a model that generates molecules closer
to a set of input molecules. 

A paper describing the software has been published as Open Access in the
Journal of Cheminformatics:
[Reinvent 4: Modern AI–driven generative molecule design](https://link.springer.com/article/10.1186/s13321-024-00812-5?utm_source=rct_congratemailt&utm_medium=email&utm_campaign=oa_20240221&utm_content=10.1186/s13321-024-00812-5).
See AUTHORS.md for references to previous papers.

This repository provides a Python-based tool to access the SMI-TED models via a REST API. Once the API is set up, use the OpenAD Toolkit to easily access the inference functions of SMI-TED. 

More information on SMI-TED can be found at:<br> 
- https://huggingface.co/ibm/materials.smi-ted
- https://github.com/IBM/materials/tree/main
- https://arxiv.org/abs/2407.20267

More information on the OpenAD Toolkit and OpenAD Service Utilities:
- https://accelerate.science/projects/openad
- https://github.com/acceleratedscience/open-ad-toolkit
- https://github.com/acceleratedscience/openad_service_utils

--- 
## Note:
this current version of the code in app.py excludes all other properties other than QM9 properties. you can change this to include QM8 and Molecule Net if checkpoints avsilable by simply changing the selected algorithms list.

## Deployment Options <!-- omit from toc -->

<!-- toc -->

- [Deployment locally using a Python virtual environment](#deployment-locally-using-a-python-virtual-environment)

- [Deployment locally via container](#deployment-locally-via-container)

- [Deployment locally via compose](#deployment-locally-via-compose)

- [Deployment On OpenShift](#deployment-on-openshift)

- [Deployment via Sky Pilot](#deployment-via-sky-pilot)

<!-- tocstop -->
Note: All of these deployment options will allow you to access SMI-TED functions using the [OpenAD Toolkit](https://github.com/acceleratedscience/open-ad-toolkit).  You may want to first install the Toolkit in its own Python environment before proceeding with deploying the SMI-TED utility. <br>

--- 

# Deployment locally using a Python virtual environment 
<br>
You will need a Python level of 3.11 & to follow these installation directions:<br>
<br>

1. Use your favorite Python environment manager (e.g., Conda, Pyenv) to create a new Python 3.11.10 environment <br>

2. Activate the new environment and install the required Python modules for SMI-TED per the "Getting Started" instructions at this site (ignore the requirement to use Python 3.9): <br>
   https://github.com/IBM/materials/<br>
   
3. Install the OpenAD Service Utilities in the new environment with the following command:<br>
   `pip install git+https://github.com/acceleratedscience/openad_service_utils.git@nested_implementation`<br>

4. Clone this repo into a new directory: <br>
   `git clone https://github.com/acceleratedscience/openad_smi_ted`<br>

5. Change directory to `openad_smi_ted`.<br>
  
6. Add the necessary environment variables used by the OpenAD service utilities:<br>
   `source ./openad_smi_ted_bash_env.sh` <br>
   
7. Start the server with the following command:<br>
   `python app.py`<br>

8. Open a new terminal session.
  
9. In the new terminal session start the OpenAD Toolkit:<br>
   `openad`<br>

10. At the OpenAD Toolkit command line execute the following command to create a new service for accessing the local server started in step 7:<br>
   `catalog model service from remote 'http://127.0.0.1:8080/' as sm`<br>

11. At the OpenAD Toolkit command line execute the following command to view the available commands:<br>
   `sm ?`

***Note***: The first time you request a particular property (e.g., "qm8-e1-cam") the OpenAD Service Utility will take some time to download and locally cache the correct models. Requests will proceed much faster once models are cached locally.  

# Deployment locally via container
<br>

***Prerequisites***: Make sure you have Docker and the Docker Buildx plugin installed on your system.<br>

1. Clone this repo into a new directory: <br>
   `git clone https://github.com/acceleratedscience/openad_smi_ted`<br>

2. To build the Docker image, change directory to `openad_smi_ted` then start the build with the following command:<br>
   `docker build -t smi-ted-app .`<br>

3. After the build is complete, execute the following command to run the container and have the server available on port 8080:
   `docker run -p 8080:8080 smi-ted-app`

4. Open a new terminal session and start the OpenAD Toolkit:<br>
   `openad`<br>

5. At the OpenAD Toolkit command line execute the following command to create a new service for accessing the local server started in step 3:<br>
   `catalog model service from remote 'http://0.0.0.0:8080/' as sm`<br>

6. At the OpenAD Toolkit command line execute the following command to view the available commands:<br>
   `sm ?`   

# Deployment On OpenShift 

Install Helm Chart
```shell
helm install smi-ted ./helm-chart
```

Start a new build
```shell
oc start-build smi-ted-build
```

Wait for the build to complete
```shell
LATEST_BUILD=$(oc get builds | grep 'smi-ted-build-' | awk '{print $1}' | sort -V | tail -n 1)

oc wait --for=condition=Complete build/$LATEST_BUILD --timeout=15m
```

Run request test (pod may take some time to initialize so curl request may fail. try again.)
```shell
curl "http://$(oc get route smi-ted-openad-model -o jsonpath='{.spec.host}')/health"
```

# Deployment locally via Compose
<br>
run on the command line `mkdir -p ~/.openad_models`

***Note:*** <br>
Initially downloading models may take some time, this will be prompted by your first request. To pre-load models you can run the following <br><br>
`mkdir -p ~/.openad_models/properties/molecules && aws s3 sync s3://ad-prod-biomed/molecules/smi_ted/ /tmp/.openad_models/properties/molecules/smi_ted --no-sign-request --exact-timestamps`
<br>
it does require installing the AWS cli which can be found here..

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html

then using Podman or Docker run the following in the same directory as the compose.yaml file:
### step 1:
`(podman or docker) compose create`<br>
### step 2:
`(podman or docker) compose start`<br>

the service will start on poert `8080` change this in the compose file if you wish it to run on another port.
### Step 3:
In openad run the following command
`catalog model service from remote 'http://127.0.0.1:8080/' as sm`

### Notes

- The container used is https://quay.io/ibmdpdev/openad_smi_ted:latest

- You can use the compose.yaml file rather than download the entire repository

https://github.com/acceleratedscience/openad_smi_ted/blob/main/compose.yaml

# Deployment via Sky Pilot
<br>
Support for skypilot on AWS is coming soon
<br>
