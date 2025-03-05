import streamlit as st
import src.station as sta
import src.monitor as mon

def main():
  st.write("Hello world")
  monitor = mon.Monitor()
  station = sta.Station(monitor.base_url, "1029TH")
  print(station.availabe_measures)

if __name__ == "__main__":
  main()
