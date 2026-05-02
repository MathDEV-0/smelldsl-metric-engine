SmellDSL Metrics Extractor
==========================

Metrics extraction and code smell preprocessing pipeline for Java projects using CK metrics and a custom Domain Specific Language (DSL).

The project automatically executes CK metric extraction, parses `.smelldsl` definitions, maps metrics to smells, and exports structured CSV files for further analysis, research, machine learning, or software quality studies.

* * * * *

Table of Contents
=================

1.  [Overview](#overview)

2.  [Architecture](#architecture)

3.  [Workflow](#workflow)

4.  [Project Structure](#project-structure)

5.  [Prerequisites](#prerequisites)

6.  [Install Dependencies](#install-dependencies)

7.  [CK Metrics Tool](#ck-metrics-tool)

8.  [Configuration](#configuration)

9.  [Running the Project](#running-the-project)

10. [SmellDSL Example](#smelldsl-example)

11. [Generated Files](#generated-files)

12. [Supported Metrics](#supported-metrics)


* * * * *

Overview
========

This project provides an automated pipeline for:

-   extracting software metrics from Java projects;

-   parsing smell definitions using a custom DSL;

-   associating metrics with smells;

-   generating structured datasets for software quality analysis.

The system was designed for:

-   software engineering research;

-   code quality analysis;

-   software architecture studies;

-   intelligent smell detection pipelines;

-   future integration with AI-based analysis.

* * * * *

Architecture
============

```
flowchart LR

A[Java Project] --> B[CK Metrics Extraction]

B --> C[class.csv / method.csv]

C --> D[SmellDSL Parser]

D --> E[Metric Extraction Engine]

E --> F[Metrics Mapping]

F --> G[CSV Export]

```

* * * * *

Workflow
========

1.  Configure project paths in `config.txt`

2.  Execute the extractor

3.  CK generates:

    -   `class.csv`

    -   `method.csv`

4.  The DSL parser reads all `.smelldsl` files

5.  Metrics are mapped to smells

6.  CSV files are generated for each analyzed class

* * * * *

Project Structure
=================

```
metrics-extractor/
│
├── metrics_extractor_java.py
├── config.txt
├── config_example.txt
├── requirements.txt
├── .gitignore
│
├── smelldsl/
│   └── .gitkeep
│
├── metrics_output/
│   └── .gitkeep
│
└── README.md

```

* * * * *

Prerequisites
=============

Python
------

Python 3.9+ recommended.

Verify installation:

```
python --version
```

* * * * *

Java
----

JDK 17+ recommended.

Verify installation:

```
java --version
```

* * * * *

Install Dependencies
====================

Create virtual environment (recommended)
----------------------------------------

### Windows

```
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```
python -m venv venv
source venv/bin/activate
```

* * * * *

Install Python dependencies
---------------------------

```
pip install -r requirements.txt
```

* * * * *

CK Metrics Tool
===============

This project uses the CK Java Metrics Tool:

🔗 <https://github.com/mauricioaniche/ck>

* * * * *

Clone CK repository
-------------------

```
git clone https://github.com/mauricioaniche/ck.git
```

* * * * *

Build CK with Maven
-------------------

Inside the CK project directory:

```
mvn clean install
```

The generated jar will usually be located at:

```
ck/target/ck-x.x.x-SNAPSHOT-jar-with-dependencies.jar
```

Example:

```
C:/Users/NoOne/ck-master/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar
```

* * * * *

Configuration
=============

Create a local `config.txt` file using `config_example.txt` as reference.

config_example.txt
------------------

```
# =========================================
# Java project path
# =========================================

PROJECT_PATH=C:/path/to/your/java/project

# =========================================
# CK jar path
# =========================================

CK_JAR_PATH=C:/path/to/ck-jar-with-dependencies.jar

# =========================================
# Output folders
# =========================================

OUTPUT_DIR=metrics_output

DSL_DIR=smelldsl

```

* * * * *

Running the Project
===================

Run:

```
python metrics_extractor_java.py
```

The pipeline will:

1.  Execute CK automatically

2.  Generate metrics CSV files

3.  Parse `.smelldsl`

4.  Export metrics datasets

* * * * *

SmellDSL Example
================

## SmellDSL Example

The DSL syntax used in this project is inspired by the original SmellDSL proposal:

https://github.com/kleinnerfarias/smelldsl

Example:

```
smelltype DesignSmell;

smell GodClass extends DesignSmell {

    feature ATFD with threshold 4, 10;

    feature TCC with threshold 3, 5;

    feature WMC with threshold 20, 50;

    treatment "Refactor into smaller classes";
}

```

* * * * *

Generated Files
===============

Example output:

```
metrics_output/

workshopmongo_godclass_UserService_metrics.csv

workshopmongo_godclass_UserService_limits.csv

```

* * * * *

Supported Metrics
=================

Class Metrics
-------------

| Metric | Description |
| --- | --- |
| ATFD | Access to Foreign Data |
| TCC | Tight Class Cohesion |
| WMC | Weighted Methods per Class |
| RFC | Response for Class |
| CBO | Coupling Between Objects |
| LCOM | Lack of Cohesion |
| DIT | Depth of Inheritance Tree |
| NOC | Number of Children |
| LOC_CLASS | Lines of Code |

* * * * *

Method Metrics
--------------

| Metric | Description |
| --- | --- |
| LOC | Lines of Code |
| CYCLO | Cyclomatic Complexity |
| MAXNESTING | Maximum Nesting |
| PARAMS | Number of Parameters |
| FANIN | Incoming Dependencies |
| FANOUT | Outgoing Dependencies |

* * * * *

