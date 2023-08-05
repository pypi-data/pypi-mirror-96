import abc
import logging
import os
import re
import networkx as nx
import textwrap
import traceback
from typing import Any, Dict, Optional, List

import colorama

from pmakeup.IPMakeupCache import IPMakeupCache
from pmakeup.JsonPMakeupCache import JsonPMakeupCache
from pmakeup.TargetDescriptor import TargetDescriptor
from pmakeup.SessionScript import SessionScript
from pmakeup.commons_types import path
from pmakeup.constants import STANDARD_MODULES, STANDARD_VARIABLES
from pmakeup.LinuxSessionScript import LinuxSessionScript
from pmakeup.WindowsSessionScript import WindowsSessionScript


class AttrDict(object):

    def __init__(self, d):
        self.__d = d

    def __getattr__(self, item: str) -> Any:
        return self.__d[item]

    def __getitem__(self, item: str) -> Any:
        return self.__d[item]

    def __contains__(self, item) -> bool:
        return item in self.__d

    def has_key(self, item: str) -> bool:
        return item in self


class PMakeupModel(abc.ABC):
    """
    The application model of pmakeup progam
    """

    def __init__(self):
        self.input_file: Optional[str] = None
        """
        File representing the "Makefile" of pmakeup
        """
        self.input_string: Optional[str] = None
        """
        String to be used in place of ::input_file
        """
        self.input_encoding: Optional[str] = None
        """
        Encoding of ::input_file
        """
        self.log_level: Optional[str] = None
        """
        level of the logger. INFO, DEBUG, CRITICAL
        """
        self.variable: Dict[str, Any] = {}
        """
        Variables that the user can inject from the command line
        """
        self.info_description: str = ""
        """
        Description to show whenever the user wants to know what a given Pmakeupfile does
        """
        self.target_network: nx.DiGraph = nx.DiGraph(name="targets")
        """
        Variables passed by the user from the command line via "--variable" argument
        """
        self.available_targets: Dict[str, TargetDescriptor] = {}
        """
        List of available targets the given pmakeupfile provides
        """
        self.requested_target_names: List[str] = []
        """
        List of targets that the user wants to perform. This
        list of targets are mpretty mch like the make one's (e.g., all, clean, install, uninstall)
        """
        self.should_show_target_help: bool = False
        """
        If true, we will print the information on how to use the given PMakefile
        """
        self.starting_cwd: path = os.path.abspath(os.curdir)
        """
        current working directory when pamke was executed
        """
        self.pmake_cache: Optional["IPMakeupCache"] = None
        """
        Cache containing data that the user wants t persist between different pmakeup runs
        """
        self._pmakefiles_include_stack: List[path] = []
        """
        Represents the PMakefile pmakeup is handling. Each time we include something, the code within it is executed.
        If an error occurs, we must know where the error is. Hence this variable is pretty useful to detect that.
        This list acts as a stack
        """
        self._eval_globals: Optional[Dict[str, Any]] = None

        self.session_script: "SessionScript" = None
        if os.name == "nt":
            self.session_script: "SessionScript" = WindowsSessionScript(self)
        elif os.name == "posix":
            self.session_script: "SessionScript" = LinuxSessionScript(self)
        else:
            self.session_script: "SessionScript" = SessionScript(self)

    def _get_eval_global(self) -> Dict[str, Any]:
        result = dict()
        for k in dir(self.session_script):
            if k.startswith("_"):
                continue
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            logging.debug(f"Adding variable {k}")
            result[k] = getattr(self.session_script, k)

        for k, v in STANDARD_MODULES:
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            logging.debug(f"Adding standard variable {k}")
            result[k] = v
        for name, value, description in STANDARD_VARIABLES:
            if name in result:
                raise KeyError(f"duplicate key \"{name}\". It is already mapped to the value {result[name]}")
            result[name] = value

        # SPECIAL VARIABLES

        if "variables" in result:
            raise KeyError(f"duplicate key \"variables\". It is already mapped to the value {result['variables']}")
        logging.debug(f"Adding standard variable 'variable'")
        attr_dict = {}
        for k, v in self.variable.items():
            attr_dict[k] = self.variable[k]
        self.variable = attr_dict
        result["variables"] = AttrDict(attr_dict)
        logging.info(f"VARIABLES PASSED FROM CLI")
        for i, (k, v) in enumerate(self.variable.items()):
            logging.info(f' {i}. {k} = {v}')

        if "model" in result:
            raise KeyError(f"duplicate key \"model\". It is already mapped to the value {result['model']}")
        logging.debug(f"Adding standard variable 'model'")
        result["model"] = self

        if "commands" in result:
            raise KeyError(f"duplicate key \"commands\". It is already mapped to the value {result['commands']}")
        logging.debug(f"Adding standard variable 'commands'")
        result["commands"] = self.session_script

        if "requested_target_names" in result:
            raise KeyError(f"duplicate key \"requested_target_names\". It is already mapped to the value {result['targets']}")
        logging.debug(f"Adding standard variable 'requested_target_names'")
        result["requested_target_names"] = self.requested_target_names

        if "interesting_paths" in result:
            raise KeyError(f"duplicate key \"interesting_paths\". It is already mapped to the value {result['interesting_paths']}")
        logging.debug(f"Adding standard variable 'interesting_paths'")
        result["interesting_paths"] = self.session_script._interesting_paths

        logging.info(f"INTERESTING PATHS")
        for i, (k, values) in enumerate(self.session_script._interesting_paths.items()):
            logging.info(f" - {i+1}. {k}: {', '.join(map(str, values))}")

        if "latest_interesting_path" in result:
            raise KeyError(
                f"duplicate key \"latest_interesting_path\". It is already mapped to the value {result['latest_interesting_path']}")
        logging.debug(f"Adding standard variable 'latest_interesting_path'")
        result["latest_interesting_path"] = self.session_script._latest_interesting_path

        logging.info(f"LATEST INTERESTING PATHS")
        for i, (k, v) in enumerate(self.session_script._latest_interesting_path.items()):
            logging.info(f" - {i+1}. {k}: {v}")

        logging.info(f"USER REQUESTED TARGETS")
        for i, t in enumerate(self.requested_target_names):
            logging.info(f" - {i+1}. {t}")

        return result

    def manage_pmakefile(self):
        """
        Main function used to programmatically call the application
        :return:
        """
        # initialize colorama
        try:
            colorama.init()
            self.execute()
        finally:
            colorama.deinit()
            if self.pmake_cache is not None:
                self.pmake_cache.update_cache()

    def execute(self):
        """
        Read the content of the PMakefile and executes it
        :return:
        """

        if self.input_string is not None:
            self.execute_string(self.input_string)
        else:
            self.execute_file(self.input_file)

    def execute_file(self, input_file: path):
        """
        Execute the content in a file
        :param input_file: file containing the code to execute
        :return:
        """

        with open(input_file, "r", encoding=self.input_encoding) as f:
            input_str = f.read()

        try:
            # add a new level in the stack
            self._pmakefiles_include_stack.append(input_file)
            # execute the file
            self.execute_string(input_str)
        finally:
            self._pmakefiles_include_stack.pop()

    def execute_string(self, string: str):
        """
        Execute the content of a string
        :param string: string to execute
        :return:
        """

        try:
            # remove the first line if it is empty
            string = textwrap.dedent(string)
            logging.debug("input string:")
            logging.debug(string)
            if self._eval_globals is None:
                self._eval_globals = self._get_eval_global()
            if self.pmake_cache is None:
                self.pmake_cache = JsonPMakeupCache("pmakeup-cache.json")
            exec(
                string,
                self._eval_globals,
                self._eval_globals
            )
        except Exception as e:
            print(f"{colorama.Fore.RED}Exception occured:{colorama.Style.RESET_ALL}")
            trace = traceback.format_exc()
            # Example of "trace"
            # Traceback (most recent call last):
            #   File "pmake/PMakeupModel.py", line 197, in execute_string
            #   File "<string>", line 43, in <module>
            #   File "<string>", line 43, in <lambda>
            # NameError: name 'ARDUINO_LIBRARY_LOCATION' is not defined
            lines = trace.splitlines()
            print(f"{colorama.Fore.RED}{traceback.format_exc()}{colorama.Style.RESET_ALL}")
            lines = lines[1:-1]
            last_line = lines[-1]

            # fetch line number
            try:
                line_no = last_line.split(", ")[1]
                m = re.match(r"^\s*line\s*([\d]+)$", line_no)
                line_no = m.group(1)
                line_no = int(line_no)
            except:
                line_no = "unknown"

            # fetch file name
            try:
                file_path = last_line.split(", ")[0]
                m = re.match(r"^\s*File\s*\"([^\"]+)\"$", file_path)
                file_path = m.group(1)
                if file_path == "<string>":
                    # this occurs when the problem is inside a PMakefile. We poll the stack
                    file_path = self._pmakefiles_include_stack[-1]
            except:
                file_path = "unknown"

            # logging.critical(f"{colorama.Fore.RED}{trace}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}Cause = {e}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}File = {file_path}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}Line = {line_no}{colorama.Style.RESET_ALL}")
            raise e

