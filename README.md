# DSH Pages Demo

一个可部署到 GitHub Pages 的小型静态页面，用于测试 GitHub Issue → Agent 修复 → PR → 评审后继续修改的流程。页面展示虚构联系人，不需要 API、数据库或真实个人信息。

发布后的页面是一个简单的“联系人导出器”产品介绍页：打开 `index.html` 即可预览。

## 环境和运行

需要 Python 3.10 或更新版本，无需安装第三方包。在仓库根目录运行：

```sh
python3 -m unittest discover -v
```

页面保留一个有意设置的视觉回归：主按钮文字与背景颜色相同，访问页面时按钮文字几乎不可见。`tests/test_site.py` 会检测这个问题。它用于让 Agent 完成一个真实的 Issue 修复；修复后所有本地测试应通过。

初始版本的测试预期为 12 项通过、1 项失败；失败项会计算按钮前景与背景的颜色对比度，要求至少 4.5:1。其余链接、资源和 CSV 行为均应通过。

## GitHub Pages

仓库为 `x-era/dsh-pages-demo`，页面地址为 `https://x-era.github.io/dsh-pages-demo/`，无需占用账号根站点的 `x-era.github.io` 仓库。初次发布完成前，这两个地址可能尚不可用。

在仓库 Settings → Pages 中选择 **GitHub Actions**。`.github/workflows/pages.yml` 会在 `main` 更新后发布页面，仅上传 `index.html`、`styles.css` 和 `.nojekyll`。Python 源码、测试和操作记录不会进入 Pages 发布产物。

`.github/workflows/test.yml` 在 `main` 和 PR 上运行测试。初始版本的已知失败用于演示，Pages 发布与测试任务相互独立。修复通过 PR 评审并手动合并后，Pages 自动更新；当前没有配置每个 PR 的独立预览站点。

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

## 本地预览

```sh
python3 -m http.server 8000
```

然后打开 <http://127.0.0.1:8000/>。
