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
│   │   ├── common
│   │   │   └── matching.py
│   │   ├── loaders
│   │   │   ├── excel_loader.py 
│   │   │   └── __init__.py
│   │   ├── models
│   │   │   ├── base.py
│   │   │   ├── __init__.py
│   │   │   ├── jmmi.py
│   │   │   └── preprocess.py
│   │   ├── orchestrator
│   │   │   ├── __init__.py
│   │   │   └── validation_pipeline.py
│   │   └── validators
│   │       ├── base.py
│   │       ├── column_validators.py
│   │       ├── config.py
│   │       ├── __init__.py
│   │       └── sheet_validators.py
│   └── tests

└── uv.lock

```

## Setup
1. Clone the repository
2. Install dependencies with [uv](https://github.com/astral-sh/uv):
```bash
   uv sync
```
3. Download a dataset. Some options include:
- https://repository.impact-initiatives.org/document/impact/031f3c9b/REACH_SSD_Dataset-Analysis_JMMI_March-2026.xlsx
- https://repository.impact-initiatives.org/document/impact/b0e5c61a/REACH_SSD_Dataset-Analysis_JMMI_February-2026.xlsx
4. Run the process
```
uv run main.py --dataset-type jmmi Step3DatasetPath
```
5. Any validation errors will be output to the terminal.

### Running process
The process follows these steps for the provided dataset:
1. Validate the schema. This process checks:    
    - for duplicate sheet names and column names within sheets to prevent matching excel data to multiple schema sheets/columns.
    - lowers all names to simplify matching

If there are any errors at this stage the process will end. 

Currently, from this point onwards all errors are accumulated and the process will not stop

2. Load the Excel file  
    - Excel sheets and columns are mapped to the schema for sheets that have to be loaded
    - Sheet names for sheets that do not have to be loaded
    - This optionally includes fuzzy matching of sheets/columns
3. Perform all the validation steps.
4. Errors are output to the user.

There are several error types:
- **Admin errors**: these are either Python errors or errors with the schema from step 1.
- **Errors**: critical errors from the validation process. Eg: a missing sheet etc
- **Warnings**: warnings from the validation process. Eg: an optional sheet is missing, possible Pii column found
- **Info**: information for user awareness. Eg: if fuzzy matching was used to match a column.
   
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
- a flag stating if the sheet is required, default True

Each of the columns listed within a sheet above has:
- a standard name
- a list of possible alternate names
- a flag stating if the column should containe unique values, default False

### Validation Rules
Validation rules are split between sheet based validation rules and column based validation rules. Each of these are designed to be able to be run on any dataset by looking at either the dataset, the dataset schema or other config values.

A structured list of validation errors is produced (errors, warnings) for each rule.

These rules are currently based on the minimum standars checklist (1.2)

#### Rules currently implemented
**Column Rules**
- Mandatory columns: checks if mandatory columns are not present in a sheet
- Unique column values (uuids): checks if a column does not contain unique values
- Pii columns: checks if any of the columns are possible pii columns

**Sheet Rules**
- Missing sheets: checks if mandatory sheets are not present
- Unexpected sheets: checks if there are any unexpcedted sheets
- Dataset sum check: checks if clean data + deleted data = raw data
- Cross sheet id check: checks if ids in child sheets are not present in a parent sheet. For example, between raw_data and clean_data


Fuzzy matching can also be attempted on the sheet and column names by setting the config values in `.env`.


    
## TODO: 
- clean validation results based on requirements 
- add other datasets and validation rules

- jira api integration
- impact repository integration
- logging and error reporting.
- adjust for infrastructure requirements