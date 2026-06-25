# Security Policy

FinPlanIQ is a portfolio project designed to demonstrate secure handling of user-uploaded FP&A datasets.

## Supported Upload Format

FinPlanIQ only accepts standard Excel workbooks using the `.xlsx` format.

The app does not support:

- `.xlsm` macro-enabled Excel files
- `.xls` legacy Excel files
- `.xlsb` binary Excel files
- `.csv` files
- compressed files such as `.zip`
- executable files
- files larger than 10 MB

## Upload Security Controls

FinPlanIQ includes basic upload safety checks:

- File extension allowlisting
- File size validation
- Rejection of unsupported file formats
- In-memory file processing
- Template-based schema validation
- Required column validation
- Numeric value validation
- Month/date validation
- Safe user-facing error messages

## Privacy Notice

Uploaded files are processed in memory during the Streamlit session.

FinPlanIQ does not intentionally save uploaded financial files to the project folder or database.

Because this is a public portfolio project, users should not upload real confidential company financial data to a public deployment.

## Data Validation

Uploaded workbooks must follow the provided template and include two sheets:

- `Revenue_COGS`
- `Opex_Headcount`

FinPlanIQ validates required fields before generating the dashboard.

## Secrets Management

No API keys, passwords, or credentials should be committed to this repository.

If future versions use external APIs, secrets should be stored using environment variables or Streamlit secrets management.

## Security Limitations

FinPlanIQ is not an enterprise-grade secure finance system.

It does not currently include:

- user authentication
- role-based access control
- persistent encrypted file storage
- enterprise audit logging
- malware scanning
- SOC 2 / compliance controls

The security features are intentionally scoped for a portfolio-ready analytics application.