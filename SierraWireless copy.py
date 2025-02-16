"This module is used for returning and formatting the seirra wireless CA and ENDC band combos."
import pandas as pd
from operator_bands import OperatorBands, OperatorBandsNR


class SierraBands:
    def __init__(self) -> None:
        """
        Initialize the class and load CA & ENDC band combinations dynamically.
        """
        self.file_path = "SWIX55C_03.09.11.00_EM9191_1007_LE_1.4_rfcombos.xlsx"
        self.ca_combos = self._load_data(sheet_name="RFCOMBOS", mode="CA")
        self.endc_combos = self._load_data(sheet_name="RFC_format sub-6", mode="ENDC")

        self.swix55c_ca_bands = self.extract_ca_combos()
        self.swix55c_endc_bands = self.extract_endc_combos()

    def _load_data(self, sheet_name: str, mode: str):
        """
        Loads the CA or ENDC band combinations dynamically with different row skips.
        """
        try:
            # ✅ Conditional row skipping for CA and ENDC
            skip_rows = [0, 1, 2] if mode == "CA" else [0, 1, 2, 3]

            if mode == "ENDC":
                df = pd.read_excel(
                    self.file_path,
                    sheet_name=sheet_name,
                    usecols=["3gpp combo (short format)"],
                    skiprows=skip_rows,
                )
            else:
                df = pd.read_excel(
                    self.file_path, sheet_name=sheet_name, skiprows=skip_rows
                )

            return df.dropna(how="all")  # ✅ Remove empty rows

        except Exception as e:
            print(f"⚠️ Error loading sheet '{sheet_name}': {e}")
            return pd.DataFrame()

    def extract_ca_combos(self) -> list:
        """
        Extracts CA (Carrier Aggregation) band combinations.
        """
        ca_bands = set()
        for column in self.ca_combos.columns:
            ca_bands.update(self.ca_combos[column].dropna().astype(str).tolist())

        # ✅ Keep "CA_" prefix to distinguish LTE CA bands
        cleaned_ca_bands = [
            band.lstrip("CA_") if "CA_" in band else band for band in ca_bands
        ]
        return sorted(cleaned_ca_bands)

    def extract_endc_combos(self) -> list:
        """
        Extracts ENDC (LTE + NR) band combinations from '3gpp combo (short format)' column.
        """
        return sorted(self.endc_combos["3gpp combo (short format)"].tolist())

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

        # ✅ Retrieve operator's LTE & NR bands
        ca_bands = self.get_operator_bands(target_operator)  # LTE
        nr_bands = self.get_operator_bands_NR(target_operator)  # 5G NR

        # ✅ Match CA bands
        tis.extend([band for band in ca_bands["TIS"] if band in self.swix55c_ca_bands])
        trp.extend([band for band in ca_bands["TRP"] if band in self.swix55c_ca_bands])

        # ✅ Match ENDC bands (LTE + NR)
        tis.extend(
            [band for band in nr_bands["TIS"] if band in self.swix55c_endc_bands]
        )
        trp.extend(
            [band for band in nr_bands["TRP"] if band in self.swix55c_endc_bands]
        )

        return {"TRP": sorted(set(trp)), "TIS": sorted(set(tis))}


if __name__ == "__main__":
    s = SierraBands()
    print(s.test_combos("AT&T"))
