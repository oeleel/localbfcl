import os
from typing import Any

from bfcl_eval.model_handler.api_inference.openai_completion import OpenAICompletionsHandler
from bfcl_eval.constants.enums import ModelStyle
from openai import OpenAI
from overrides import override


class OpenRouterHandler(OpenAICompletionsHandler):
    """
    Handler for models accessed through OpenRouter API.
    OpenRouter provides OpenAI-compatible API access to various models including Qwen.
    
    To use this handler:
    1. Set OPENROUTER_API_KEY in your .env file
    2. The model_name should be the OpenRouter model identifier (e.g., "qwen/qwen-2.5-72b-instruct")
    """

    def __init__(
        self,
        model_name,
        temperature,
        registry_name,
        is_fc_model,
        **kwargs,
    ) -> None:
        super().__init__(model_name, temperature, registry_name, is_fc_model, **kwargs)
        self.model_style = ModelStyle.OPENAI_COMPLETIONS
        # Override the client to use OpenRouter's endpoint
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    #### FC methods ####

    @override
    def _query_FC(self, inference_data: dict):
        message: list[dict] = inference_data["message"]
        tools = inference_data["tools"]
        inference_data["inference_input_log"] = {"message": repr(message), "tools": tools}

        kwargs = {
            "messages": message,
            "model": self.model_name,
            "temperature": self.temperature,
        }

        if len(tools) > 0:
            kwargs["tools"] = tools

        return self.generate_with_backoff(**kwargs)

    #### Prompting methods ####

    @override
    def _query_prompting(self, inference_data: dict):
        message: list[dict] = inference_data["message"]
        inference_data["inference_input_log"] = {"message": repr(message)}

        return self.generate_with_backoff(
            messages=message,
            model=self.model_name,
            temperature=self.temperature,
        )

