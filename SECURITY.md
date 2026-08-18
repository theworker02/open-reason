# Security

## Dataset execution

Open Reason contains executable programming tasks. Treat verification as untrusted-code execution. Use Docker isolation in production. The subprocess backend is a development fallback, not a security boundary.

## Reporting vulnerabilities

Please use GitHub Security Advisories on `theworker02/open-reason`. Do not open public issues for exploitable sandbox escapes.

## Scope

In scope: sandbox isolation failures, supply-chain issues in this repository, accidental inclusion of secrets or PII.

Out of scope: model misuse, and theoretical jailbreaks of models trained on the dataset.
