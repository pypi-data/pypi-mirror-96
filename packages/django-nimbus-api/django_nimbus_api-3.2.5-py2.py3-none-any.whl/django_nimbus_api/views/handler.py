# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback
from ..settings import api_settings
from ..err_code import APIError, ErrCode

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    logger.error(exc)
    _enabled = api_settings.API_CATCH_EXCEPTION_ENABLED
    _err_func = api_settings.API_CATCH_EXCEPTION_HANDLER
    if isinstance(exc, Http404):
        exc = APIError(ErrCode.ERR_COMMON_NOT_FOUND, status_code=404)
    elif isinstance(exc, PermissionDenied):
        exc = APIError(ErrCode.ERR_COMMON_PERMISSION, status_code=403)

    # if isinstance(exc, DingTalkException):
    #     headers = {}
    #     data = "{code}|{msg}".format(code=exc.errcode, msg=exc.errmsg)
    #     status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
    #     set_rollback()
    #     return Response(data, status=status_code, headers=headers)

    if isinstance(exc, APIError):
        headers = {}
        err = exc.get_res_dict()
        data = {"detail": err}
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
        set_rollback()
        return Response(data, status=status_code, headers=headers)

    response = exception_handler(exc, context)
    if response:
        return response

    if _enabled and not response and isinstance(exc, Exception):
        headers = {}
        if _err_func and callable(_err_func):
            response = _err_func(exc, context)
            set_rollback()
            return response
        else:
            data = "{msg}".format(msg=exc)
            status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
            set_rollback()
            return Response(data, status=status_code, headers=headers)

    return None
