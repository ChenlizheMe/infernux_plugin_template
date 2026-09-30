# Infernux 插件模板

这是 [Infernux](https://github.com/ChenlizheMe/Infernux) 游戏引擎的官方插件项目模板。无论你准备开发 Python 扩展、原生库、Java 工具、WebAssembly 模块，还是分发 Shader、材质、网页和其他项目资源，都可以从这个仓库开始。

[English](README.md) · [Infernux 引擎](https://github.com/ChenlizheMe/Infernux) · [插件开发文档](https://github.com/ChenlizheMe/Infernux/tree/master/docs) · [官方插件](https://github.com/ChenlizheMe/Infernux#plugins)

```mermaid
flowchart LR
    A[源码与构建工具] --> B[package/]
    B --> C[package.py]
    C --> D[可安装的 .inxpkg]
    D --> E[Infernux 编辑器与 Player]
```

## 创建第一个插件

1. 在 GitHub 页面点击 **Use this template**，创建并克隆自己的插件仓库。
2. 修改 `package/inx_package.json`：填写全局唯一的小写 `reference`、插件名称、版本号和支持的 Infernux 版本范围。
3. 运行时文件放在 `package/runtime/`，只供编辑器使用的代码放在 `package/editor/`，插件窗口中的介绍文档放在 `package/plugin_pages/`。其他资产可以按插件需要组织目录。
4. 构建并校验安装包：

   ```powershell
   python package.py build dist/example-plugin.inxpkg
   python package.py verify dist/example-plugin.inxpkg
   ```

`package.py` 只使用 Python 标准库，打包时不需要安装 Infernux。仓库可以自由使用 CMake、Gradle、Cargo、npm 或其他构建工具；只需把用户运行插件时真正需要的文件放进 `package/`。

在 Infernux 项目中，被选中的文件夹本身就是包根：在 Project/File Manager 中选中它，右键选择**导出 InxPackage...**。安装后插件页面中的完整教程会说明生命周期所有权、热重载、Player 组件注册、大型包导入以及仅 Editor 使用的 Flask 独立工具窗口。

## 目录结构

```text
your-plugin/
├─ package.py                  独立的 InxPackage 打包器
├─ README.md                   GitHub 仓库说明
├─ package/
│  ├─ inx_package.json         标识、版本与引擎兼容范围
│  ├─ runtime/                 编辑器和导出的 Player 都可使用
│  ├─ editor/                  仅供编辑器使用的代码、工具和 translations.json
│  ├─ plugin_pages/            插件窗口中显示的介绍页面
│  ├─ requirements.txt         可选的 Python 依赖
│  └─ shaders/、web/、samples/ 可选的插件资产
└─ .github/workflows/          自动校验与发布流程
```

最终只有 `package/` 会进入 `.inxpkg`。源码、构建配置、仓库 README、测试和临时产物都留在包外。打包器不会限制文件类型；Infernux 根据目录位置决定安装位置以及是否随 Player 导出。

## 自动发布

每个 Pull Request 和推送到 `main` 的提交都会校验 manifest，并确认两次构建得到完全一致的包。准备发布时，先更新 manifest 中的版本，再推送对应的 `v<version>` 标签。GitHub Actions 会把 `.inxpkg` 和 `infernux-plugin-release.json` 自动上传到 GitHub Release，供 Infernux 插件窗口识别和安装。

完整的生产项目可以参考 [Windows](https://github.com/ChenlizheMe/infernux_windows)、[Linux](https://github.com/ChenlizheMe/infernux_linux)、[Web](https://github.com/ChenlizheMe/infernux_web)、[Android](https://github.com/ChenlizheMe/infernux_android) 和 [MCP](https://github.com/ChenlizheMe/infernux_mcp) 官方插件。

插件面板文档只从 `plugin_pages/` 发现。Runtime 与 Editor preload 被明确分开：运行时组件与 preload 会 Cook 进 Player，Editor 面板和工具不会。线程、服务、文件监听与回调一经创建就应交给 `PreloadContext.add_cleanup()`；引擎会在热重载、禁用、卸载与项目关闭时移除生命周期拥有的贡献。

模板包含 `editor/translations.json`。Infernux 会在 Editor preload 前加载这份归属于插件包的词条表，把它用于面板标题及每一级菜单，并在禁用、卸载或热重载时自动移除。

## 许可证

[MIT](LICENSE)。
