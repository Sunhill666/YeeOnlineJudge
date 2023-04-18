import base64

import requests

from utils.judger.judgeclient import JudgeClient


class Submission:
    source_code = None
    stdin = None
    expected_output = None

    language_id = None

    compiler_options = None
    command_line_arguments = None
    cpu_time_limit = None
    cpu_extra_time = None
    wall_time_limit = None
    memory_limit = None
    stack_limit = None
    max_processes_and_or_threads = None
    enable_per_process_and_thread_time_limit = None
    enable_per_process_and_thread_memory_limit = None
    max_file_size = None
    redirect_stderr_to_stdout = None
    enable_network = None
    number_of_runs = None
    additional_files = None
    callback_url = None

    stdout = None
    stderr = None
    compile_output = None

    message = None
    exit_code = None
    exit_signal = None
    status = None
    created_at = None
    finished_at = None
    token = None
    time = None
    wall_time = None
    memory = None

    _encoded_send_fields = {"source_code", "stdin", "expected_output"}
    _encoded_response_fields = {"stderr", "stdout", "compile_output"}
    _encoded_fields = _encoded_send_fields | _encoded_response_fields
    _extra_send_fields = {"cpu_time_limit", "cpu_extra_time", "wall_time_limit", "memory_limit", "stack_limit",
                          "max_processes_and_or_threads", "enable_per_process_and_thread_time_limit",
                          "enable_per_process_and_thread_memory_limit", "max_file_size", "number_of_runs",
                          "compiler_options", "command_line_arguments", "redirect_stderr_to_stdout", "enable_network",
                          "additional_files", "callback_url"}
    _extra_response_fields = {"time", "memory", "token", "message", "status", "exit_code", "exit_signal", "created_at",
                              "finished_at", "wall_time"}
    _response_fields = _encoded_response_fields | _extra_response_fields | {"language_id"}
    _send_fields = _encoded_send_fields | _extra_send_fields
    _fields = _response_fields | _send_fields

    def keys(self):
        return list(self._fields)

    def __getitem__(self, item):
        if item in self._encoded_fields:
            item = getattr(self, item)
            if item:
                return item.decode()
            return None

        return getattr(self, item)

    def load(self):
        client = JudgeClient()
        headers = {"Content-Type": "application/json"}
        params = {
            "base64_encoded": "true",
            "fields": ",".join(self._response_fields)
        }
        r = client.session.get(f"{client.endpoint}/submissions/{self.token}/", headers=headers, params=params)
        r.raise_for_status()

        json = r.json()
        self.set_properties(dict(json))

    def submit(self, wait=False):
        client = JudgeClient()
        headers = {"Content-Type": "application/json"}
        params = {"base64_encoded": "true", "wait": str(wait).lower()}
        language_id = self.language_id

        data = {
            "source_code": base64.b64encode(self.source_code).decode('ascii'),
            "language_id": language_id,
        }
        if self.stdin:
            data.update({"stdin": base64.b64encode(self.stdin).decode('ascii')})
        if self.expected_output:
            data.update({"expected_output": base64.b64encode(self.expected_output).decode('ascii')})

        for field in self._extra_send_fields:
            if self.__getattribute__(field) is not None:
                data.update({field: self.__getattribute__(field)})

        r = client.session.post(f"{client.endpoint}/submissions/", headers=headers, params=params, json=data)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            print(data.get('source_code'))
            print(r.json())

        json = r.json()
        self.set_properties(dict(json))

    def set_properties(self, r):
        for key, value in r.items():
            if key in self._encoded_fields:
                setattr(self, key, base64.b64decode(value.encode()) if value else None)
            else:
                setattr(self, key, value)


def get(submission_token):
    submission = Submission()
    submission.token = submission_token
    submission.load()
    return submission


def submit(source_code, language, stdin=None, expected_output=None, **kwargs):
    submission = Submission()
    submission.set_properties(kwargs)
    submission.source_code = source_code
    submission.language_id = language
    submission.stdin = stdin
    submission.expected_output = expected_output
    submission.submit(wait=kwargs.get('wait', False))
    return submission
