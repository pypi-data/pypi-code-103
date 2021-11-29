# -*- coding: utf-8 -*-

import base64
import json
import pytest
import queue
import tuxsuite.build
import requests
import tuxsuite.exceptions


@pytest.mark.parametrize(
    "url,result",
    [
        ("git@github.com:torvalds/linux.git", False),  # ssh type urls not supported
        ("https://github.com/torvalds/linux.git", True),
        ("http://github.com/torvalds/linux.git", True),
        ("git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git", True),
        ("https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git", True),
        (
            "https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux.git",
            True,
        ),
    ],
)
def test_is_supported_git_url(url, result):
    assert tuxsuite.build.Build.is_supported_git_url(url) == result


headers = {"Content-type": "application/json", "Authorization": "header"}


class TestPostRequest:
    def test_post_request_pass(self, post, response, mocker):
        request = {"a": "b"}
        response._content = b'{"a": "b"}'
        assert tuxsuite.build.post_request(
            url="http://foo.bar.com/pass", headers=headers, request=request
        ) == {"a": "b"}
        post.assert_called_with(
            "http://foo.bar.com/pass",
            data='{"a": "b"}',
            headers=headers,
            timeout=mocker.ANY,
        )

    def test_post_request_timeout(self, post, response, mocker):
        request = {"a": "b"}
        response.status_code = 504

        with pytest.raises(requests.exceptions.HTTPError):
            tuxsuite.build.post_request(
                url="http://foo.bar.com/timeout",
                headers=headers,
                request=request,
            )

    def test_post_request_bad_request(self, post, response):
        request = {"a": "b"}
        response.status_code = 400
        response._content = b'{"tuxbuild_status": "a", "status_message": "b"}'

        with pytest.raises(tuxsuite.exceptions.BadRequest):
            tuxsuite.build.post_request(
                url="http://foo.bar.com/bad_request", headers=headers, request=request
            )


class TestGetRequest:
    def test_get_request_pass(self, get, response, mocker):
        response._content = b'{"a": "b"}'

        assert tuxsuite.build.get_request(
            url="http://foo.bar.com/pass", headers=headers
        ) == {"a": "b"}
        get.assert_called_with(
            "http://foo.bar.com/pass",
            headers=headers,
            timeout=mocker.ANY,
            params=None,
        )

    def test_get_request_timeout(self, get, response):
        response.status_code = 504

        with pytest.raises(requests.exceptions.HTTPError):
            tuxsuite.build.get_request(
                url="http://foo.bar.com/timeout", headers=headers
            )

    def test_get_request_500(self, get, response):
        response.status_code = 500

        with pytest.raises(requests.exceptions.HTTPError):
            tuxsuite.build.get_request(
                url="http://foo.bar.com/timeout", headers=headers
            )

    def test_get_request_bad_request(self, get, response):
        response.status_code = 400

        with pytest.raises(requests.exceptions.HTTPError):
            tuxsuite.build.get_request(
                url="http://foo.bar.com/bad_request", headers=headers
            )

    def test_get_request_connectionfailure(self, get):
        get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            tuxsuite.build.get_request(
                url="http://foo.bar.com/connection_failure", headers=headers
            )


@pytest.fixture
def start_time():
    pytest.time = 0


def mock_time():
    return pytest.time


def mock_sleep(n):
    pytest.time += n
    return pytest.time


@pytest.fixture(autouse=True)
def time(mocker, start_time):
    return mocker.patch("time.time", side_effect=mock_time)


@pytest.fixture(autouse=True)
def sleep(mocker, start_time):
    return mocker.patch("time.sleep", side_effect=mock_sleep)


@pytest.fixture
def build_attrs():
    return {
        "group": "tuxsuite",
        "project": "unittests",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }


@pytest.fixture
def build(build_attrs):
    b = tuxsuite.build.Build(**build_attrs)
    b.uid = "myuid"
    return b


