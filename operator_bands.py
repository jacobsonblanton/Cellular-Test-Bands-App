"This module is for storing the non-essential and essential operator bands. "
import pandas as pd
import re
from pprint import pprint


class OperatorBands:
    def __init__(self, file_path=None):
        """
        Initialize the OperatorBands class with an optional custom file path.
        """
        default_path = r"C:\Users\jblanton\Documents\Intertek\Required Bands CA-ENDC\CTIA-01.02-Operator-Priority-List-V4.0.1.xlsx"
        self.file_path = file_path if file_path else default_path

        self.ca_df = pd.read_excel(
            io=self.file_path,
            sheet_name="NonEssential High Priority",
            usecols="B,D:F",
            skiprows=[0, 1, 2, 3, 67, 68, 69, 70, 71],
        )

        self.tis_ca_df = self.ca_df.iloc[:22]
        self.trp_ca_df = self.ca_df.iloc[34:62]

        self.trp_bands = self.trp_ca_df.to_dict("list")
        self.tis_bands = self.tis_ca_df.to_dict("list")

    def _clean_band_name(self, band_name: str) -> str:
        """
        Helper function to clean and normalize band names.
        """
        if not isinstance(band_name, str):
            return band_name

        # Replace "_" with "-" for standardization
        band_name = band_name.replace("_", "-")

        # Split bands if "or" exists
        band_parts = band_name.split(" or ")

        cleaned_bands = []
        for part in band_parts:
            # Extract only the valid band structure: e.g., "2A-12A", "2A-30A"
            match = re.search(r"([0-9A-]+A)(?:\d*,?\d*)?", part)
            if match:
                cleaned_bands.append(match.group(1))

        return (
            cleaned_bands if len(cleaned_bands) > 1 else cleaned_bands[0]
        )  # Ensure output consistency

    def _process_bands(self, bands: dict, operator: str) -> list:
        """
        Helper function to clean all band values for a given operator.
        """
        if operator not in bands:
            return []

        cleaned_band_list = []
        for band in bands[operator]:
            if isinstance(band, str):
                cleaned_band = self._clean_band_name(band)
                if isinstance(cleaned_band, list):
                    cleaned_band_list.extend(
                        cleaned_band
                    )  # Ensure each band is a separate list item
                else:
                    cleaned_band_list.append(cleaned_band)

        return cleaned_band_list

    def clean_data(self, operator: str) -> dict:
        """
        Cleans and formats operator band data for TIS and TRP.
        """
        return {
            "TIS": self._process_bands(self.tis_bands, operator),
            "TRP": self._process_bands(self.trp_bands, operator),
        }


class OperatorBandsNR:
    def __init__(self, file_path=None):
        """
        Initialize the OperatorBandsNR class with an optional custom file path.
        """
        default_path = r"C:\Users\jblanton\Documents\Intertek\Required Bands CA-ENDC\CTIA-01.02-Operator-Priority-List-V4.0.1.xlsx"
        self.file_path = file_path if file_path else default_path

        self.nr_df = pd.read_excel(
            io=self.file_path,
            sheet_name="NonEssential High Priority",
            usecols="H,J:L",
            skiprows=[0, 1, 2, 3, 67, 68, 69, 70, 71],
        )

        self.tis_nr_df = self.nr_df.iloc[:17]
        self.trp_nr_df = self.nr_df.iloc[33:57]

        self.tis_bands = self.tis_nr_df.to_dict("list")
        self.trp_bands = self.trp_nr_df.to_dict("list")

    def _clean_band_name(self, band_name: str) -> list:
        """
        Cleans and normalizes LTE & NR band names:
        - Keeps `-` for LTE bands and `_n` for NR bands.
        - Ensures correct `_nXXA` formatting for NR bands.
        - Removes unwanted trailing numbers after `A`.
        """
        if not isinstance(band_name, str):
            return [band_name]  # Ensure return is always a list

        # ✅ Print original band before cleaning (for debugging)
        print(f"🔎 Original Band: {band_name}")

        # ✅ Remove spaces, superscripts (¹,²,³), and extra underscores
        band_name = re.sub(r"\s+", "", band_name)
        band_name = re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]", "", band_name)  # Remove superscripts
        band_name = re.sub(r"_+", "_", band_name)  # Fix multiple underscores

        # ✅ Ensure 'DC_' prefix
        if not band_name.startswith("DC_"):
            band_name = "DC_" + band_name.lstrip("DC_")

        # ✅ Fix LTE + NR format (Ensure LTE parts `-XXA` remain before `_nXXA`)
        band_name = re.sub(
            r"(\d+A(?:-\d+A)*)-n?(\d+A)", r"\1_n\2", band_name
        )  # Convert `-nXXA` into `_nXXA`

        # ✅ Remove trailing numbers **ONLY AFTER** `_nXXA` or `A`
        band_name = re.sub(r"([0-9A_-]+A)(_n[0-9A]+A)?\d+$", r"\1\2", band_name)

        # ✅ Ensure full valid LTE/NR band name extraction
        match = re.search(r"DC_[0-9A_-]+A(_n[0-9A]+A)?", band_name)

        if match:
            main_band = match.group(0)

            # ✅ Print cleaned band after regex extraction
            print(f"✅ Processed Band: {main_band}")

            return [main_band]

        # ✅ Print fallback band if regex fails
        print(f"⚠️ No Match Found, Returning: {band_name}")
        return [band_name]

    def _process_bands(self, bands: dict, operator: str) -> list:
        """
        Processes and cleans a list of bands.
        """
        operator_mapping = {
            "AT&T": "AT&T.1",
            "T-Mobile": "T-Mobile.1",
            "Verizon": "Verizon4",
            "US Cellular": "US Cellular.1",
        }
        normalized_operator = operator_mapping.get(operator, operator)

        if normalized_operator not in bands:
            print(
                f"⚠️ Operator '{operator}' not found in dataset. Available keys: {bands.keys()}"
            )
            return []

        cleaned_bands = set()
        for band in bands[normalized_operator]:
            if isinstance(band, str):
                if (
                    band in operator_mapping
                ):  # ✅ Ensure operator names are not treated as bands
                    print(f"⚠️ Skipping Operator Name: {band}")
                    continue

                print(f"🔎 Processing Band: {band}")  # ✅ Print before cleaning

                cleaned_band = self._clean_band_name(band)

                for item in cleaned_band:
                    print(f"✅ Cleaned Band: {item}")  # ✅ Print after cleaning
                    cleaned_bands.add(item)

        print(f"🔥 Final Cleaned Bands List: {sorted(cleaned_bands)}")
        return sorted(cleaned_bands)

    def clean_data(self, operator: str) -> dict:
        """
        Cleans and formats operator band data for TIS and TRP (NR).
        """
        return {
            "TIS": self._process_bands(self.tis_bands, operator),
            "TRP": self._process_bands(self.trp_bands, operator),
        }


if __name__ == "__main__":
    op = OperatorBands()
    opnr = OperatorBandsNR()
    # pprint(op.clean_data("AT&T"))
    pprint(opnr.clean_data("AT&T"))
    # pprint(opnr.tis_bands)
    # pprint(opnr.trp_bands)
