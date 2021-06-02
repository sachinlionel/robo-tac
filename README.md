# Robotac
        Robot - TMS (TestRail) Integration promotes TestCase as code concept.
        TestCase as code:
        - TestCases are written only once, like as we do write them while automating in robot.
        - TestCases are closer to SUT and gets revision along with SUT.
        - Robotac integration tool keeps robot test cases and test rail test in-sync.
## Installation

```
pip install git+https://github.com/sachinlionel/robotac.git
```


### Requires .env of below template on execution folder:

```dotenv
# Required
TR_USER=test_admin@gmail.com    # TestRail email address
TR_PASSWORD=YREd-e-w-344fXWECEDC2-iXJ456432fdrtg04  # TestRail api token
TR_BASE_URL=https://your_comapny.testrail.com/  # TestRail web address
TR_PROJECT_ID=5     # Project ID where you want to copy robot tests
TR_SECTION_ID=189   # Section where you want to copy robot tests
TAC_TEST_SUITE=catalog_api  # Local robot tests folder's reference from execution folder
TAC_TEST_TAG_PREFIX=test_case_id=C  # Tag for robot files
# Optional
TAC_IGNORE_TEST_TAG=not_ready  # Tag to ignore specific set of robot tests
TAC_JIRA_REF=PP- # Tag for jira references
```

### Features:
- Adds local robot test cases to test rail
- Ignore set of test cases using `TAC_IGNORE_TEST_TAG` in .env
- Update test rail tests if local robot test case changes
- Copy test rail test tag to robot test case when test is newly added from local to test rail,
  set `TAC_TEST_TAG_PREFIX` for good test tag prefix.
- Copy tags that match with `TAC_JIRA_REF` to test rail references 
- todo:: Copy robot test case keywords into test rail steps

### Points to remember:
- Unique Section names across project.
- Unique TestCase name within section.
### How to run?

```log
(venv) skn@test-machine:~/int-tests$ robotac-tr
Ignoring testd44d, it has ignore_tag: not_ready
**************************
Checking test cases syntax
**************************
************************************************
Checking and updating test cases to that has tag
************************************************
- Search Catalog Api and verify results are wrapped in ItemCollection
+ Search new Catalog Api and verify results are wrapped in ItemCollection
?       ++++

**********************************
Adding new test cases to Test Rail
**********************************
subsection Catalog Api exists already
subsection Search By Post Method exists already
Creating test case: Search old Catalog Api and verify results are wrapped in ItemCollection
Added test_case_id=C641 tag for robot test case: Search old Catalog Api and verify results are wrapped in ItemCollection
```


