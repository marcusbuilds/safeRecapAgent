import ollama

def test_ollama():
    client = ollama.Client()
    model = "gpt-oss:latest"
    #model = "safeRecap"
    # Example prompt
    prompt = "What is lego?"
    response = client.generate(model=model, prompt=prompt)
    print(f"Ollama response: {response.response}")