# MiniAzure — Build Log

## Session 1 — Resource Groups
- config.py, utils.py, core/resource_group.py, cli.py
- Commands: group create / list / show / delete

## Session 2 — VMs
- core/vm_agent.py, core/vm_runtime.py, core/vm.py
- VMs are real processes with PIDs
- Commands: vm create / list / show / start / stop / restart / delete / stats / logs

## Session 3 — Blob Storage
- core/storage.py, core/blob_server.py
- Storage accounts, containers, blobs over HTTP
- Commands: storage create / list / show / delete
-          storage container create / list / delete
-          storage upload / blob list / blob delete
