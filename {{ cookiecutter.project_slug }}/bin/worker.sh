#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

celery --app project worker -l INFO
# TODO: if ENV_TYPE == "development", then reload: https://github.com/celery/celery/issues/1658#issuecomment-2370753320
