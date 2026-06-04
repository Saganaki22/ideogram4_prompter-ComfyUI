"""ComfyUI node definitions for Ideogram 4 magic prompts."""

from __future__ import annotations

import json
import logging
import math
import urllib.error
import urllib.request

logger = logging.getLogger("Ideogram4_prompter-ComfyUI")

API_URL = "https://api.ideogram.ai/v1/ideogram-v4/magic-prompt"
API_KEY_URL = "https://ideogram.ai/manage-api"

IDEOGRAM_ASPECT_RATIOS = [
    "1x4",
    "1x3",
    "1x2",
    "9x16",
    "10x16",
    "2x3",
    "3x4",
    "4x5",
    "1x1",
    "5x4",
    "4x3",
    "3x2",
    "16x10",
    "16x9",
    "2x1",
    "3x1",
    "4x1",
]

MAGIC_PROMPT_ASPECT_RATIOS = ["AUTO", *IDEOGRAM_ASPECT_RATIOS]

ASPECT_RATIO_VALUES = {
    "AUTO": "AUTO",
    **{ratio: ratio for ratio in IDEOGRAM_ASPECT_RATIOS},
}


def _aspect_ratio_value(option: str) -> str:
    option = str(option or "AUTO").strip()
    if option in ASPECT_RATIO_VALUES:
        return ASPECT_RATIO_VALUES[option]
    if option.upper() == "AUTO":
        return "AUTO"
    return option.split()[0].replace(":", "x")


def _resolved_ideogram_aspect_ratio(aspect_ratio: str, fallback: str = "1x1") -> str:
    aspect_ratio = str(aspect_ratio or "").strip()
    if aspect_ratio in IDEOGRAM_ASPECT_RATIOS:
        return aspect_ratio

    normalized = aspect_ratio.split()[0].replace(":", "x")
    if normalized in IDEOGRAM_ASPECT_RATIOS:
        return normalized

    return fallback


def _ratio_dimensions(aspect_ratio: str) -> tuple[int, int]:
    width, height = aspect_ratio.split("x", 1)
    return int(width), int(height)


def _read_error_body(error: urllib.error.HTTPError) -> str:
    try:
        return error.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


class Ideogram4MagicPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "tooltip": "Get a free key at https://ideogram.ai/manage-api, click Generate API key, then paste it here.",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Text prompt to enhance with Ideogram 4 Magic Prompt.",
                    },
                ),
                "aspect_ratio": (
                    "COMBO",
                    {
                        "options": MAGIC_PROMPT_ASPECT_RATIOS,
                        "default": "AUTO",
                        "tooltip": "AUTO lets Ideogram choose. Other values are the exact Ideogram 4 aspect ratios.",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 2**31 - 1,
                        "tooltip": "Cache buster only. Change this to rerun the same prompt for a different Magic Prompt output if the result is not to your liking. Not sent to Ideogram and not for reproducible results.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "COMBO")
    RETURN_NAMES = ("magic_prompt_json", "aspect_ratio")
    OUTPUT_TOOLTIPS = (
        "The free Ideogram Magic Prompt API json_prompt response as formatted JSON.",
        "Resolved Ideogram 4 aspect ratio. Plug this into the Ideogram 4 Resolution Selector aspect_ratio input.",
    )
    FUNCTION = "generate"
    CATEGORY = "Ideogram"
    DESCRIPTION = (
        "Generate an Ideogram 4 magic prompt JSON string from text. "
        "Get a free API key at https://ideogram.ai/manage-api, click Generate API key, "
        "and paste it into the api_key field. The request is sent to Ideogram's free "
        "Magic Prompt API and the returned json_prompt is output as JSON."
    )

    def generate(self, api_key: str, prompt: str, aspect_ratio: str, seed: int) -> tuple[str, str]:
        api_key = str(api_key or "").strip()
        prompt = str(prompt or "").strip()
        _ = seed

        if not api_key:
            raise ValueError("Ideogram API key is required.")
        if not prompt:
            raise ValueError("Prompt is required.")

        api_aspect_ratio = _aspect_ratio_value(aspect_ratio)
        payload = {
            "text_prompt": prompt,
            "aspect_ratio": api_aspect_ratio,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "Api-Key": api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            error_body = _read_error_body(error)
            message = error_body[:2000] if error_body else error.reason
            raise RuntimeError(f"Ideogram API error {error.code}: {message}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Ideogram API request failed: {error.reason}") from error

        fallback_aspect_ratio = "1x1" if api_aspect_ratio == "AUTO" else api_aspect_ratio

        try:
            data = json.loads(response_body)
        except json.JSONDecodeError:
            logger.warning("Ideogram returned non-JSON response.")
            return (response_body, fallback_aspect_ratio)

        magic_prompt = data.get("json_prompt", data)
        resolved_aspect_ratio = _resolved_ideogram_aspect_ratio(
            str(data.get("aspect_ratio") or ""),
            fallback=fallback_aspect_ratio,
        )
        return (
            json.dumps(magic_prompt, ensure_ascii=False, indent=2),
            resolved_aspect_ratio,
        )


class Ideogram4ResolutionSelector:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (
                    "COMBO",
                    {
                        "options": IDEOGRAM_ASPECT_RATIOS,
                        "default": "1x1",
                        "tooltip": "Exact Ideogram 4 aspect ratio. Can be connected from Ideogram 4 Magic Prompt.",
                    },
                ),
                "megapixels": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.1,
                        "max": 16.0,
                        "step": 0.1,
                        "tooltip": "Target total megapixels. 1.0 MP is about 1024x1024 for square.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "aspect_ratio_text")
    OUTPUT_TOOLTIPS = (
        "Calculated width in pixels, rounded to a multiple of 8.",
        "Calculated height in pixels, rounded to a multiple of 8.",
        "The selected Ideogram 4 aspect ratio as text for preview nodes.",
    )
    FUNCTION = "select"
    CATEGORY = "Ideogram"
    DESCRIPTION = "Calculate width and height from any Ideogram 4 aspect ratio and a megapixel target."

    def select(self, aspect_ratio: str, megapixels: float) -> tuple[int, int, str]:
        aspect_ratio = _resolved_ideogram_aspect_ratio(aspect_ratio)
        width_ratio, height_ratio = _ratio_dimensions(aspect_ratio)
        total_pixels = float(megapixels) * 1024 * 1024
        scale = math.sqrt(total_pixels / (width_ratio * height_ratio))
        width = max(8, round(width_ratio * scale / 8) * 8)
        height = max(8, round(height_ratio * scale / 8) * 8)
        return (width, height, aspect_ratio)


NODE_CLASS_MAPPINGS = {
    "Ideogram4MagicPrompt": Ideogram4MagicPrompt,
    "Ideogram4ResolutionSelector": Ideogram4ResolutionSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Ideogram4MagicPrompt": "Ideogram 4 Magic Prompt",
    "Ideogram4ResolutionSelector": "Ideogram 4 Resolution Selector",
}
