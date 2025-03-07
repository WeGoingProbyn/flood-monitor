import streamlit as st
import src.errors as err
import src.station as sta
import src.monitor as mon

st.set_page_config(layout="wide")

def main():
  # Collect all unique stations
  monitor = mon.Monitor()

  # if an error occured in the monitor constructor
  if not monitor.good_construction:
    st.error("App was unable to gather all unique monitoring " +
              "stations and set time and date ranges. " +
              "This is a fatal error and the app cannot continue " +
              "from here, check console output for more information", 
              icon="🚨"
             )
  else:
    # Chose station using river, town, and station
    col1, col2, col3 = st.columns(3)
    with col1:
      # Limit by river names
      river_name = st.selectbox(
        "Choose a river:",
        sorted(monitor.unique_stations["riverName"].unique()),
      )
    cond_river = monitor.unique_stations["riverName"] == river_name

    with col2:
      # limit by towns which are on this rives
      # .unique() may remove duplicate unkowns?
      town_name = st.selectbox(
        "Choose a town:",
        sorted(monitor.unique_stations.loc[cond_river, "town"].unique()),
      )
    cond_town = monitor.unique_stations["town"] == town_name

    with col3:
      # Finally, chose the station, should be unique choice by this stage
      station_ref = st.selectbox(
        "Choose a station:",
        sorted(monitor.unique_stations.loc[cond_river & cond_town, "label"]),
      )

    cond_ref = monitor.unique_stations["label"] == station_ref
    sta_ref = monitor.unique_stations.loc[cond_river & cond_town & cond_ref, "notation"]

    # A unique reference wasnt found for this station
    if len(sta_ref) == 0:
      st.warning(
        f"Could not find the unique reference for the station being requested",
        icon="⚠️"
      )

    else:
      # A station has more than 1 unique reference
      if len(sta_ref) > 1:
        st.warning(
          "Found multiple references for the station being requested, " +
          "using the first reference found in the array",
          icon="⚠️"
        )

      # always take the first unique station reference
      station = sta.Station(monitor.base_url, sta_ref.iloc[0])

      # if an error occured in the station constructor
      if not station.good_construction:
        st.warning(
          "The app encountered an error while trying to build " +
          "a data structure. This is a recoverable " + 
          f"error but data for station {station_ref} could " +
          "not be retrieved or diplayed, see console output for more information",
          icon="⚠️"
        )
      else:
        # For every measurement found in this statement, show the line chart and table
        for (measure, unit) in station.availabe_measures:
          col1, col2 = st.columns([3,1], vertical_alignment="top", border=True)
          match station.request_measure(measure, monitor.start_time, monitor.base_url):
            case err.Err(error, src):
              # If an error has been pushed up, make the user aware of this
              # on both the std output and on the front end page
              print(error.why() + " " + src)
              with col1:
                st.warning(
                  f"Something went wrong when querying {measure.to_string()} for this station " +
                  f"with error: {error.why()} and source: {src}",
                  icon="⚠️"
                )
            case err.Ok(df):
              # if everything behaves as expected, show the line graph in column 1
              with col1:
                st.line_chart(
                  data=df, 
                  x="dateTime", 
                  y="value", 
                  x_label=f"date and time ({monitor.start_time[:-10]} - {monitor.end_time[:-10]})",
                  y_label=f"{measure.to_string()} ({unit})"
                )
              with col2:
                # show table in column 2
                st.dataframe(df)

if __name__ == "__main__":
  main()
