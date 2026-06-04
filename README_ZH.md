# Ideogram 4 Prompter for ComfyUI

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Publisher](https://img.shields.io/badge/Publisher-saganaki22-purple)](https://github.com/Saganaki22)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-none-brightgreen)](requirements.txt)
[![Ideogram](https://img.shields.io/badge/Ideogram-4%20Magic%20Prompt-black)](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

[English](README.md) | [中文](README_ZH.md)

这是一个简单的 ComfyUI 自定义节点包，用于调用 Ideogram 4 Magic Prompt，并提供支持 Ideogram 4 全部比例的分辨率选择节点。

免费获取 Ideogram API Key: [Ideogram Manage API](https://ideogram.ai/manage-api)

## 为什么做这个节点包

Ideogram 4 可以使用结构化 JSON prompt schema，但很多用户很难稳定写对这个 schema，即使用本地 LLM agent 也经常会出错。这个节点包就是为了解决这个麻烦。

Ideogram 的 Magic Prompt API 可以使用，而且很适合放进 ComfyUI 工作流里。这个节点会把你的普通提示词发送到 Ideogram Magic Prompt API，然后返回结构化 JSON prompt。这样就不需要在本地消耗算力去生成或修复 Ideogram JSON prompt，也更适合算力有限的用户。

使用这个节点需要 Ideogram API Key 和网络连接。你的 API Key、prompt 和选择的 aspect ratio 会通过 Ideogram API 发送。

## 安装

### 通过 ComfyUI Manager 安装

1. 打开 ComfyUI Manager。
2. 点击 **Custom Nodes Manager**。
3. 搜索 `Ideogram 4 Prompter` 或 `ideogram4_prompter-ComfyUI`。
4. 点击 **Install**。
5. 重启 ComfyUI。

### 手动安装

将仓库克隆到 `ComfyUI/custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Saganaki22/ideogram4_prompter-ComfyUI.git
```

然后重启 ComfyUI。

本节点没有额外的 Python 依赖。

## 节点

### Ideogram 4 Magic Prompt

输入:

- `api_key`: Ideogram API Key。打开 [Ideogram Manage API](https://ideogram.ai/manage-api)，免费注册，点击 **Generate API key**，然后把生成的 Key 粘贴到节点里。这个 Key 会作为 `Api-Key` header 发送。
- `prompt`: 需要增强的文本提示词。
- `aspect_ratio`: Ideogram 4 原生比例选择器。`AUTO` 在最上面，后面是 Ideogram 4 支持的全部比例: `1x4`, `1x3`, `1x2`, `9x16`, `10x16`, `2x3`, `3x4`, `4x5`, `1x1`, `5x4`, `4x3`, `3x2`, `16x10`, `16x9`, `2x1`, `3x1`, `4x1`。
- `seed`: 仅用于打破 ComfyUI 缓存。想用同一个 prompt 重新请求一次 Magic Prompt、尝试不同输出时可以修改它。它不会发送给 Ideogram，也不能用于可复现结果。

输出:

- `magic_prompt_json`: Ideogram 免费 Magic Prompt API 返回的结果，以格式化 JSON 的形式作为 ComfyUI `STRING` 输出。
- `aspect_ratio`: Ideogram 4 解析后的比例，作为 combo 输出。如果输入选择 `AUTO`，这里会输出 Ideogram API 实际返回的比例。

### Ideogram 4 Resolution Selector

输入:

- `aspect_ratio`: Ideogram 4 比例 combo。可以直接连接 `Ideogram 4 Magic Prompt` 节点的 `aspect_ratio` 输出。
- `megapixels`: 目标总像素量，单位是百万像素。

输出:

- `width`: 计算后的宽度，四舍五入到 8 的倍数。
- `height`: 计算后的高度，四舍五入到 8 的倍数。
- `aspect_ratio_text`: 以 `STRING` 输出当前选择的 Ideogram 4 比例，方便连接文本预览节点。

## 推荐工作流

1. 添加 `Ideogram 4 Magic Prompt` 节点。
2. 把 Ideogram API Key 粘贴到 `api_key`。
3. 在多行 `prompt` 输入框里输入提示词。
4. 选择 aspect ratio，或者保持 `AUTO`。
5. 如果想用同一个 prompt 强制重新调用 Magic Prompt API，可以修改 `seed`。
6. 如果想查看生成的 JSON，可以把 `magic_prompt_json` 连接到文本预览节点。
7. 把 `magic_prompt_json` 作为 prompt 字符串传给你的 Ideogram 工作流或 sampler。
8. 把 `Ideogram 4 Magic Prompt.aspect_ratio` 连接到 `Ideogram 4 Resolution Selector.aspect_ratio`。
9. 在 `Ideogram 4 Resolution Selector` 上设置 `megapixels`。
10. 把 `width` 和 `height` 输出传给 Ideogram sampler。

如果选择 `AUTO`，Ideogram 会自动决定 aspect ratio。Magic Prompt 节点会输出这个解析后的比例，然后 Resolution Selector 会根据你的 `megapixels` 数值计算像素宽高。

## 工作方式

Magic Prompt 节点会把你的提示词发送到 Ideogram 免费 Magic Prompt API:

[https://api.ideogram.ai/v1/ideogram-v4/magic-prompt](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

Ideogram 会返回结构化的 `json_prompt` 和 `aspect_ratio`。本节点把 `json_prompt` 输出为 JSON 字符串，同时输出解析后的比例，方便连接到 `Ideogram 4 Resolution Selector` 计算宽高。

因为它使用 Ideogram 的在线 API，所以必须有网络连接才能工作。好处是可以节省本地算力，并减少处理 JSON schema 的麻烦。

## 示例工作流

仓库里包含一个 ComfyUI 示例工作流:

- [example_workflows/ideogram4_prompter_example_workflow-t2i.json](example_workflows/ideogram4_prompter_example_workflow-t2i.json)
- [example_workflows/ideogram4_prompter_example_workflow-t2i.png](example_workflows/ideogram4_prompter_example_workflow-t2i.png)