class TestBuild:
    def test_kconfig(self, build):
        assert type(build.kconfig) == list

    @pytest.mark.parametrize(
        "attr,value",
        (
            ("git_repo", None),
            ("git_ref", None),
            ("target_arch", None),
            ("kconfig", None),
            ("kconfig", ()),
            ("toolchain", None),
        ),
    )
    def test_requires_mandatory_attributes(self, build_attrs, attr, value):
        build_attrs[attr] = value
        with pytest.raises(AssertionError) as assertion:
            tuxsuite.build.Build(**build_attrs)
        assert attr in str(assertion)

    def test_validates_git_url(self, build_attrs):
        build_attrs["git_repo"] = "ssh://foo.com:bar.git"
        with pytest.raises(AssertionError) as assertion:
            tuxsuite.build.Build(**build_attrs)
        assert "git url must be in the form" in str(assertion)

    def test_headers(self, build):
        assert build.headers["Content-Type"] == "application/json"
        assert build.headers["Authorization"] == build.token

    def test_user_agent(self, build):
        assert build.headers["User-Agent"].startswith("tuxsuite/")

    def test_git_sha(self, build_attrs):
        del build_attrs["git_ref"]
        build_attrs["git_sha"] = "deadbeef"
        build = tuxsuite.build.Build(**build_attrs)
        assert build.git_sha == "deadbeef"

    def test_git_ref_or_git_sha_required(self, build_attrs):
        del build_attrs["git_ref"]
        with pytest.raises(AssertionError) as assertion:
            tuxsuite.build.Build(**build_attrs)
        assert "git_ref" in str(assertion)
        assert "git_sha" in str(assertion)

    def test_build_name(self, build_attrs):
        del build_attrs["build_name"]
        build_attrs["build_name"] = "melody"
        build = tuxsuite.build.Build(**build_attrs)
        assert build.build_name == "melody"

    def test_submit_build_git_ref(self, build, build_attrs, mocker):
        post_request = mocker.patch("tuxsuite.build.post_request")
        api_build_url = (
            build_attrs["tuxapi_url"] + "/v1/groups/tuxsuite/projects/unittests/builds"
        )

        build.build()
        post_request.assert_called_with(
            api_build_url,
            mocker.ANY,
            {
                "builds": [
                    {
                        "git_repo": build_attrs["git_repo"],
                        "git_ref": build_attrs["git_ref"],
                        "toolchain": build_attrs["toolchain"],
                        "target_arch": build_attrs["target_arch"],
                        "kconfig": [build_attrs["kconfig"]],
                        "build_name": build_attrs["build_name"],
                        "client_token": mocker.ANY,
                        "environment": {},
                        "targets": [],
                        "make_variables": {},
                        "kernel_image": build_attrs["kernel_image"],
                    },
                ],
                "patches": {},
            },
        )

    def test_submit_build_git_sha(self, build, build_attrs, mocker):
        post_request = mocker.patch("tuxsuite.build.post_request")
        api_build_url = (
            build_attrs["tuxapi_url"] + "/v1/groups/tuxsuite/projects/unittests/builds"
        )

        build.git_ref = None
        build.git_sha = "badbee"
        build.build()
        post_request.assert_called_with(
            api_build_url,
            mocker.ANY,
            {
                "builds": [
                    {
                        "git_repo": build_attrs["git_repo"],
                        "git_sha": "badbee",
                        "toolchain": build_attrs["toolchain"],
                        "target_arch": build_attrs["target_arch"],
                        "kconfig": [build_attrs["kconfig"]],
                        "build_name": build_attrs["build_name"],
                        "client_token": mocker.ANY,
                        "environment": {},
                        "targets": [],
                        "make_variables": {},
                        "kernel_image": build_attrs["kernel_image"],
                    },
                ],
                "patches": {},
            },
        )

    def test_client_token(self, build):
        assert type(build.client_token) is str

    def test_build_name_type(self, build):
        assert type(build.build_name) is str

    def test_submit_build_environment(self, build, build_attrs, mocker):
        build_attrs["environment"] = {
            "KCONFIG_ALLCONFIG": "arch/arm64/configs/defconfig",
        }
        post_request = mocker.patch("tuxsuite.build.post_request")
        api_build_url = (
            build_attrs["tuxapi_url"] + "/v1/groups/tuxsuite/projects/unittests/builds"
        )

        build.git_ref = None
        build.git_sha = "badbee"
        build.environment = {
            "KCONFIG_ALLCONFIG": "arch/arm64/configs/defconfig",
        }
        build.build()
        post_request.assert_called_with(
            api_build_url,
            mocker.ANY,
            {
                "builds": [
                    {
                        "git_repo": build_attrs["git_repo"],
                        "git_sha": "badbee",
                        "toolchain": build_attrs["toolchain"],
                        "target_arch": build_attrs["target_arch"],
                        "kconfig": [build_attrs["kconfig"]],
                        "build_name": build_attrs["build_name"],
                        "client_token": mocker.ANY,
                        "environment": build_attrs["environment"],
                        "targets": [],
                        "make_variables": {},
                        "kernel_image": build_attrs["kernel_image"],
                    }
                ],
                "patches": {},
            },
        )

    def test_submit_build_targets(self, build, build_attrs, mocker):
        build_attrs["targets"] = ["dtbs", "config"]
        post_request = mocker.patch("tuxsuite.build.post_request")
        api_build_url = (
            build_attrs["tuxapi_url"] + "/v1/groups/tuxsuite/projects/unittests/builds"
        )

        build.git_ref = None
        build.git_sha = "badbee"
        build.targets = ["dtbs", "config"]
        build.build()
        post_request.assert_called_with(
            api_build_url,
            mocker.ANY,
            {
                "builds": [
                    {
                        "git_repo": build_attrs["git_repo"],
                        "git_sha": "badbee",
                        "toolchain": build_attrs["toolchain"],
                        "target_arch": build_attrs["target_arch"],
                        "kconfig": [build_attrs["kconfig"]],
                        "build_name": build_attrs["build_name"],
                        "client_token": mocker.ANY,
                        "targets": build_attrs["targets"],
                        "environment": {},
                        "make_variables": {},
                        "kernel_image": build_attrs["kernel_image"],
                    },
                ],
                "patches": {},
            },
        )

    def test_submit_build_make_variables(self, build, build_attrs, mocker):
        build_attrs["make_variables"] = {"W": "12", "LLVM": "1"}
        post_request = mocker.patch("tuxsuite.build.post_request")
        api_build_url = (
            build_attrs["tuxapi_url"] + "/v1/groups/tuxsuite/projects/unittests/builds"
        )

        build.git_ref = None
        build.git_sha = "badbee"
        build.make_variables = {"W": "12", "LLVM": "1"}
        build.build()
        post_request.assert_called_with(
            api_build_url,
            mocker.ANY,
            {
                "builds": [
                    {
                        "git_repo": build_attrs["git_repo"],
                        "git_sha": "badbee",
                        "toolchain": build_attrs["toolchain"],
                        "target_arch": build_attrs["target_arch"],
                        "kconfig": [build_attrs["kconfig"]],
                        "build_name": build_attrs["build_name"],
                        "client_token": mocker.ANY,
                        "targets": [],
                        "environment": {},
                        "make_variables": {"W": "12", "LLVM": "1"},
                        "kernel_image": build_attrs["kernel_image"],
                    },
                ],
                "patches": {},
            },
        )


