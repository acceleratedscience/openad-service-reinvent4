# REINVENT 4 &nbsp;/&nbsp; Generative Models with SMILES Output

<!--
The description & support tags are consumed by the generate_docs() script
in the openad-website repo, to generate the 'Available Services' page:
https://openad.accelerate.science/docs/model-service/available-services
-->

<!-- support:apple_silicon:false -->
<!-- support:gcloud:true -->

[![License MIT](https://img.shields.io/github/license/acceleratedscience/openad_service_utils)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docs](https://img.shields.io/badge/website-live-brightgreen)](https://acceleratedscience.github.io/openad-docs/) <br>
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## About

<!-- description -->
This OpenAD service provides access to the **REINVENT 4** molecular design tool, which is used for de novo design, scaffold hopping, R-group replacement, linker design, molecule optimization, and other small molecule design tasks. REINVENT uses a Reinforcement Learning (RL) algorithm to generate optimized molecules compliant with a user-defined property profile defined as a multi-component score. Transfer Learning (TL) can be used to create or pre-train a model that generates molecules closer to a set of input molecules. 

More information:  
[github.com/MolecularAI/REINVENT4](https://github.com/MolecularAI/REINVENT4)  
[link.springer.com/article/10.1186/s13321-024-00812-5](https://link.springer.com/article/10.1186/s13321-024-00812-5)
<!-- /description -->

For instructions on how to deploy and use this service in OpenAD, please refer to the [OpenAD docs](https://openad.accelerate.science/docs/model-service/deploying-models).

<br>

## Deployment Options

- ✅ [Deployment via container + compose.yaml](https://openad.accelerate.science/docs/model-service/deploying-models#deployment-via-container-composeyaml-recommended)
- ✅ [Deployment via container](https://openad.accelerate.science/docs/model-service/deploying-models#deployment-via-container)
- ✅ [Local deployment using a Python virtual environment](https://openad.accelerate.science/docs/model-service/deploying-models#local-deployment-using-a-python-virtual-environment)
- ✅ [Cloud deployment to Google Cloud Run](https://openad.accelerate.science/docs/model-service/deploying-models#cloud-deployment-to-google-cloud-run)
- ✅ [Cloud deployment to Red Hat OpenShift](https://openad.accelerate.science/docs/model-service/deploying-models#cloud-deployment-to-red-hat-openshift)
- ✅ [Cloud deployment to SkyPilot on AWS](https://openad.accelerate.science/docs/model-service/deploying-models/#cloud-deployment-to-skypilot-on-aws)
