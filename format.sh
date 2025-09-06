set -x

ruff --select F401 --select I001 --fix . 
ruff format .
ruff --fix .

