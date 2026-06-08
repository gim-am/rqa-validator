from .base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap

CHOICES_SHEET = SchemaSheetMap(
    standard_name="choices",
    alternate_names=["kobo_choices"],
    mandatory_columns=[
        SchemaColumnMap(standard_name="list_name"),
        SchemaColumnMap(standard_name="name"),
    ],
)

SURVEY_SHEET = SchemaSheetMap(
    standard_name="survey",
    alternate_names=["kobo_survey"],
    mandatory_columns=[
        SchemaColumnMap(
            standard_name="type",
            process_values=[
                ProcessValueMap(
                    process_name="data_type_numeric_check",
                    values=["integer", "decimal"],
                ),
                ProcessValueMap(process_name="data_type_temporal_check", values=["date"]),
            ],
        ),
        SchemaColumnMap(standard_name="name"),
        SchemaColumnMap(standard_name="calculation"),
    ],
)
DELETION_SHEET = SchemaSheetMap(
    standard_name="deletion_log",
    alternate_names=[],
    mandatory_columns=[
        SchemaColumnMap(standard_name="uuid", alternate_names=["_uuid"], is_unique=True)
    ],
)

READ_ME_SHEET = SchemaSheetMap(standard_name="read_me", alternate_names=["read.me", "read me"])

SAMPLING_INFO_SHEET = SchemaSheetMap(
    standard_name="sampling_info",
    alternate_names=["sampling_info"],
    required=False,
)

VARIABLE_TRACKER_SHEET = SchemaSheetMap(
    standard_name="variable_tracker", alternate_names=["variable_tracker"]
)

ENUMERATOR_PERFORMANCE_SHEET = SchemaSheetMap(
    standard_name="enumerator_performance_log",
    alternate_names=["enumerator_performance_log"],
    required=False,
)


def create_base_cleaning_log_sheet(
    name: str, id_column: str | None, id_column_alt: list[str] | None
) -> SchemaSheetMap:
    sheet = SchemaSheetMap(
        standard_name=name,
        alternate_names=[],
        mandatory_columns=[
            SchemaColumnMap(standard_name="old_value"),
            SchemaColumnMap(standard_name="new_value"),
            SchemaColumnMap(
                standard_name="change_type",
                alternate_names=["changed"],
                process_values=[
                    ProcessValueMap(
                        process_name="cleaning_log_validation",
                        values=["yes", "change_response", "blank_response"],
                    )
                ],
            ),
            SchemaColumnMap(
                standard_name="question", alternate_names=["variable", "question.name"]
            ),
        ],
    )

    if id_column is not None:
        sheet.add_mandatory_column(
            SchemaColumnMap(
                standard_name=id_column,
                alternate_names=id_column_alt if id_column_alt is not None else [],
            )
        )
    return sheet


CONSENT_COLUMN = SchemaColumnMap(
    standard_name="consent",
    alternate_names=["consentement"],
    process_values=[
        ProcessValueMap(
            process_name="consent_check_validation",
            values=["yes", "oui"],
        )
    ],
)
