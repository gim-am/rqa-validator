Generate pot file for one file
'''
xgettext -d base -o locales/messages.pot src/rqa_validator/validators/schema_validators/unexpected_sheets_validator.py 
'''

generate pot file for multiple files
'''
xgettext -d base -o locales/messages.pot src/rqa_validator/validators/schema_validators/*.py
'''

build mo file
'''
msgfmt -o locales/en/LC_MESSAGES/messages.mo locales/en/LC_MESSAGES/messages.po
'''