class TestWatch:
    @staticmethod
    def watch(obj):
        states = []
        for state in obj.watch():
            states.append(state)
        return states


class TestBuildWatch(TestWatch):
    @pytest.fixture(autouse=True)
    def set_build_key(self, build):
        build.build_key = "0123456789"
        return build

    @pytest.fixture
    def build_statuses(self):
        return [
            {
                "state": "queued",
                "result": "unknown",
                "tuxbuild_status": "queued",
                "status_message": "Queued",
                "git_short_log": "Bla bla bla",
            },
            {
                "state": "building",
                "result": "unknown",
                "tuxbuild_status": "building",
                "status_message": "Building ...",
                "git_short_log": "Bla bla bla",
            },
            {
                "state": "finished",
                "result": "pass",
                "tuxbuild_status": "complete",
                "status_message": "Building ...",
                "git_short_log": "Bla bla bla",
                "build_status": "pass",
                "warnings_count": 0,
                "errors_count": 0,
            },
        ]

    @pytest.fixture(autouse=True)
    def get_request(self, mocker, build_statuses):
        return mocker.patch("tuxsuite.build.get_request", side_effect=build_statuses)

    def test_watch(self, build):
        watch = iter(build.watch())
        s1 = next(watch)
        assert s1.state == "queued"

        s2 = next(watch)
        assert s2.state == "building"

        build.status["tuxbuild_status"] = "complete"
        build.status["build_status"] = "pass"
        build.status["warnings_count"] = 0
        s3 = next(watch)
        assert s3.state == "complete"

    def test_watch_pass(self, build):
        states = self.watch(build)
        assert len(states) > 1
        state = states[-1]
        assert state.state == "complete"
        assert state.status == "pass"
        assert state.warnings == 0

    def test_watch_pass_warnings(self, build, build_statuses):
        build_statuses[-1]["warnings_count"] = 5

        state = self.watch(build)[-1]
        assert "Pass (5 warnings)" in state.message
        assert state.warnings == 5

    def test_watch_pass_one_warning(self, build, build_statuses):
        build_statuses[-1]["warnings_count"] = 1

        state = self.watch(build)[-1]
        assert "Pass (1 warning)" in state.message
        assert state.warnings == 1

    def test_watch_fail(self, build, build_statuses):
        build_statuses[-1]["build_status"] = "fail"
        build_statuses[-1]["errors_count"] = 5

        state = self.watch(build)[-1]
        assert "Fail (5 errors)" in state.message
        assert state.errors == 5

    def test_watch_fail_1_error(self, build, build_statuses):
        build_statuses[-1]["build_status"] = "fail"
        build_statuses[-1]["errors_count"] = 1

        state = self.watch(build)[-1]
        assert "Fail (1 error)" in state.message
        assert state.errors == 1

    def test_watch_fail_status_message(self, build, build_statuses):
        build_statuses[-1]["build_status"] = "fail"
        build_statuses[-1]["errors_count"] = 1
        build_statuses[-1]["status_message"] = "failed to foo the bar"

        state = self.watch(build)[-1]
        assert "with status message 'failed to foo the bar'" in state.message

    def test_watch_not_completed(self, build, mocker, build_statuses):
        build_statuses[-1]["build_status"] = None
        build_statuses[-1]["tuxbuild_status"] = "error"
        build_statuses[-1]["status_message"] = "the infrastructure failed"
        build_statuses.append(build_statuses[0])
        build_statuses.append(build_statuses[1])
        build_statuses.append(build_statuses[2])
        build_statuses.append(build_statuses[0])
        build_statuses.append(build_statuses[1])
        build_statuses.append(build_statuses[2])

        mocker.patch("tuxsuite.build.Build.build")
        state = self.watch(build)[-1]
        assert state.state != "complete"
        assert state.status is None
        assert "the infrastructure failed" in state.message

    def test_retries_on_errors(self, build, mocker, build_statuses):
        build_statuses[-1]["build_status"] = None
        build_statuses[-1]["tuxbuild_status"] = "error"
        build_statuses[-1]["state"] = "finished"
        build_statuses[-1]["result"] = "error"
        build_statuses[-1]["status_message"] = "the infrastructure failed"
        build_statuses.append(build_statuses[0])
        build_statuses.append(build_statuses[1])
        build_statuses.append(build_statuses[2])
        build_statuses.append(build_statuses[0])
        build_statuses.append(build_statuses[1])
        build_statuses.append(build_statuses[2])
        build_build = mocker.patch("tuxsuite.build.Build.build")

        states = self.watch(build)
        assert build_build.call_count == 2
        assert [state.state for state in states] == [
            "queued",
            "building",
            "error",
            "queued",
            "building",
            "error",
            "queued",
            "building",
            "error",
        ]

    def test_retry_succeeds_in_the_second_attempt(self, build, mocker, build_statuses):
        complete = build_statuses[-1].copy()
        build_statuses[-1]["build_status"] = None
        build_statuses[-1]["tuxbuild_status"] = "error"
        build_statuses[-1]["state"] = "finished"
        build_statuses[-1]["result"] = "error"
        build_statuses[-1]["status_message"] = "the infrastructure failed"
        build_statuses.append(build_statuses[0])
        build_statuses.append(build_statuses[1])
        build_statuses.append(complete)
        build_build = mocker.patch("tuxsuite.build.Build.build")

        states = self.watch(build)
        assert build_build.call_count == 1
        assert [state.state for state in states] == [
            "queued",
            "building",
            "error",
            "queued",
            "building",
            "complete",
        ]

    def test_from_queued_directly_to_completed(self, build, mocker, build_statuses):
        build_statuses.pop(1)
        states = self.watch(build)
        assert [s.state for s in states] == ["queued", "complete"]

    def test_timeout(self, build, mocker, get_request):
        get_request.side_effect = iter(
            lambda: {
                "state": "queued",
                "result": "unknown",
                "tuxbuild_status": "queued",
            },
            1,
        )
        with pytest.raises(tuxsuite.exceptions.Timeout):
            self.watch(build)

    def test_resists_unknown_state(self, build, build_statuses):
        build_statuses.insert(
            2,
            {
                "state": "spiralling",
                "result": "spiralling",
                "tuxbuild_status": "spiralling",
                "status_message": "Spiralling out of control",
                "git_short_log": "Bla bla bla",
            },
        )
        states = self.watch(build)
        assert [s.state for s in states] == [
            "queued",
            "building",
            "spiralling",
            "complete",
        ]

    def test_output_with_multiple_kconfigs(self, build):
        build.kconfig = ["defconfig", "https://raw.foo.com/kconfig/myconfig.txt"]
        assert "(defconfig+1)" in str(build)
        assert "https://raw.foo.com/kconfig/myconfig.txt" not in str(build)


