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

    def remove_invalid_combos(self, trp: list, tis: list, target_operator: str) -> dict:
        """
        Removes invalid band combinations based on CTIA operator-specific rules.
        """
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

        if target_operator in removal_rules:
            for category in ["TRP", "TIS"]:
                if category == "TRP":
                    bands_list = trp  # Ensure TRP list is updated
                else:
                    bands_list = tis  # Ensure TIS list is updated

                to_remove = (
                    set()
                )  # Track items to remove instead of modifying the list during iteration

                #  FIRST: Collect bands that need to be removed
                for primary, secondaries in removal_rules[target_operator].get(
                    category, []
                ):
                    if primary in bands_list:  # Check if primary exists in TRP or TIS
                        for secondary in (
                            secondaries
                            if isinstance(secondaries, list)
                            else [secondaries]
                        ):
                            if (
                                secondary in bands_list
                            ):  #  Ensure secondary exists before removing primary
                                #  Add Debugging Output
                                print(
                                    f"🔎 Checking Rule: If {secondary} exists, remove {primary}"
                                )
                                print(f"📋 Before Removal: {bands_list}")
                                to_remove.add(primary)
                                print(f"🗑️ To Remove: {to_remove}")

                # SECOND: Remove the collected items in a separate step
                bands_list[:] = [band for band in bands_list if band not in to_remove]

        return {
            "TRP": trp,
            "TIS": tis,
        }  #  Ensures modified TRP & TIS lists are returned

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

        print(f"🔍 Extracted EN-DC TRP Bands: {endc_trp}")
        print(f"🔍 Extracted EN-DC TIS Bands: {endc_tis}")

        # ✅ Remove invalid CA combos (without losing EN-DC bands)
        filtered_bands = self.remove_invalid_combos(
            matched_bands["TRP"], matched_bands["TIS"], target_operator
        )
        return filtered_bands

        print(f"🟢 TRP After CA Filtering: {filtered_bands['TRP']}")
        print(f"🟢 TIS After CA Filtering: {filtered_bands['TIS']}")

        # ✅ Remove invalid EN-DC combos
        filtered_endc = self.remove_invalid_combos_endc(
            filtered_bands["TRP"], filtered_bands["TIS"], target_operator
        )

        print(f"🔴 TRP After EN-DC Filtering: {filtered_endc['TRP']}")
        print(f"🔴 TIS After EN-DC Filtering: {filtered_endc['TIS']}")

        # ✅ Ensure EN-DC Bands Are Re-Added After Filtering
        final_trp = sorted(set(filtered_endc["TRP"]) | endc_trp)
        final_tis = sorted(set(filtered_endc["TIS"]) | endc_tis)

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
    # q = QuectelBands()
    # pprint(q.test_combos("RM500Q-GL", "AT&T"))
    pprint(req.test_combos("Quectel", "RM500Q-GL", "AT&T"))
    # # pprint(req.remove_invalid_combos_endc())
