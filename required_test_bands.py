"This module is for returning the required testing bands for module provided."
import pandas as pd
from operator_bands import OperatorBands, OperatorBandsNR
from Quectel import QuectelBands
from SierraWireless import SierraBands
from Telit import Telit
import json
import importlib
from pprint import pprint


class RequiredTestBands:
    "This is a class for providing methods and functions related to retrieving the required bands for testing for the given module."

    def __init__(self) -> None:
        self.modules = self.load_modules() or {}
        self.data = None

    def load_modules(self) -> dict:
        """
        Loads cellular module classes dynamically based on config.json.
        """
        try:
            with open(
                r"C:\Users\jblanton\Documents\Intertek\Required Bands CA-ENDC\config.json",
                "r",
            ) as config_file:
                config = json.load(config_file)

            modules = {}
            for module_name, class_path in config["modules"].items():
                try:
                    module_name, class_name = class_path.rsplit(".", 1)
                    print(f"Loading {module_name}.{class_name}...")  # Debugging
                    module = importlib.import_module(module_name)
                    modules[module_name] = getattr(module, class_name)()
                except Exception as e:
                    print(f"Error loading module {module_name}: {e}")

            return modules
        except FileNotFoundError:
            print("Error: config.json file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: config.json is not properly formatted.")
            return {}

    # def get_data(self, target_operator: str | None) -> dict:
    #     self.data = OperatorBands().clean_data(operator=target_operator)
    #     return self.data

    def _normalize_bands(self, band_list):
        """
        Converts all band names to a consistent format (hyphens instead of underscores).
        """
        return [band.replace("_", "-") for band in band_list]

    def _process_removal(self, band_list, category, removal_rules):
        """
        Ensures multiple passes of filtering to completely remove invalid bands.
        """
        dependency_map = {}

        # Step 1: Build dependency map {primary: [list of secondaries]}
        for primary, secondaries in removal_rules.get(category, []):
            if not isinstance(secondaries, list):
                secondaries = [secondaries]
            dependency_map[primary] = secondaries

        removed = True  # Flag to continue iterating if something was removed
        while removed:
            removed = False
            to_remove = set()

            for primary, secondaries in dependency_map.items():
                if primary in band_list and any(
                    sec in band_list for sec in secondaries
                ):
                    print(
                        f"🗑 Removing '{primary}' because superior band exists: {secondaries}"
                    )
                    to_remove.add(primary)
                    removed = True  # Continue iteration if we remove anything

            band_list[:] = [band for band in band_list if band not in to_remove]

        return band_list

    def remove_invalid_combos(self, trp: list, tis: list, target_operator: str) -> dict:
        """
        Removes invalid band combinations based on CTIA operator-specific rules.
        """

        trp = self._normalize_bands(trp)
        tis = self._normalize_bands(tis)

        removal_rules = {
            "AT&T": {
                "TRP": [
                    ("2A-4A", "2A-66A"),
                    ("2A-66A", "2A-12A-66A"),
                    ("4A-5A", "66A-5A"),
                    ("4A-12A", "66A-12A"),
                    ("2A-4A-5A", "2A-5A-66A"),
                    ("2A-4A-12A", "2A-12A-66A"),
                    ("4A-12A-30A", "66A-12A-30A"),
                    ("2A-5A", ["2A-5A-30A", "2A-4A-5A", "2A-5A-66A"]),
                    ("2A-12A", ["2A-12A-30A", "2A-4A-12A", "2A-12A-66A"]),
                    ("4A-12A", ["4A-12A-30A", "66A-12A-30A"]),
                ],
                "TIS": [
                    ("2A-12A", "2A-12A-30A"),
                    ("2A-29A", "2A-29A-30A"),
                    ("2A-30A", ["2A-12A-30A", "2A-29A-30A"]),
                    ("2A-4A-12A", "2A-12A-66A"),
                    ("2A-4A-5A", "2A-5A-66A"),
                ],
            },
            "T-Mobile": {
                "TRP": [
                    ("66A-12A", "66A-12A-66A"),
                    ("12A-66A", "12A-66A-66A"),
                    ("2A-12A", "2A-12A-66A"),
                    ("12A-2A", "12A-2A-66A"),
                    ("2A-66A", "2A-66A-66A"),
                    ("66A-2A", "66A-2A-66A"),
                    ("66A-66A", ["66A-12A-66A", "66A-2A-66A"]),
                ],
                "TIS": [
                    ("66A-12A", "66A-12A-66A"),
                    ("66A-2A", ["66A-2A-12A", "66A-2A-66A", "66A-2A-2A"]),
                    ("66A-66A", ["66A-2A-66A", "66A-12A-66A"]),
                    ("12A-2A", ["12A-2A-66A", "12A-2A-2A"]),
                    ("2A-12A", "2A-12A-66A"),
                ],
            },
            "Verizon": {
                "TRP": [
                    ("2A-4A", "2A-66A"),
                    ("4A-2A", "66A-2A"),
                    ("2A-13A", ["2A-4A-13A", "2A-13A-66A"]),
                    ("13A-2A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("4A-13A", "66A-13A"),
                    ("4A-13A", ["4A-2A-13A", "66A-2A-13A"]),
                    ("66A-13A", ["4A-2A-13A", "66A-2A-13A"]),
                    ("13A-4A", "13A-66A"),
                    ("13A-4A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("13A-66A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("2A-5A", ["2A-4A-5A", "2A-5A-66A"]),
                    ("5A-2A", ["5A-2A-4A", "5A-2A-66A"]),
                    ("4A-5A", "66A-5A"),
                    ("4A-5A", ["5A-2A-4A", "5A-2A-66A"]),
                    ("66A-5A", ["5A-2A-4A", "5A-2A-66A"]),
                    ("5A-4A", "5A-66A"),
                    ("5A-4A", ["5A-2A-4A", "5A-2A-66A"]),
                    ("5A-66A", ["5A-2A-4A", "5A-2A-66A"]),
                    ("2A-48A", "2A-48A-66A"),
                    ("48A-2A", "48A-2A-66A"),
                    ("13A-48A", "13A-48A-66A"),
                    ("48A-13A", "48A-13A-66A"),
                    ("48A-66A", ["48A-2A-66A", "48A-13A-66A"]),
                    ("66A-48A", ["66A-2A-48A", "66A-13A-48A"]),
                ],
                "TIS": [
                    ("13A-4A", "13A-66A"),
                    ("13A-4A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("13A-66A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("2A-4A", "2A-66A"),
                    ("2A-4A", ["2A-5A-4A", "2A-5A-66A"]),
                    ("2A-66A", ["2A-5A-4A", "2A-5A-66A"]),
                    ("13A-2A", ["13A-2A-4A", "13A-2A-66A"]),
                    ("2A-5A", ["2A-4A-5A", "2A-5A-66A"]),
                    ("13A-48A", "13A-48A-66A"),
                    ("66A-48A", "66A-2A-48A"),
                ],
            },
        }

        if target_operator not in removal_rules:
            return {"TRP": trp, "TIS": tis}

        # Apply filtering to TRP and TIS separately
        trp_filtered = self._process_removal(trp, "TRP", removal_rules[target_operator])
        tis_filtered = self._process_removal(tis, "TIS", removal_rules[target_operator])

        return {"TRP": trp_filtered, "TIS": tis_filtered}

    def remove_invalid_combos_endc(
        self, trp: list, tis: list, target_operator: str
    ) -> dict:
        """
        Removes invalid EN-DC band combinations based on CTIA operator-specific rules.
        Ensures that only valid EN-DC bands are removed.
        """
        endc_removal_rules = {
            "AT&T": {
                "TRP": [
                    ("DC_2A_n5A", "DC_2A_n5A_n30A"),
                    ("DC_2A_n66A", "DC_2A_n66A_n5A"),
                    ("DC_12A_n77A", ["DC_12A_n77A_n2A", "DC_12A_n77A_n66A"]),
                    ("DC_30A_n2A", "DC_30A_n2A_n66A"),
                ],
                "TIS": [
                    ("DC_2A_n30A", ["DC_2A_n30A_n5A", "DC_2A_n30A_n66A"]),
                    ("DC_5A_n2A", ["DC_5A_n2A_n30A"]),
                    ("DC_66A_n30A", ["DC_66A_n30A_n12A", "DC_66A_n30A_n5A"]),
                ],
            },
            "T-Mobile": {
                "TRP": [
                    ("DC_66A_n30A", "DC_66A_n30A_n66A"),
                    ("DC_2A_n66A", ["DC_2A_n66A_n30A", "DC_2A_n66A_n5A"]),
                    ("DC_12A_n77A", ["DC_12A_n77A_n5A"]),
                ],
                "TIS": [
                    ("DC_5A_n2A", ["DC_5A_n2A_n30A", "DC_5A_n2A_n66A"]),
                    ("DC_12A_n77A", "DC_12A_n77A_n2A"),
                ],
            },
            "Verizon": {
                "TRP": [
                    ("DC_2A_n5A", "DC_2A_n5A_n66A"),
                    ("DC_12A_n2A", ["DC_12A_n2A_n30A"]),
                    ("DC_30A_n66A", "DC_30A_n66A_n5A"),
                ],
                "TIS": [
                    ("DC_12A_n77A", "DC_12A_n77A_n66A"),
                    ("DC_66A_n30A", ["DC_66A_n30A_n2A", "DC_66A_n30A_n5A"]),
                ],
            },
        }

        # ✅ Required EN-DC Test Bands for Each Operator
        valid_endc_bands = {
            "AT&T": {
                "TRP": {
                    "DC_2A_n5A",
                    "DC_2A_n30A",
                    "DC_5A_n2A",
                    "DC_5A_n30A",
                    "DC_12A_n2A",
                    "DC_12A_n30A",
                    "DC_14A_n30A",
                    "DC_30A_n2A",
                    "DC_30A_n5A",
                    "DC_30A_n66A",
                    "DC_66A_n30A",
                    "DC_2A_n66A",
                    "DC_2A_n12A",
                    "DC_2A_n29A",
                    "DC_2A_n14A",
                    "DC_14A_n66A",
                    "DC_66A_n260A",
                },
                "TIS": {
                    "DC_2A_n5A",
                    "DC_2A_n30A",
                    "DC_5A_n2A",
                    "DC_5A_n30A",
                    "DC_12A_n2A",
                    "DC_12A_n30A",
                    "DC_12A_n77A",
                    "DC_14A_n30A",
                    "DC_30A_n2A",
                    "DC_30A_n5A",
                    "DC_30A_n66A",
                    "DC_66A_n30A",
                    "DC_2A_n66A",
                    "DC_2A_n12A",
                    "DC_2A_n14A",
                    "DC_12A_n66A",
                    "DC_14A_n66A",
                    "DC_66A_n260A",
                },
            },
            "T-Mobile": {
                "TRP": {
                    "DC_2A_n41A",
                    "DC_66A_n41A",
                    "DC_2A_n71A",
                    "DC_66A_n71A",
                    "DC_66A_n25A",
                    "DC_2A_n66A",
                    "DC_66A_n258A",
                    "DC_66A_n260A",
                },
                "TIS": {
                    "DC_2A_n41A",
                    "DC_66A_n41A",
                    "DC_2A_n71A",
                    "DC_66A_n71A",
                    "DC_2A_n66A",
                    "DC_66A_n258A",
                    "DC_66A_n260A",
                },
            },
            "Verizon": {
                "TRP": {
                    "DC_2A_n5A",
                    "DC_13A_n2A",
                    "DC_13A_n5A",
                    "DC_13A_n66A",
                    "DC_48A_n5A",
                    "DC_2A_n77A",
                    "DC_13A_n77A",
                    "DC_66A_n77A",
                    "DC_66A_n260A",
                    "DC_66A_n261A",
                },
                "TIS": {
                    "DC_2A_n5A",
                    "DC_13A_n2A",
                    "DC_13A_n5A",
                    "DC_13A_n66A",
                    "DC_48A_n5A",
                    "DC_2A_n77A",
                    "DC_13A_n77A",
                    "DC_66A_n77A",
                    "DC_66A_n260A",
                    "DC_66A_n261A",
                },
            },
        }

        # ✅ Ensure the target operator is in the rules
        if target_operator in endc_removal_rules:
            for category in ["TRP", "TIS"]:
                bands_list = trp if category == "TRP" else tis
                to_remove = set()

                # ✅ First Pass: Identify Bands to Remove (Only If Primary & Secondary Exist)
                for primary, secondaries in endc_removal_rules[target_operator].get(
                    category, []
                ):
                    if primary in bands_list:
                        for secondary in (
                            secondaries
                            if isinstance(secondaries, list)
                            else [secondaries]
                        ):
                            if secondary in bands_list:
                                print(
                                    f"🔎 Marking {primary} for removal because {secondary} exists"
                                )
                                to_remove.add(primary)

                # ✅ Second Pass: Remove Marked Bands
                bands_list[:] = [band for band in bands_list if band not in to_remove]
                print(f"✅ After Removal ({category}): {bands_list}")

        return {"TRP": trp, "TIS": tis}

    def test_combos(self, module_family: str, model: str, target_operator: str) -> dict:
        """
        Retrieves valid test bands for the selected module family and model.
        Ensures EN-DC bands are included in the final output.
        """
        if module_family not in self.modules:
            print(f"❌ Error: Module family '{module_family}' not found.")
            return {}

        module_instance = self.modules.get(module_family)
        # 🔥 Debugging: Check if module_instance is found
        if module_instance is None:
            print(
                f"❌ Error: Module family '{module_family}' not found in self.modules"
            )
            return {}

        print(f"✅ Module Instance Found: {module_family}")

        # ✅ Get test bands from Quectel/SierraWireless/Telit
        matched_bands = module_instance.test_combos(model, target_operator)

        # 🔥 Debugging: Check raw output before filtering
        print(f"🔥 Matched Bands Before Any Processing: {matched_bands}")

        if not matched_bands:
            print(f"⚠️ Warning: No test bands found for {module_family} - {model}.")
            return {}

        print(f"🔥 Matched Bands from Module: {matched_bands}")  # Debugging

        # ✅ Separate EN-DC bands before filtering
        endc_trp = {band for band in matched_bands["TRP"] if "DC" in band}
        endc_tis = {band for band in matched_bands["TIS"] if "DC" in band}

        ca_trp = set(matched_bands["TRP"]) - endc_trp
        ca_tis = set(matched_bands["TIS"]) - endc_tis

        print(f"🔍 Extracted EN-DC TRP Bands: {endc_trp}")
        print(f"🔍 Extracted EN-DC TIS Bands: {endc_tis}")
        print(f"🔍 Extracted CA TRP Bands: {ca_trp}")
        print(f"🔍 Extracted CA TIS Bands: {ca_tis}")

        # ✅ Step 2: Filter CA bands separately
        filtered_ca = self.remove_invalid_combos(
            list(ca_trp), list(ca_tis), target_operator
        )
        return filtered_ca
        filtered_trp = filtered_ca["TRP"]
        filtered_tis = filtered_ca["TIS"]

        print(f"🟢 TRP After CA Filtering: {filtered_trp}")
        print(f"🟢 TIS After CA Filtering: {filtered_tis}")

        # ✅ Step 3: Filter EN-DC bands separately
        filtered_endc = self.remove_invalid_combos_endc(
            list(endc_trp), list(endc_tis), target_operator
        )

        print(f"🔴 TRP After EN-DC Filtering: {filtered_endc['TRP']}")
        print(f"🔴 TIS After EN-DC Filtering: {filtered_endc['TIS']}")

        # ✅ Step 4: Merge the separately filtered CA & EN-DC bands
        final_trp = sorted(set(filtered_trp) | set(filtered_endc["TRP"]))  # Merge
        final_tis = sorted(set(filtered_tis) | set(filtered_endc["TIS"]))

        print(f"✅ Final TRP Bands: {final_trp}")
        print(f"✅ Final TIS Bands: {final_tis}")

        return {"TRP": final_trp, "TIS": final_tis}

    def export_to_excel(self, module_family: str, model: str, target_operator: str):
        """
        Exports the required test bands for the selected module family and model to an Excel file.
        """
        test_bands = self.test_combos(module_family, model, target_operator)

        if not test_bands:
            print(f"No data to export for {module_family} - {model}.")
            return

        # Convert to Pandas DataFrame
        df = pd.DataFrame(test_bands)

        # Save to Excel with a structured filename
        filename = f"{module_family}_{model}_Test_Bands.xlsx"
        df.to_excel(filename, index=False)

        print(f"✅ Data exported successfully to {filename}")


if __name__ == "__main__":
    req = RequiredTestBands()
    pprint(req.test_combos("Quectel", "RM500Q-GL", "AT&T"))
