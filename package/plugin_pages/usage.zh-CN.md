# 插件开发教程

本页随插件一起分发，并显示在 Infernux 的**插件**窗口中。它描述的就是用户实际安装的包，因此插件变化时也应同步更新这里。

## 包边界

只有仓库 `package/` 目录中的内容会进入 `.inxpkg`。仓库工具、CI 文件、中间构建产物以及该目录外的源素材都不会进入发行包。

```text
package/
├─ inx_package.json
├─ runtime/
│  └─ your_studio/example_plugin/
│     ├─ component.py
│     └─ preload.py
├─ editor/
│  ├─ translations.json
│  └─ your_studio/example_plugin_editor/
│     ├─ panel.py
│     └─ preload.py
├─ plugin_pages/
│  ├─ usage.md
│  ├─ usage.zh-CN.md
│  └─ media/
├─ requirements.txt
└─ samples/
```

三个保留目录各自承担明确职责：

- `runtime/` 放置 Editor 与构建后 Player 都需要的代码和原始资源，游戏组件应放在这里。Player 构建会编译这些 Python 源码，并自动发布组件、可序列化类型和 GUID 记录。
- `editor/` 放置面板、命令、导入工具及其它编辑功能。它只在 Editor 加载，不进入 Player。
- `plugin_pages/` 放置插件窗口显示的 Markdown、文本和相对引用图片。这里仅是文档，不执行代码。

包根下其它目录属于普通资产。Infernux 会把它们导入 `Assets/Plugins`，并通过正常资源与 Player Cook 流程处理。

## 组件和模块身份

`ExampleRotator` 是普通的 `InxComponent`。把它添加到 GameObject 后，可在 Inspector 调整 **Speed**。运行时代码应位于真正的 Python 包中，并使用明确的包导入。不要修改 `sys.path`、自行生成模块名，也不要替换 `sys.modules["infernux"]`。

每个源文件打包时都会获得稳定的资源 GUID。构建 Player 时，引擎把项目脚本和插件运行时脚本统一冻结到同一份组件/类型注册表和路径到 GUID 目录中。因此，Editor 序列化的组件会在 Windows、Linux、Web 和 Android Player 中解析为同一类型，作者无需维护第二份 Player 注册表。

已经发布的资产如需保持 GUID，应提交它的 `.meta` 文件。没有 `.meta` 时，独立打包器会生成确定性的 GUID 元数据。

## Preload 生命周期

需要在场景脚本之前完成的工作应继承 `InxPreload`。运行时 preload 放在 `runtime/`，Editor preload 放在 `editor/`；运行时 preload 不应导入 Editor 代码。

`preload(context)` 是资源取得阶段，`unload()` 是插件自行释放阶段。容易遗漏的资源应在取得后立刻登记清理函数：

```python
class ServicePreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        server = start_server()
        context.add_cleanup(server.stop)

    def unload(self) -> None:
        pass
```

清理函数会在 `unload()` 后按登记的逆序各执行一次；如果 `preload()` 执行到一半失败，也会执行。HTTP 服务、工作线程、文件监听、事件订阅和回调都应由它托管。每个清理过程都应完整且有时间边界：停止接收新任务、发出结束信号、等待线程退出，最后释放 socket 或句柄。

保存的候选脚本存在 Python 语法错误时，引擎会继续运行最后一次成功的生命周期。保存有效代码后，才会以一次替换事务完成热重载。在 Editor preload 中注册的面板、命令和快捷键归该事务所有，会在替换前自动移除。

### 大型 Python 包

`requirements.txt` 声明插件需要安装的 Python distribution。游戏逻辑依赖 `torch` 这类大型模块时，在运行时 preload 中导入是合理的：代价只在场景脚本启动前支付一次，不会推迟到每次 Play 或第一次游戏事件。

原生扩展模块可能持有进程全局状态。Infernux 会检测 preload 新加载的原生 Python 模块，并把替换或卸载标记为需要重启 Editor。只有插件创建了其它无法完全释放的进程状态时，才需要主动调用 `context.require_restart(reason)`。纯 Python 状态和正确关闭的 Flask 服务不需要它。

