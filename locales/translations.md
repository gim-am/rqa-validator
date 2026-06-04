# Adding a new message to translation files
To add an entirely new message (ie, the key has not been used before) to a translation a few steps need to be followed. 
1. For non-validator files, Import the helper if not already done
```python
from ..utils.il8n import _
```
2. Set a key and the required parameters. For a `ValidationResult` this would look something like this:
```python
ValidationResult(
    rule=rule,
    message=_(
        "data_helpers.get_data_loaded_column", #key
        column=column_name, #paramaters
        sheet=loaded_sheet.data_sheet_name,
    ),
    severity=SeverityLevel.ERROR,
    sheet_name=loaded_sheet.data_sheet_name,
    column_name=column_name,
)
```
or this if it is being used in a class that inherits from `BaseValidator`:
```python
ValidationResult(
    rule=self.name,
    message=self._(
        "duplicate_sheet_match_validator.duplicate_sheets",
        count=matches_df.select(pl.col("sheet")).unique().height,
    ),
    severity=SeverityLevel.ERROR,
    details=matches_df.to_dict(),
)
```
The key could either be an existing key or a new unique key.

**The following steps are only relevant if new keys are being created.**

3. Once all the changes have been made the template file can be generated. In a terminal, this can be done file for one file:

```bash
xgettext -d base -o locales/messages.pot src/rqa_validator/validators/schema_validators/unexpected_sheets_validator.py 
```

or for multiple files
```bash
xgettext -d base -o locales/messages.pot src/rqa_validator/validators/schema_validators/*.py
```
The output will be stored in `locales/messages.pot` and will contain the keys from the file and an empty message string
```
#: src/rqa_validator/validators/data_helpers.py:88
msgid "data_helpers.get_data_loaded_column"
msgstr ""
```
These can be coppied into the relevant `.po` file, for example `en/LC_MESSAGES/messages.po`

4. Set the message. The parameters can be set in the message between {}. 
```
#: src/rqa_validator/validators/data_helpers.py:88
msgid "data_helpers.get_data_loaded_column"
msgstr "A column for '{column}' in sheet '{sheet}' is expected."
```
5. Once all the messages have been set, the `.mo` file needs to be generated. Using the terminal:

```bash
msgfmt -o locales/en/LC_MESSAGES/messages.mo locales/en/LC_MESSAGES/messages.po
```
6. Commit changes to the repository.

# Translate an existsing message
If there is an existing message in one language and a translation is required then the process is a little easier. 
1. Cope the existing message (msgid, msgstr) into the relevant language file. For example, from `en/LC_MESSAGES/messages.po` to `fr/LC_MESSAGES/messages.po`
2. Translate the contents of msgstr but DO NOT change the text between the curley braces {}. For example, this:
```
#: src/rqa_validator/validators/data_helpers.py:88
msgid "data_helpers.get_data_loaded_column"
msgstr "A column for '{column}' in sheet '{sheet}' is expected."
```
will change to this:
```
#: src/rqa_validator/validators/data_helpers.py:88
msgid "data_helpers.get_data_loaded_column"
msgstr "French translation '{column}' French translation '{sheet}' French translation."
```
3. Once all the translations have been done, rebuild the `.mo` file. Using the terminal and referencing the relevant locale (in this case fr):

```bash
msgfmt -o locales/fr/LC_MESSAGES/messages.mo locales/fr/LC_MESSAGES/messages.po
```
4. Commit changes to the repository.