import json
import typing


class GeneratorBackend(typing.Protocol):
    def complete(self, system: str, user: str, *, max_tokens: int = 700) -> str:
        ...


class TemplateBackend:
    def complete(self, system: str, user: str, *, max_tokens: int = 700) -> str:
        # If user contains the %%RENDER%% marker followed by JSON, process it
        if "%%RENDER%%" in user:
            try:
                # Extract the JSON part after %%RENDER%%
                render_start = user.find("%%RENDER%%") + len("%%RENDER%%")
                json_part = user[render_start:].strip()
                
                # Parse the JSON
                data = json.loads(json_part)
                facts = data.get("facts", {})
                style = data.get("style", "prose")
                
                # Build the clinical note based on style
                if style == "proforma":
                    # Each fact in a separate headed line
                    lines = []
                    for key, value in facts.items():
                        lines.append(f"{key}: {value}")
                    return "\n".join(lines)
                elif style == "prose":
                    # Single paragraph with all facts
                    values = [f"{k}: {v}" for k, v in facts.items()]
                    return " ".join(values)
                elif style == "terse":
                    # Telegraphic fragments
                    fragments = []
                    for key, value in facts.items():
                        fragments.append(f"{key}: {value}")
                    return "\n".join(fragments)
                elif style == "letter":
                    # Dear Colleague, ... Yours sincerely wrapper
                    lines = ["Dear Colleague,", ""]
                    for key, value in facts.items():
                        lines.append(f"{key}: {value}")
                    lines.extend(["", "Yours sincerely,", ""])
                    return "\n".join(lines)
                else:
                    # Default to prose if style is unknown
                    values = [f"{k}: {v}" for k, v in facts.items()]
                    return " ".join(values)
            except (json.JSONDecodeError, KeyError):
                # If JSON parsing fails, return the user text as-is
                pass
        
        # Otherwise, return the user text unchanged
        return user


class OllamaBackend:
    def __init__(self, model: str, host: str = "http://127.0.0.1:11434"):
        self.model = model
        self.host = host
    
    def complete(self, system: str, user: str, *, max_tokens: int = 700) -> str:
        raise NotImplementedError("ollama backend not wired yet")


class OpenAICompatibleBackend:
    def __init__(self, base_url: str, model: str, api_key_env: str):
        self.base_url = base_url
        self.model = model
        self.api_key_env = api_key_env
    
    def complete(self, system: str, user: str, *, max_tokens: int = 700) -> str:
        raise NotImplementedError


def get_backend(name: str, **kwargs) -> GeneratorBackend:
    if name == "template":
        return TemplateBackend()
    elif name == "ollama":
        return OllamaBackend(**kwargs)
    elif name == "openai-compatible":
        return OpenAICompatibleBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {name}")


__all__ = [
    "GeneratorBackend",
    "TemplateBackend",
    "OllamaBackend",
    "OpenAICompatibleBackend", 
    "get_backend"
]