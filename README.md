# DSH Pages Demo

一个可部署到 GitHub Pages 的小型静态页面，用于测试 GitHub Issue → Agent 修复 → PR → 评审后继续修改的流程。页面展示虚构联系人，不需要 API、数据库或真实个人信息。

发布后的页面是一个简单的“联系人导出器”产品介绍页：打开 `index.html` 即可预览。

## 环境和运行

需要 Python 3.10 或更新版本，无需安装第三方包。在仓库根目录运行：

```sh
python3 -m unittest discover -v
```

页面早期版本保留了有意设置的视觉回归：主按钮文字与背景颜色相同，按钮文字几乎不可见。`tests/test_site.py` 会检测这个问题。该回归已修复：主按钮使用 `--ink` 文字配 `--cta`（`#58c793`）绿色背景，对比度约 7.85:1，悬停时换成 `--cta-hover`；修复前后的截图见 `docs/screenshots/`。

演练版本曾保留一个跳转回归：点击首页“查看测试流程”按钮不能滚动到下方流程区。该回归已修复：主按钮的锚点原来误写为 `#workfow`，改为与顶部“流程”链接一致的 `#workflow` 后，点击会平滑滚动到流程区。`tests/test_site.py` 的 `test_primary_action_scrolls_to_workflow_section` 会锁定这一行为，现有链接检查也会捕获错误的锚点；当前 19 项测试应全部通过。按钮对比度、页面动画及 CSV 功能保持不变，跳转前后的点击截图见 `docs/screenshots/cta-scroll-*.png`。

## GitHub Pages

仓库为 `x-era/dsh-pages-demo`，页面地址为 `https://x-era.github.io/dsh-pages-demo/`，无需占用账号根站点的 `x-era.github.io` 仓库。初次发布完成前，这两个地址可能尚不可用。

在仓库 Settings → Pages 中选择 **GitHub Actions**。`.github/workflows/pages.yml` 会在 `main` 更新后发布页面，仅上传 `index.html`、`styles.css` 和 `.nojekyll`。Python 源码、测试和操作记录不会进入 Pages 发布产物。

`.github/workflows/test.yml` 在 `main` 和 PR 上运行测试。初始版本的已知失败用于演示，Pages 发布与测试任务相互独立。修复通过 PR 评审并手动合并后，Pages 自动更新；当前没有配置每个 PR 的独立预览站点。

## 页面动效

页面动效全部由 `styles.css` 实现，不使用 JavaScript，因此 Pages 发布产物仍然只有 `index.html`、`styles.css` 和 `.nojekyll`。

- 首屏入场：页头、标题、正文、按钮和预览卡片依次淡入并轻微上移，总时长约 0.4 秒。
- 持续动效：预览卡片缓慢上下漂浮，状态圆点和迷你折线图轻微呼吸，作为页面唯一的循环动画。
- 交互反馈：导航、主按钮、文字链接、功能卡片和流程条目在悬停时轻微位移或变色，键盘聚焦时显示可见的焦点描边。

所有动效都写在 `@media (prefers-reduced-motion: no-preference)` 中；当系统开启“减少动态效果”时，页面回退为完全静态的原始版本（`scroll-behavior` 也一并改回 `auto`）。`tests/test_motion.py` 会检查这一约束，以及页面不依赖 JavaScript。动效前后的对照与入场中间帧见 `docs/screenshots/motion-*.png`。

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
