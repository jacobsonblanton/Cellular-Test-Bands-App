"This module is used for collecting and formatting the quectel CA band combinations for module."
import pandas as pd
from operator_bands import OperatorBands, OperatorBandsNR
from pprint import pprint


class QuectelBands:
    def __init__(self, file_path=None):
        """
        Initialize the QuectelBands class with the CA and NR combinations from an Excel file.
        """
        default_path = r"C:\Users\jblanton\Documents\Intertek\Required Bands CA-ENDC\Quectel_RM50xQ_Series_CA_EN-DC_Features_V1.6.xlsx"
        self.file_path = file_path if file_path else default_path

        # ✅ Define sheet-specific column mappings
        self.sheet_columns = {
            "RM500Q-GL": ["A", "F", "K", "R", "Y"],
            "RM502Q-AE": [
                "AE",
                "AL",
                "AS",
                "AZ",
                "BG",
                "BN",
                "BU",
            ],  # Different columns for NR bands
            "RM500Q-AE&RM505Q-AE": ["A", "F", "K", "R", "Y"],
        }

        # ✅ Load separate dataframes for CA (LTE) and NR (5G)
        self.ca_combos = self._load_data(self.sheet_columns.keys(), mode="CA")
        self.nr_combos = self._load_data(self.sheet_columns.keys(), mode="NR")

    def _load_data(self, sheets, mode="CA"):
        """
        Dynamically loads different columns depending on whether CA (LTE) or NR (5G) bands are being accessed.
        """
        data = {}

        # ✅ Load all sheet names and strip spaces to match dynamically
        sheet_mapping = {
            sheet.strip(): sheet for sheet in pd.ExcelFile(self.file_path).sheet_names
        }

        for sheet in sheets:
            try:
                # ✅ Match the sheet name dynamically
                if sheet.strip() not in sheet_mapping:
                    print(f"⚠️ Sheet '{sheet}' not found in Excel file.")
                    continue

                sheet_name = sheet_mapping[sheet.strip()]  # Ensure correct mapping

                # ✅ Load the first few rows to extract column names dynamically
                preview_df = pd.read_excel(
                    self.file_path, sheet_name=sheet_name, nrows=1
                )
                actual_columns = list(
                    preview_df.columns
                )  # Extract actual column headers

                # ✅ Auto-detect columns based on keywords
                if mode == "CA":
                    selected_columns = [
                        col for col in actual_columns if "CA" in col or "LTE" in col
                    ]
                elif mode == "NR":
                    selected_columns = [
                        col for col in actual_columns if "NR" in col or "EN-DC" in col
                    ]
                else:
                    selected_columns = (
                        actual_columns  # Default to all columns if mode is unknown
                    )

                # ✅ Load the actual data with identified column names
                data[sheet] = pd.read_excel(
                    self.file_path,
                    sheet_name=sheet_name,
                    usecols=selected_columns,  # ✅ Use dynamically selected columns
                    skiprows=[1, 2, 3],
                )

                print(f"✅ Loaded '{sheet}' with columns: {selected_columns}")

            except Exception as e:
                print(f"⚠️ Error loading sheet {sheet}: {e}")

        return data

    def clean_data(self, data: pd.DataFrame) -> dict:
        """
        Cleans the data by removing empty rows and formatting band names.
        """
        test_bands = {}
        for key in data.keys():
            bands = data[key].dropna(how="all").astype(str).tolist()
            test_bands[key] = [
                band.lstrip("CA_") if "CA_" in band else band for band in bands
            ]
        return test_bands

    def get_operator_bands(self, target_operator: str) -> dict:
        """
        Retrieves and cleans operator LTE band data.
        """
        return OperatorBands().clean_data(operator=target_operator)

    def get_operator_bands_NR(self, target_operator: str) -> dict:
        """
        Retrieves and cleans operator NR band data.
        """
        return OperatorBandsNR().clean_data(operator=target_operator)

    def test_combos(self, module: str, target_operator: str) -> dict:
        """
        Matches TRP and TIS bands from module data with the target operator's CA (LTE) and NR (5G) requirements.
        """
        if module not in self.ca_combos or module not in self.nr_combos:
            raise ValueError(f"Invalid module: {module}")

        # ✅ Retrieve Operator's CA (LTE) and NR (5G) bands
        ca_bands = self.get_operator_bands(target_operator)  # LTE bands
        nr_bands = self.get_operator_bands_NR(target_operator)  # NR bands

        # ✅ Retrieve Module's CA & NR Bands
        lte_bands = self.clean_data(self.ca_combos[module])
        nr_bands_module = self.clean_data(self.nr_combos[module])

        # ✅ Merge CA and NR Band Matching
        trp = [
            band
            for key in lte_bands
            for band in ca_bands["TRP"] + nr_bands["TRP"]  # Combine LTE + NR
            if band in lte_bands[key] or band in nr_bands_module.get(key, [])
        ]
        tis = [
            band
            for key in lte_bands
            for band in ca_bands["TIS"] + nr_bands["TIS"]  # Combine LTE + NR
            if band in lte_bands[key] or band in nr_bands_module.get(key, [])
        ]

        return {"TRP": sorted(set(trp)), "TIS": sorted(set(tis))}


if __name__ == "__main__":
    q = QuectelBands()
    print(q.test_combos("RM502Q-AE", "AT&T"))
    # print(q.test_combos("RM502Q-AE", "T-Mobile"))
