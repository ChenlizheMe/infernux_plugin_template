# Infernux 插件模板

[English](README.md)

![插件包布局](InxPluginPages/media/package-layout.svg)

这个仓库用于创建同时包含运行时代码、编辑器工具、文档、本地化页面和示例资产的 Infernux 插件。开发时可以把仓库直接放进项目，也可以点击 GitHub 的 **Use this template** 创建独立仓库。

## 快速开始

1. 将 `InxPackage.json` 中的 `your-studio/example-plugin` 改成全局唯一的小写标识。
2. 重命名 `Runtime/your_studio/example_plugin` 和 `Editor/your_studio/example_plugin_editor`，并同步修改 import 和面板 `type_id`。
3. 在 Infernux 项目中直接打开这个仓库，像普通项目资产一样编辑并测试组件和编辑器面板。
4. 在 `infernux` 环境中构建分发包：

   ```powershell
   conda activate infernux
   python .infernux-dev/build.py
   ```

5. 在另一个项目中导入 `dist/example-plugin.inxpkg`，或在插件面板中输入仓库 Git 地址安装。

## 目录说明

```text
infernux-plugin/
├─ InxPackage.json                 插件标识、版本、引擎范围和依赖
├─ requirements.txt               pip 依赖和注册表插件标识
├─ README.md                       插件面板默认简介
├─ README.zh-CN.md                 简体中文简介
├─ LICENSE                         默认许可证页面
├─ CHANGELOG.md
├─ CHANGELOG.zh-CN.md
├─ Runtime/
│  └─ your_studio/example_plugin/ 玩家包可用的组件、API 和预载生命周期
├─ Editor/
│  └─ your_studio/example_plugin_editor/ 仅编辑器使用的面板和创作工具
├─ InxPluginPages/
│  ├─ Usage.md                     附加信息选项页
│  ├─ Usage.zh-CN.md               使用固定 zh-CN 后缀的中文页
│  └─ media/                       README 和信息页引用的图片
├─ Samples/
│  ├─ Scenes/
│  ├─ Materials/
│  └─ Scripts/                     安装到 Assets/Plugins 的普通资产
├─ .infernux-dev/                  本地构建和校验工具，不进入插件包
└─ .github/workflows/              仓库校验，不进入插件包
```

`Runtime/`、`Editor/`、manifest、README、许可证、requirements 和 `InxPluginPages/` 属于受控包内容，安装到 `Packages/<reference>`。其它顶层内容安装到 `Assets/Plugins/<reference>`，因此场景、材质、Prefab、纹理和脚本都可以随插件分发，同时不会污染项目根目录。

## 配置示例

```json
{
  "reference": "your-studio/example-plugin",
  "name": "Example Plugin",
  "version": "0.1.0",
  "engine": ">=0.3.7,<0.4",
  "dependencies": ["your-studio/foundation"],
  "requirements": "requirements.txt"
}
```

标识本身就是命名空间，可以使用 `company/physics/jolt` 这样的多级结构。插件依赖会先通过插件注册表解析，再处理 pip 依赖。`requirements.txt` 可以包含普通 pip 语法、注册表插件标识和嵌套 `.inxpkg` 路径。

## 预载与编辑器工具

只有继承 `InxPreload` 的类会被提前导入。使用 `preload()` 注册进程内服务或载入编辑器贡献，并在 `unload()` 中释放无需重启即可移除的状态。玩家构建会忽略 `Editor/`；示例预载也只会在 `context.runtime` 为 false 时导入面板。

## 本地化

英文或默认内容使用不带后缀的文件名，简体中文只使用固定的 `.zh-CN`：

- `README.md` 与 `README.zh-CN.md`
- `Usage.md` 与 `Usage.zh-CN.md`
- `LICENSE` 与可选的 `LICENSE.zh-CN.md`

相对路径图片可以和文档放在一起，或统一放入 `InxPluginPages/media/`。
