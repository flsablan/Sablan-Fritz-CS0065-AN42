#Task 1A
facts = {
    #power-related facts
    "power": {
        "powered_on": True,
        "battery_level": 15, # percent
        "is_charging": False,
    },
    #performance-related facts
    "performance": {
        "cpu_temperature": 90, # degrees Celsius
        "fan_noise_loud": True,
    },
    #display-related facts
    "display": {
        "screen_flicker": False,
        "screen_black": False,
    },
}


#Task 2A
def rule_low_battery(facts):
    #If battery is below 20% and the laptop is not charging, then tell the user to plug in the charger
    if facts["power"]["battery_level"] < 20 and not facts["power"]["is_charging"]:
        return "Plug in the charger"


def rule_wont_turn_on(facts):
    #If the laptop is not powered on, then do a hard reset and try another outlet
    if not facts["power"]["powered_on"]:
        return "Hold the power button for 15 seconds and try a different outlet"


def rule_overheating(facts):
    #If the CPU temperature is above 85, then clean the vents and use a cooling pad
    if facts["performance"]["cpu_temperature"] > 85:
        return "Clean the air vents and use a cooling pad"


def rule_loud_fan(facts):
    #If the fan is loud, then close heavy programs
    if facts["performance"]["fan_noise_loud"]:
        return "Close heavy programs running in the background"


def rule_screen_flicker(facts):
    #If the screen is flickering, thenupdate the display driver
    if facts["display"]["screen_flicker"]:
        return "Update the display driver"


def rule_black_screen(facts):
    # If the screen is black while the laptop is on, then connect an external monitor to test the display.
    if facts["power"]["powered_on"] and facts["display"]["screen_black"]:
        return "Connect an external monitor to test the display"

rules = [
    rule_low_battery,
    rule_wont_turn_on,
    rule_overheating,
    rule_loud_fan,
    rule_screen_flicker,
    rule_black_screen,
]


#Task 2B
def inference_engine(facts, rules):
    """Reads the knowledge base, checks each rule, returns all inferred actions."""
    actions = []
    for rule in rules:
        result = rule(facts)
        if result is not None:
            actions.append(result)
    return actions


#Task 2C
def run_rbr():
    print("=" * 50)
    print("RULE-BASED REASONING (RBR)")
    print("=" * 50)

    print("Input facts (knowledge base):")
    for category, items in facts.items():
        for name, value in items.items():
            print(f"  [{category}] {name} = {value}")

    inferred = inference_engine(facts, rules)

    print("\nRule-Based Reasoning Actions:")
    if inferred:
        for action in inferred:
            print(f"- {action}")
    else:
        print("- No rule matched. No action needed.")


#Task 3A
FEATURES = [
    "wont_turn_on",
    "overheating",
    "loud_fan",
    "screen_flicker",
    "slow_performance",
]

case_base = [
    {"problem": {"wont_turn_on": True, "overheating": False, "loud_fan": False,
                 "screen_flicker": False, "slow_performance": False},
     "solution": "Check the power cable and charger."},

    {"problem": {"wont_turn_on": False, "overheating": True, "loud_fan": True,
                 "screen_flicker": False, "slow_performance": True},
     "solution": "Clean the vents and use a cooling pad."},

    {"problem": {"wont_turn_on": False, "overheating": False, "loud_fan": False,
                 "screen_flicker": True, "slow_performance": False},
     "solution": "Update or reinstall the display driver."},

    {"problem": {"wont_turn_on": False, "overheating": False, "loud_fan": False,
                 "screen_flicker": False, "slow_performance": True},
     "solution": "Close background apps and free up disk space."},
]


#Task 3B
def similarity(new_problem, old_problem):
    """Fraction of features with the same value (0.0 = nothing alike, 1.0 = identical)."""
    matches = 0
    for feature in FEATURES:
        if new_problem.get(feature) == old_problem.get(feature):
            matches += 1
    return matches / len(FEATURES)


def retrieve(new_problem, case_base):
    """RETRIEVE: find the stored case most similar to the new problem."""
    best_case = None
    best_score = -1
    for case in case_base:
        score = similarity(new_problem, case["problem"])
        if score > best_score:
            best_case, best_score = case, score
    return best_case, best_score


#Task 3C
def reuse(best_case):
    """REUSE: use the solution of the most similar case."""
    return best_case["solution"]


#Task 3D
def revise(suggested_solution):
    """REVISE: let the student adjust the solution, or keep it unchanged."""
    answer = input("Is this solution OK? (y = keep / n = change it): ").strip().lower()
    if answer == "n":
        new_solution = input("Enter your revised solution: ").strip()
        if new_solution:
            return new_solution
    return suggested_solution


#Task 3E
def retain(new_problem, final_solution, case_base):
    """RETAIN: store the solved problem as a new case for future use."""
    case_base.append({"problem": new_problem, "solution": final_solution})


def ask_yes_no(question):
    """Helper: ask a yes/no question and return True or False."""
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("Please type y or n.")


def run_cbr():
    print("\n" + "=" * 50)
    print("CASE-BASED REASONING (CBR)")
    print("=" * 50)

    while True:
        print("\nDescribe the new problem:")
        new_problem = {}
        for feature in FEATURES:
            new_problem[feature] = ask_yes_no(f"  {feature.replace('_', ' ')}?")

        #1. RETRIEVE
        best_case, score = retrieve(new_problem, case_base)
        print(f"\n[RETRIEVE] Most similar case found (similarity: {score:.0%})")
        print(f"           Past problem: {best_case['problem']}")

        #2. REUSE
        suggestion = reuse(best_case)
        print(f"[REUSE]    Suggested solution: {suggestion}")

        #3. REVISE
        final_solution = revise(suggestion)
        print(f"[REVISE]   Final solution: {final_solution}")

        #4. RETAIN
        retain(new_problem, final_solution, case_base)
        print(f"[RETAIN]   Case saved. Case base now has {len(case_base)} cases.")

        if not ask_yes_no("\nSolve another problem?"):
            break


#MAIN
if __name__ == "__main__":
    run_rbr()
    run_cbr()