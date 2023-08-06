import os
import time
import subprocess
from contextlib import contextmanager

import pytest

import skein


@contextmanager
def set_skein_config(tmpdir):
    tmpdir = str(tmpdir)
    old = skein.properties.config_dir
    try:
        skein.properties._mapping['config_dir'] = tmpdir
        yield tmpdir
    finally:
        skein.properties._mapping['config_dir'] = old


@pytest.fixture
def skein_config(tmpdir_factory):
    with set_skein_config(tmpdir_factory.mktemp('config')) as config:
        yield config


@pytest.fixture(scope="session")
def security(tmpdir_factory):
    path = str(tmpdir_factory.mktemp('security'))
    return skein.Security.new_credentials().to_directory(path)


@pytest.fixture(scope="session")
def has_kerberos_enabled():
    return HAS_KERBEROS


@pytest.fixture(scope="session")
def hadoop3():
    return HADOOP3


KEYTAB_PATH = "/home/testuser/testuser.keytab"
HTTP_KEYTAB_PATH = "/home/testuser/HTTP.keytab"
HAS_KERBEROS = os.environ.get('HADOOP_TESTING_CONFIG', '').lower() == 'kerberos'
HADOOP3 = os.environ.get('HADOOP_TESTING_VERSION', '').lower() == 'cdh6'


@pytest.fixture(scope="session")
def http_keytab():
    if not os.path.exists(HTTP_KEYTAB_PATH):
        pytest.skip("HTTP keytab not found")
    return HTTP_KEYTAB_PATH


def do_kinit():
    subprocess.check_call(["kinit", "-kt", KEYTAB_PATH, "testuser"])


@pytest.fixture(scope="session")
def kinit():
    if HAS_KERBEROS:
        do_kinit()


@pytest.fixture
def not_logged_in():
    if not HAS_KERBEROS:
        pytest.skip("Without kerberos, users are always logged in")
    try:
        subprocess.check_call(["kdestroy"])
        yield
    finally:
        do_kinit()


@pytest.fixture(scope="session")
def client(security, kinit):
    with skein.Client(security=security) as client:
        yield client


sleeper = skein.Service(resources=skein.Resources(memory=32, vcores=1),
                        script='sleep infinity')


sleep_until_killed = skein.ApplicationSpec(name="sleep_until_killed",
                                           queue="default",
                                           tags={'sleeps'},
                                           services={'sleeper': sleeper})


def check_is_shutdown(client, app_id, status=None):
    timeleft = 5
    while timeleft:
        if client.application_report(app_id).state != 'RUNNING':
            break
        time.sleep(0.1)
        timeleft -= 0.1
    else:
        assert False, "Application wasn't properly terminated"

    if status is not None:
        assert client.application_report(app_id).final_status == status


def wait_for_completion(client, app_id, timeout=30):
    while timeout:
        final_status = client.application_report(app_id).final_status
        if final_status != 'UNDEFINED':
            return final_status
        time.sleep(0.1)
        timeout -= 0.1
    else:
        assert False, "Application timed out"


@contextmanager
def ensure_shutdown(client, app_id, status=None):
    try:
        yield
    except Exception:
        client.kill_application(app_id)
        raise
    finally:
        try:
            check_is_shutdown(client, app_id, status=status)
        except AssertionError:
            client.kill_application(app_id)
            raise


@contextmanager
def run_application(client, spec=sleep_until_killed, connect=True):
    if connect:
        app = client.submit_and_connect(spec)
        app_id = app.id
    else:
        app_id = app = client.submit(spec)
    with ensure_shutdown(client, app_id):
        yield app


def wait_for_containers(app, n, **kwargs):
    timeleft = 5
    while timeleft:
        containers = app.get_containers(**kwargs)
        if len(containers) == n:
            break
        time.sleep(0.1)
        timeleft -= 0.1
    else:
        assert False, "timeout"

    return containers


def get_logs(client, app_id, tries=20, user=''):
    for i in range(tries):
        try:
            return client.application_logs(app_id, user=user).dumps()
        except Exception:
            if i == tries - 1:
                raise
        time.sleep(0.20)
