import pandas as pd
import numpy as np
import matplotlib as plt
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl import load_workbook, Workbook
from operator_priority import OperatorPriorityList

# from required_bands import RequiredBands

quectel_sheet = "Quectel_RM50xQ_Series_CA_EN-DC_Features_V1.6.xlsx"
oper = OperatorPriorityList()


class Quectel:
    "A class for gathering and cleaning the bands for the quectel modems."

    def __init__(self) -> None:
        self.rm500q = self.clean_data(data=(self.gather_data()["RM500Q-GL"]))
        self.rm502q = self.clean_data(data=self.gather_data()["RM502Q-AE "])
        self.rm505q = self.clean_data(data=self.gather_data()["RM500Q-AE&RM505Q-AE"])

    def gather_data(self):
        rm500gl = pd.read_excel(
            io=quectel_sheet,
            sheet_name=["RM500Q-GL", "RM502Q-AE ", "RM500Q-AE&RM505Q-AE"],
        )

        return rm500gl

    def clean_data(self, data: pd.DataFrame):
        columns = data.columns
        for col in range(len(columns)):
            if columns[col] == f"Unnamed: {col}":
                data.drop(columns=[f"Unnamed: {col}"], inplace=True)

        return data


class RequiredBands(object):
    "A class that will retrieve and store all requied testing bands per carrier and module manufacturer."

    q = Quectel()

    def __init__(self) -> None:
        self.att_tis = self.clean_data(oper.att_ca_tis_trp()["TIS"])
        self.att_trp = self.clean_data(oper.att_ca_tis_trp()["TRP"])
        self.tmo_tis = self.clean_data(oper.tmo_ca_tis_trp()["TIS"])
        self.tmo_trp = self.clean_data(oper.tmo_ca_tis_trp()["TRP"])
        self.vzw_tis = self.clean_data(oper.vzw_ca_tis_trp()["TIS"])
        self.vzw_trp = self.clean_data(oper.vzw_ca_tis_trp()["TRP"])

    def clean_data(self, bands: list[str]) -> list:
        "formating the data to same comparable form"
        self.bands = bands

        for i in range(len(bands)):
            bands[i] = bands[i][
                : bands[i].find("A", len(bands[i]) - 4, len(bands[i])) + 1
            ]
            if "or" in bands[i]:
                bands.append(bands[i].split("or")[1].strip())
                bands[i] = bands[i].split("or")[0].strip()
                bands[i] = bands[i][
                    : bands[i].find("A", len(bands[i]) - 4, len(bands[i])) + 1
                ]
            if "_" in bands[i]:
                bands[i] = bands[i].replace("_", "-")

        return bands

    def test_bands(self, data):
        if data is self.q.rm500q:
            rm500qca = self.q.rm500q.iloc[3:, [0, 1]]
            rm500qca.dropna(how="all", inplace=True)
            rm_2ca = rm500qca["RM500Q-GL    2CA"].dropna(how="all")
            rm_2ca = rm_2ca.apply(lambda x: x.lstrip("CA_")).to_list()
            rm_3ca = rm_3ca = rm500qca["RM500Q-GL    3CA"].dropna(how="all")
            rm_3ca = rm_3ca.apply(lambda x: x.lstrip("CA_")).to_list()

            rm_ca = rm_2ca + rm_3ca
            ca_bands = {
                "ATT": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_trp
                    ],
                },
                "TMO": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_trp
                    ],
                },
                "VZW": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_trp
                    ],
                },
            }
        elif data is self.q.rm502q:
            rm502qca = self.q.rm502q.iloc[3:, [0, 1]]
            rm502qca.dropna(how="all", inplace=True)
            rm_2ca = rm502qca["RM502Q-AE  LTE  2CA"].dropna(how="all")
            rm_2ca = rm_2ca.apply(lambda x: x.lstrip("CA_")).to_list()
            rm_3ca = rm_3ca = rm502qca["RM502Q-AE  LTE  3CA"].dropna(how="all")
            rm_3ca = rm_3ca.apply(lambda x: x.lstrip("CA_")).to_list()

            rm_ca = rm_2ca + rm_3ca
            ca_bands = {
                "ATT": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_trp
                    ],
                },
                "TMO": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_trp
                    ],
                },
                "VZW": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_trp
                    ],
                },
            }
        elif data is self.q.rm505q:
            rm505qca = self.q.rm505q.iloc[3:, [0, 1]]
            rm505qca.dropna(how="all", inplace=True)
            rm_2ca = rm505qca["RM500Q-AE&RM505Q-AE     2CA"].dropna(how="all")
            rm_2ca = rm_2ca.apply(lambda x: x.lstrip("CA_")).to_list()
            rm_3ca = rm_3ca = rm505qca["RM500Q-AE&RM505Q-AE   3CA"].dropna(how="all")
            rm_3ca = rm_3ca.apply(lambda x: x.lstrip("CA_")).to_list()

            rm_ca = rm_2ca + rm_3ca
            ca_bands = {
                "ATT": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.att_trp
                    ],
                },
                "TMO": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.tmo_trp
                    ],
                },
                "VZW": {
                    "TIS": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_tis
                    ],
                    "TRP": [
                        rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in self.vzw_trp
                    ],
                },
            }

        return ca_bands

    def ednc_test_bands(self, data):
        if data is self.q.rm500q:
            rm500qfr = self.q.rm500q.iloc[3:, [2, 3, 4]]
            rm500qfr.dropna(how="all", inplace=True)
            rm500qfr_one = rm500qfr["RM500Q-GL   EN-DC (1LTE + 1NR)"].dropna(how="all")
            rm500qfr_one = rm500qfr_one.apply(lambda x: x.lstrip("DC_")).to_list()
            rm500qfr_two = rm500qfr["RM500Q-GL   EN-DC (2LTE + 1NR)"].dropna(how="all")
            rm500qfr_two = rm500qfr_two.apply(lambda x: x.lstrip("DC_")).to_list()
            rm500qfr_three = rm500qfr["RM500Q-GL   EN-DC  (3LTE + 1NR)"].dropna(
                how="all"
            )
            rm500qfr_three = rm500qfr_three.apply(lambda x: x.lstrip("DC_")).to_list()
            rm_fr = rm500qfr_one + rm500qfr_two + rm500qfr_three
            fr_bands = {
                "ATT": {
                    "TIS": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.att_tis
                    ],
                    "TRP": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.att_trp
                    ],
                },
                "TMO": {
                    "TIS": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.tmo_tis
                    ],
                    "TRP": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.tmo_trp
                    ],
                },
                "VZW": {
                    "TIS": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.vzw_tis
                    ],
                    "TRP": [
                        rm_fr[x] for x in range(len(rm_fr)) if rm_fr[x] in self.vzw_trp
                    ],
                },
            }

        return fr_bands

    def export(self, rb, sheetname):
        "Exporting the band combinations to the an excel sheet."

        att = pd.DataFrame.from_dict(rb["ATT"], orient="index")
        att = att.transpose()
        att.rename_axis(mapper="ATT", axis=0)
        tmo = pd.DataFrame.from_dict(rb["TMO"], orient="index")
        tmo = tmo.transpose()
        tmo.rename_axis(mapper="TMO", axis=0)
        vzw = pd.DataFrame.from_dict(rb["VZW"], orient="index")
        vzw = vzw.transpose()
        vzw.rename_axis(mapper="VZW", axis=0)
        bands = pd.concat(
            objs=[att, tmo, vzw], ignore_index=False, keys=["ATT", "TMO", "VZW"], axis=1
        )
        with pd.ExcelWriter(
            "Required CA-ENDC Band Combinations.xlsx",
            mode="a",
            if_sheet_exists="replace",
        ) as writer:
            bands.to_excel(
                excel_writer=writer,
                sheet_name=sheetname,
            )

    def fmat(self):
        self.export(self.test_bands(self.q.rm500q), "RM500Q")
        self.export(self.test_bands(self.q.rm502q), "RM502Q")
        self.export(self.test_bands(self.q.rm505q), "RM505Q")

        wb = load_workbook("Required CA-ENDC Band Combinations.xlsx")
        for sheet in wb.get_sheet_names():
            sheet.column_dimensions.width = 12
        wb.save("Required CA-ENDC Band Combinations.xlsx")


if __name__ == "__main__":
    r = RequiredBands()
    r.fmat()
