"This module is used to load and format the required bands from the carrier module manufacturer datasheets."

import pandas as pd
import os
import py2exe
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
from quectel_modules import RM500Q_GL
from operator_priority import OperatorPriorityList

oper = OperatorPriorityList()
rm500 = RM500Q_GL()


class RequiredBands(object):
    "A class that will retrieve and store all requied testing bands per carrier and module manufacturer."

    def __init__(self) -> None:
        self.att_tis = oper.att_ca_tis_trp()["TIS"]
        self.att_trp = oper.att_ca_tis_trp()["TRP"]
        self.tmo_tis = oper.tmo_ca_tis_trp()["TIS"]
        self.tmo_trp = oper.tmo_ca_tis_trp()["TRP"]
        self.vzw_tis = oper.vzw_ca_tis_trp()["TIS"]
        self.vzw_trp = oper.vzw_ca_tis_trp()["TRP"]
        self.rm500 = rm500.rm500q_gl_bands

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

    def quectel_rm500q_gl_bands(self) -> dict:
        "returning the required NON-ESSENTIAL testing bands for the quectel rm500g_gxl"
        rm = self.rm500
        att_tis = self.clean_data(self.att_tis)
        att_trp = self.clean_data(self.att_trp)
        tmo_tis = self.clean_data(self.tmo_tis)
        tmo_trp = self.clean_data(self.tmo_trp)
        vzw_tis = self.clean_data(self.vzw_tis)
        vzw_trp = self.clean_data(self.vzw_trp)

        rm_ca = rm["2CA"] + rm["3CA"]
        test_bands = {
            "ATT": {
                "TIS": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in att_tis],
                "TRP": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in att_trp],
            },
            "TMO": {
                "TIS": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in tmo_tis],
                "TRP": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in tmo_trp],
            },
            "VZW": {
                "TIS": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in vzw_tis],
                "TRP": [rm_ca[x] for x in range(len(rm_ca)) if rm_ca[x] in vzw_trp],
            },
        }
        return test_bands

    def export_data(self) -> None:
        "Exporting the band combinations to the an excel sheet."
        rb = self.quectel_rm500q_gl_bands()
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

        bands.to_excel(
            excel_writer="Required CA-ENDC Band Combinations.xlsx",
            sheet_name="Quectel Modems",
        )
