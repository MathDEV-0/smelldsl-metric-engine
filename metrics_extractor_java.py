import os
import subprocess
import pandas as pd
from lark import Lark, Visitor
from lark.visitors import Interpreter

# RODAR JAR:
#    java -jar C:\Users\User\Downloads\ck-master\ck-master\target\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar . true 0 false output


# =========================================================
# LOAD CONFIG
# =========================================================

CONFIG_FILE = "config.txt"

config = {}

if not os.path.exists(CONFIG_FILE):

    print(f"\nConfig file '{CONFIG_FILE}' not found.")
    print("Please create a config.txt with the following format:")
    print("PROJECT_PATH=path/to/java/project")
    print("CK_JAR_PATH=path/to/ck-jar-with-dependencies.jar")
    exit()

with open(CONFIG_FILE, "r", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        config[key.strip()] = value.strip()

# =========================================================
# READ PATHS
# =========================================================

PROJECT_PATH = config["PROJECT_PATH"]

CK_JAR_PATH = config["CK_JAR_PATH"]

# nome do lote
CURRENT_LOT = os.path.basename(PROJECT_PATH)

# pasta output
CK_OUTPUT_DIR = os.path.join(
    PROJECT_PATH,
    "output"
)

os.makedirs(CK_OUTPUT_DIR, exist_ok=True)

# =========================================================
# RUN CK
# =========================================================

print("\nExecutando CK...")

command = [
    "java",
    "-jar",
    CK_JAR_PATH,
    PROJECT_PATH,
    "true",
    "0",
    "false",
    CK_OUTPUT_DIR
]

try:

    subprocess.run(
        command,
        check=True
    )

    print("CK executado com sucesso!")

except subprocess.CalledProcessError as e:

    print("\nErro ao executar CK:")
    print(e)

    exit()

# =========================================================
# CSV PATHS
# =========================================================

CLASSES_CSV = os.path.join(
    CK_OUTPUT_DIR,
    "class.csv"
)

METHODS_CSV = os.path.join(
    CK_OUTPUT_DIR,
    "method.csv"
)

print("\nCSV de classes:", CLASSES_CSV)
print("CSV de métodos:", METHODS_CSV)

# =========================================================
# DSL GRAMMAR
# =========================================================

GRAMMAR = r"""
%import common.WS
%import common.CNAME
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING

%ignore WS
%ignore /\/\/[^\n]*/

NAME: /[A-Za-z_][A-Za-z0-9_-]*/

SEMI: ";"
LBRACE: "{"
RBRACE: "}"
DOT: "."
COMMA: ","

AND: "AND"
OR: "OR"
COMP: "==" | "!=" | ">=" | "<=" | ">" | "<"

SCALETYPE: "Nominal" | "Ordinal" | "Interval" | "Ratio" | "Others"

start         : (domain_type | rule_stmt)*

domain_type   : smelltype_decl | smell_decl

smelltype_decl: "smelltype" NAME SEMI?

smell_decl    : "smell" NAME opt_extends LBRACE smell_content RBRACE

opt_extends   : "extends" NAME
              | -> no_extends

smell_content : feature_decl+ symptom_opt treatment_opt

feature_decl  : "feature" NAME opt_scale "with" "threshold" measure_list SEMI?

opt_scale     : "is" SCALETYPE
              | -> no_scale

measure_list  : measure (COMMA measure)*

measure       : NAME
              | ESCAPED_STRING
              | SIGNED_NUMBER

symptom_opt   : symptom?
treatment_opt : treatment?

symptom       : "symptom" simple_text SEMI?
treatment     : "treatment" simple_text SEMI?

simple_text   : ESCAPED_STRING
              | NAME

rule_stmt     : "rule" NAME "when" logic_expr "then" literal SEMI?

logic_expr    : logic_term (OR logic_term)*

logic_term    : logic_factor (AND logic_factor)*

logic_factor  : comparison
              | "(" logic_expr ")"

comparison    : ref COMP ref

ref           : NAME DOT NAME

literal       : ESCAPED_STRING
              | SIGNED_NUMBER
              | NAME
"""

# =========================================================
# FEATURE REGISTRY
# =========================================================

FEATURE_REGISTRY = {

    # =========================================
    # CLASS METRICS
    # =========================================

    "ATFD": {
        "csv": "class",
        "column": "fanout",
        "aggregation": "direct"
    },

    "TCC": {
        "csv": "class",
        "column": "tcc",
        "aggregation": "direct"
    },

    "WMC": {
        "csv": "class",
        "column": "wmc",
        "aggregation": "direct"
    },

    "RFC": {
        "csv": "class",
        "column": "rfc",
        "aggregation": "direct"
    },

    "LOC_CLASS": {
        "csv": "class",
        "column": "loc",
        "aggregation": "direct"
    },

    "CBO": {
        "csv": "class",
        "column": "cbo",
        "aggregation": "direct"
    },

    "LCOM": {
        "csv": "class",
        "column": "lcom",
        "aggregation": "direct"
    },

    "DIT": {
        "csv": "class",
        "column": "dit",
        "aggregation": "direct"
    },

    "NOC": {
        "csv": "class",
        "column": "noc",
        "aggregation": "direct"
    },

    # =========================================
    # METHOD METRICS
    # =========================================

    "LOC": {
        "csv": "method",
        "column": "loc",
        "aggregation": "max"
    },

    "CYCLO": {
        "csv": "method",
        "column": "wmc",
        "aggregation": "max"
    },

    "MAXNESTING": {
        "csv": "method",
        "column": "maxNestedBlocksQty",
        "aggregation": "max"
    },

    "PARAMS": {
        "csv": "method",
        "column": "parametersQty",
        "aggregation": "max"
    },

    "FANIN": {
        "csv": "method",
        "column": "fanin",
        "aggregation": "max"
    },

    "FANOUT": {
        "csv": "method",
        "column": "fanout",
        "aggregation": "max"
    }
}

# =========================================================
# VISITOR
# =========================================================

class MetricVisitor(Interpreter):

    def __init__(self):

        self.smells = {}

    def smell_decl(self, tree):

        smell_name = tree.children[0].value

        self.smells[smell_name] = {}
        for child in tree.children:

            if hasattr(child, "data"):

                if child.data == "smell_content":

                    self.process_smell_content(
                        child,
                        smell_name
                    )

    def process_smell_content(self, tree, smell_name):

        for child in tree.children:

            if hasattr(child, "data"):

                if child.data == "feature_decl":

                    feature_name = child.children[0].value

                    thresholds = []

                    # pega thresholds
                    for item in child.find_data("measure"):

                        value = item.children[0]

                        if hasattr(value, "type"):

                            if value.type == "SIGNED_NUMBER":

                                thresholds.append(value.value)

                    limit_value = None

                    if thresholds:

                        limit_value = thresholds[-1]

                    self.smells[smell_name][feature_name] = limit_value

# =========================================================
# EXTRACTOR
# =========================================================

class MetricExtractor:

    def __init__(self):

        self.parser = Lark(GRAMMAR, start="start")

    def extract(self, dsl_text):

        tree = self.parser.parse(dsl_text)

        visitor = MetricVisitor()

        visitor.visit(tree)

        return visitor.smells

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DSL_DIR = os.path.join(BASE_DIR, "smelldsl")

OUTPUT_DIR = os.path.join(BASE_DIR, "metrics_output")

CURRENT_LOT = "workshopmongo"
#CURRENT_LOT = "quickbite"


CLASSES_CSV = r"C:\Users\User\Documents\workspace-spring-tools-for-eclipse-4.31.0.RELEASE\workshopmongo\output\class.csv"

METHODS_CSV = r"C:\Users\User\Documents\workspace-spring-tools-for-eclipse-4.31.0.RELEASE\workshopmongo\output\method.csv"

# =========================================================
# CREATE FOLDERS
# =========================================================

os.makedirs(DSL_DIR, exist_ok=True)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# LOAD CSVs
# =========================================================

classes_df = pd.read_csv(CLASSES_CSV)

methods_df = pd.read_csv(METHODS_CSV)

# =========================================================
# LOAD DSL FILES
# =========================================================

dsl_files = [

    file for file in os.listdir(DSL_DIR)

    if file.endswith(".smelldsl")
]

if not dsl_files:

    print("\nNenhum .smelldsl encontrado em:")
    print(DSL_DIR)

    exit()

# =========================================================
# PROCESS DSL FILES
# =========================================================

for dsl_file in dsl_files:

    print(f"\nProcessando: {dsl_file}")

    dsl_path = os.path.join(DSL_DIR, dsl_file)

    with open(dsl_path, "r", encoding="utf-8") as f:

        dsl_text = f.read()

    extractor = MetricExtractor()

    smells = extractor.extract(dsl_text)

    print("\n[SMELLS EXTRAÍDOS]")
    print(smells)

    # =====================================================
    # PROCESS EACH CLASS
    # =====================================================

    for _, class_row in classes_df.iterrows():

        class_full_name = class_row["class"]

        class_name = class_full_name.split(".")[-1]

        metrics_output = []

        limits_output = []

        # =================================================
        # PROCESS EACH SMELL
        # =================================================

        for smell_name, features in smells.items():

            for feature_name, limit_value in features.items():

                if feature_name not in FEATURE_REGISTRY:
                    continue

                config = FEATURE_REGISTRY[feature_name]

                csv_type = config["csv"]

                column = config["column"]

                aggregation = config["aggregation"]

                value = None

                # =============================================
                # CLASS METRIC
                # =============================================

                if csv_type == "class":

                    if column in class_row:

                        value = class_row[column]

                # =============================================
                # METHOD METRIC
                # =============================================

                elif csv_type == "method":

                    class_methods = methods_df[
                        methods_df["class"] == class_full_name
                    ]

                    if column not in class_methods.columns:
                        continue

                    metric_series = class_methods[column].dropna()

                    if len(metric_series) == 0:
                        continue

                    if aggregation == "max":

                        value = metric_series.max()

                    elif aggregation == "mean":

                        value = metric_series.mean()

                    elif aggregation == "sum":

                        value = metric_series.sum()

                # =============================================
                # IGNORE INVALID VALUES
                # =============================================

                if pd.isna(value):
                    continue

                if value == -1:
                    continue

                # =============================================
                # SAVE METRIC
                # =============================================

                metrics_output.append(
                    f"{smell_name}.{feature_name},{value}"
                )

                # =============================================
                # SAVE LIMIT
                # =============================================

                if limit_value is not None:

                    limits_output.append(
                        f"{smell_name}.{feature_name}.LIMIT,{limit_value}"
                    )

        # =================================================
        # WRITE METRICS FILE
        # =================================================

        if metrics_output:
            #remove o .smelldsl do nome do arquivo para usar no nome do limits
            dsl_file_normalized = dsl_file.replace(".smelldsl", "")
            metrics_file = os.path.join(
                OUTPUT_DIR,
                f"{CURRENT_LOT}_{dsl_file_normalized}_{class_name}_metrics.csv"
            )

            with open(metrics_file, "w", encoding="utf-8") as f:

                f.write("Metrica,Valor\n")

                for line in metrics_output:

                    f.write(line + "\n")

        # =================================================
        # WRITE LIMITS FILE
        # =================================================

        if limits_output:
            #remove o .smelldsl do nome do arquivo para usar no nome do limits
            dsl_file_normalized = dsl_file.replace(".smelldsl", "")

            limits_file = os.path.join(
                OUTPUT_DIR,
                f"{CURRENT_LOT}_{dsl_file_normalized}_{class_name}_limits.csv"
            )

            with open(limits_file, "w", encoding="utf-8") as f:

                f.write("Metrica,Valor\n")

                for line in limits_output:

                    f.write(line + "\n")

print("\nArquivos gerados em:")
print(OUTPUT_DIR)
