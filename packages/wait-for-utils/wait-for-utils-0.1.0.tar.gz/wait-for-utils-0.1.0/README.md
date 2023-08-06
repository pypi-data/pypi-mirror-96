# wait-for-utils
![Python Main Release](https://github.com/mtizima/wait-for-utils/workflows/Python%20Main%20Release/badge.svg)

Wait for service(s) to be available before startup docker container.

## Installation
```bash
pip install wait-for-utils
```

## Usage


#### PostgreSQL
Example:
```bash
wait-for-postgres -
```
Additional documentation:
```bash
wait-for-postgres --help
```

By default, all settings are taken from the environment variables.
* **POSTGRES_DB**
* **POSTGRES_USER**
* **POSTGRES_PASSWORD**
* **POSTGRES_HOST**
* **POSTGRES_PORT** 
* **POSTGRES_CHECK_TIMEOUT**
* **POSTGRES_CHECK_INTERVAL**
