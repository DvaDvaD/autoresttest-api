import asyncio
import os
import shutil
import tempfile
import json
import yaml
from app.models.test_config import TestConfiguration, TestRunResult
from app.core.config import settings


class AutoRestTestModel:
    def __init__(self, model_path: str):
        self._lock = asyncio.Lock()

    async def run_test(self, config: TestConfiguration) -> TestRunResult:
        print("model_service.run_test invoked.")
        temp_dir = tempfile.mkdtemp()
        print(f"Temporary directory created: {temp_dir}")
        try:
            spec_data = json.loads(config.spec_file_content)
            spec_path = os.path.join(temp_dir, "spec.yaml")
            with open(spec_path, "w") as f:
                yaml.dump(spec_data, f)

            config_path = os.path.join(temp_dir, "configurations.py")
            print("Creating configurations.py...")
            with open(config_path, "w") as f:
                f.write(f"SPECIFICATION_LOCATION = '{spec_path}'\n")
                f.write(f"OPENAI_LLM_ENGINE = '{config.llm_engine}'\n")
                f.write(f"DEFAULT_TEMPERATURE = {config.llm_engine_temperature}\n")
                f.write(f"USE_CACHED_GRAPH = {config.use_cached_graph}\n")
                f.write(f"USE_CACHED_TABLE = {config.use_cached_q_tables}\n")
                f.write(f"LEARNING_RATE = {config.rl_agent_learning_rate}\n")
                f.write(f"DISCOUNT_FACTOR = {config.rl_agent_discount_factor}\n")
                f.write(f"MAX_EXPLORATION = {config.rl_agent_max_exploration}\n")
                f.write(f"TIME_DURATION = {config.time_duration_seconds}\n")
                f.write(f"MUTATION_RATE = {config.mutation_rate}\n")
                f.write("ENABLE_HEADER_AGENT = False\n")
            print("configurations.py created.")

            master_cache_dir = "models_store/autoresttest/src/cache"
            temp_src_dir = os.path.join(temp_dir, "src")
            temp_cache_dir = os.path.join(temp_src_dir, "cache")

            shutil.copytree("models_store/autoresttest/src", temp_src_dir, ignore=shutil.ignore_patterns('cache'))

            async with self._lock:
                if os.path.exists(master_cache_dir):
                    shutil.copytree(master_cache_dir, temp_cache_dir)

            script_to_run = "AutoRestTest.py"
            original_script_path = f"models_store/autoresttest/{script_to_run}"
            script_path = os.path.join(temp_dir, script_to_run)

            with open(original_script_path, "r") as f:
                script_content = f.read()

            with open(script_path, "w") as f:
                f.write(script_content)

            with open(os.path.join(temp_dir, ".env"), "w") as f:
                f.write(f"OPENAI_API_KEY={settings.OPENAI_API_KEY}")

            print(f"Executing script: {script_path}")

            python_executable = os.path.join(
                os.environ.get("VIRTUAL_ENV", "/usr/bin"), "bin", "python"
            )

            process = await asyncio.create_subprocess_exec(
                python_executable,
                "-u",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir,
                env={"OPENAI_API_KEY": settings.OPENAI_API_KEY},
            )

            async def stream_output(stream, prefix):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    print(f"{prefix}: {line.decode().strip()}")

            stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
            stderr_task = asyncio.create_task(stream_output(process.stderr, "stderr"))

            await asyncio.gather(stdout_task, stderr_task)

            await process.wait()
            print("Script execution finished.")

            if process.returncode != 0:
                print("Error running script. See stderr output above for details.")
                # Handle error appropriately
                return TestRunResult(
                    summary={"message": "Test execution failed"}, raw_file_urls={}
                )

            async with self._lock:
                if os.path.exists(master_cache_dir):
                    shutil.rmtree(master_cache_dir)
                shutil.copytree(temp_cache_dir, master_cache_dir)

            # For now, return a placeholder. We'll implement the real result later.
            print("Returning result.")
            return TestRunResult(
                summary={"message": "Test completed successfully"}, raw_file_urls={}
            )
        finally:
            print(f"Temporary directory not deleted for inspection: {temp_dir}")
            # shutil.rmtree(temp_dir)
