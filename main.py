from src.agent.tracker import tracker_agent
import pyfiglet
import asyncio

async def main():

    # Create a font layout
    # The font used in your example is called 'big'
    banner_art = pyfiglet.figlet_format("ApplyTrack AI", font="big")

    print(f"\n{banner_art}\n\n")

    while True:

        user_input = input("\nEnter the task: ")

        if user_input.lower() == "exit" or user_input.lower() == "quit":
            print("GoodBye!")
            break

        await tracker_agent(user_input)

if __name__ == "__main__":
    asyncio.run(main())