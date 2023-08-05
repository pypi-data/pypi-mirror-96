from __future__ import print_function

from enum import Enum

from halo_app.classes import AbsBaseClass

class Error(AbsBaseClass):
    message:str = None
    cause:Exception = None

    def __init__(self,message:str, cause:Exception):
      self.message = message
      self.cause = cause

class Notification(AbsBaseClass):
    errors:[Error]  = []

    def addError(self,message:str,exception:Exception):
        self.errors.add(Error(message,exception))

    def hasErrors(self)->bool:
        if len(self.errors) > 0:
            return True
        return False

    def errorMessage(self):
        msg = ''
        for i in self.errors:
            msg = msg + i.message + '-' + i.e.message + ','
        return msg
