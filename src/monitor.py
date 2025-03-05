import requests
import pandas as pd
import datetime as dt
import src.errors as err

class Monitor:
  """
  A class for managing all active measuring stations returned
  from the flood-monitoring API and managing time range data and format

  Attributes
  ----------
  base_url: str
    The base url used for all requests to the flood-monitoring api

  start_time: str
    The string representation of the start time for the 
    time range of data being requested

  end_time: str
    The string representation of the end time for the 
    time range of data being requested

  all_active_stations: pandas.DataFrame
    The dataframe constructed from the dict returned 
    on requesting data for all active measuring stations

  unique_stations: pandas.DataFrame
    The dataframe containing only the subset of columns 
    in all_active_stations which identify each station

  Methods
  -------
  get_active_stations() -> Result
    Requests all active stations from the flood-monitoring api
    checks if returned data exists and if the structure makes sense

  set_time_range() -> None
    Updates the start and end time strings being used to request data,
    always takes a period of the last 24 hours
  """
  def __init__(self) -> None:
    self.base_url = "https://environment.data.gov.uk/flood-monitoring"
    self.set_time_range()

    # Make sure the API requests are accepted and return consistent structure
    # We only take active stations to avoid needing to remove inconsistent entries
    match self.get_active_stations():
      case err.Err(error):
        print(error.why())
        raise AssertionError("Could not retrieve unique stations on startup, is the API down?")
      case err.Ok(df):
        self.all_active_stations = df

        # To allow picking of a station through its river, town, and label
        # notation is the unique identifier used to request data for the same station
        self.unique_stations = df[["notation", "riverName", "town", "catchmentName", "label"]]

  def get_active_stations(self) -> err.Result:
    """
    Requests all active stations from the flood-monitoring api
    checks if returned data exists and if the structure makes sense.

    Returns
    -------
    ApiReject if the api rejects the request
    BadReturn if the "items" entry does not exist in the json format
    BadReturn if the "riverName", "notation", "label", or "town"
      columns do not exist in the dataframe constructed from the json dict

    Ok(pandas.DataFrame) if the api accepts the request, the structure 
      is consistent and the dataframe is built correctly
    """
    response = requests.get(f"{self.base_url}/id/stations?status=Active")

    # Api has rejected our request
    if response.status_code != 200:
      return err.Err(err.MonitorError.ApiReject)
    
    data = response.json()
    
    # Return structure of request is not consistent with assumptions
    if "items" not in data:
      return err.Err(err.MonitorError.BadReturn)
    else:
      df = pd.DataFrame.from_dict(data["items"])

      # Cannot identify stations without these columns
      if not {"riverName", "notation", "label", "town"}.issubset(df.columns.values):
        return err.Err(err.MonitorError.BadReturn)

      return err.Ok(df)
   
  def set_time_range(self) -> None:
    """
    Updates the start and end time strings being used to request data,
    always takes a period of the last 24 hours

    Does not return, updates end_time and start_time inplace
    """
    # collect time for time series data
    end = dt.datetime.now()
    start = end - dt.timedelta(hours=24)

    # API expects time bound requests to have 
    # Year-Month-DayTHour:Minute:SecondZ format
    self.end_time = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    self.start_time = start.strftime("%Y-%m-%dT%H:%M:%SZ")

