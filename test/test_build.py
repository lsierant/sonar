from sonar.sonar import (
    process_image,
    find_dockerfile,
)

from types import SimpleNamespace as sn

from unittest.mock import patch, mock_open, call


@patch("sonar.sonar.docker_push")
@patch("sonar.sonar.docker_tag")
@patch("sonar.sonar.docker_build")
@patch("sonar.sonar.urlretrieve")
@patch("sonar.sonar.create_ecr_repository")
def test_dockerfile_from_url(
    patched_docker_build,
    patched_docker_tag,
    patched_docker_push,
    patched_urlretrive,
    patched_create_ecr_repository,
):
    with open("test/yaml_scenario6.yaml") as fd:
        with patch("builtins.open", mock_open(read_data=fd.read())) as _mock_file:
            pipeline = process_image(
                image_name="image0",
                skip_tags=[],
                include_tags=["test_dockerfile_from_url"],
                build_args={},
            )

    patched_urlretrive.assert_called_once()
    patched_docker_build.assert_called_once()
    patched_docker_tag.assert_called_once()
    patched_docker_push.assert_called_once()
    patched_create_ecr_repository.assert_called_once()


@patch(
    "sonar.sonar.tempfile.NamedTemporaryFile", return_value=sn(name="random-filename")
)
@patch("sonar.sonar.urlretrieve")
def test_find_dockerfile_fetches_file_from_url(patched_urlretrieve, patched_tempfile):
    # If passed a dockerfile which starts with https://
    # make sure urlretrieve and NamedTemporaryFile is called
    dockerfile = find_dockerfile("https://something")

    patched_urlretrieve.assert_called_once()
    patched_tempfile.assert_called_once_with(delete=False)
    assert dockerfile == "random-filename"

    patched_urlretrieve.reset_mock()

    # If dockerfile is a localfile, urlretrieve should not be called.
    dockerfile = find_dockerfile("/localfile/somewhere")
    patched_urlretrieve.assert_not_called()
    assert dockerfile == "/localfile/somewhere"


@patch("sonar.sonar.docker_push")
@patch("sonar.sonar.docker_tag")
@patch("sonar.sonar.docker_build")
def test_labels_are_passed_to_docker_push(_docker_build, _docker_tag, patched_docker_push):
    pipeline = process_image(
        image_name="image1",
        skip_tags=[],
        include_tags=[],
        build_args={},
        build_options={},
        inventory="test/yaml_scenario9.yaml",
    )

    # the labels have been specified in the test scenario and should be passed to docker_build.
    calls = [
        call(".", "Dockerfile", buildargs={}, labels={"label-0": "value-0", "label-1": "value-1", "label-2": "value-2"})
    ]

    _docker_build.assert_has_calls(calls)
    _docker_build.assert_called_once()
