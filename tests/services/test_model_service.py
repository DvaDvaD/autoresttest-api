import pytest
import json
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.model_service import AutoRestTestModel
from app.models.test_config import TestConfiguration, TestRunResult

# --- Helpers for Mocking Async Subprocess ---


class MockStream:
    def __init__(self, lines):
        self.lines = lines
        self.cursor = 0

    async def readline(self):
        if self.cursor >= len(self.lines):
            return b""
        line = self.lines[self.cursor]
        self.cursor += 1
        return line


class MockProcess:
    def __init__(self, returncode=0, stdout_lines=None, stderr_lines=None):
        self.returncode = returncode
        self.stdout = MockStream(stdout_lines or [])
        self.stderr = MockStream(stderr_lines or [])
        self.terminate_called = False

    async def wait(self):
        pass

    def terminate(self):
        self.terminate_called = True


# --- Tests ---


def test_validate_and_prepare_config_success():
    service = AutoRestTestModel()
    config = TestConfiguration(
        spec_file_content=json.dumps(
            {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0"}}
        )
    )

    with patch(
        "app.services.model_service.tempfile.mkdtemp", return_value="/tmp/mock_dir"
    ) as mock_mkdtemp, patch(
        "app.services.model_service.ResolvingParser"
    ) as mock_parser, patch(
        "builtins.open", new_callable=MagicMock
    ) as mock_open:

        # We assume open() works fine for writing the spec
        prepared = service.validate_and_prepare_config(config)

        assert prepared["temp_dir"] == "/tmp/mock_dir"
        assert prepared["spec_path"] == "/tmp/mock_dir/spec.yaml"
        assert prepared["config"] == config
        mock_parser.assert_called_once()


def test_validate_and_prepare_config_invalid_json():
    service = AutoRestTestModel()
    config = TestConfiguration(spec_file_content="{invalid-json")

    with pytest.raises(HTTPException) as exc:
        service.validate_and_prepare_config(config)
    assert exc.value.status_code == 400
    assert "Invalid JSON format" in exc.value.detail


def test_validate_and_prepare_config_invalid_spec():
    service = AutoRestTestModel()
    config = TestConfiguration(spec_file_content=json.dumps({"openapi": "3.0.0"}))

    # Mock ResolvingParser to raise an exception
    with patch(
        "app.services.model_service.tempfile.mkdtemp", return_value="/tmp/mock_dir"
    ), patch(
        "app.services.model_service.ResolvingParser",
        side_effect=Exception("Spec Error"),
    ), patch(
        "builtins.open", new_callable=MagicMock
    ), patch(
        "app.services.model_service.shutil.rmtree"
    ) as mock_rmtree:

        with pytest.raises(HTTPException) as exc:
            service.validate_and_prepare_config(config)

        assert exc.value.status_code == 400
        assert "Invalid OpenAPI specification" in exc.value.detail
        mock_rmtree.assert_called_once_with("/tmp/mock_dir")


@pytest.mark.asyncio
async def test_execute_test_process_success():
    service = AutoRestTestModel()
    config = TestConfiguration(
        spec_file_content="{", api_url_override="http://test.local"
    )
    prepared_data = {
        "temp_dir": "/tmp/mock_dir",
        "spec_path": "/tmp/mock_dir/spec.yaml",
        "config": config,
    }

    # Prepare mock process output
    success_result = {
        "summary": {"total": 10, "failed": 0},
        "raw_file_urls": {"report": "http://minio/report.html"},
    }
    stdout_lines = [
        b"Starting test...\n",
        f"RESULT: {json.dumps(success_result)}\n".encode("utf-8"),
    ]

    mock_proc = MockProcess(returncode=0, stdout_lines=stdout_lines)

    with patch(
        "asyncio.create_subprocess_exec", return_value=mock_proc
    ) as mock_exec, patch("builtins.open", new_callable=MagicMock), patch(
        "app.services.model_service.shutil.copytree"
    ), patch(
        "app.services.model_service.shutil.rmtree"
    ) as mock_rmtree:

        result, error = await service.execute_test_process(prepared_data, "job-123")

        assert error is None
        assert isinstance(result, TestRunResult)
        assert result.summary == success_result["summary"]

        mock_exec.assert_called_once()
        mock_rmtree.assert_called_once_with("/tmp/mock_dir")


@pytest.mark.asyncio
async def test_execute_test_process_failure_stderr():
    service = AutoRestTestModel()
    prepared_data = {
        "temp_dir": "/tmp/mock_dir",
        "spec_path": "/tmp/mock_dir/spec.yaml",
        "config": TestConfiguration(spec_file_content="{}"),
    }

    mock_proc = MockProcess(returncode=1, stderr_lines=[b"Some fatal error occurred\n"])

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc), patch(
        "builtins.open", new_callable=MagicMock
    ), patch("app.services.model_service.shutil.copytree"), patch(
        "app.services.model_service.shutil.rmtree"
    ):

        result, error = await service.execute_test_process(prepared_data, "job-fail")

        assert result is None
        assert error is not None
        assert (
            "The developer is too broke" in error
        )  # Checks specific error message mapping logic


