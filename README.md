ABOUT HOPE Country Report
=========================


## Contributing

### System Requirements

- python 3.11
- [pdm](https://pdm.fming.dev/2.9/)

## Configure development environment

### Clone repo and install requirements
    git clone https://github.com/unicef/hope-country-report 
    pdm venv create 3.11
    pdm install
    pdm venv activate in-project
    pre-commit install

### configure your environment

Uses `./manage.py env` to check required (and optional) variables to put 

    ./manage.py env --check

### Run upgrade to run migrations and initial setup

    ./manage.py upgrade

### (Optional) Create some sample data

    ./manage.py demo

If `DEBUG=True` you can login using any username/password. Note that:

    - If username starts with `admin` will be created a superuser   
    - If username starts with `user`  will be created a standard user (no staff, no admin)