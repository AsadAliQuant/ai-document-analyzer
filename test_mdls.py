import json
import ollama

def get_field(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

try:
    # List the installed models
    response = ollama.list()

    # Support both dict responses and typed objects (ListResponse)
    if isinstance(response, dict):
        models = response.get("models", [])
    else:
        models = getattr(response, "models", [])

    if isinstance(models, list) and len(models) > 0:
        print("Installed Ollama Models:")
        print("------------------------")
        for model in models:
            # Tolerate schema variations: typed objects have 'model', dicts might have 'name' or 'model'
            name = (
                get_field(model, "name")
                or get_field(model, "model")
                or "unknown"
            )
            size_bytes = get_field(model, "size", 0)

            size_gb = (
                round(size_bytes / (1024 ** 3), 2)
                if isinstance(size_bytes, (int, float)) and size_bytes
                else "unknown"
            )

            print(f"Name: {name}")
            print(f"Size: {size_gb} GB")
            print("------------------------")
    else:
        print("No models are currently installed in Ollama.")

except Exception as e:
    print(f"An error occurred: {e}")
    # Help debugging by printing raw response if available
    try:
        print("Raw response:")
        # Newer clients return pydantic models; try model_dump first
        if hasattr(response, "model_dump"):
            print(json.dumps(response.model_dump(), indent=2))
        else:
            print(response)
    except Exception:
        pass
    print("Please make sure the Ollama server is running in the background.")