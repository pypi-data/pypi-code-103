#!/usr/bin/env python3
# coding: utf-8

import volkanic.introspect


class KnownError(volkanic.introspect.ErrorBase):
    pass


class BusinessError(KnownError):
    extra = {'code': 1}


C1Error = BusinessError


class TechnicalError(KnownError):
    extra = {'code': 2}

    def __str__(self):
        s = super().__str__()
        return f'{s} <{self.error_key}>'


C2Error = TechnicalError


class ErrorInfo(volkanic.introspect.ErrorInfo):
    message = 'Application Error'

    def to_dict(self, code=3):
        if isinstance(self.exc, volkanic.introspect.ErrorBase):
            return self.exc.to_dict()
        return {
            'code': code,
            'error_key': self.error_key,
            'message': f'{self.message} <{self.error_key}>',
        }
