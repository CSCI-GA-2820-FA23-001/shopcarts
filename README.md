# Shopcarts Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


## Overview

This repository contains code for the Customer shopcart for an e-commerce web site. This shows how to create a REST API with subordinate resources like shopcarts that have items:

Note: This repo has a both a .devcontainer folder and a Vagrantfile for two ways to bring up a development environment.


## How to Run/Test

This is a flask application. Thus, use

```
Flaks Run
```
to run the application. 

For now, the front end pages is not included. But test cases (under the folder of tests) for api routes are provided. You could run the following unit test command for the application:

- development mode for test all cases

```
python -m unittest
```
- use these to get test coverage of files under /service
```
coverage run -m unittest
coverage report
```

- get detail of all tests cases, green indicates passed cases, red indicates failed cases
```
green
```

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants
└── templates              - front-end pages
    └── index.html         - default index page

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
└── factories.py    - test factory to make fake objects for testing
```

## Information about this repo
These are the RESTful routes for `shopcarts` and `items`
```
Endpoint            Methods  Rule
----------------    -------  -----------------------------------------------------
index               GET      /
indexSecond         GET      /index/<idxName> 

list_shopcarts      GET      /shopcarts
create_shopcarts    POST     /shopcarts
get_shopcarts       GET      /shopcarts/<int:shopcart_id> 
update_shopcarts    PUT      /shopcarts/<int:shopcart_id> 
delete_shopcart     DELETE   /shopcarts/<int:shopcart_id> 

list_items          GET      /shopcarts/<int:shopcart_id>/items   
create_items        POST     /shopcarts/<int:old_cart_id>/items
read_item           GET      /shopcarts/<int:cart_id>/items/<int:item_id> 
update_item         PUT      /shopcarts/<int:cart_id>/items/<int:item_id>  
delete_items        DELETE   /shopcarts/<int:shopcart_id>/items/<int:item_id>
delete_all_items    DELETE   /shopcarts/<int:shopcart_id>/items  
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
