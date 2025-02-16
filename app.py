import tkinter as tk
import ttkbootstrap as tb
import pandas as pd
from tkinter import filedialog
from required_test_bands import RequiredTestBands


class Dataframe(tb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True, fill="both", padx=10, pady=10)

        # Label: Select Module Family
        tb.Label(self, text="Select Module Family:", font=("Arial", 12)).pack(
            padx=5, pady=5
        )

        # Dropdown: Module Family Selection
        self.module_family_var = tk.StringVar()
        self.module_family_dropdown = tb.Combobox(
            self, textvariable=self.module_family_var, state="readonly"
        )
        self.module_family_dropdown["values"] = ("Quectel", "Telit", "Sierra Wireless")
        self.module_family_dropdown.pack(expand=True, fill="both", padx=5, pady=5)
        self.module_family_dropdown.bind(
            "<<ComboboxSelected>>", self.update_model_dropdown
        )

        # Label: Select Module Model
        tb.Label(self, text="Select Module Model:", font=("Arial", 12)).pack(
            padx=5, pady=5
        )

        # Dropdown: Module Model Selection (Populated Dynamically)
        self.model_var = tk.StringVar()
        self.model_dropdown = tb.Combobox(
            self, textvariable=self.model_var, state="readonly"
        )
        self.model_dropdown.pack(expand=True, fill="both", padx=5, pady=5)

        # Label: Select Target Operator
        tb.Label(self, text="Select Target Operator:", font=("Arial", 12)).pack(
            padx=5, pady=5
        )

        # Dropdown: Target Operator Selection
        self.operator_var = tk.StringVar()
        self.operator_dropdown = tb.Combobox(
            self, textvariable=self.operator_var, state="readonly"
        )
        self.operator_dropdown["values"] = ("AT&T", "Verizon", "T-Mobile")
        self.operator_dropdown.pack(expand=True, fill="both", padx=5, pady=5)
        self.operator_dropdown.current(0)  # Default to AT&T

        # Export Button
        self.export_button = tb.Button(
            self, text="Export Test Bands", command=self.export_data
        )
        self.export_button.pack(fill="both", expand=True, padx=10, pady=10)

        # Status Label
        self.status_label = tb.Label(
            self, text="", font=("Arial", 10), bootstyle="info"
        )
        self.status_label.pack(padx=5, pady=5)

    def update_model_dropdown(self, event=None):
        """Dynamically updates the model dropdown based on selected module family."""
        module_family = self.module_family_var.get()

        # Define model options per module family
        model_options = {
            "Quectel": ["RM500Q-GL", "RM502Q-AE", "RM500Q-AE&RM505Q-AE"],
            "Telit": ["FN980", "FN990", "LE910C1"],
            "Sierra Wireless": ["EM9190", "EM9191", "WP7607"],
        }

        # Update model dropdown values
        if module_family in model_options:
            self.model_dropdown["values"] = model_options[module_family]
            self.model_dropdown.current(0)  # Select first model by default
        else:
            self.model_dropdown["values"] = ()
            self.model_var.set("")

    def export_data(self):
        """Retrieves test bands and exports them to an Excel file."""
        module_family = self.module_family_var.get()
        model = self.model_var.get()
        carrier = self.operator_var.get()  # Get selected target operator

        if not module_family or not model or not carrier:
            self.status_label.config(
                text="⚠️ Please select all fields!", bootstyle="danger"
            )
            return

        req = RequiredTestBands()
        test_bands = req.test_combos(module_family, model, carrier)

        if not test_bands:
            self.status_label.config(text="❌ No test bands found!", bootstyle="danger")
            return

        # Ensure DataFrame is properly structured before exporting
        df = pd.DataFrame.from_dict(test_bands, orient="index").transpose()

        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"{module_family}_{model}_{carrier}_Test_Bands.xlsx",
        )

        if filename:  # Save only if user selects a file
            df.to_excel(filename, index=False)
            self.status_label.config(
                text=f"✅ Data exported successfully!", bootstyle="success"
            )


class App(tb.Window):
    def __init__(self, title="Cellular Test Bands Exporter", themename="superhero"):
        super().__init__(title, themename)
        self.geometry("400x400")  # Increased height to fit new operator dropdown
        self.container = tb.Frame(self)
        self.container.pack(expand=True, fill="both")
        Dataframe(self.container)


if __name__ == "__main__":
    app = App()
    app.mainloop()
