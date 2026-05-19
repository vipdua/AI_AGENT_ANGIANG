from core.audit import (
    get_audit_logs
)

logs = get_audit_logs()

for log in logs:

    print(log)