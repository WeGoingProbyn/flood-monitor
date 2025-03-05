import requests
import src.errors as err
from enum import Enum

class Measure(Enum):
  Flow = 0
  Wind = 1
  Tidal = 2
  Stage = 3
  Downstage = 4
  Groundwater = 5
  Temperature = 6

class Station:
  """
  A class to contain all of the information returned when
  requesting measurements from a given monitoring station

  Attributes
  ----------
  station_reference: str
    the unique identifier used to request data for this station

  available_measires: [Measure]
    The array of available measurements types when querying measurements this station

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

      # Find the type of measurement being given
      match measure["parameter"]:
        case "flow":
          self.availabe_measures.append(Measure.Flow)
        case "wind":
          self.availabe_measures.append(Measure.Wind)
        case "temperature":
          self.availabe_measures.append(Measure.Temperature)
        case "level":
          if "qualifier" not in measure:
            print(
              (f"Level parameter found for station: {self.station_reference}, " 
                "but no qualifier found to distinguish level type, skipping")
            )
            continue

          # Need to find the type of level being measured from
          # the qualifier field as 1 station may provide more than 1 type of level
          match measure["qualifier"]:
            case "Stage":
              self.availabe_measures.append(Measure.Stage)
            case "Downstream Stage":
              self.availabe_measures.append(Measure.Downstage)
            case "Groundwater":
              self.availabe_measures.append(Measure.Groundwater)
            case "Tidal":
              self.availabe_measures.append(Measure.Tidal)
            case _:
              print(
                f"Found unexpected qualifier: {measure["qualifier"]}, for level measurement"
              )
              continue
        case _:
          print(
            f"Found unexpected measurement: {measure["parameter"]}, for station: {self.station_reference}"
          )
    return err.Ok(0)


  # def request_measure(self, measure: Measure, base_url: str) -> err.Result:
  #   """
  #   Parameters
  #   ----------
  #   measure: Measure
  #     The measure to request from the flood-monitoring API
  #
  #   base_url: str
  #     The base url used for requesting data from the flood-monitoring
  #     API, should be passed from an instance of Monitor class for consistency
  #
  #   Returns
  #   -------
  #
  #   """