class TestBuildWait:
    def test_wait(self, build, mocker):
        watch = mocker.patch("tuxsuite.build.Build.watch")
        build.wait()
        assert watch.call_count > 0

    def test_wait_returns_last_state(self, build, mocker):
        watch = mocker.patch("tuxsuite.build.Build.watch")
        first = mocker.MagicMock()
        last = mocker.MagicMock()
        watch.return_value = [first, last]
        assert build.wait() is last


@pytest.fixture
def builds():
    return [
        {"toolchain": "gcc-9", "target_arch": "x86_64", "kconfig": "defconfig"},
        {"toolchain": "gcc-8", "target_arch": "x86_64", "kconfig": "defconfig"},
        {"toolchain": "gcc-9", "target_arch": "arm64", "kconfig": "defconfig"},
        {"toolchain": "gcc-8", "target_arch": "arm64", "kconfig": "defconfig"},
        {
            "toolchain": "gcc-9",
            "target_arch": "x86_64",
            "kconfig": "defconfig",
            "build_name": "test_build_name",
        },
    ]


@pytest.fixture
def build_set(build_attrs, builds):
    return tuxsuite.build.BuildSet(
        builds,
        group=build_attrs["group"],
        project=build_attrs["project"],
        git_repo=build_attrs["git_repo"],
        git_ref=build_attrs["git_ref"],
        kbapi_url=build_attrs["kbapi_url"],
        tuxapi_url=build_attrs["tuxapi_url"],
        token=build_attrs["token"],
    )


