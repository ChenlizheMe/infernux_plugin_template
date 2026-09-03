# Infernux 插件模板

[English](README.md)

这个模板把“怎么开发”与“最终分发什么”彻底分开。仓库外层可以使用 CMake、Cargo、Gradle、npm 或任意工具；只有放进 `package/` 的文件才进入 `.inxpkg`。外层 README、构建配置、CI、源码树和临时产物都不会被打包。

## 快速开始

1. 修改 `package/inx_package.json`，设置全局唯一的小写插件标识。
2. Player 可用文件放进 `package/runtime/`，仅编辑器可用文件放进 `package/editor/`，普通资产放进 `package/` 下其它小写目录。
3. 外层构建完成后，把最终依赖的 `.dll`、`.so`、`.pyd`、`.wasm`、Java 资源、Shader、材质、网页或任意文件放进 `package/`。
4. 不安装 Infernux，直接打包和校验：

   ```powershell
   python package.py build dist/example-plugin.inxpkg
   python package.py verify dist/example-plugin.inxpkg
   ```

## 目录结构

```text
infernux-plugin/
├─ package.py                     只依赖 Python 标准库的打包器
├─ CMakeLists.txt / build.gradle  可选开发工具，不进入包
├─ README.md                      仓库文档，不进入包
├─ package/
│  ├─ inx_package.json            插件身份与引擎兼容范围
│  ├─ runtime/                    Editor 与 Player 均可用
│  ├─ editor/                     只供 Editor 使用
│  ├─ plugin_pages/               插件面板中的独立页面
│  ├─ requirements.txt            可选、固定文件名的 Python 依赖
│  └─ samples/、shaders/、web/    安装到 Assets/Plugins 的普通资产
└─ .github/workflows/             仓库自动化，不进入包
```

manifest 不再包含 `requirements` 或 `dependencies` 字段。存在 `requirements.txt` 时，引擎按固定文件名识别。包格式不会猜测 `.pyd`、`.wasm`、材质、Shader、HTML 或未知文件的含义，它们都只是字节；目录位置决定文件所有权和是否导出到 Player。

```json
{
  "$schema": "infernux.inxpackage.source",
  "reference": "your-studio/example-plugin",
  "name": "Example Plugin",
  "version": "0.1.0",
  "engine": ">=0.4,<0.5",
  "intro": "A minimal Infernux runtime and editor extension."
}
```

插件面板文档只从 `plugin_pages/` 发现；仓库根部 README 和许可证不再被当成插件文件。推送 `v<version>` tag 后，模板工作流会构建两次并比较确定性字节，然后发布 `.inxpkg` 与 `infernux-plugin-release.json`。
