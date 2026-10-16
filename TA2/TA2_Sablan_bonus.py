#Bonus

import random

environment = {"A": None, "B": None, "C": None}


def ask_room_state(room):
    """Ask the user for a room's initial state until the input is valid."""
    while True:
        answer = input(f"Is room {room} Dirty or Clean? ").strip().capitalize()
        if answer in ("Dirty", "Clean"):
            return answer
        print("Please type 'dirty' or 'clean'.")


def is_dirty(env, room):
    return env[room] == "Dirty"


def clean_room(env, room):
    env[room] = "Clean"


def show_grid(env, agent_room):
    """Text-based grid: the agent's room shows 'Agent', others show state."""
    cells = []
    for room, state in env.items():
        label = "Agent" if room == agent_room else state
        cells.append(f"[{room}-{label}]")
    print("  ".join(cells))


class VacuumAgent:
    def __init__(self, start_room="A"):
        self.location = start_room

    def move_to(self, room):
        self.location = room

    def perceive_and_act(self, env):
        #Rule 1 - if dirty, clean it
        if is_dirty(env, self.location):
            clean_room(env, self.location)
            return f"Room {self.location} has been cleaned."

        #Rule 2 - if clean, move to the other room
        dirty_rooms = [r for r in env if is_dirty(env, r)]
        if dirty_rooms:
            target = random.choice(dirty_rooms)
            self.move_to(target)
            return f"Moving to room {target}"

        return "All rooms are clean. Agent is idle."


def main():
    for room in environment:
        environment[room] = ask_room_state(room)

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
        print(f"\nStep {step}:")
        show_grid(environment, agent.location)   # state before acting
        action = agent.perceive_and_act(environment)
        print(action)
        show_grid(environment, agent.location)   # state after acting

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()