class TestBuildSet:
    def test_expand_spec(self, build_set):
        assert len(build_set.builds) == 5
        assert build_set
        assert build_set.builds[0].git_repo is not None

    def test_updates_builds_with_returned_data(self, build_set, post, response):
        builds = build_set.builds
        server_data = [
            {
                "uid": "myuid1",
                "download_url": "https://builds.example/com/00000000000",
            },
            {
                "uid": "myuid2",
                "download_url": "https://builds.example/com/11111111111",
            },
            {
                "uid": "myuid3",
                "download_url": "https://builds.example/com/22222222222",
            },
            {
                "uid": "myuid4",
                "download_url": "https://builds.example/com/33333333333",
            },
            {
                "uid": "myuid5",
                "download_url": "https://builds.example/com/44444444444",
            },
        ]
        data = [
            dict(**builds[i].generate_build_request()[0], **server_data[i])
            for i in range(len(builds))
        ]
        response._content = json.dumps(list(reversed(data))).encode()
        build_set.build()

        assert builds[0].uid == "myuid1"
        assert builds[1].uid == "myuid2"
        assert builds[2].uid == "myuid3"
        assert builds[3].uid == "myuid4"
        assert builds[4].uid == "myuid5"


class TestBuildSetWatch(TestWatch):
    def test_watch(self, build_set, mocker):
        build_watch = mocker.patch("tuxsuite.build.Build.watch")
        state1 = mocker.MagicMock()
        state1.final = False
        state2 = mocker.MagicMock()
        state2.final = True
        build_watch.return_value = [state1, state2]

        states = self.watch(build_set)
        assert len(states) == 2 * len(build_set.builds)

    def test_watch_when_threads_crash(self, build_set, mocker, capsys):
        build_watch = mocker.patch("tuxsuite.build.Build.watch")
        build_watch.side_effect = RuntimeError("BOOM")
        mocker.patch("queue.Queue.get", side_effect=queue.Empty)

        self.watch(build_set)

        # if the test reaches this point, it means BuildSet.watch didn't get
        # stuck waiting forever.
        _, err = capsys.readouterr()
        assert "ERROR for build" in err


