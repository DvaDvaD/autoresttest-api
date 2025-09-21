import asyncio
import os
import shutil
import tempfile
import joblib
import time
from app.models.test_config import TestConfiguration, TestRunResult


class AutoRestTestModel:
    def __init__(self, model_path: str):
        pass
        # try:
        #     self.model = joblib.load(model_path)
        # except FileNotFoundError:
        #     self.model = None

    async def run_test(self, config: TestConfiguration) -> TestRunResult:
        print("model_service.run_test invoked.")
        temp_dir = tempfile.mkdtemp()
        print(f"Temporary directory created: {temp_dir}")
        try:
            spec_path = os.path.join(temp_dir, "spec.yaml")
            with open(spec_path, "w") as f:
                f.write(config.spec_file_content)

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
            print("configurations.py created.")

            script_to_run = "dummy_autoresttest.py"
            original_script_path = f"models_store/autoresttest/{script_to_run}"
            script_path = os.path.join(temp_dir, script_to_run)
            
            with open(original_script_path, "r") as f:
                script_content = f.read()
            
            with open(script_path, "w") as f:
                f.write(script_content)

            print(f"Executing script: {script_path}")

            process = await asyncio.create_subprocess_exec(
                "python",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir,
            )

            stdout, stderr = await process.communicate()
            print("Script execution finished.")

            if process.returncode != 0:
                print(f"Error running script: {stderr.decode()}")
                # Handle error appropriately
                return TestRunResult(
                    summary={"message": "Test execution failed"}, raw_file_urls={}
                )

            # For now, return a placeholder. We'll implement the real result later.
            print("Returning result.")
            return TestRunResult(
                summary={"message": "Test completed successfully"}, raw_file_urls={}
            )
        finally:
            shutil.rmtree(temp_dir)