## 独立 Flask 工具窗口

基于 Flask 的创作工具应放在 `editor/`。从 Editor `InxPreload` 启动它，明确绑定本机回环地址，让操作系统分配可用端口，并通过 `context.add_cleanup` 登记完整关闭过程。再从插件面板或平台浏览器命令打开返回的本地 URL。不要在模块导入时启动 Flask，也不要启用开发重载器；它会产生生命周期不拥有的子进程。

```python
from threading import Thread
from werkzeug.serving import make_server

class ToolWindowPreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        app = create_app()
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = Thread(target=server.serve_forever, name="example-tool", daemon=True)
        thread.start()

        def stop() -> None:
            server.shutdown()
            thread.join(timeout=5.0)
            if thread.is_alive():
                raise RuntimeError("Example tool server did not stop")
            server.server_close()

        context.add_cleanup(stop)
        self.url = f"http://127.0.0.1:{server.server_port}/"
```

采用此方案时，把 Flask 与 Werkzeug 的精确版本写入 `requirements.txt`。除非 Player 本身确实要提供该服务，否则浏览器界面和服务端都应留在 `editor/`。

## Editor 面板与词条表

示例 Editor preload 会在自己的生命周期事务中导入 `panel.py`。它的五级位置是**扩展 → 示例插件 → 工具 → 诊断 → 实时 → 示例插件**。`menu_path` 为每一级提供默认文本，与之平行的 `menu_path_keys` 元组为每一级提供可选词条键；某一级需要保持原文时填写空字符串。一至五级以及更深路径都使用同一套协议。

插件词条表固定放在 `editor/translations.json`。Infernux 会在导入插件的 Editor preload 前完成校验和发布，并随插件生命周期自动移除。文件必须使用 `infernux.editor_translations` schema，包含 Editor 支持的全部语言，而且每种语言必须声明完全相同、带插件命名空间的键集合。插件不得覆盖引擎词条或其它插件拥有的键。第一级直接使用引擎的 `menu.extensions`，其余各级使用插件自己的命名空间。该文件属于 Editor，绝不会进入 Player。

## 从 File Manager 打包

在项目中直接开发插件时：

1. 创建一个文件夹，其中包含 `runtime`、`editor`、`plugin_pages`、可选普通资产以及可选的 `inx_package.json`。
2. 在 Project/File Manager 中选中该文件夹。
3. 右键并选择**导出 InxPackage...**。
4. 选择目标 `.inxpkg` 文件。
5. 在 Project 中双击生成的包，导入前检查文件角色与 GUID。

被选中的文件夹本身就是包根目录，不要在其中再增加一层 `package/`。多选会保留各项相对于共同父目录的路径。

对于当前 Git 仓库，`package/` 已经是包根。可从任意工作目录构建和验证：

```text
python package.py build dist/example-plugin.inxpkg
python package.py verify dist/example-plugin.inxpkg
```

完全相同的输入必须产生完全相同的字节。随附的 GitHub workflow 会检查 Python 源码、构建两次并比较两个归档；推送 `v<version>` tag 时，会发布 `.inxpkg` 及其 release manifest。

## 安装、更新和移除

可以在 Project 中打开 `.inxpkg`，也可以在插件窗口添加本地路径或 GitHub 仓库。检查将要写入的文件后再安装。运行时脚本通过插件生命周期热更新；不可逆的原生生命周期会明确要求重启，不会假装已经热重载。

更新属于事务。保留现有资产 GUID、提升 manifest 版本、发布对应的 `v<version>` tag，引擎会保留启用状态、用户移动的资产和导入设置。卸载会移除插件拥有的文件和生命周期贡献；本地用户文件以及已经转移给其它所有者的资产会保留。

## 发布检查表

- Runtime 代码不导入 Editor 模块。
- Editor 服务会释放线程、socket、监听器和回调。
- 组件能在 Editor 添加，也能在构建后的 Player 加载。
- 插件页面用中英文准确描述实际发行行为。
- `python package.py verify ...` 成功。
- 全新安装、热重载、禁用、更新、Player 构建和卸载均成功；只有原生状态确实要求时才重启。
