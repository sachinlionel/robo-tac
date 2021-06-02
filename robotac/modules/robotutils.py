from robot.model import SuiteVisitor
from robot.parsing.model import TestCase
from robot.parsing import get_model, Token
from robot.parsing.model import TestCaseSection
from os import getenv

from robot.running import TestSuiteBuilder


def add_tags_to_test_case(test_case, test_case_id, test_name):
    tags_section = get_tags_section_from_test_case_body(test_case.body)
    add_tag_to_tags_section(tags_section, test_case_id, test_name)

def get_tags_section_from_test_case_body(test_case_body):
    for section in test_case_body:
        if section.type == Token.TAGS:
            return section


def add_tag_to_tags_section(tags_section, tr_test_id, test_case_name):
    tag_prefix = getenv("TAC_TEST_TAG_PREFIX")
    tag_value = f"{tag_prefix}{tr_test_id}"
    new_token_off_set = tags_section.tokens[-1].col_offset + 4
    seaprator_tag = Token(
        type=Token.SEPARATOR,
        value=' '*4,
        lineno=tags_section.data_tokens[0].lineno,
        col_offset=new_token_off_set
    )
    new_tag = Token(
        type=Token.TAGS,
        value=tag_value,
        lineno=tags_section.data_tokens[0].lineno,
        col_offset=seaprator_tag.end_col_offset
    )
    tags_section.tokens[-1].col_offset = new_tag.end_col_offset
    tags_list = list(tags_section.tokens)
    tags_list.insert(-1, seaprator_tag)
    tags_list.insert(-1, new_tag)
    tags_section.tokens = tuple(tags_list)
    print(f"Added {tag_value} tag for robot test case: {test_case_name}")

class LocalFinderTests:

    def __init__(self, rf_test: TestCase):
        self.rf_test = rf_test
        self.has_tr_tag = False
        self.tr_tag = self.get_existng_tr_tag()
        self.tr_test_id = self.get_test_id()
        self.tr_jira_references = self.get_existng_jira_ref_from_tag()

    def get_existng_tr_tag(self):
        for tag in self.rf_test.tags:
            if getenv("TAC_TEST_TAG_PREFIX") in tag:
                self.has_tr_tag = True
                return tag

    def get_test_id(self):
        if self.has_tr_tag:
            return self.tr_tag.lstrip(getenv("TAC_TEST_TAG_PREFIX"))

    def get_existng_jira_ref_from_tag(self):
        ref = getenv("TAC_JIRA_REF")
        tags = []
        if ref:
            for tag in self.rf_test.tags:
                if ref in tag:
                    tags.append(tag)
        return (tags or None)

class LocalResourceModel:

    def __init__(self, source_file):
        self.model = get_model(source_file)
        self.test_case_section = None

        # Get test case section
        for section in self.model.sections:
            if isinstance(section, TestCaseSection):
                self.test_case_section = section

        if not self.test_case_section:
            raise SyntaxError(f"{source_file} does not have test section")

        # Get test cases
        self.test_cases = [block for block in self.test_case_section.body if isinstance(block, TestCase)]

        if not self.test_cases:
            raise SyntaxError(f"{source_file} does not have test cases")


class TestCasesFinder(SuiteVisitor):
    def __init__(self):
        self.tests = list()
        self.robot_files = set()

    def visit_test(self, test):
        ignore_tag = getenv("TAC_IGNORE_TEST_TAG")
        if not ignore_tag in test.tags:
            self.tests.append(LocalFinderTests(test))
            self.robot_files.add(test.parent)
        else:
            print(f"Ignoring {test.name}, it has ignore_tag: {ignore_tag}")

    def get_tests(self, has_tag=False):
        return list(filter(lambda test: test.has_tr_tag is has_tag, self.tests))


def get_robot_finder():
    builder = TestSuiteBuilder()
    testsuite = builder.build(getenv("TAC_TEST_SUITE"))
    finder = TestCasesFinder()
    testsuite.visit(finder)
    return finder