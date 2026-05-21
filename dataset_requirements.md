# Dataset Requirements

This is an extension of the minimum standards checklist. It lists additional requirements for datasets to help ensure that they can properly undergo all required validation steps. 

## All Datasets

Don’t rename standard Kobo columns. E.g : _index, _parent_index, column names in kobo_survey and kobo_choices etc

## JMMI Dataset

Sheet and column names listed below should be exact matches.

| **Expected Sheet Names** | **Expected Column Names** | **Notes** |
| --- | --- | --- |
| raw_data |   • uuid or x_uuid<br> • consent |  |
| clean_data |   • uuid or x_uuid <br>• stratum | Stratum only required for weighted analysis though this is not currently being checked. |
| deletion_log |   • uuid or x_uuid |  |
| cleaning_log |   • uuid or x_uuid  <br>• old_value <br>• new_value <br> • change_type <br> • question |  |
| kobo_survey |   • type <br> • name |  |
| kobo_choices |   • list_name <br> • name |  |
| read_me |  |  |
| variable_tracker |  |  |
| meb_analysis |  |  |
| mfs_analysis |  |  |
| sampling_info |  | Mandatory when weights are added, otherwise optional |
| enumerator_performance_log |  | Optional |

## Other Datasets

Other datasets will require a base list of sheets to be present. The dataset is analysed to classify the other sheets. This includes checking if loops are present.

### Regarding Loops

#### Parent Sheets

If there are loops it is expected that there will be both a parent ‘raw’ data sheet and a parent ‘clean’ data sheet. Child sheets are expected to have a column that links to the parent sheet.

#### Cleaning Logs

The number of cleaning logs is flexible.

If there is one cleaning log for the entire dataset it should contain ID columns for the parent clean data sheet and each of the child sheets. This allows the validation process to determine which sheet the cleaning log record relates to. The ID column names should match the ID column names in the parent and child sheets.

If there are individual cleaning logs for parents and children then only one ID column which links to the relevant clean data sheet is required. 

### Base Sheets

Sheet and column names listed below should be exact matches.

| **Sheet Name** | **Expected Columns** | Notes |
| --- | --- | --- |
| deletion_log | uuid or x_uuid | Only one per dataset. <br> ID column name should match the ID column in both clean and raw data sheets. |
| kobo_survey |   • type <br> • name |  |
| kobo_choices |   • list_name <br> • name |  |
| read_me |  |  |
| variable_tracker |  |  |
| sampling_info |  | Mandatory when weights are added, otherwise optional |
| enumerator_performance_log |  | Optional |

### Other Sheets

For other sheets, there is some flexibility in their naming but each name must contain certain identifying information. The requirements differ slightly if there are parent-child relationships from loops.

#### Parent Sheets or No Loops

When there are parent sheets due to loops or if there are no loops the following sheets and naming conventions are required. 

The specific names for the sheets is flexible as long as the specified naming requirements are met. 

| **Sheet Type** | **Naming Requirements** | **Expected Columns** | **Notes** |
| --- | --- | --- | --- |
| raw_data | Name must include ‘raw’ |   • A unique ID column. Eg: uuid <br> • consent  |  |
| clean_data | Name must include ‘clean’ |   • A unique ID column. Eg: uuid <br> • stratum |  |
| cleaning_log <br> (if one sheet per dataset) | Name must include ‘log’ and ‘clean’ |   • ID column/s for the Parent sheet and each of the child sheets (if there are loops). <br> • old_value <br> • new_value <br> • change_type <br> • question | ID column names should match those of the parent and child sheets. |

#### Child Sheets From Loops

The specific names for the sheets is flexible as long as the specified naming requirements are met. 

ID column names for child sheets is flexible but the name should be consistent between linked sheets.

| **Sheet Type** | **Naming Requirements** | **Expected Columns** | **Notes** |
| --- | --- | --- | --- |
| raw_data | Name must include ‘raw’ |   • ID column of the parent sheet <br> • A unique id column|  
| clean_data | Name must include ‘clean’ |   • ID column of the parent sheet<br> • A unique id column |  |
| cleaning_log <br> (if one sheet for each parent and child sheet) | Name must include ‘log’ and ‘clean’ |   • ID Column of the linked sheet <br> • old_value <br> • new_value <br> • change_type <br> • question | ID column name should match that of the linked parent or child sheets. |

