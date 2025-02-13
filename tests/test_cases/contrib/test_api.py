# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - Resource SDK (BlueKing - Resource SDK) available.
Copyright (C) 2023 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at https://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""

from unittest import mock

from django.test import TestCase

from drf_resource.exceptions import APIRequestError
from tests.mock.contrib.api import (
    MockErrorSession,
    MockGetAPI,
    MockGetError,
    MockGetResultFalse,
    MockGetTypeError,
    MockPostAPI,
    MockSession,
)


class TestAPIResource(TestCase):
    @mock.patch("bk_resource.contrib.api.requests.session", MockSession)
    def test_get_request(self):
        self.assertIsInstance(MockGetAPI().request(), dict)

    @mock.patch("bk_resource.contrib.api.requests.session", MockSession)
    def test_post_request(self):
        MockPostAPI().request(username="admin")

    @mock.patch("bk_resource.contrib.api.requests.session", MockErrorSession)
    def test_http_error(self):
        with self.assertRaises(APIRequestError):
            MockGetAPI().request()

    def test_error(self):
        with self.assertRaises(APIRequestError):
            MockGetError().request()

    def test_result_type_error(self):
        with self.assertRaises(APIRequestError):
            MockGetTypeError().request()

    def test_result_false(self):
        with self.assertRaises(APIRequestError):
            MockGetResultFalse().request()
