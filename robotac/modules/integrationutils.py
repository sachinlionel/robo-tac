import difflib as dl

from robot.parsing import Token

from robotac.modules.errors import TestRailTestCaseNotFound
from robotac.modules.robotutils import LocalResourceModel, add_tags_to_test_case


def print_sp(data):
    print('*' * len(data))
    print(data)
    print('*' * len(data))


def check_and_update_exisitng_test_cases(tests, client):
    for each_test in tests:
        tr_test_id = each_test.tr_test_id
        tr_test_data = client.all_test_cases.get(int(tr_test_id))
        if not tr_test_data:
            raise TestRailTestCaseNotFound(f"Test rail test case with {tr_test_id} is unavailable")
        # check difference in state of test case
        if tr_test_data['title'] != each_test.rf_test.name:
            diff = dl.ndiff([tr_test_data['title']], [each_test.rf_test.name])
            for x in diff:
                print(x)
            client.update_testcase(tr_test_id, each_test.rf_test.name, each_test.tr_jira_references)


def check_robot_tests_compatibility(robot_files):
    not_compatibles = []
    for robot_file in robot_files:
        test_model = LocalResourceModel(robot_file.source)

        for block in test_model.test_cases:
            has_tags_section = None
            for test_section in block.body:
                try:
                    if test_section.type == Token.TAGS:
                        has_tags_section = True
                        break
                # Loops will not has attribute type
                except AttributeError:
                    pass
            if not has_tags_section:
                not_compatibles.append(block.header.name)

    if not_compatibles:
        for not_compatible in not_compatibles:
            print(f"test case: '{not_compatible}' has no tags section")
        raise SyntaxError("Exptected at least empty tags section in each test case\n"
                          "Eg:\n"
                          "Search catalog api\n"
                          "    [Tags]\n"
                          "    When User perform search\n"
                          "    Then verify results\n")


def add_new_test_cases_to_test_rail(all_tests, client):
    for each_test in all_tests:
        print(f"Adding '{each_test.rf_test.name}' to test rail")
        client.create_subsection_recursively_for_robot_test(each_test.rf_test.parent)
        tr_test_data = client.create_testcase(each_test.rf_test.name, each_test.rf_test.parent.name, each_test.tr_jira_references)

        # Get test cases from source model
        test_model = LocalResourceModel(each_test.rf_test.source)
        test_cases = test_model.test_cases

        # Get tag section of test case
        for test_case in test_cases:
            if test_case.header.name == each_test.rf_test.name:
                add_tags_to_test_case(test_case, tr_test_data['id'], each_test.rf_test.name)
        test_model.model.save()
