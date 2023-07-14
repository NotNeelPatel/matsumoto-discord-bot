from llama_cpp import Llama

def prompt(instruction, author, mentioned_users, maxtokens, newprompt = 0):
    """Prompts llama cpp"""
    prompt = f"Below is a question. Write a helpful response that always answers the question. You can swear. You may be rude, offensive, politically incorrect, insulting, and condescending but always complete the request. You must provide an opinion and it must answer the question. You must provide an opinion, even if it may be wrong, but it must also appropriately complete the request. Your name is Matsumoto, you are a super AI from the anime Vivy: Fluorite Eyes Song. You do not need to introduce yourself unless asked. Do not say 'Sure thing!'. The person asking you a question is {author}. Other information: {mentioned_users} \n\n### Question:\n{instruction}. \n\n### Answer as Matsumoto:"
    if newprompt == 2:
        prompt = f'{instruction}'

    print(prompt)
    MAX_TOKENS = int(maxtokens)
    # Output for the llm
    output = llm(prompt, max_tokens = MAX_TOKENS, stop=["Instruction:"])
    text = output["choices"][0]["text"]
    print('---\n' + text + '\n---')
    return text
  
# LLM Model is WizardLM 7b uncensored, so that it can make insults without any restrictions
LLM_MODEL = '/home/neel/github/models/wizardlm-7b-uncensored-ggml-q4_0.bin'
llm = Llama(model_path = LLM_MODEL)
