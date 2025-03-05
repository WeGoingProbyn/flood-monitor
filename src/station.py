import requests
import pandas as pd
from enum import Enum
import src.errors as err

class Measure(Enum):
  Flow = 0
  Wind = 1
  Tidal = 2
  Stage = 3
  Downstage = 4
  Groundwater = 5
  Temperature = 6

  def to_string(self) -> str:
    match self:
      case Measure.Flow:
        return "flow"
      case Measure.Wind:
        return "wind"
      case Measure.Tidal:
        return "tidal level"
      case Measure.Stage:
        return "stage level"
      case Measure.Downstage:
        return "downstream stage level"
      case Measure.Groundwater:
        return "groundwater level"
      case Measure.Temperature:
        return "temperature"

def measure_from_string(ty: str) -> err.Result:
  string = ty.lower()
  match string:
    case "flow":
      return err.Ok(Measure.Flow)
    case "wind":
      return err.Ok(Measure.Wind)
    case "tidal level":
      return err.Ok(Measure.Tidal)
    case "stage":
      return err.Ok(Measure.Stage)
    case "downstream stage":
      return err.Ok(Measure.Downstage)
    case "groundwater":
      return err.Ok(Measure.Groundwater)
    case _:
      return err.Err(err.MonitorError.BadStringToEnum)

class Station:
  """
  A class to contain all of the information returned when
  requesting measurements from a given monitoring station

  Attributes
  ----------
  station_reference: str
    the unique identifier used to request data for this station

  available_measires: [(Measure, str)]
    The array of available (measurement, units) types when querying measurements this station

  Methods
  -------
  """
  def __init__(self, base_url: str, reference: str) -> None:
    """
    Init function for constructing a station instance,
    requires the unique station reference used in the api

    queries the flood-monitor api to gather expected measurement types
    using the station reference used to instantiate the object

    Parameters
    ----------
    base_url: str
      The base url used for requesting data from the flood-monitoring
      API, should be passed from an instance of Monitor class for consistency

    reference: str
      the unique identifier used to request data for this station
    """
    self.availabe_measures = []
    self.station_reference = reference

    # If we cannot find the available measures for this
    # station there is no need to crash the server, just log
    # the failure and allow user to try a different station
    match self.find_available_measures(base_url):
      case err.Err(error):
        print(error.why())
        print(
          f"Could not find the available measurements for station: {self.station_reference}"
        )
      case err.Ok(_):
        print(f"Successfully collected measurement types for station: {self.station_reference}")

  def find_available_measures(self, base_url: str) -> err.Result:
    """
    Query the api for this station to obtain the available
    measurement types which can be requested

    Updates self.available_measures appending Measure enum to
    determine which types of measurements are to be expected when requested

    Parameters
    ----------
    base_url: str
      The base url used for requesting data from the flood-monitoring
      API, should be passed from an instance of Monitor class for consistency

    Returns
    -------
    ApiReject if the initial api call returns any code other than 200
    BadReturn if the response does not contain the items key
    BadReturn if the response does not contain the measurement key inside the items dict
    """
    self.availabe_measures = []
    response = requests.get(f"{base_url}/id/stations/{self.station_reference}")

    # Request failed when != 200
    if response.status_code != 200:
      return err.Err(err.MonitorError.ApiReject)

    data = response.json()
    if "items" not in data:
      return err.Err(err.MonitorError.BadReturn)
    elif "measures" not in data["items"]:
      return err.Err(err.MonitorError.BadReturn)

    # If there is only 1 measurement a dict is returned
    # otherwise an array is used, need to add the dict to
    # an array if only 1 measurement is returned to loop over consistently
    if isinstance(data["items"]["measures"], dict):
      data["items"]["measures"] = [data["items"]["measures"]]

    for measure in data["items"]["measures"]:
      if "parameter" not in measure:
        print(
          (f"Parameter descriptor not found in measurement "
           f"for station: {self.station_reference}, skipping")
        )
        continue

      # Extract the unit type
      units = measure["unit"].rsplit("#", 1)[-1]
      # Find the type of measurement being given
      if measure["parameter"] == "level":
        # the level parameter can come from different types of measurements
        # need to use the qualifier to distinguish between them 
         match measure_from_string(measure["qualifier"]):
          case err.Ok(ty):
            self.availabe_measures.append((ty, units))
          case err.Err(error):
            print(error.why())
            print(f"Could not convert \"{measure["qualifier"]}\" into Measure enum type")       
      else:
        # Otherwise the parameter can be used to determine the measurement type
        match measure_from_string(measure["parameter"]):
          case err.Ok(ty):
            self.availabe_measures.append((ty, units))
          case err.Err(error):
            print(error.why())
            print(f"Could not convert \"{measure["parameter"]}\" into Measure enum type")
    return err.Ok(0)


  def request_measure(self, measure: Measure, start_time: str, base_url: str) -> err.Result:
    """
    Parameters
    ----------
    measure: Measure
      The measure to request from the flood-monitoring API

    start_time: str
      The formatted start time held by a Monitor instance

    base_url: str
      The base url used for requesting data from the flood-monitoring
      API, should be passed from an instance of Monitor class for consistency

    Returns
    -------

    """
    ext = None
    match measure:
      case Measure.Flow:
        ext = f"?parameter=flow&since={start_time}"
      case Measure.Wind:
        ext = f"?parameter=wind&since={start_time}"
      case Measure.Tidal:
        ext = f"?parameter=level&qualifier=Tidal Level&since={start_time}"
      case Measure.Stage:
        ext = f"?parameter=level&qualifier=Stage&since={start_time}"
      case Measure.Downstage:
        ext = f"?parameter=level&qualifier=Downstream Stage&since={start_time}"
      case Measure.Groundwater:
        ext = f"?parameter=level&qualifier=Groundwater&since={start_time}"
      case Measure.Temperature:
        ext = f"?parameter=temperature&since={start_time}"

    response = requests.get(f"{base_url}/id/stations/{self.station_reference}/readings{ext}")

    if response.status_code != 200:
      return err.Err(err.MonitorError.ApiReject)

    data = response.json()
    if "items" not in data:
      return err.Err(err.MonitorError.BadReturn)

    df = pd.DataFrame.from_dict(data["items"])
    return err.Ok(df[["dateTime", "value"]])


