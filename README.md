# Prototype for validation of RQA datasets
**Aim**: To develop a hopefully flexible framework that can handle different datasets with non-standard sheet and column names that have different validation rules.

```bash
├── config.py
├── .env
├── .gitignore
├── main.py
├── pyproject.toml
├── .python-version
├── README.md
├── src
│   ├── rqa_validator
│   │   ├── loaders
│   │   │   ├── excel_loader.py
│   │   │   └── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── jmmi.py
│   │   │   ├── matching.py
│   │   │   ├── preprocess.py
│   │   │   └── schema.py
│   │   ├── orchestrator
│   │   │   ├── __init__.py
│   │   │   └── validation_pipeline.py
│   │   ├── utils
│   │   │   └── __init__.py
│   │   └── validators
│   │       ├── base.py
│   │       ├── column_validators.py
│   │       ├── config.py
│   │       ├── __init__.py
│   │       ├── preprocess.py
│   │       └── sheet_validators.py
│   └── tests
│       ├── __init__.py
│       └── validators
│           ├── column_validators
│           │   ├── __init__.py
│           │   ├── test_mandatory_columns.py
│           │   ├── test_pii_columns.py
│           │   └── test_unique_columns.py
│           ├── __init__.py
│           └── sheet_validators
│               ├── __init__.py
│               ├── test_cross_sheet_id_check.py
│               ├── test_cross_sheet_row_sum_check.py
│               ├── test_missing_sheets.py
│               └── test_unexpected_sheets.py
└── uv.lock

```


## Dataset Definitions
A dataset will have a schema and a list of validation rules that need to be run.

### Basic Structure For Dataset Schemas

Within models, dataset schemas can be defined. A schema has:
- A list of sheets to be loaded
- A list of sheets that dont need to be loaded

Each of these sheets has:
- a standard name
- a list of possible alternate names
- a list of mandatory columns
- a flag stating if the sheet is required
- a list of possible uuid column names

Each of the columns listed within a sheet above has:
- a standard name
- a list of possible alternate names

### Validation Rules
Validation rules are split between sheet based validation rules and column based validation rules. Each of these are designed to be able to be run on any dataset by looking at either the dataset, the dataset schema or other config values.

A structured list of validation errors is produced (errors, warnings) for each rule.

These rules are currently based on the minimum standars checklist (1.2)

#### Rules currently implemented
**Column Rules**
- Mandatory columns: checks if mandatory columns or uuid columns are not present in a sheet
- Unique column values (uuids): checks if a column does not contain unique values
- Pii columns: checks if any of the columns are possible pii columns

**Sheet Rules**
- Missing sheets: checks if mandatory sheets are not present
- Unexpected sheets: checks if there are any unexpcedted sheets
- Dataset sum check: checks if clean data + deleted data = raw data


## Loading Excel Data
Data is currely loaded from a file on disk one sheet at a time. This process:
- Checks to see if the sheet needs to be loaded
- Stores the original name and the mapped name (based on the schema)
- Stores unexpected sheets


    
## TODO: 
- clean validation results based on requirements 
- add other datasets and validation rules

- jira api integration
- impact repository integration
- logging and error reporting.
- adjust for infrastructure requirements