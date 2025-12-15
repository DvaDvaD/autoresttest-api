import asyncio
import json
import os
import shutil
import tempfile

import yaml
from fastapi import HTTPException
from prance import ResolvingParser

from app.core.config import settings
from app.models.test_config import TestConfiguration, TestRunResult


class AutoRestTestModel:
    def validate_and_prepare_config(self, config: TestConfiguration) -> dict:
        """
        Performs synchronous validation of the request config.
        Raises HTTPException on failure.
        Returns a dictionary of prepared data if successful.
        """
        print("Validating and preparing config...")
        try:
            spec_data = json.loads(config.spec_file_content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

        temp_dir = tempfile.mkdtemp()
        spec_path = os.path.join(temp_dir, "spec.yaml")
        with open(spec_path, "w") as f:
            yaml.dump(spec_data, f)

        try:
            ResolvingParser(spec_path, strict=False)
        except Exception as e:
            shutil.rmtree(temp_dir)
            raise HTTPException(
                status_code=400, detail=f"Invalid OpenAPI specification: {e}"
            )

        return {"temp_dir": temp_dir, "spec_path": spec_path, "config": config}

    async def execute_test_process(
        self, prepared_data: dict, job_id: str
    ) -> tuple[TestRunResult | None, str | None]:
        """
        Executes the long-running test process and returns a result or an error detail.
        """
        temp_dir = prepared_data["temp_dir"]
        spec_path = prepared_data["spec_path"]
        config = prepared_data["config"]
        process = None
        stderr_output = []

        try:
            config_path = os.path.join(temp_dir, "configurations.py")
            with open(config_path, "w") as f:
                f.write(f"SPECIFICATION_LOCATION = '{spec_path}'\n")
                f.write("OPENAI_LLM_ENGINE = 'gemini-2.0-flash-lite'\n")
                f.write(
                    f"API_URL_OVERRIDE = '{config.api_url_override if config.api_url_override else ''}'\n"
                )
                f.write(f"DEFAULT_TEMPERATURE = {config.llm_engine_temperature}\n")
                f.write(f"USE_CACHED_GRAPH = {config.use_cached_graph}\n")
                f.write(f"USE_CACHED_TABLE = {config.use_cached_q_tables}\n")
                f.write(f"LEARNING_RATE = {config.rl_agent_learning_rate}\n")
                f.write(f"DISCOUNT_FACTOR = {config.rl_agent_discount_factor}\n")
                f.write(f"MAX_EXPLORATION = {config.rl_agent_max_exploration}\n")
                f.write(f"TIME_DURATION = {config.time_duration_seconds}\n")
                f.write(f"MUTATION_RATE = {config.mutation_rate}\n")
                f.write("ENABLE_HEADER_AGENT = False\n")

            src_dir = "models_store/autoresttest/src"
            shutil.copytree(src_dir, os.path.join(temp_dir, "src"))

            script_to_run = "AutoRestTest.py"
            original_script_path = f"models_store/autoresttest/{script_to_run}"
            script_path = os.path.join(temp_dir, script_to_run)

            with open(original_script_path, "r") as f:
                script_content = f.read()
            with open(script_path, "w") as f:
                f.write(script_content)

            with open(os.path.join(temp_dir, ".env"), "w") as f:
                f.write(f"OPENAI_API_KEY={settings.OPENAI_API_KEY}")

            python_executable = os.path.join(
                os.environ.get("VIRTUAL_ENV", "/usr/bin"), "bin", "python"
            )

            process = await asyncio.create_subprocess_exec(
                python_executable,
                "-u",
                script_path,
                job_id,
                "one",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir,
                env={
                    "OPENAI_API_KEY": settings.OPENAI_API_KEY,
                    "UPSTASH_REDIS_REST_URL": settings.UPSTASH_REDIS_REST_URL,
                    "UPSTASH_REDIS_REST_TOKEN": settings.UPSTASH_REDIS_REST_TOKEN,
                    "NEXTJS_BACKEND_URL": settings.NEXTJS_BACKEND_URL,
                    "INTERNAL_API_SECRET": settings.INTERNAL_API_SECRET,
                    "MINIO_ACCESS_KEY": settings.MINIO_ACCESS_KEY,
                    "MINIO_SECRET_KEY": settings.MINIO_SECRET_KEY,
                    "MINIO_ENDPOINT": settings.MINIO_ENDPOINT,
                    "MINIO_BUCKET": settings.MINIO_BUCKET,
                },
                limit=1024 * 1024,  # 1 MiB
            )

            result_holder = {}

            async def stream_output(stream, prefix, output_list=None):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    line_str = line.decode().strip()
                    if output_list is not None:
                        output_list.append(line_str)

                    if prefix == "stdout" and line_str.startswith("RESULT:"):
                        try:
                            result_json = line_str.replace("RESULT: ", "", 1)
                            result_holder["data"] = json.loads(result_json)
                        except json.JSONDecodeError:
                            print(f"Error decoding result JSON: {line_str}")
                    else:
                        print(f"{prefix}: {line_str}")

            stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
            stderr_task = asyncio.create_task(
                stream_output(process.stderr, "stderr", stderr_output)
            )

            await asyncio.gather(stdout_task, stderr_task)
            await process.wait()

            if process.returncode == 0 and "data" in result_holder:
                final_result = result_holder["data"]
                result = TestRunResult(
                    summary=final_result.get("summary", {}),
                    raw_file_urls=final_result.get("raw_file_urls", {}),
                    config=config,
                )
                return result, None
            else:
                if stderr_output:
                    error_detail = (
                        "Test script failed: The developer is too broke to pay for LLMs"
                    )
                else:
                    error_detail = "Test execution failed with a non-zero exit code but no error message."
                return None, error_detail
        finally:
            if process and process.returncode is None:
                print("Process cancelled, terminating...")
                process.terminate()
                await process.wait()
            print(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)
