import time

from  openai_assistant.core import openai_access
from openai_assistant.core.tool_executor import ToolExecutorInterface

from openai.types.beta import Thread
from openai.types.beta.threads import Run
import json


class OpenaiAssistantProxy():
    def __init__(self, asst_id, tool_executor:ToolExecutorInterface):
        self.asst_id = asst_id
        self.tool_executor = tool_executor
        self.__create_thread()
        self.run_id = None
        self.tool_outputs = []

    def __create_thread(self):
        thread: Thread = openai_access.create_thread()
        self.thread_id = thread.id

    def __create_message(self, msg):
        openai_access.create_message(self.thread_id, "user", msg)

    def __create_run(self):
        run: Run = openai_access.create_run(thread_id=self.thread_id, assistant_id=self.asst_id)
        self.run_id = run.id

    def send_user_message(self, user_message):
        self.run_id = None
        self.tool_outputs = []

        self.__create_message(user_message)
        self.__create_run()
        result = self.__process()
        return result, self.tool_outputs

    def __process(self):
        while (True):
            run_status = openai_access.get_run(thread_id=self.thread_id, run_id=self.run_id)

            if run_status.status == 'completed':
                result =  self.__retrieve_completed_message()
                return result
                break
            elif run_status.status == 'requires_action':
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                call_results = self.__execute_tools(tool_calls)
                self.__submit_tool_outputs(call_results)
            elif run_status.status in ['in_progress', 'queued']:
                time.sleep(.3)
            else:
                raise Exception(f"Non-actionable status: {run_status.status}")

    def __execute_tools(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            call_id = tool_call.id
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            output = self.tool_executor.execute_tool(function_name, arguments)
            result = {
                "call_id": call_id,
                "output": json.dumps(output[0] if isinstance(output, tuple) else output)
            }
            results.append(result)
            if(output):
                self.tool_outputs.append(output)
        return results

    def __submit_tool_outputs(self, list):
        tool_outputs = [{"tool_call_id": result["call_id"], "output": result["output"]} for result in list]
        openai_access.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=tool_outputs
        )

    def __retrieve_completed_message(self):
        messages = openai_access.get_thread_messages(thread_id=self.thread_id)
        response = messages.data[0].content[0].text.value
        return response