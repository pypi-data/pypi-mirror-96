# KDB to Vault Tools

[![codecov](https://codecov.io/gh/moaddib666/kdb-vault-tools/branch/master/graph/badge.svg?token=2P8a1JEjSn)](https://codecov.io/gh/moaddib666/kdb-vault-tools)

Package that allow migrate from kdb to vault and vise versa

### Example
- Start vault in development mode
```bash
docker-compose up
```

- Prepare simple script or use `kdb_2_vault.py`

```python
from kdb_vault_tools import Processor

def create_kdb():
    vault_conf = {"url": "http://localhost:1234", "token": "myroot"}
    kdb_conf = {
        "filename": "kdb_tmp/secrets-20190422.kdbx",
        "password": "superSecret123",
    }

    processor = Processor(vault_settings=vault_conf, kdb_settings=kdb_conf)
    processor.sync_from_vault()
    processor.write_kdb()


def fill_vault():
    vault_conf = {"url": "http://localhost:1234", "token": "myroot"}
    kdb_conf = {
        "filename": "kdb_tmp/secrets-20190422.kdbx",
        "password": "superSecret123",
    }

    processor = Processor(vault_settings=vault_conf, kdb_settings=kdb_conf)
    processor.sync_from_kdb()
    processor.write_vault(base_path="/sandbox/org/team/foo/") 
```

### History
Version 0.1.0 (2021-02-23) - Base Concept

### Credits
Lead Developer - Max Nikitenko (moaddib666@gmail.com)

### License
- MIT
