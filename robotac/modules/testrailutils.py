import os

import requests
import base64

import json

from robot.running import TestSuite


class APIClient:
    def __init__(self, base_url):
        self.user = ''
        self.password = ''
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'index.php?/api/v2/'

    def send_get(self, uri, filepath=None):
        """Issue a GET request (read) against the API.

        Args:
            uri: The API method to call including parameters, e.g. get_case/1.
            filepath: The path and file name for attachment download; used only
                for 'get_attachment/:attachment_id'.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('GET', uri, filepath)

    def send_post(self, uri, data):
        """Issue a POST request (write) against the API.

        Args:
            uri: The API method to call, including parameters, e.g. add_case/1.
            data: The data to submit as part of the request as a dict; strings
                must be UTF-8 encoded. If adding an attachment, must be the
                path to the file.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('POST', uri, data)

    def __send_request(self, method, uri, data):
        url = self.__url + uri

        auth = str(
            base64.b64encode(
                bytes('%s:%s' % (self.user, self.password), 'utf-8')
            ),
            'ascii'
        ).strip()
        headers = {'Authorization': 'Basic ' + auth}

        if method == 'POST':
            if uri[:14] == 'add_attachment':  # add_attachment API method
                files = {'attachment': (open(data, 'rb'))}
                response = requests.post(url, headers=headers, files=files)
                files['attachment'].close()
            else:
                headers['Content-Type'] = 'application/json'
                payload = bytes(json.dumps(data), 'utf-8')
                response = requests.post(url, headers=headers, data=payload)
        else:
            headers['Content-Type'] = 'application/json'
            response = requests.get(url, headers=headers)

        if response.status_code > 201:
            try:
                error = response.json()
            except:  # response.content not formatted as JSON
                error = str(response.content)
            raise APIError('TestRail API returned HTTP %s (%s)' % (response.status_code, error))
        else:
            if uri[:15] == 'get_attachment/':  # Expecting file, not JSON
                try:
                    open(data, 'wb').write(response.content)
                    return (data)
                except:
                    return ("Error saving attachment.")
            else:
                try:
                    return response.json()
                except:  # Nothing to return
                    return {}


class APIError(Exception):
    pass


class TestRailAPIClient(APIClient):

    def __init__(self):
        super().__init__(os.getenv("TR_BASE_URL"))
        self.user = os.getenv("TR_USER")
        self.password = os.getenv("TR_PASSWORD")
        self.project_id = os.getenv("TR_PROJECT_ID")
        self.section_id = os.getenv("TR_SECTION_ID")
        self._all_sections = self._get_all_sections_of_a_project()
        self._all_test_cases = self._get_all_testcases()

    @property
    def all_test_cases(self):
        return self._all_test_cases

    def _get_all_sections_of_a_project(self):
        get_sections_uri = f'get_sections/{self.project_id}'
        response = self.send_get(get_sections_uri)
        return response['sections']

    def _get_all_testcases(self):
        get_testcases_uri = f'get_cases/{self.project_id}/{self.section_id}'
        return {test['id']: test for test in self.send_get(get_testcases_uri)['cases']}

    def get_section_id(self, section_name):
        section_name = section_name.replace('_', ' ').title()
        for _ in self._all_sections:
            if _['name'] == section_name:
                return _['id']

    def get_section_testcases(self, section_id):
        return {case: self._all_test_cases[case] for case in self._all_test_cases
                if ['section_id'] is section_id}

    def create_subsection(self, name, parent_id=None):
        if not self.get_section_id(name):
            print(f"creating subsection: '{name}' under '{'root' if not parent_id else parent_id}'")
            data = {
                'name': name,
                'parent_id': parent_id if parent_id else self.section_id
            }
            add_section_uri = f'add_section/{self.project_id}'
            section = self.send_post(add_section_uri, data=data)
            self._all_sections.append(section)
        else:
            print(f"subsection {name} exists already")

    def create_subsection_recursively_for_robot_test(self, subsection: TestSuite):
        parent = subsection.parent
        while not subsection.parent:
            self.create_subsection(subsection.name)
            return
        else:
            self.create_subsection(subsection.parent.name)
            parent_id = self.get_section_id(parent.name)
            self.create_subsection(subsection.name, parent_id=parent_id)

    def create_testcase(self, name, section_name, refs=None):
        section_id = self.get_section_id(section_name)
        data = {
            'title': name,
            'refs': ','.join(refs) if refs else refs
        }
        print(f"Creating test case: {name}")
        uri = f'add_case/{section_id}'
        test_case = self.send_post(uri, data)
        self._all_test_cases[int(test_case['id'])] = test_case
        return test_case

    def update_testcase(self, case_id, name, refs=None):
        uri = f'update_case/{case_id}'
        data = {
            'title': name,
            'refs': ','.join(refs) if refs else refs
        }
        print(f"Updating '{name}'")
        self.all_test_cases[int(case_id)] = self.send_post(uri, data)

