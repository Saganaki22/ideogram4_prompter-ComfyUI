# Ideogram 4 Prompter for ComfyUI

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Publisher](https://img.shields.io/badge/Publisher-saganaki22-purple)](https://github.com/Saganaki22)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-none-brightgreen)](requirements.txt)
[![Ideogram](https://img.shields.io/badge/Ideogram-4%20Magic%20Prompt-black)](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

[English](README.md) | [中文](README_ZH.md)

Simple ComfyUI custom nodes for Ideogram 4 Magic Prompt and Ideogram 4 aspect-ratio resolution selection.

Get a free Ideogram API key here: [Ideogram Manage API](https://ideogram.ai/manage-api)

## Why this exists

Ideogram 4 can use a structured JSON prompt schema, but many people struggle to write that schema correctly, even when using a local LLM agent. This node pack was made to remove that friction.

The Magic Prompt API was available, free to use, and a good fit for ComfyUI workflows. Instead of spending local compute trying to generate valid Ideogram JSON prompts, this node sends your basic prompt to Ideogram's Magic Prompt API and returns the structured JSON prompt for you. It is especially helpful for users with less compute, or anyone who wants to avoid the hassle of hand-writing or debugging the JSON prompt schema.

This requires an Ideogram API key and an internet connection. Your API key, prompt, and selected aspect ratio are sent through Ideogram's API.

## Install

### ComfyUI Manager

1. Open ComfyUI Manager.
2. Click **Custom Nodes Manager**.
3. Search for `Ideogram 4 Prompter` or `ideogram4_prompter-ComfyUI`.
4. Click **Install**.
5. Restart ComfyUI.

### Manual

Clone this repo into `ComfyUI/custom_nodes/`:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Saganaki22/ideogram4_prompter-ComfyUI.git
```

Then restart ComfyUI.

No extra Python packages are required.

## Nodes

### Ideogram 4 Magic Prompt

Inputs:

- `api_key`: Ideogram API key. Go to [Ideogram Manage API](https://ideogram.ai/manage-api), sign up for free, click **Generate API key**, then paste the generated key into the node. The key is sent as the `Api-Key` header.
- `prompt`: Text prompt to enhance.
- `aspect_ratio`: Native Ideogram 4 aspect ratio selector. `AUTO` is first, followed by the exact Ideogram 4 ratios: `1x4`, `1x3`, `1x2`, `9x16`, `10x16`, `2x3`, `3x4`, `4x5`, `1x1`, `5x4`, `4x3`, `3x2`, `16x10`, `16x9`, `2x1`, `3x1`, and `4x1`.
- `seed`: Cache buster only. Change it to rerun the same prompt for a different Magic Prompt output if the result is not to your liking. It is not sent to Ideogram and is not for reproducible results.

Outputs:

- `magic_prompt_json`: The free Ideogram Magic Prompt API response, returned as formatted JSON in a ComfyUI `STRING`.
- `aspect_ratio`: The resolved Ideogram 4 aspect ratio as a combo output. If the input was `AUTO`, this is the aspect ratio returned by Ideogram.

### Ideogram 4 Resolution Selector

Inputs:

- `aspect_ratio`: Ideogram 4 aspect ratio combo. You can connect this from the `Ideogram 4 Magic Prompt` node's `aspect_ratio` output.
- `megapixels`: Target total megapixels.

Outputs:

- `width`: Calculated width, rounded to a multiple of 8.
- `height`: Calculated height, rounded to a multiple of 8.
- `aspect_ratio_text`: The selected Ideogram 4 aspect ratio as a `STRING`, useful for text preview nodes.

## Recommended workflow

1. Add `Ideogram 4 Magic Prompt`.
2. Paste your Ideogram API key into `api_key`.
3. Enter your prompt in the multiline `prompt` field.
4. Choose an aspect ratio, or leave it on `AUTO`.
5. Change `seed` when you want to force another Magic Prompt API call for the same prompt.
6. Connect `magic_prompt_json` to a text preview node if you want to inspect the generated JSON.
7. Pass `magic_prompt_json` as the prompt string for your Ideogram workflow or sampler.
8. Connect `Ideogram 4 Magic Prompt.aspect_ratio` to `Ideogram 4 Resolution Selector.aspect_ratio`.
9. Set `megapixels` on `Ideogram 4 Resolution Selector`.
10. Pass the selector's `width` and `height` outputs to your Ideogram sampler.

When `AUTO` is selected, Ideogram chooses the aspect ratio. The Magic Prompt node outputs that resolved ratio, and the Resolution Selector calculates pixel dimensions from it using your `megapixels` value.

## How it works

The Magic Prompt node sends your prompt to Ideogram's free Magic Prompt API:

[https://api.ideogram.ai/v1/ideogram-v4/magic-prompt](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

Ideogram returns a structured `json_prompt` and an `aspect_ratio`. This node outputs the prompt as a JSON string and outputs the resolved aspect ratio so it can drive the `Ideogram 4 Resolution Selector`.

Because this uses Ideogram's hosted API, it needs network access to work. The tradeoff is that it saves local compute and avoids a lot of JSON schema hassle.

## Example workflow

An example ComfyUI workflow is included:

- [example_workflows/ideogram4_prompter_example_workflow-t2i.json](example_workflows/ideogram4_prompter_example_workflow-t2i.json)
- [example_workflows/ideogram4_prompter_example_workflow-t2i.png](example_workflows/ideogram4_prompter_example_workflow-t2i.png)
