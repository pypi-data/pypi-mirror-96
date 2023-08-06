"""
Projects Connection
===================
"""

from typing import Union, Optional, List

from requests import Response

from deepcrawl.api import ApiConnection
from deepcrawl.api.api_endpoints import get_api_endpoint
from .issues import DeepCrawlIssue
from .majestic_settings import MajesticSettings
from .project_settings import ProjectSettings
from .project_upload import DeepCrawlProjectUpload
from .projects import DeepCrawlProject
from .schedule import DeepCrawlSchedule


class ProjectConnection(ApiConnection):
    """
    PROJECT

        * endpoint: /accounts/{account_id}/projects
        * http methods: GET, POST
        * methods: get_projects, create_project

        - endpoint: /accounts/{account_id}/projects/{project_id}
        - http methods: GET, PATCH, DELETE
        - methods: get_project, update_project_settings, delete_project

    PROJECT UPLOAD

        * endpoint: /accounts/{account_id}/projects/{project_id}/uploads
        * http methods: GET, POST
        * methods: get_project_uploads, create_project_upload

        - endpoint: /accounts/{account_id}/projects/{project_id}/uploads/{upload_id}
        - http methods: GET, PATCH, DELETE
        - methods: get_project_upload, update_project_upload, delete_project_upload

    MAJESTIC

        * endpoint: /accounts/{account_id}/projects/{project_id}/majestic_configuration
        * http methods: GET, PATCH
        * methods: get_majestic_settings, update_majestic_settings

    ISSUES

        * endpoint: issues /accounts/{account_id}/projects/{project_id}/issues
        * http methods: GET, POST
        * methods: get_issues, create_issue

        - endpoint: issue /accounts/{account_id}/projects/{project_id}/issues/{issue_id}
        - http methods: GET, PATCH, DELETE
        - methods: get_issue, update_issue, delete_issue
    """

    """
    PROJECT
    """

    def create_project(self, account_id: Union[int, str], project_settings: dict) -> DeepCrawlProject:
        """Create a project.
        Project settings argument can be dict or a ProjectSettings instance.

        .. code-block::

            project_settings = {
                "name": str,
                "site_primary": "url",
                "crawl_subdomains": bool,
                "crawl_types": [str],
                "crawl_rate": int,
                "limit_levels_max": int,
                "limit_pages_max": int,
                "auto_finalize": bool,
                "site_secondaries": ["url|regex"],
                "start_urls": ["url"],
                "urls_included": ["url|regex"],
                "urls_excluded": ["url|regex"],
                "page_groupings": [
                    {
                      "name": str,
                      "url_match": "url|regex",
                      "crawl_sample": float
                    }
                ],
                "crawl_css_js": bool,
                "crawl_disallowed_pages": bool,
                "crawl_external_urls": bool,
                "crawl_nofollow_links": bool,
                "crawl_noindex_pages": bool,
                "crawl_non_html_file_types": bool,
                "crawl_not_included_urls": bool,
                "location": str,
                "is_stealth_mode": bool,
                "user_agent": "iphone",
                "custom_header_user_agent": str,
                "custom_header_user_agent_short": str,
                "mobile_user_agent": str,
                "mobile_custom_header_user_agent": str,
                "mobile_custom_header_user_agent_short": str,
                "custom_extractions": [
                    {
                      "label": str,
                      "regex": "regec",
                      "clean_html_tags": bool,
                      "match_number_from": int,
                      "match_number_to": int,
                      "filter": "regex"
                    }
                ],
                "robots_overwrite": str,
                "custom_dns": [
                    {
                      "hostname": str,
                      "ip_address": str
                    }
                ],
                "site_test": "url",
                "crawl_test_site": bool,
                "site_test_user": str,
                "site_test_pass": str,
                "url_rewrite_query_parameters": [str],
                "url_rewrite_regex_parameters": [
                    {
                      "match_from": "regex",
                      "match_to": "regex"
                    }
                ],
                "use_rewrite_rules": bool,
                "url_rewrite_strip_fragment": bool,
                "api_callback": "url",
                "alert_emails": [str],
                "alert_setting": str,
                "splunk_enabled": str,
                "use_mobile_settings": str,
                "mobile_url_pattern": "regex",
                "mobile_homepage_url": "regex"
            }

        >>> connection.create_project(0, project_settings)
        [0 1] www.test.com Project

        :param account_id: account id
        :type account_id: int or str
        :param project_settings: project configuration
        :type project_settings: dict or ProjectSettings
        :return: Project instance
        :rtype: DeepCrawlProject
        """
        if isinstance(project_settings, ProjectSettings):
            project_settings = project_settings.to_dict

        endpoint_url: str = get_api_endpoint(endpoint='projects', account_id=account_id)
        response = self.dc_request(url=endpoint_url, method='post', json=project_settings)
        return DeepCrawlProject(project_data=response.json(), account_id=account_id)

    def get_project(self, account_id: Union[int, str], project_id: Union[int, str]) -> DeepCrawlProject:
        """Get project

        >>> connection.get_project(0, 1)
        [0 1] www.test.com Project

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :return: Requested project
        :rtype: DeepCrawlProject
        """
        endpoint_url: str = get_api_endpoint(endpoint='project', account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='get')
        return DeepCrawlProject(project_data=response.json(), account_id=account_id)

    def update_project_settings(
            self, account_id: Union[int, str], project_id: Union[int, str], settings: dict
    ) -> DeepCrawlProject:
        """Update the project settings.
        Settings argument can be dict or a ProjectSettings instance.

        >>> connection.update_project_settings(0, 1, settings)
        [0 1] www.test.com Project

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param settings: new settings configuration
        :type settings: dict or ProjectSettings
        :return: Updated project
        :rtype: DeepCrawlProject
        """
        if isinstance(settings, ProjectSettings):
            settings = settings.to_dict

        endpoint_url: str = get_api_endpoint(endpoint='project', account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='patch', json=settings)
        return DeepCrawlProject(project_data=response.json(), account_id=account_id)

    def delete_project(self, account_id: Union[int, str], project_id: Union[int, str]) -> Response:
        """Delete project

        >>> response = connection.delete_project(0, 1)
        >>> response.status_code
        204

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :return: HTTP 204 No Content
        """
        endpoint_url = get_api_endpoint(endpoint='project', account_id=account_id, project_id=project_id)
        return self.dc_request(url=endpoint_url, method='delete')

    def get_projects(
            self, account_id: Union[int, str], filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlProject]:
        """Get projects

        >>> connection.get_projects(0)
        [[0 1] www.test.com Project, [0 2] www.test2.com Project]

        :param account_id: account id
        :type account_id: int or str
        :param filters: filters
        :type filters: dict
        :param kwargs: extra arguments, like pagination ones
        :type kwargs: dict
        :return: list of projects
        :rtype: list
        """
        endpoint_url: str = get_api_endpoint(endpoint='projects', account_id=account_id)
        projects: List[dict] = self.get_paginated_data(url=endpoint_url, method='get', filters=filters, **kwargs)

        list_of_projects = []
        for project in projects:
            list_of_projects.append(
                DeepCrawlProject(project_data=project, account_id=account_id)
            )
        return list_of_projects

    """
    PROJECT UPLOAD
    """

    def create_project_upload(
            self, account_id: Union[int, str], project_id: Union[int, str], upload_data: dict, files: list
    ) -> DeepCrawlProjectUpload:
        """Create a project upload
        Project uploads allow you upload files to be used within a crawl such as log files and backlinks,
        this allows you to utilise outputs from other systems with DeepCrawl.

        .. code-block::

            upload_data = {
                "crawl_type": str,
                "project_upload_type": str,
                "enabled": bool
            }
            files = [('file', open("tests/files/test_urls.txt", "rb")]

        >>> connection.create_project_upload(0, 1, upload_data, files)
        [0 1] filename.csv

        :param account_id:
        :type account_id: int or str
        :param project_id:
        :type project_id: int or str
        :param upload_data:
        :type upload_data: dict
        :param files:
        :type files: list
        :return: Project upload instance
        :rtype: DeepCrawlProjectUpload
        """
        endpoint_url: str = get_api_endpoint(endpoint="project_uploads", account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='post', content_type=None, data=upload_data, files=files)
        return DeepCrawlProjectUpload(project_upload_data=response.json(), account_id=account_id, project_id=project_id)

    def get_project_upload(
            self, account_id: Union[int, str], project_id: Union[int, str], project_upload_id: Union[int, str]
    ) -> DeepCrawlProjectUpload:
        """Get project upload

        >>> connection.get_project_upload(0, 1, 5)
        [0 1] filename.csv

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param project_upload_id:
        :type project_upload_id: int
        :return: Requested project upload instance
        :rtype: DeepCrawlProjectUpload
        """
        endpoint_url: str = get_api_endpoint(
            endpoint="project_upload",
            account_id=account_id, project_id=project_id, project_upload_id=project_upload_id
        )
        response = self.dc_request(url=endpoint_url, method='get')
        return DeepCrawlProjectUpload(project_upload_data=response.json(), account_id=account_id, project_id=project_id)

    def enable_project_upload(
            self, account_id: Union[int, str], project_id: Union[int, str], project_upload_id: Union[int, str]
    ) -> DeepCrawlProjectUpload:
        """Enable project upload

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param project_upload_id:
        :type project_upload_id: int
        :return: Enabled project upload instance
        :rtype: DeepCrawlProjectUpload
        """
        endpoint_url: str = get_api_endpoint(
            endpoint="project_upload",
            account_id=account_id, project_id=project_id, project_upload_id=project_upload_id
        )
        response = self.dc_request(url=endpoint_url, method='patch', json={"enabled": True})
        return DeepCrawlProjectUpload(project_upload_data=response.json(), account_id=account_id, project_id=project_id)

    def disable_project_upload(
            self, account_id: Union[int, str], project_id: Union[int, str], project_upload_id: Union[int, str]
    ) -> DeepCrawlProjectUpload:
        """Disable project upload

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param project_upload_id:
        :type project_upload_id: int
        :return: Disabled project upload instance
        :rtype: DeepCrawlProjectUpload
        """
        endpoint_url: str = get_api_endpoint(
            endpoint="project_upload",
            account_id=account_id, project_id=project_id, project_upload_id=project_upload_id
        )
        response = self.dc_request(url=endpoint_url, method='patch', json={"enabled": False})
        return DeepCrawlProjectUpload(project_upload_data=response.json(), account_id=account_id, project_id=project_id)

    def delete_project_upload(
            self, account_id: Union[int, str], project_id: Union[int, str], project_upload_id: Union[int, str]
    ) -> Response:
        """Delete project upload

        >>> response = connection.delete_project_upload(0, 1, 5)
        >>> response.status_code
        204

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param project_upload_id:
        :type project_upload_id: int
        :return: HTTP 204 No Content
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='project_upload', account_id=account_id, project_id=project_id, project_upload_id=project_upload_id
        )
        return self.dc_request(url=endpoint_url, method='delete')

    def get_project_uploads(
            self, account_id: Union[int, str], project_id: Union[int, str], filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlProjectUpload]:
        """Get project uploads

        >>> connection.get_project_uploads(0, 1)
        [[0 1] filename.csv, [0 1] filename2.csv]

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param filters: filters
        :type filters: dict
        :param kwargs: extra arguments, like pagination ones
        :type kwargs: dict
        :return: list of project uploads
        :rtype: list
        """
        endpoint_url: str = get_api_endpoint(endpoint='project_uploads', account_id=account_id, project_id=project_id)
        project_uploads: List[dict] = self.get_paginated_data(url=endpoint_url, method='get', filters=filters, **kwargs)
        list_of_project_uploads = []
        for project in project_uploads:
            list_of_project_uploads.append(
                DeepCrawlProjectUpload(project_upload_data=project, account_id=account_id, project_id=project_id)
            )
        return list_of_project_uploads

    def get_project_upload_types(self) -> List[dict]:
        endpoint_url: str = get_api_endpoint(endpoint='project_upload_types')
        return self.dc_request(url=endpoint_url, method='get').json()

    def get_project_upload_type(self, project_upload_type_code: str) -> dict:
        endpoint_url: str = get_api_endpoint(
            endpoint='project_upload_type',
            project_upload_type_code=project_upload_type_code
        )
        return self.dc_request(url=endpoint_url, method='get').json()

    """
    MAJESTIC
    """

    def get_majestic_settings(self, account_id: Union[int, str], project_id: Union[int, str]) -> MajesticSettings:
        """Get projects majestic settings

        >>> connection.get_majestic_settings(0, 1)
        <deepcrawl.projects.majestic_settings.MajesticSettings at 0x108b29600>

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :return: majestic settings instance
        :rtype: MajesticSettings
        """
        endpoint_url: str = get_api_endpoint(endpoint='majestic', account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='get')
        return MajesticSettings(majestic_settings=response.json())

    def update_majestic_settings(
            self, account_id: Union[int, str], project_id: Union[int, str], majestic_settings: dict
    ) -> MajesticSettings:
        """Update majestic settings
        Majestic settings argument can be dict or a MajesticSettings instance.

        .. code-block::

            majestic_settings = {
                "enabled": bool,
                "max_rows": int,
                "use_historic_data": bool,
                "use_root_domain": bool
            }

        >>> connection.update_majestic_settings(0, 1, majestic_settings)

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param majestic_settings: majestic settings configuration
        :type majestic_settings: dict or MajesticSettings
        :return: updated majestic settings instance
        :rtype: MajesticSettings
        """
        if isinstance(majestic_settings, MajesticSettings):
            majestic_settings = majestic_settings.to_dict_mutable_fields

        endpoint_url: str = get_api_endpoint(endpoint='majestic', account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='patch', json=majestic_settings)
        return MajesticSettings(majestic_settings=response.json())

    """
    ISSUES
    """

    def create_issue(
            self, account_id: Union[int, str], project_id: Union[int, str], issue_data: dict
    ) -> DeepCrawlIssue:
        """Create issue

        .. code-block::

            issue_data = {
                "title": str,
                "description": str,
                "priority": str,
                "identified": str,
                "remaining": str,
                "deadline_at": str,
                "discovered_at": str,
                "actions": str,
                "dismissed": str,
                "notify_assignees": str,
                "fixed_at": str,
                "report_template": str,
                "filters": str,
                "q": str,
                "report_type": str,
                "assigned_to": str
            }

        >>> connection.create_issue(0, 1, issue_data)
        [0 1 3] Issue Title

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param issue_data: issue configuration
        :type issue_data: dict
        :return: issue instance
        :rtype: DeepCrawlIssue
        """
        url: str = get_api_endpoint("issues", account_id=account_id, project_id=project_id)
        response = self.dc_request(url=url, method='post', json=issue_data)
        return DeepCrawlIssue(account_id=account_id, project_id=project_id, issue_data=response.json())

    def get_issue(
            self, account_id: Union[int, str], project_id: Union[int, str], issue_id: Union[int, str]
    ) -> DeepCrawlIssue:
        """Get issue

        >>> connection.get_issue(0, 1, 2)
        [0 1 3] Issue Title

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param issue_id: issue id
        :type issue_id: int
        :return: issue instance
        :rtype: DeepCrawlIssue
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='issue',
            account_id=account_id, project_id=project_id, issue_id=issue_id
        )
        response = self.dc_request(url=endpoint_url, method='get')
        return DeepCrawlIssue(issue_data=response.json(), account_id=account_id, project_id=project_id)

    def update_issue(
            self, account_id: Union[int, str], project_id: Union[int, str], issue_id: Union[int, str], issue_data: dict
    ) -> DeepCrawlIssue:
        """Update issue

        >>> connection.update_issue(0, 1, 2, issue_data)
        [0 1 3] Issue Title

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param issue_id: issue id
        :type issue_id: int
        :param issue_data: issue configuration
        :type issue_data: dict
        :return: updated issue instance
        :rtype: DeepCrawlIssue
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='issue',
            account_id=account_id, project_id=project_id, issue_id=issue_id
        )
        response = self.dc_request(url=endpoint_url, method='patch', json=issue_data)
        return DeepCrawlIssue(issue_data=response.json(), account_id=account_id, project_id=project_id)

    def delete_issue(
            self, account_id: Union[int, str], project_id: Union[int, str], issue_id: Union[int, str]
    ) -> Response:
        """Delete issue

        >>> response = connection.delete_issue(0, 1, 2)
        >>> response.status_code
        204

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param issue_id: issue id
        :type issue_id: int
        :return: HTTP 204 No Content
        """
        url: str = get_api_endpoint("issue", account_id=account_id, project_id=project_id, issue_id=issue_id)
        return self.dc_request(url=url, method='delete')

    def get_issues(
            self, account_id: Union[int, str], project_id: Union[int, str], filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlIssue]:
        """Get issues

        >>> connection.get_issues(0, 1)
        [[0 1 3] Issue Title, [0 1 3] Issue Title2]

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param filters: filters
        :type filters: dict
        :param kwargs: extra arguments, like pagination ones
        :type kwargs: dict
        :return: list of issues
        :rtype: list
        """
        request_url: str = get_api_endpoint("issues", account_id=account_id, project_id=project_id)
        issues_response: List[dict] = self.get_paginated_data(request_url, method='get', filters=filters, **kwargs)

        list_of_issues = []
        for issue in issues_response:
            list_of_issues.append(DeepCrawlIssue(issue_data=issue, project_id=project_id, account_id=account_id))
        return list_of_issues

    """
    SCHEDULES
    """

    def create_schedule(
            self, account_id: Union[int, str], project_id: Union[int, str], schedule_data: dict
    ) -> DeepCrawlSchedule:
        """Create schedule

        >>> connection.create_schedule(0, 1, schedule_data)
        [0 1 4] 2021-03-22 12:09:11+00:00

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param schedule_data: schedule configuration
        :type schedule_data: dict
        :return: schedule instance
        :rtype: DeepCrawlSchedule
        """
        endpoint_url: str = get_api_endpoint(endpoint='crawl_schedules', account_id=account_id, project_id=project_id)
        response = self.dc_request(url=endpoint_url, method='post', json=schedule_data)
        return DeepCrawlSchedule(account_id=account_id, project_id=project_id, schedule_data=response.json())

    def get_schedule(
            self, account_id: Union[int, str], project_id: Union[int, str], schedule_id: Union[int, str]
    ) -> DeepCrawlSchedule:
        """Get schedule

        >>> connection.get_schedule(1, 2, 3)
        [0 1 3] 2021-03-22 12:09:11+00:00

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param schedule_id: issue id
        :type schedule_id: int
        :return: schedule instance
        :rtype: DeepCrawlSchedule
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='crawl_schedule',
            account_id=account_id, project_id=project_id, schedule_id=schedule_id
        )
        response = self.dc_request(url=endpoint_url, method='get')
        return DeepCrawlSchedule(account_id=account_id, project_id=project_id, schedule_data=response.json())

    def update_schedule(
            self, account_id: Union[int, str], project_id: Union[int, str], schedule_id: Union[int, str],
            schedule_data: dict
    ) -> DeepCrawlSchedule:
        """Update schedule

        >>> connection.update_schedule(1, 2, 3, schedule_data)
        [0 1 3] 2021-04-22 12:09:11+00:00

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param schedule_id: issue id
        :type schedule_id: int
        :param schedule_data: schedule configuration
        :type schedule_data: dict
        :return: updated schedule instance
        :rtype: DeepCrawlSchedule
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='crawl_schedule',
            account_id=account_id, project_id=project_id, schedule_id=schedule_id
        )
        response = self.dc_request(url=endpoint_url, method='patch', json=schedule_data)
        return DeepCrawlSchedule(account_id=account_id, project_id=project_id, schedule_data=response.json())

    def delete_schedule(
            self, account_id: Union[int, str], project_id: Union[int, str], schedule_id: Union[int, str]
    ) -> Response:
        """Delete current schedule instance

        >>> response = connection.delete_schedule(1, 2, 3)
        >>> response.status_code
        204

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param schedule_id: issue id
        :type schedule_id: int
        :return: HTTP 204 No Content
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='crawl_schedule',
            account_id=account_id, project_id=project_id, schedule_id=schedule_id
        )
        return self.dc_request(url=endpoint_url, method='delete')

    def get_schedules(
            self, account_id: Union[int, str], project_id: Union[int, str], filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlSchedule]:
        """Get schedules

        >>> connection.get_schedules(1, 2)
        [[0 1 3] 2021-03-22 12:09:11+00:00, [0 1 4] 2021-03-22 12:09:11+00:00]

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :return: list of schedules
        :rtype: list
        """
        endpoint_url: str = get_api_endpoint(endpoint='crawl_schedules', account_id=account_id, project_id=project_id)
        schedules: List[dict] = self.get_paginated_data(url=endpoint_url, method='get', filters=filters, **kwargs)

        list_of_schedules = []
        for schedule in schedules:
            list_of_schedules.append(
                DeepCrawlSchedule(account_id=account_id, project_id=project_id, schedule_data=schedule)
            )
        return list_of_schedules
