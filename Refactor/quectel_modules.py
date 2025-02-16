"This is module retrieves all supported CA and NR bands from the Quectel modules. "
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import pandas as pd
from pprint import pprint


class RM500Q_GL(object):
    "A class for collecting and storing data related to the Quectel RM500Q_GL module."

    def __init__(self) -> None:
        self.rm500q_gl = pd.read_excel(
            io="Quectel_RM50xQ_Series_CA_EN-DC_Features_V1.6.xlsx",
            sheet_name="RM500Q-GL",
        )
        self.rm500q_gl_bands = self.clean_data()

    def clean_data(self):
        "Cleaning the spreadsheet to provide all combinations (CA and ENDC)."
        rm = self.rm500q_gl
        rm = rm.iloc[5:415]
        cols = rm.columns.values
        for i in range(len(cols)):
            if cols[i] == f"Unnamed: {i}":
                rm = rm.drop(columns=cols[i])
        rm.dropna(how="all", inplace=True)
        self.rm2ca = rm["RM500Q-GL    2CA"]
        self.rm2ca = (
            self.rm2ca.dropna(how="all").apply(lambda x: x.lstrip("CA_")).to_list()
        )
        self.rm3ca = rm["RM500Q-GL    3CA"]
        self.rm3ca = (
            self.rm3ca.dropna(how="all").apply(lambda x: x.lstrip("CA_")).to_list()
        )
        self.rm_1lte_nr = rm["RM500Q-GL   EN-DC (1LTE + 1NR)"]
        self.rm_1lte_nr = self.rm_1lte_nr.dropna(how="all").to_list()
        self.rm_2lte_nr = rm["RM500Q-GL   EN-DC (2LTE + 1NR)"]
        self.rm_2lte_nr = self.rm_2lte_nr.dropna(how="all").to_list()
        self.rm_3lte_nr = rm["RM500Q-GL   EN-DC  (3LTE + 1NR)"]
        self.rm_3lte_nr = self.rm_3lte_nr.dropna(how="all").to_list()

        return {
            "2CA": self.rm2ca,
            "3CA": self.rm3ca,
            "1 LTE 1 NR": self.rm_1lte_nr,
            "2 LTE 1 NR": self.rm_2lte_nr,
            "3 LTE 1 NR": self.rm_3lte_nr,
        }