@pytest.mark.asyncio
async def test_execute_test_process_silent_failure():
    service = AutoRestTestModel()
    prepared_data = {
        "temp_dir": "/tmp/mock_dir",
        "spec_path": "/tmp/mock_dir/spec.yaml",
        "config": TestConfiguration(spec_file_content="{}"),
    }

    # Return code non-zero but no stderr
    mock_proc = MockProcess(returncode=1)

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc), patch(
        "builtins.open", new_callable=MagicMock
    ), patch("app.services.model_service.shutil.copytree"), patch(
        "app.services.model_service.shutil.rmtree"
    ):

        result, error = await service.execute_test_process(prepared_data, "job-fail")

        assert result is None
        assert error is not None
        assert "Test execution failed with a non-zero exit code" in error


@pytest.mark.asyncio
async def test_execute_test_process_malformed_json_result():
    service = AutoRestTestModel()
    prepared_data = {
        "temp_dir": "/tmp/mock_dir",
        "spec_path": "/tmp/mock_dir/spec.yaml",
        "config": TestConfiguration(spec_file_content="{}"),
    }

    # Output contains a RESULT line with invalid JSON
    stdout_lines = [
        b"Starting...\n",
        b"RESULT: {invalid-json\n",
        b"Done.\n",
    ]
    mock_proc = MockProcess(returncode=0, stdout_lines=stdout_lines)

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc), patch(
        "builtins.open", new_callable=MagicMock
    ), patch("app.services.model_service.shutil.copytree"), patch(
        "app.services.model_service.shutil.rmtree"
    ):

        # Capture stdout to verify the error message was printed
        with patch("builtins.print") as mock_print:
            result, error = await service.execute_test_process(
                prepared_data, "job-json-err"
            )

        # Should return error because "data" key was never populated in result_holder
        # Since returncode is 0 but data is missing, it falls to the 'else' block
        # And since stderr is empty, it returns the generic error message
        assert result is None
        assert (
            error
            == "Test execution failed with a non-zero exit code but no error message."
        )

        # Verify that the JSON decode error was printed
        assert any(
            "Error decoding result JSON" in str(call)
            for call in mock_print.call_args_list
        )


# @pytest.mark.asyncio
# async def test_execute_test_process_cancellation():
#     service = AutoRestTestModel()
#     prepared_data = {
#         "temp_dir": "/tmp/mock_dir",
#         "spec_path": "/tmp/mock_dir/spec.yaml",
#         "config": TestConfiguration(spec_file_content="{}"),
#     }
#
#     # Simulate a running process (returncode is None)
#     mock_proc = MockProcess(returncode=0)
#
#     with patch("asyncio.create_subprocess_exec", return_value=mock_proc), patch(
#         "builtins.open", new_callable=MagicMock
#     ), patch("app.services.model_service.shutil.copytree"), patch(
#         "app.services.model_service.shutil.rmtree"
#     ):
#
#         # Mock asyncio.gather to raise CancelledError (or any exception)
#         with patch("asyncio.gather", side_effect=asyncio.CancelledError):
#             with pytest.raises(asyncio.CancelledError):
#                 await service.execute_test_process(prepared_data, "job-cancel")
#
#     # Verify terminate was called
#     assert mock_proc.terminate_called is True
#

