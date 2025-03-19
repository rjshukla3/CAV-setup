# CV2X based vehicle planning and control
This repo contains source codes for CV2X based vehicle control.

The codes are based on Commsignia V2X Remote Python SDK. The SDK is a python package to access low level functionality of the Commsignia V2X stack. 

### Setup
Please refer to group project folder [Commsignia](https://buffalo.box.com/s/f4c25fn1orqedz6q7veceno4writetx1) for details on how to setup Commsignia APIs. 

Python interface are used primarily used. Both C and python interfaces shares the same functionalities to V2X stack. C interface has extension to Commsignia safety services at the application level.

It is recommended to build an virtual environment for Python API usages. E.g., on Mac os (M1 chip).
```
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz
    python3 -m pip install requirements.txt
```

The Python API requires the package requires python 3.7 or newer version, we recommend using Python 3.9.
Please add necessary packages to the [requirements.txt](requirements.txt) file.

To installing the package, `pip3 install $whl_dist` (`whl_dist` is the built distribution).
The current sdk version in use is `Unplugged-RT-y20.39.4-b205116-pythonsdk.tar.xz`. 

### Protocol on testing the codes

All codes need to be tested before merging.

To facilitate the test procedure, the following protocol will be enforced. The goal of this protocol is to make sure any code changes during the test be recorded properly and can be retrieve in the future.

1. Maintain a fork of this repo under your account (your origin). The repo in CHELabUB 

2. Push a test branch with all the testing code and script that are relevant to this repo to your own fork. The branch shall be name with `test_yyyymmdd_xxx` where `_xxx` are required unless there is no ambiguity, it can be word(s) used to describe test purpose.

3. Submit a PR to the upstream branch, mark it with label "test" describe briefly the test procedure and expected outcomes. 

4. Once the test is concluded, briefly summarize the results and then close the PR.

Remark 1: Reuse the same branch for different tests are allowed (though not encouraged), as long as the commits can clearly indicate the changes across different tests.

Remark 2: When merging the code, a designated PR is needed with links towards the test PRs as a proof.
