#TASK 1

environment = {"A": None, "B": None}


def ask_room_state(room):
    """Ask the user for a room's initial state until the input is valid."""
    while True:
        answer = input(f"Is room {room} Dirty or Clean? ").strip().capitalize()
        if answer in ("Dirty", "Clean"):
            return answer
        print("Please type 'dirty' or 'clean'.")


def is_dirty(env, room):
    """Return True if the given room is dirty."""
    return env[room] == "Dirty"


def clean_room(env, room):
    """Clean the given room (set its state to Clean)."""
    env[room] = "Clean"

#TASK 2

class VacuumAgent:
    def __init__(self, start_room="A"):
        self.location = start_room

    def move(self):
        """Switch to the other room."""
        self.location = "B" if self.location == "A" else "A"

    def perceive_and_act(self, env):
        """Perceive the current room and act using the rules."""
        if is_dirty(env, self.location):
            #Rule 1 - if dirty, clean it
            clean_room(env, self.location)
            return f"Room {self.location} has been cleaned."
        else:
            #Rule 2 - if clean, move to the other room
            self.move()
            return f"Moving to room {self.location}"

#TASK 3

def main():
    for room in environment:
        environment[room] = ask_room_state(room)

    #steps
    while True:
        try:
            steps = int(input("\nHow many steps should the agent run? "))
            if steps > 0:
                break
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a whole number.")

    agent = VacuumAgent("A")

    for step in range(1, steps + 1):
        print(f"\nStep {step}: Agent is in room {agent.location}")
        action = agent.perceive_and_act(environment)  # perceive + act
        print(action)
        print(f"Environment state: {environment}")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()