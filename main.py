import streamlit as st
import src.station as sta
import src.monitor as mon

import src.errors as err

def main():
  # st.write("Hello world")
  monitor = mon.Monitor()

  option = st.selectbox(
    "Choose a station!",
    ("1029TH", "44239"),
  )
  station = sta.Station(monitor.base_url, option)

  for _,(measure, _) in enumerate(station.availabe_measures):
    match station.request_measure(measure, monitor.start_time, monitor.base_url):
      case err.Err(error):
        print(error.why())
      case err.Ok(df):
        st.line_chart(data=df, x="dateTime", y="value")

if __name__ == "__main__":
  main()
