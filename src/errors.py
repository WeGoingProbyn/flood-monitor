from enum import Enum
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

class MonitorError(Enum):
  BadReturn = 0
  ApiReject = 1
  BadStringToEnum = 2

  def why(self):
    match self:
      case MonitorError.BadReturn:
        return "API request did not return expected data"
      case MonitorError.ApiReject:
        return "API Rejected request and returned no data"
      case MonitorError.BadStringToEnum:
        return "Could not convert requested string into analogous enum type"

T = TypeVar("T")

@dataclass
class Ok(Generic[T]):
  value: T

@dataclass
class Err(Generic[T]):
  error: MonitorError

Result = Union[Ok[T], Err[T]]

def test() -> Result:
  return Err(MonitorError.BadReturn)
