# RQA Validator: a tool for validating datasets
**Purpose**: To provide a flexible framework that can process and validate different standardised and less-standardised datasets.

## Project structure
This project is designed to allow for the validation of different excel based datasets through the construction of a dataset schema and specifying a list of validation rules that are required to be run. Both the schema components and the validation components are designed to be modular. This helps to support the easy building and management of schemas, validation rules and their intergration with the validation framework.

### Suported Datasets
To run the process a dataset must be specidifed. The current suported datasets and their paramater values include:

| **Dataset** | **Paramater Value** |
| --- | --- | 
|JMMI|jmmi|
|All other datasets| other

## Environment Setup
1. Clone the repository
2. Install dependencies with [uv](https://github.com/astral-sh/uv):
```bash
   uv sync
```
3. Download a dataset. Some options include:
- for JMMI: https://repository.impact-initiatives.org/document/impact/031f3c9b/REACH_SSD_Dataset-Analysis_JMMI_March-2026.xlsx
- For other: https://repository.impact-initiatives.org/document/impact/d77de3de/KEN_2401_MSNA_data_camps.xlsx

4. Run the process
```
uv run main.py --dataset-type jmmi "path/to/excel/file.xlsx"
```
or
```
uv run main.py --dataset-type other "path/to/excel/file.xlsx"
```
5. Any validation errors will be returned.
### Integration with other projects or workflows
If incorporating this into another project or workflow it is probably easier to use the orchestrator directly:
```python
from src.rqa_validator.orchestrator.validation_pipeline import ValidationPipeline

results = ValidationPipeline().run_all(filepath="path/to/excel/file.xlsx", dataset_type="other", locale='en') #or jmmi
```
### Validation Message Translations
Most user messages (Error, Warnings, Info, Passed) support translations into other languages. This is a work in progress. If a message is not available for a specific language, the message will default to English. 

See [translations](locales/translations.md) for details on managing/expanding these.

### Running Rules Individually
If testing or debugging, it is possible to run individual validation rules. To do this, first load the data setting the appropriate filepath and then run the required rule. For JMMI:

```python
from src.rqa_validator.models.jmmi import JMMIDataset
from src.rqa_validator.loaders.excel_loader import ExcelLoader
# use whichever rule is required
from src.rqa_validator.validators.data_validators import RawToCleanToLog


schema = JMMIDataset().schema
loader = ExcelLoader(schema)
data, results = loader.load("path/to/excel/file.xlsx")

# run the required rule setting the appropriate parmaters
RawToCleanToLog(schema=schema).validate(data=data)

```
or for other datasets:
```python
from src.rqa_validator.models.dynamic_model import DynamicDataset
from src.rqa_validator.loaders.excel_loader import ExcelLoader
# Use whichever rule is required
from src.rqa_validator.validators.data_validators import CrossSheetIdCheck

dataset = DynamicDataset()
loader = ExcelLoader(dataset.schema)
dataset.data, excel_results = loader.load("path/to/excel/file.xlsx",
                                            load_all_sheets= True  )
dataset.process_data()

# run the required rule setting the appropriate parmaters
CrossSheetIdCheck(dataset.schema).validate(dataset.data)
```
## Contributing and Reporting Issues
If you are interested in expanding the list of supported languages for the validation messages get in touch. 

If you encounter any bugs report these on the [project issues page](https://github.com/gim-am/rqa-validator/issues).