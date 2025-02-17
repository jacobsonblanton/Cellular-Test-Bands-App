"This module is for retrieving the Telit modules supported RF band combos."
import pandas as pd
from operator_bands import OperatorBands, OperatorBandsNR
from pprint import pprint
from os import path, getcwd


class Telit:
    def __init__(self) -> None:
        """
        Initialize the class and load CA & ENDC band combinations dynamically.
        """
        self.file_path = path.join(
            getcwd(), "30691NT12001A _FN990_Family_CA_ENDC_List_Rev.3_draft.xlsx"
        )
        self.ca_bands = self._load_ca_combos()
        self.endc_bands = self._load_endc_combos()

    def _load_ca_combos(self):
        """
        Loads the CA band combinations dynamically from 'Table 1'.
        """
        try:
            df = pd.read_excel(
                self.file_path,
                sheet_name="Table 1",
                usecols=[0],
                skiprows=lambda x: x in range(212),
            )  #  Load only first column
            df.columns = ["CA configuration"]  #  Rename to expected column name
            df = df.iloc[:1565]
            # Strip "CA_" prefix if present
            ca_bands = df.dropna()["CA configuration"].astype(str).tolist()
            ca_bands = [
                band.lstrip("CA_") if band.startswith("CA_") else band
                for band in ca_bands
            ]

            return ca_bands
        except Exception as e:
            print(f"⚠️ Error loading CA data: {e}")
            return []

    def _load_endc_combos(self):
        """
        Loads the ENDC band combinations from 'ENDC_Combos'.
        """
        try:
            df = pd.read_excel(
                self.file_path, sheet_name="ENDC_Combos", usecols=[0], skiprows=0
            )  #  Load only first column
            df.columns = ["EN-DC Combinations"]  #  Rename to expected column name
            return df.dropna()["EN-DC Combinations"].astype(str).tolist()
        except Exception as e:
            print(f"⚠️ Error loading ENDC data: {e}")
            return []

    def get_operator_bands(self, target_operator: str) -> dict:
        """
        Retrieves and cleans LTE band data from operator bands.
        """
        return OperatorBands().clean_data(operator=target_operator)

    def get_operator_bands_NR(self, target_operator: str) -> dict:
        """
        Retrieves and cleans NR band data from operator bands.
        """
        return OperatorBandsNR().clean_data(operator=target_operator)

    def test_combos(self, target_operator: str) -> dict:
        """
        Matches TRP and TIS bands from module data with the target operator's CA & ENDC requirements.
        """
        tis, trp = [], []

        # Retrieve operator's LTE & NR bands
        ca_bands = self.get_operator_bands(target_operator)  # LTE
        nr_bands = self.get_operator_bands_NR(target_operator)  # 5G NR

        # Match CA bands
        tis.extend([band for band in ca_bands["TIS"] if band in self.ca_bands])
        trp.extend([band for band in ca_bands["TRP"] if band in self.ca_bands])

        # Match ENDC bands (LTE + NR)
        tis.extend([band for band in nr_bands["TIS"] if band in self.endc_bands])
        trp.extend([band for band in nr_bands["TRP"] if band in self.endc_bands])

        return {"TRP": sorted(set(trp)), "TIS": sorted(set(tis))}


if __name__ == "__main__":
    t = Telit()
    pprint(t.test_combos(target_operator="AT&T"))