class TestBuildSetWait:
    def test_wait(self, build_set, mocker):
        watch = mocker.patch("tuxsuite.build.BuildSet.watch")
        state1 = mocker.MagicMock()
        state1.final = False
        state2 = mocker.MagicMock()
        state2.final = True
        watch.return_value = [state1, state1, state2, state2]

        results = build_set.wait()
        assert results == [state2, state2]


@pytest.fixture
def results(build_attrs):
    return tuxsuite.build.Results(
        group=build_attrs["group"],
        project=build_attrs["project"],
        kbapi_url=build_attrs["kbapi_url"],
        tuxapi_url=build_attrs["tuxapi_url"],
        token=build_attrs["token"],
        uid="1sewrBhxNVbsURAKBjeXX8pyjwY",
    )


class TestResults:
    def test_get_build(self, results, response, get, mocker):
        response._content = b'{"a": "b"}'

        assert response.status_code == 200
        assert results.get_build() == {"a": "b"}
        get.assert_called_with(
            results.tuxapi_url
            + "/v1/groups/{}/projects/{}/builds/{}".format(
                results.group, results.project, results.uid
            ),
            headers=results.headers,
            timeout=mocker.ANY,
            params=None,
        )

    def test_get_test(self, results, response, get, mocker):
        url = results.tuxapi_url + "/v1/groups/{}/projects/{}/tests/{}".format(
            results.group, results.project, results.uid
        )
        response._content = b'{"a": "b"}'

        assert response.status_code == 200
        assert results.get_test() == ({"a": "b"}, url)
        get.assert_called_with(
            url,
            headers=results.headers,
            timeout=mocker.ANY,
            params=None,
        )

    def test_get_plan(self, results, mocker):
        get_plan = mocker.patch("tuxsuite.build.Plan.get_plan")
        result = results.get_plan()
        assert get_plan.call_count == 1
        assert isinstance(result, type(()))

    def test_get_all(self, results, response, get):
        response._content = b'{"a": "b"}'

        result = results.get_all()
        assert response.status_code == 200
        assert get.call_count == 3
        assert isinstance(result, type(()))


class TestHandlePatch:
    def test_handle_patch_unknown(self):
        with pytest.raises(Exception) as excinfo:
            tuxsuite.build.handle_patch("/tmp/patch")
        assert "series file not found in patch directory" in str(excinfo)

    def test_handle_patch_mbox(self, mocker, sample_patch, sample_patch_file):
        guess = mocker.patch(
            "mimetypes.guess_type", return_value=("application/mbox", None)
        )
        result = tuxsuite.build.handle_patch(sample_patch_file)
        assert guess.call_count == 1
        assert isinstance(result, type(()))
        assert isinstance(type(result[0]), type(str))
        assert base64.b64decode(result[1]) == sample_patch.encode("utf-8")

    def test_handle_patch_dir(self, sample_patch_dir):
        result = tuxsuite.build.handle_patch(sample_patch_dir)
        assert isinstance(result, type(()))
        assert isinstance(type(result[0]), type(str))
        assert isinstance(type(result[1]), type(str))

    def test_handle_patch_tgz(self, mocker, sample_patch_tgz):
        result = tuxsuite.build.handle_patch(sample_patch_tgz)
        assert isinstance(result, type(()))
        assert isinstance(type(result[0]), type(str))
        assert isinstance(type(result[1]), type(str))

    def test_handle_patch_tgz_no_series(self, mocker, sample_patch_tgz_no_series):
        with pytest.raises(Exception) as excinfo:
            tuxsuite.build.handle_patch(sample_patch_tgz_no_series)
        assert "series file missing in patch archive" in str(excinfo)

    def test_handle_patch_url(self):
        url = "https://test.example.com/url"
        result = tuxsuite.build.handle_patch(url)
        assert isinstance(result, type(()))
        assert isinstance(type(result[0]), type(str))
        assert result[0] == url
        assert base64.b64decode(result[1]) == b""
