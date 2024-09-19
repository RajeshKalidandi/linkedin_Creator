from gpt4all import GPT4All

try:
    models = GPT4All.list_models()
    print("Available models:")
    for model in models:
        print(model)
except Exception as e:
    print(f"Error listing models: {e}")
