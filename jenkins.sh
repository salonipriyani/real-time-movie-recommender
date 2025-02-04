echo "Starting tests"
echo "Branch name: $GIT_BRANCH"
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
pytest -v
coverage run -m pytest
coverage report
coverage html