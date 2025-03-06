import streamlit as st
import src.errors as err
import src.station as sta
import src.monitor as mon

st.set_page_config(layout="wide")

def main():
  # st.write("Hello world")
  monitor = mon.Monitor()

  col1, col2, col3 = st.columns(3)
  with col1:
    river_name = st.selectbox(
      "Choose a river!",
      monitor.unique_stations["riverName"].unique(),
    )
  cond_river = monitor.unique_stations["riverName"] == river_name

  with col2:
    town_name = st.selectbox(
      "Choose a town!",
      monitor.unique_stations.loc[cond_river, "town"].unique(),
    )
  cond_town = monitor.unique_stations["town"] == town_name

  with col3:
    station_ref = st.selectbox(
      "Choose a station!",
      monitor.unique_stations.loc[cond_river & cond_town, "label"],
    )

  cond_ref = monitor.unique_stations["label"] == station_ref
  sta_ref = monitor.unique_stations.loc[cond_river & cond_town & cond_ref, "notation"]

  if len(sta_ref) == 0:
    print("you nonce")
  elif len(sta_ref) == 1:
    station = sta.Station(monitor.base_url, sta_ref.iloc[0])
    print(station.availabe_measures)

    for (measure, unit) in station.availabe_measures:
      col1, col2 = st.columns([3,1], vertical_alignment="top", border=True)
      match station.request_measure(measure, monitor.start_time, monitor.base_url):
        case err.Err(error):
          print(error.why())
          st.write("Something went wrong when querying data for this station!")
        case err.Ok(df):
          with col1:
            st.line_chart(
              data=df, 
              x="dateTime", 
              y="value", 
              x_label="date and time",
              y_label=f"{measure.to_string()} ({unit})"
            )
          with col2:
            st.dataframe(df)
  else:
    print(sta_ref)

if __name__ == "__main__":
  main()
