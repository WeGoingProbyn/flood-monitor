import requests
import pandas as pd
from enum import Enum
import src.errors as err

class Measure(Enum):
  """
  An enum representing the possible measurements
  which can be obtained when querying the flood-management API
  """
  Flow = 0
  Wind = 1
  Tidal = 2
  Stage = 3
  Logged = 4
  Downstage = 5
  Groundwater = 6
  Temperature = 7

  def to_string(self) -> str:
    """
    A function which converts this enum into its corresponding
    string representation given by the flood-management API

    Returns
    -------
    The string version of this Measure enum
    """
    match self:
      case Measure.Flow:
        return "flow"
      case Measure.Wind:
        return "wind"
      case Measure.Tidal:
        return "tidal level"
      case Measure.Stage:
        return "stage"
      case Measure.Logged:
        return "logged"
      case Measure.Downstage:
        return "downstream stage"
      case Measure.Groundwater:
        return "groundwater"
      case Measure.Temperature:
        return "temperature"

def measure_from_string(ty: str) -> err.Result:
  """
  A function which converts a string into its corresponding
  Measure enum representation

  Parameters
  ----------
  ty: str
    The string representation of the measure being converted into
    analogous Measure enum

  Returns
  -------
  BadStringToEnum if the string passed into this function does not
  correspond to an analogous Measure in the enum class

  Ok(Measure) if the string is converted correctly
  """
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
    case "logged":
      return err.Ok(Measure.Logged)
    case "downstream stage":
      return err.Ok(Measure.Downstage)
    case "groundwater":
      return err.Ok(Measure.Groundwater)
    case _:
      return err.Err(
        err.MonitorError.BadStringToEnum,
        "Could not convert string to measurement enum"
      )

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

  good_construct: bool
    boolean used to check if an error occured during object
    construction

  Methods
  -------
  find_available_measures(self, base_url: str) -> Result
    Queries the flood-monitoring API to determine which measurements
    can be expected when retrieving data from the requested station

  request_measures(self, measure: Measure, start_time: str, base_url: str) -> Result
    Queries the flood-monitoring API for the requested measure from the instance
    which the request is made and the start time passed into the function
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
      case err.Err(error, src):
        print(error.why())
        print(
          f"Could not find the available measurements for station: {self.station_reference}" +
          f"With source: {src}"
        )
        self.good_construction = False
      case err.Ok(_):
        print(
          f"Successfully collected measurement types for station: {self.station_reference}"
        )
        self.good_construction = True

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
      return err.Err(
        err.MonitorError.ApiReject,
        f"API did not return status 200 when requesting "+
        f"available measures for station: {self.station_reference}"
      )

    data = response.json()
    if "items" not in data:
      return err.Err(
        err.MonitorError.BadReturn,
        f"API did not return json structure with items " +
        f"key when requesting available measures for station {self.station_reference}"
      )
    elif "measures" not in data["items"]:
      return err.Err(
        err.MonitorError.BadReturn,
        f"API did not return items json structure with measures " +
        f"key when requesting available measures for station {self.station_reference}"
      )

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
      units = None
      if not "unit" in measure:
        units = "unkown"
      else:
        units = measure["unit"].rsplit("#", 1)[-1]

      # Find the type of measurement being given
      if measure["parameter"] == "level":
        # the level parameter can come from different types of measurements
        # need to use the qualifier to distinguish between them 
         match measure_from_string(measure["qualifier"]):
          case err.Ok(ty):
            if not any(existing_ty == ty for existing_ty, _ in self.availabe_measures):
              self.availabe_measures.append((ty, units))
          case err.Err(error):
            print(error.why())
            print(f"Could not convert \"{measure["qualifier"]}\" into Measure enum type")       
      else:
        # Otherwise the parameter can be used to determine the measurement type
        match measure_from_string(measure["parameter"]):
          case err.Ok(ty):
            if not any(existing_ty == ty for existing_ty, _ in self.availabe_measures):
              self.availabe_measures.append((ty, units))
          case err.Err(error):
            print(error.why())
            print(f"Could not convert \"{measure["parameter"]}\" into Measure enum type")
    
    # Some returns provide duplicate measures
    # self.availabe_measures = list(dict.fromkeys(self.availabe_measures))
    return err.Ok(0)


  def request_measure(self, measure: Measure, start_time: str, base_url: str) -> err.Result:
    """
    A method which requests a measure from the flood-monitoring API
    for this station given a passed starting time

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
    ApiReject if the status code returned on the HTTP request was not 200
    BadReturn if the json structure returned by the API call does not contain items key
    BadReturn if the json structure inside the items dict does not contain "dateTime" and
    "value" keys

    Ok(pandas.DataFrame) if the returned structure contains necessary keys and
    the dataframe is constructed correctly
    """

    # Determine the extension required to request from API
    ext = None
    match measure:
      case Measure.Flow | Measure.Wind | Measure.Temperature:
        ext = f"?parameter={measure.to_string()}"
      case Measure.Tidal | Measure.Stage | Measure.Downstage | Measure.Groundwater | Measure.Logged:
        ext = f"?parameter=level&qualifier={measure.to_string().capitalize()}"

    # request data
    response = requests.get(f"{base_url}/id/stations/{self.station_reference}/readings{ext}&since={start_time}")
    if response.status_code != 200:
      return err.Err(
        err.MonitorError.ApiReject,
        f"API did not return status code 200 when requesting " +
        f"measurement: {measure.to_string()} for station: {self.station_reference}"
      )

    data = response.json()
    if "items" not in data:
      print(
        f"item key not found for measure: {measure.to_string} " + 
        f"and station: {self.station_reference}"
      )
      return err.Err(
        err.MonitorError.BadReturn,
        f"API did not return json structure with items key for " +
        f"measure: {measure.to_string()} and station: {self.station_reference}"
      )

    # build dataframe from json response
    df = pd.DataFrame.from_dict(data["items"])
    if not {"dateTime", "value"}.issubset(df.columns.values):
      print(
        f"dateTime, or value keys not found for measure: " +
        f"{measure.to_string()} and station: {self.station_reference}"
      )
      return err.Err(
        err.MonitorError.BadReturn,
        f"API did not return items json structure with dateTime or value key for " +
        f"measure: {measure.to_string()} and station: {self.station_reference}"
      )
    else:
      df["dateTime"] = pd.to_datetime(df["dateTime"])
      return err.Ok(df[["dateTime", "value"]])


