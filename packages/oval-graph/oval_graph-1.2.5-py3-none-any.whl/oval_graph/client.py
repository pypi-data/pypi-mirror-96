import re
import argparse
import tempfile
import os
import webbrowser
import subprocess
from datetime import datetime
import sys

from .xml_parser import XmlParser
from .exceptions import NotChecked
from .__init__ import __version__


class Client():
    def __init__(self, args):
        self.parser = None
        self.MESSAGES = self._get_message()
        self.arg = self.parse_arguments(args)
        self.hide_passing_tests = self.arg.hide_passing_tests
        self.source_filename = self.arg.source_filename
        self.rule_name = self.arg.rule_id
        self.out = self.arg.output
        self.verbose = self.arg.verbose

        self.parts = self.get_src('parts')
        self.START_OF_FILE_NAME = 'graph-of-'
        self.date = str(datetime.now().strftime("-%d_%m_%Y-%H_%M_%S"))
        self.isatty = sys.stdout.isatty()

        self.all_rules = self.arg.all
        self.all_in_one = None
        self.display_html = None

        self.show_failed_rules = False
        self.show_not_selected_rules = False

        self.xml_parser = None

        self.html_builder = None

        self._set_attributes()

        self.web_browsers = []

    def _set_attributes(self):
        self.xml_parser = self.xml_parser = XmlParser(self.source_filename)

    def _get_message(self):
        MESSAGES = {
            'description': '',
            'source_filename': '',
        }
        return MESSAGES

    def print_red_text(self, text):
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + str(text) + CEND)

    def run_gui_and_return_answers(self):
        if self.isatty:
            if self.all_rules:
                return self._get_rules()
            else:
                try:
                    import inquirer
                    return inquirer.prompt(self.get_questions())
                except ImportError:
                    print(self.get_selection_rules())
                    return None
        else:
            return self._get_rules()

    def _get_rules(self):
        return {
            'rules': self._get_only_fail_rule(
                self.search_rules_id())} if self.show_failed_rules else {
            'rules': self.search_rules_id()}

    def get_list_of_matched_rules(self):
        return self._get_only_fail_rule(
            self.search_rules_id()) if self.show_failed_rules else self.search_rules_id()

    def get_list_of_lines(self):
        lines = ['== The Rule ID regular expressions ==']
        for rule in self.get_list_of_matched_rules():
            lines.append("^" + rule + "$")
        if self.show_not_selected_rules:
            for line in self.get_lines_of_wanted_not_selected_rules():
                lines.append(line)
        lines.append(
            "Interactive rule selection is not available,"
            " because inquirer is not installed."
            " Copy id of the rule you want to visualize and"
            " paste it into a command with regular"
            " expression characters(^$).\n"
            "Alternatively, use the --all or --all-in-one arguments.")
        return lines

    def get_selection_rules(self):
        return "\n".join(self.get_list_of_lines())

    def get_lines_of_wanted_not_selected_rules(self):
        out = []
        out.append('== The not selected rule IDs ==')
        for rule in self._get_wanted_rules_from_array_of_IDs(
                self.xml_parser.notselected_rules):
            out.append(rule + '(Not selected)')
        return out

    def get_choices(self):
        if self.show_not_selected_rules:
            print("\n".join(self.get_lines_of_wanted_not_selected_rules()))
        return self.get_list_of_matched_rules()

    def get_questions(self):
        choices = self.get_choices()
        from inquirer.questions import Checkbox as checkbox
        questions = [
            checkbox(
                'rules',
                message=(
                    "= The Rules IDs = (move - UP and DOWN arrows,"
                    " select - SPACE or LEFT and RIGHT arrows, submit - ENTER)"),
                choices=choices,
            ),
        ]
        return questions

    def _get_only_fail_rule(self, rules):
        return list(
            filter(
                lambda rule: self.xml_parser.used_rules[rule]['result'] == 'fail',
                rules))

    def _get_wanted_rules_from_array_of_IDs(self, rules):
        return [
            x for x in rules if re.search(
                self.rule_name, x)]

    def search_rules_id(self):
        return self._check_rules_id(
            self._get_wanted_rules_from_array_of_IDs(
                self.xml_parser.used_rules.keys()),
            self._get_wanted_rules_from_array_of_IDs(
                self.xml_parser.notselected_rules))

    def _check_rules_id(self, rules, notselected_rules):
        if len(notselected_rules) and not rules:
            raise ValueError(
                ('Rule(s) "{}" was not selected, '
                 "so there are no results. The rule is"
                 ' "notselected" because it'
                 " wasn't a part of the executed profile"
                 " and therefore it wasn't evaluated "
                 "during the scan.")
                .format(notselected_rules))
        elif not notselected_rules and not rules:
            raise ValueError('404 rule "{}" not found!'.format(self.rule_name))
        else:
            return rules

    def get_save_src(self, rule):
        if self.out is not None:
            os.makedirs(self.out, exist_ok=True)
            return os.path.join(
                self.out,
                self.START_OF_FILE_NAME + rule + '.html')
        return os.path.join(
            tempfile.gettempdir(),
            self.START_OF_FILE_NAME + rule + '.html')

    def get_src(self, src):
        _dir = os.path.dirname(os.path.realpath(__file__))
        return str(os.path.join(_dir, src))

    def _build_and_save_html(self, dict_oval_trees, src, rules, out_src):
        self.html_builder.save_html(dict_oval_trees, src, rules)
        out_src.append(src)

    def open_results_in_web_browser(self, paths_to_results):
        if self.display_html:
            try:
                self.web_browsers.append(subprocess.Popen(
                    ["firefox", *paths_to_results]))
            except BaseException:
                default_web_browser_name = webbrowser.get().name
                self.web_browsers.append(subprocess.Popen(
                    [default_web_browser_name, *paths_to_results]))

    def kill_web_browsers(self):
        for web_browser in self.web_browsers:
            web_browser.kill()

    def _prepare_data(self, rules, dict_oval_trees, out_src):
        for rule in rules['rules']:
            try:
                self._put_to_dict_oval_trees(dict_oval_trees, rule)
                if not self.all_in_one:
                    self._build_and_save_html(
                        dict_oval_trees, self._get_src_for_one_graph(
                            rule), dict(
                            rules=[rule]), out_src)
                    dict_oval_trees = {}
            except NotChecked as error:
                self.print_red_text(error)
        if self.all_in_one:
            self._build_and_save_html(
                dict_oval_trees, self.get_save_src(
                    'rules' + self.date), rules, out_src)

    def prepare_data(self, rules):
        out_src = []
        oval_tree_dict = dict()
        self._prepare_data(rules, oval_tree_dict, out_src)
        self.open_results_in_web_browser(out_src)
        return out_src

    def parse_arguments(self, args):
        self.prepare_parser()
        return self.parser.parse_args(args)

    def prepare_args_when_output_is_html(self):
        self.parser.add_argument(
            '-i',
            '--all-in-one',
            action="store_true",
            default=False,
            help="Processes all rules into one file.")
        self.parser.add_argument(
            '-d',
            '--display',
            action="store_true",
            default=False,
            help="Enables opening a web browser with a graph, when is used --output.")

    def prepare_args_when_user_can_list_in_rules(self):
        self.parser.add_argument(
            '--show-failed-rules',
            action="store_true",
            default=False,
            help="Show only FAILED rules")
        self.parser.add_argument(
            '--show-not-selected-rules',
            action="store_true",
            default=False,
            help="Show notselected rules. These rules will not be visualized.")

    def prepare_parser(self):
        self.parser = argparse.ArgumentParser(
            prog='oval-graph',
            description=self.MESSAGES.get('description'))
        self.parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s ' + __version__)
        self.parser.add_argument(
            '-a',
            '--all',
            action="store_true",
            default=False,
            help="Process all matched rules.")
        self.parser.add_argument(
            '--hide-passing-tests',
            action="store_true",
            default=False,
            help=(
                "Do not display passing tests for better orientation in"
                " graphs that contain a large amount of nodes."))
        self.parser.add_argument(
            '-v',
            '--verbose',
            action="store_true",
            default=False,
            help="Displays details about the results of the running command.")
        self.parser.add_argument(
            '-o',
            '--output',
            action="store",
            default=None,
            help='The file where to save output.')
        self.parser.add_argument(
            "source_filename",
            help=self.MESSAGES.get('source_filename'))
        self.parser.add_argument(
            "rule_id", help=(
                "Rule ID to be visualized. A part from the full rule ID"
                " a part of the ID or a regular expression can be used."
                " If brackets are used in the regular expression "
                "the regular expression must be quoted."))
