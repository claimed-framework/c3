import json
import logging
import os
import re
from parser import ContentParser


class Pythonscript:
    def __init__(self, path, function_name: str = None):

        self.path = path
        with open(path, 'r') as f:
            self.script = f.read()

        self.name = os.path.basename(path)[:-3].replace('_', '-')
        assert '"""' in self.script, 'Please provide a description of the operator inside the first doc string.'
        self.description = self.script.split('"""')[1].strip()
        self.envs = self._get_env_vars()

    def _get_env_vars(self):
        cp = ContentParser()
        env_names = cp.parse(self.path)['env_vars']
        return_value = dict()
        for env_name in env_names:
            comment_line = str()
            for line in self.script.split('\n'):
                if re.search("[\"']" + env_name + "[\"']", line):
                    # Check the description for current variable
                    if not comment_line.strip().startswith('#'):
                        # previous line was no description, reset comment_line.
                        comment_line = ''
                    if comment_line == '':
                        logging.info(f'Interface: No description for variable {env_name} provided.')
                    if ',' in comment_line:
                        logging.info(
                            f"Interface: comment line for variable {env_name} contains commas which will be deleted.")
                        comment_line = comment_line.replace(',', '')

                    if "int(" in line:
                        type = 'Integer'
                    elif "float(" in line:
                        type = 'Float'
                    elif "bool(" in line:
                        type = 'Boolean'
                    else:
                        type = 'String'
                    if ',' in line:
                        default = line.split(',')[1].split(')')[0]
                    else:
                        default = None
                    return_value[env_name] = {
                        'description': comment_line.replace('#', '').strip(),
                        'type': type,
                        'default': default
                    }
                    break
                comment_line = line
        return return_value

    def get_requirements(self):
        requirements = []
        for line in self.script.split('\n'):
            pattern = r"([ ]*pip[ ]*install[ ]*)([A-Za-z=0-9.\-: ]*)"
            result = re.findall(pattern, line)
            if len(result) == 1:
                requirements.append((result[0][0].strip() + ' ' + result[0][1].strip()))
        return requirements

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_inputs(self):
        return {key: value for (key, value) in self.envs.items() if not key.startswith('output_')}

    def get_outputs(self):
        return {key: value for (key, value) in self.envs.items() if key.startswith('output_')}