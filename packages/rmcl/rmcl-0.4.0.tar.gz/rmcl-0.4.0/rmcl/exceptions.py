# Copyright 2019 Stijn Van Campenhout
# This file is part of rmcl and is distributed under the MIT license.

class AuthError(Exception):
    """Authentication error"""
    def __init__(self, msg):
        super(AuthError, self).__init__(msg)


class DocumentNotFound(Exception):
    """Could not found a requested document"""
    def __init__(self, msg):
        super(DocumentNotFound, self).__init__(msg)


class UnsupportedTypeError(Exception):
    """Not the expected type"""
    def __init__(self, msg):
        super(UnsupportedTypeError, self).__init__(msg)


class FolderNotFound(Exception):
    """Could not found a requested folder"""
    def __init__(self, msg):
        super(FolderNotFound, self).__init__(msg)


class ApiError(Exception):
    """Could not found a requested document"""
    def __init__(self, msg, response=None):
        self.response = response
        super(ApiError, self).__init__(msg)


class VirtualItemError(Exception):
    """An operation can not be done on a virtual item."""
    pass
