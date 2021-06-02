from os import getenv as ge


class TestRailTestCaseNotFound(Exception):
    pass


def check_envs():
    all_vars = [
        ge("TR_USER"),
        ge("TR_PASSWORD"),
        ge("TR_PROJECT_ID"),
        ge("TR_SECTION_ID"),
        ge("TR_BASE_URL"),
        ge("TAC_TEST_SUITE"),
        ge("TAC_TEST_TAG_PREFIX")
    ]
    if not all(all_vars):
        raise ValueError("Did not find one on following env vars\n"
                         "TR_USER, TR_PASSWORD, TR_PROJECT_ID, TR_SECTION_ID, \n"
                         "TR_BASE_URL, TAC_TEST_SUITE, TAC_TEST_TAG_PREFIX")
