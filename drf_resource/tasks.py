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

from functools import wraps

from blueapps.core.celery import celery_app
from celery.result import AsyncResult
from django.utils.module_loading import import_string

from drf_resource.exceptions import CustomError
from drf_resource.utils.logger import logger
from drf_resource.utils.request import set_local_username


@celery_app.task(bind=True)
def run_perform_request(self, resource_obj, username, request_data):
    """
    将resource作为异步任务执行
    :param self: 任务对象
    :param resource_obj: Resource实例
    :param username: 用户
    :param request_data: 请求数据
    :return: resource处理后的返回数据
    """
    if isinstance(resource_obj, str):
        resource_obj = import_string(resource_obj)()
    set_local_username(username)
    resource_obj._task_manager = self
    validated_request_data = resource_obj.validate_request_data(request_data)
    response_data = resource_obj.perform_request(validated_request_data)
    validated_response_data = resource_obj.validate_response_data(response_data)
    return validated_response_data


def _fetch_data_from_result(async_result):
    """
    从异步任务结果中提取步骤信息
    :param async_result: AsyncResult 对象
    :return: message, data: 步骤信息，步骤数据
    """
    info = async_result.info
    try:
        message = info.get("message")
        data = info.get("data")
    except Exception:
        message = None
        data = None
    return message, data


def query_task_result(task_id):
    """
    查询任务结果
    """
    result = AsyncResult(task_id)

    # 任务是否完成
    is_completed = False

    message, data = _fetch_data_from_result(result)

    if result.successful() or result.failed():
        is_completed = True
        try:
            # 任务执行完成，则读取结果数据
            message = None
            data = result.get()
        except CustomError as e:
            message = e.message
            data = e.data
        except Exception as e:
            logger.exception("Caught exception when running async resource task : %s" % e)
            message = "%s" % e
            data = None

    return {
        "task_id": task_id,
        "is_completed": is_completed,
        "state": result.state,
        "message": message,
        "data": data,
    }


def step(state=None, message=None, data=None):
    """
    步骤装饰器
    :param state: 当前状态，字符串
    :param message: 步骤信息
    :param data: 步骤数据
    """

    # 兼容不带括号的情况
    if callable(state):
        real_func = state
        real_state = None
    else:
        real_func = None
        real_state = state

    def decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 不传递步骤名称，则默认使用函数名的全大写形式作为步骤名称
            _state = real_state or func.__name__.upper()
            # 更新任务状态
            self.update_state(state=_state, message=message, data=data)
            return func(self, *args, **kwargs)

        return wrapper

    if real_func:
        return decorate(real_func)

    return decorate
