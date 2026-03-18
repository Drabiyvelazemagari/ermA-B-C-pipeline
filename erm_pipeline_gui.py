import sys
import os
import pandas as pd

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QLineEdit, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal


# =========================
# PIPELINE LOGIC (same as before)
# =========================

def normalize(acc):
    return acc.split(".")[0] if isinstance(acc, str) else acc


def run_pipeline(mge_path, is_db_path, members_path, cds_path, out_dir, out_name, log):

    if not all([mge_path, is_db_path, members_path, cds_path, out_dir, out_name]):
        raise ValueError("Please provide all input files, output directory, and output name.")

    def step(msg):
        log(msg)

    try:
        # =========================
        # LOAD FILES
        # =========================
        step("[1/9] Loading files...")

        mge = pd.read_csv(mge_path)
        is_db = pd.read_csv(is_db_path)
        members = pd.read_csv(members_path, sep="\t")
        cds = pd.read_csv(cds_path, sep="\t")

        # =========================
        # VALIDATION
        # =========================
        step("[2/9] Validating inputs...")

        required_mge = ["accession", "start", "end", "name", "type"]
        required_is = ["name", "family"]
        required_members = ["accession", "genus", "species", "replicon"]
        required_cds = ["accession", "start", "end"]

        def check_columns(df, required, fname):
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise ValueError(f"{fname} missing columns: {missing}")

        check_columns(mge, required_mge, "MGE file")
        check_columns(is_db, required_is, "IS DB file")
        check_columns(members, required_members, "Members file")
        check_columns(cds, required_cds, "CDS file")

        # =========================
        # CLEAN
        # =========================
        step("[3/9] Cleaning MGE...")
        mge = mge[mge["type"] != "putative"].copy()

        # =========================
        # FAMILY MAPPING
        # =========================
        step("[4/7] Mapping IS families...")
        is_map = dict(zip(is_db["name"], is_db["family"]))
        mge["family"] = mge["name"].map(is_map).fillna("unknown")

        # =========================
        # COORDINATES
        # =========================
        step("[5/9] Adding erm coordinates...")

        def normalize(acc):
            return acc.split(".")[0] if isinstance(acc, str) else acc

        cds["accession"] = cds["accession"].apply(normalize)
        mge["accession"] = mge["accession"].apply(normalize)

        coord_map = dict(zip(cds["accession"], zip(cds["start"], cds["end"])))

        mge["erm_start"] = mge["accession"].map(lambda x: coord_map.get(x, (None, None))[0])
        mge["erm_end"] = mge["accession"].map(lambda x: coord_map.get(x, (None, None))[1])

        # =========================
        # DISTANCE + RELATION
        # =========================
        step("[6/9] Computing distances and relationships...")

        def compute_distance(row):
            if pd.isna(row["erm_start"]):
                return None
            if row["end"] < row["erm_start"]:
                return row["erm_start"] - row["end"]
            elif row["start"] > row["erm_end"]:
                return row["start"] - row["erm_end"]
            else:
                return 0

        mge["distance"] = mge.apply(compute_distance, axis=1)

        def rel(row):
            if row["distance"] == 0:
                return "overlap"
            elif row["end"] < row["erm_start"]:
                return "upstream"
            else:
                return "downstream"

        mge["relationship"] = mge.apply(rel, axis=1)

        # =========================
        # EMBEDDED + FILTER
        # =========================
        step("[7/9] Detecting embedded + filtering ≤5kb...")

        def embedded(row):
            if pd.isna(row["erm_start"]):
                return False
            return row["start"] <= row["erm_start"] and row["end"] >= row["erm_end"]

        mge["embedded"] = mge.apply(embedded, axis=1)

        mge = mge[(mge["distance"] <= 5000) | (mge["embedded"])]

        # =========================
        # SUMMARY
        # =========================
        step("[8/9] Generating summary...")

        summary_rows = []
        for acc, group in mge.groupby("accession"):
            if group["embedded"].any():
                category = "embedded_transposon"
            elif len(group) == 1:
                category = "single_IS"
            else:
                category = "multiple_IS"

            summary_rows.append({
                "accession": acc,
                "category": category,
                "min_distance": group["distance"].min()
            })

        summary = pd.DataFrame(summary_rows)

        # =========================
        # ANNOTATION
        # =========================
        step("[9/9] Adding species + localization...")

        members["accession"] = members["accession"].apply(normalize)
        members["species_full"] = (
            members["genus"].fillna("") + " " + members["species"].fillna("")
        ).str.strip()

        tax_map = dict(zip(members["accession"], members["species_full"]))
        loc_map = dict(zip(members["accession"], members["replicon"]))

        mge["species"] = mge["accession"].map(tax_map)
        mge["genome_localization"] = mge["accession"].map(loc_map)

        summary["species"] = summary["accession"].map(tax_map)
        summary["genome_localization"] = summary["accession"].map(loc_map)

        # =========================
        # SAVE
        # =========================
        step("Saving outputs...")

        os.makedirs(out_dir, exist_ok=True)

        mge.to_csv(os.path.join(out_dir, f"{out_name}_FULL.csv"), index=False)
        summary.to_csv(os.path.join(out_dir, f"{out_name}_SUMMARY.csv"), index=False)

        step("✅ Pipeline completed successfully.")

    except Exception as e:
        log(f"❌ ERROR: {str(e)}")


# =========================
# THREAD
# =========================

class Worker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        try:
            run_pipeline(*self.paths, log=self.log_signal.emit)
        except Exception as e:
            self.log_signal.emit(f"ERROR: {str(e)}")


# =========================
# GUI
# =========================

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("erm Pipeline GUI")

        # ✅ create and assign layout properly
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # inputs
        self.mge_input = self.make_input("MGE file")
        self.is_input = self.make_input("IS DB file")
        self.members_input = self.make_input("Members file")
        self.cds_input = self.make_input("CDS log file")
        self.out_dir_input = self.make_input("Output directory", folder=True)

        # output name
        self.out_name = QLineEdit()
        self.out_name.setPlaceholderText("Output name")

        # run button
        self.run_btn = QPushButton("RUN PIPELINE")
        self.run_btn.clicked.connect(self.run_pipeline)

        # log window
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # add to layout
        self.main_layout.addWidget(self.out_name)
        self.main_layout.addWidget(self.run_btn)
        self.main_layout.addWidget(self.log)

    def make_input(self, label_text, folder=False):
        label = QLabel(label_text)
        line = QLineEdit()
        btn = QPushButton("Browse")

        def browse():
            if folder:
                path = QFileDialog.getExistingDirectory()
            else:
                path, _ = QFileDialog.getOpenFileName()
            if path:
                line.setText(path)

        btn.clicked.connect(browse)

        # ✅ use self.main_layout, NOT self.layout()
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(line)
        self.main_layout.addWidget(btn)

        return line

    def log_message(self, msg):
        self.log.append(msg)

def run_pipeline(self):
    self.log.clear()
    self.log.append("🚀 Starting pipeline...\n")

    paths = [
        self.mge_input.text(),
        self.is_input.text(),
        self.members_input.text(),
        self.cds_input.text(),
        self.out_dir_input.text(),
        self.out_name.text()
    ]

    self.worker = Worker(paths)
    self.worker.log_signal.connect(self.log_message)
    self.worker.start()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
