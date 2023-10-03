# -*- coding: ascii -*-
u"""
:Copyright:

 Copyright 2023
 Andr\xe9 Malo or his licensors, as applicable

:License:

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

============
 Test setup
============

Test setup
"""
__author__ = u"Andr\xe9 Malo, Andr\xe9s Reyes Monge"

import time as _time

import docker as _docker
import pytest as _pytest

POSTGRES_PASSWORD = "supersecretpassword"
POSTGRES_PORT = 65432
POSTGRES_USER = "postgres"
POSTGRES_DB = "postgres"
POSTGRES_HOST = "127.0.0.1"


def _wait_for_postgres_init(container):
    while True:
        _time.sleep(1)
        logs = container.logs().decode("ascii")
        if (
            "PostgreSQL init process complete; ready for start up."
            not in logs
        ):
            continue

        last_log = logs.splitlines()[-1]
        if "database system is ready to accept connections" not in last_log:
            continue

        break


@_pytest.fixture(
    name="postgres_docker",
    params=[11, 12, 13, 14, 15, 16],
    ids=[
        "postgres_v11",
        "postgres_v12",
        "postgres_v13",
        "postgres_v14",
        "postgres_v15",
        "postgres_v16",
    ],
)
def postgres_docker_fixture(request):
    """Start a postgres DB"""
    client = _docker.from_env()
    postgres_version = request.param
    container = client.containers.run(
        image="postgres:{version}".format(version=postgres_version),
        auto_remove=True,
        environment=dict(
            POSTGRES_PASSWORD=POSTGRES_PASSWORD,
        ),
        name="postgres-test-%s" % postgres_version,
        ports={"5432/tcp": (POSTGRES_HOST, POSTGRES_PORT)},
        detach=True,
        remove=True,
    )

    _wait_for_postgres_init(container)

    yield

    container.stop()


@_pytest.fixture()
def postgres_url(postgres_docker):
    """Return connection URL for DB"""
    # pylint: disable = unused-argument

    yield "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
        POSTGRES_USER,
        POSTGRES_PASSWORD,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB,
    )
