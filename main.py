from scr.chat import ChatAgent

if __name__ == "__main__":
    agent = ChatAgent()
    while True:
        print("="*50)
        prompt = input("请输入：")
        print(agent.chat(prompt))
