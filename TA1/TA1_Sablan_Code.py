import agentpy as ap
import random
import matplotlib.pyplot as plt


class RandomWalker(ap.Agent):

    def setup(self):
        self.path = []

    def step(self):
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]

        x, y = self.position
        possible_positions = []

        # Find valid neighboring positions
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy

            if (
                0 <= new_x < self.model.p.grid_size[0]
                and 0 <= new_y < self.model.p.grid_size[1]
            ):
                possible_positions.append((new_x, new_y))

        # Identify positions occupied by other agents
        occupied_positions = {
            agent.position
            for agent in self.model.agents
            if agent is not self
        }

        # Select an unoccupied neighboring position
        free_positions = [
            position
            for position in possible_positions
            if position not in occupied_positions
        ]

        if free_positions:
            self.position = random.choice(free_positions)
        else:
            self.position = (x, y)

        self.path.append(self.position)


class RandomWalkModel(ap.Model):

    def setup(self):
        self.agents = ap.AgentList(
            self,
            self.p.agents,
            RandomWalker
        )

        # Assign initial positions
        for agent in self.agents:
            agent.position = (
                random.randint(0, self.p.grid_size[0] - 1),
                random.randint(0, self.p.grid_size[1] - 1)
            )

            agent.path = [agent.position]

    def step(self):
        for agent in self.agents:
            agent.step()

    def end(self):
        print("\nFinal Positions:")
        position_counts = {}

        for agent_number, agent in enumerate(
            self.agents,
            start=1
        ):
            print(f"Agent {agent_number}: {agent.position}")

            if agent.position not in position_counts:
                position_counts[agent.position] = 0

            position_counts[agent.position] += 1

        print("\nFinal Position Distribution:")

        for position, count in position_counts.items():
            print(
                f"Position {position}: "
                f"{count} agent(s)"
            )


def run_simulation(
    scenario_name,
    num_agents,
    grid_size,
    num_steps
):
    print("\n" + "=" * 60)
    print(scenario_name)
    print("=" * 60)
    print(f"Number of agents: {num_agents}")
    print(f"Grid size: {grid_size} x {grid_size}")
    print(f"Number of steps: {num_steps}")

    parameters = {
        "agents": num_agents,
        "grid_size": (grid_size, grid_size),
        "steps": num_steps
    }

    model = RandomWalkModel(parameters)
    model.setup()

    # Run the simulation
    for _ in range(num_steps):
        model.step()

    model.end()

    # Plot the paths of all agents
    plt.figure(figsize=(8, 8))

    for agent_number, agent in enumerate(
        model.agents,
        start=1
    ):
        x_values = [
            position[0]
            for position in agent.path
        ]

        y_values = [
            position[1]
            for position in agent.path
        ]

        plt.plot(
            x_values,
            y_values,
            marker="o",
            markersize=3,
            label=f"Agent {agent_number}"
        )

        # Mark the final position
        plt.scatter(
            agent.position[0],
            agent.position[1],
            s=100
        )

    plt.xlim(-0.5, grid_size - 0.5)
    plt.ylim(-0.5, grid_size - 0.5)
    plt.xticks(range(grid_size))
    plt.yticks(range(grid_size))
    plt.grid(True)

    plt.title(
        f"{scenario_name}\n"
        "Random Walk Agent Paths"
    )
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return model


# Main program
if __name__ == "__main__":

    print("=" * 60)
    print("RANDOM WALK SIMULATION USING AGENTPY")
    print("LABORATORY TASKS 1-4")
    print("=" * 60)

    # Scenario 1: 5 agents, 20 steps
    scenario1 = run_simulation(
        scenario_name="Scenario 1",
        num_agents=5,
        grid_size=10,
        num_steps=20
    )

    # Scenario 2: 10 agents, 50 steps
    scenario2 = run_simulation(
        scenario_name="Scenario 2",
        num_agents=10,
        grid_size=10,
        num_steps=50
    )

    # Compare scenarios
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON")
    print("=" * 60)

    print("""
Scenario 1:
- 5 agents
- 10 x 10 grid
- 20 steps

Scenario 2:
- 10 agents
- 10 x 10 grid
- 50 steps
""")
