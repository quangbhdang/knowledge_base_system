# Conda Command Knowledge Base System

A Knowledge Base of Conda command that you might need to use daily. 

It core ability is storing important command for conda as well as some simple diagnosis rules to help you navigate Conda.

## Tables of command

| Type | Command |
|------|---------|
| Verify install and check version | `conda info` |
| Update base environment | `conda update --name base conda`|
|create a new environment | `conda create -- name ENVNAME`|
|activate environment | `conda 

## FAQ

Here are a table of error id, condition and conclusion of fix.

| ID  | Condition     | Conclusion       |
|-----|---------------|------------------|
| 001 | env_not_found | Run `conda env list` to check envrionments or recreate with  `conda create --name <env>`|
| 002 |
