import streamlit as st

from skgstat_uncertainty.api import API

def main_app(api: API):
    st.title('Model Simulation')

    st.stop()


if __name__ == "__main__":
    def run(data_path = None, db_name = None):
        api = API(data_path=data_path, db_name=db_name)
        main_app(api)
    import fire
    fire.Fire(run)
