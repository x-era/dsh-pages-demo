# Contact CSV Demo

一个仅依赖 Python 标准库的小项目，用于测试 GitHub Issue → Agent 修复 → PR → 评审后继续修改的流程。使用虚构联系人，不需要 API、数据库或真实个人信息。

## 环境和运行

需要 Python 3.10 或更新版本，无需安装第三方包。在仓库根目录运行：

```sh
python3 -m unittest discover -v
```

**初始版本包含一个有意保留的缺陷**：邮政编码的前导零会丢失。对应回归测试应失败，其余测试应通过。这个失败用于让 Agent 完成真实修复；初始仓库不要求全绿，也未启用 GitHub Actions。

## 接口

```python
from contact_exporter import export_contacts

text = export_contacts([
    {"name": "Alice", "postal_code": "02108"},
    {"name": "Bob, Jr.", "postal_code": "94105"},
])
```

`export_contacts(contacts)` 接受由字典组成的可迭代对象；字典的 `name`、`postal_code` 都是字符串。返回带 `name,postal_code` 表头的 CSV **字符串**，保留输入顺序和字段原值，不修改输入。邮政编码属于标识符，不应被当作数值处理。逗号、引号、Unicode 和字段内换行必须遵循 CSV 转义规则。

空输入返回只有表头的 CSV。额外字段不导出，缺少必需字段不在本次演示范围内。

## 示例数据

`examples/contacts.json` 是虚构输入。可以在仓库根目录查看导出结果：

```sh
python3 - <<'PY'
import json
from pathlib import Path
from contact_exporter import export_contacts

contacts = json.loads(Path("examples/contacts.json").read_text(encoding="utf-8"))
print(export_contacts(contacts), end="")
PY
```

## 修改约定

- 修复应保持接口兼容，保留原始测试，并为新增场景补充测试。
- 在独立分支修改，通过 PR 交付，附上实际测试结果。
- 不自动合并，不引入与任务无关的依赖或外部服务。
