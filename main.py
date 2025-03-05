# import streamlit as st
import src.station as sta
import src.monitor as mon

import src.errors as err

import matplotlib.pyplot as plt

def main():
  # st.write("Hello world")
  monitor = mon.Monitor()
  station = sta.Station(monitor.base_url, "1029TH")

  match station.request_measure(sta.Measure.Downstage, monitor.start_time, monitor.base_url):
    case err.Err(error):
      print(error.why())
    case err.Ok(df):
      plt.plot(df["dateTime"], df["value"])
      plt.savefig("./test.png")
  

if __name__ == "__main__":
  main()
