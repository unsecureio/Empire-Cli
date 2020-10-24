import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class UseListenerMenu(object):
    def __init__(self):
        self.display_name = "uselistener"
        self.selected_type = ''
        self.listener_options = {}

    def autocomplete(self):
        return self._cmd_registry + [
            'help',
            'main',
        ]

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if len(cmd_line) > 0 and cmd_line[0] in ['uselistener']:
                for type in state.listener_types['types']:
                    yield Completion(type, start_position=-len(word_before_cursor))
            elif len(cmd_line) > 0 and cmd_line[0] in ['set']:
                for type in state.get_listener_options(self.selected_type)['listeneroptions']:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                for word in self.autocomplete():
                    if word.startswith(word_before_cursor):
                        yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    @command
    def use(self, module: str) -> None:
        """
        Use the selected listener

        Usage: use <module>
        """
        if module in state.listener_types['types']:
            self.selected_type = module
            self.display_name = 'uselistener/' + self.selected_type
            self.listener_options = state.get_listener_options(self.selected_type)['listeneroptions']

            listener_list = []
            for key, value in self.listener_options.items():
                values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
                values.reverse()
                temp = [key] + values
                listener_list.append(temp)

            table = SingleTable(listener_list)
            table.title = 'Listeners List'
            table.inner_row_border = True
            print(table.table)

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current listener

        Usage: set <key> <value>
        """
        if key in self.listener_options:
            self.listener_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(f'Set {key} to {value}')

    @command
    def unset(self, key: str) -> None:
        """
        Unset a listener option.

        Usage: unset <key>
        """
        if key in self.listener_options:
            self.listener_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(f'Unset {key}')

    @command
    def info(self):
        """
        Print the current listener options

        Usage: info
        """
        listener_list = []
        for key, value in self.listener_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            listener_list.append(temp)

        table = SingleTable(listener_list)
        table.title = 'Listeners List'
        table.inner_row_border = True
        print(table.table)

    @command
    def start(self):
        """
        Create the current listener

        Usage: start
        """
        # todo validation and error handling
        # Hopefully this will force us to provid more info in api errors ;)
        post_body = {}
        for key, value in self.listener_options.items():
            post_body[key] = self.listener_options[key]['Value']

        response = state.create_listener(self.selected_type, post_body)

        print(response)
