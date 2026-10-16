import json
import copy

CASE_BASE_FILE = "case_base.json"


#1. CASE BASE
#problem attributes
#disaster_type: "typhoon" | "flood" | "earthquake"
#area_type: "urban" | "rural" | "coastal"
#flood_risk: 1 (none), 5 (severe flooding)
#severity: 1 (weak), 5 (strong)
#population: number of people in the affected area
#lead_time_hours: hours of warning before impact
#solution attributes
#evacuation_strategy, evacuation_start_hours_before, evacuees,
#relief_packs, rescue_boats, medical_teams, notes
def seed_case_base():
    return [
        {
            "id": 1,
            "name": "Typhoon Ursula (2019)",
            "problem": {
                "disaster_type": "typhoon", "area_type": "coastal",
                "flood_risk": 3, "severity": 3,
                "population": 120000, "lead_time_hours": 48,
            },
            "solution": {
                "evacuation_strategy": "Pre-emptive evacuation of coastal barangays to school shelters",
                "evacuation_start_hours_before": 24,
                "evacuees": 30000, "relief_packs": 8000,
                "rescue_boats": 10, "medical_teams": 6,
            },
        },
        {
            "id": 2,
            "name": "Typhoon Odette (2021)",
            "problem": {
                "disaster_type": "typhoon", "area_type": "urban",
                "flood_risk": 4, "severity": 5,
                "population": 300000, "lead_time_hours": 36,
            },
            "solution": {
                "evacuation_strategy": "Mandatory evacuation of low-lying areas, pre-position rescue teams",
                "evacuation_start_hours_before": 30,
                "evacuees": 90000, "relief_packs": 25000,
                "rescue_boats": 30, "medical_teams": 15,
            },
        },
        {
            "id": 3,
            "name": "Typhoon Ondoy / Ketsana (2009)",
            "problem": {
                "disaster_type": "flood", "area_type": "urban",
                "flood_risk": 5, "severity": 4,
                "population": 500000, "lead_time_hours": 6,
            },
            "solution": {
                "evacuation_strategy": "Emergency rooftop and boat rescue, then evacuation to high-ground centers",
                "evacuation_start_hours_before": 3,
                "evacuees": 150000, "relief_packs": 40000,
                "rescue_boats": 60, "medical_teams": 25,
            },
        },
        {
            "id": 4,
            "name": "Bohol Earthquake (2013)",
            "problem": {
                "disaster_type": "earthquake", "area_type": "rural",
                "flood_risk": 1, "severity": 4,
                "population": 80000, "lead_time_hours": 0,
            },
            "solution": {
                "evacuation_strategy": "Open-field evacuation camps, structural inspection of buildings",
                "evacuation_start_hours_before": 0,
                "evacuees": 40000, "relief_packs": 12000,
                "rescue_boats": 0, "medical_teams": 12,
            },
        },
        {
            "id": 5,
            "name": "Habagat Flooding (2012)",
            "problem": {
                "disaster_type": "flood", "area_type": "urban",
                "flood_risk": 4, "severity": 3,
                "population": 400000, "lead_time_hours": 12,
            },
            "solution": {
                "evacuation_strategy": "Early evacuation of riverside communities, activate pumping stations",
                "evacuation_start_hours_before": 8,
                "evacuees": 100000, "relief_packs": 30000,
                "rescue_boats": 40, "medical_teams": 18,
            },
        },
    ]


#2.SIMILARITY ASSESSMENT
WEIGHTS = {
    "disaster_type": 0.25,
    "area_type": 0.15,
    "flood_risk": 0.20,
    "severity": 0.15,
    "population": 0.15,
    "lead_time_hours": 0.10,
}

TYPE_SIMILARITY = {
    frozenset(["typhoon", "flood"]): 0.6,
    frozenset(["typhoon", "earthquake"]): 0.1,
    frozenset(["flood", "earthquake"]): 0.1,
}


def sim_disaster_type(a, b):
    if a == b:
        return 1.0
    return TYPE_SIMILARITY.get(frozenset([a, b]), 0.0)


def sim_area_type(a, b):
    if a == b:
        return 1.0
    #urban and coastal share dense settlements
    return 0.5 if {a, b} == {"urban", "coastal"} else 0.0


def sim_scale(a, b, max_range):
    """Numeric closeness on a fixed scale: 1.0 = identical, 0.0 = max apart."""
    return 1 - abs(a - b) / max_range


def sim_ratio(a, b):
    """Closeness for open-ended numbers such as population."""
    if max(a, b) == 0:
        return 1.0
    return min(a, b) / max(a, b)


def similarity(new_problem, old_problem):
    """Return (total_score, per-attribute scores) between two problems."""
    parts = {
        "disaster_type": sim_disaster_type(new_problem["disaster_type"], old_problem["disaster_type"]),
        "area_type": sim_area_type(new_problem["area_type"], old_problem["area_type"]),
        "flood_risk": sim_scale(new_problem["flood_risk"], old_problem["flood_risk"], 4),
        "severity": sim_scale(new_problem["severity"], old_problem["severity"], 4),
        "population": sim_ratio(new_problem["population"], old_problem["population"]),
        "lead_time_hours": sim_scale(
            min(new_problem["lead_time_hours"], 48),
            min(old_problem["lead_time_hours"], 48), 48),
    }
    total = sum(WEIGHTS[k] * parts[k] for k in parts)
    return total, parts


#3. CBR CYCLE FUNCTIONS
def retrieve(new_problem, case_base):
    """RETRIEVE: rank every stored case by similarity (highest first)."""
    ranked = []
    for case in case_base:
        score, parts = similarity(new_problem, case["problem"])
        ranked.append((score, case, parts))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked


def reuse_and_adapt(new_problem, best_case):
    """
    REUSE + ADAPT: start from the retrieved solution, then modify it so it
    fits the differences between the new and the old problem.
    Returns the adapted solution and a log explaining each adaptation.
    """
    old_p = best_case["problem"]
    sol = copy.deepcopy(best_case["solution"])
    log = []

    #a. Scale resource quantities by population size.
    scale = new_problem["population"] / old_p["population"]
    for key in ("evacuees", "relief_packs", "medical_teams"):
        before = sol[key]
        sol[key] = round(before * scale)
        log.append(f"{key}: {before:,} x population ratio {scale:.2f} -> {sol[key]:,}")

    #b. Rescue boats depend on population and flood risk
    boats_before = sol["rescue_boats"]
    flood_factor = new_problem["flood_risk"] / old_p["flood_risk"]
    sol["rescue_boats"] = round(boats_before * scale * flood_factor)
    log.append(f"rescue_boats: {boats_before} x pop {scale:.2f} x flood {flood_factor:.2f} "
               f"-> {sol['rescue_boats']}")

    #c. Higher severity than the old case, then evacuate a larger share
    if new_problem["severity"] > old_p["severity"]:
        extra = 1 + 0.10 * (new_problem["severity"] - old_p["severity"])
        before = sol["evacuees"]
        sol["evacuees"] = round(before * extra)
        log.append(f"evacuees raised by {int((extra - 1) * 100)}% (higher severity): "
                   f"{before:,} -> {sol['evacuees']:,}")

    #d. Lead time: if less warning than before, start evacuating earlier
    old_start = sol["evacuation_start_hours_before"]
    if new_problem["lead_time_hours"] < old_start:
        sol["evacuation_start_hours_before"] = max(new_problem["lead_time_hours"] - 1, 0)
        log.append(f"evacuation start cut from {old_start}h to "
                   f"{sol['evacuation_start_hours_before']}h before impact (shorter warning time)")
    else:
        log.append(f"evacuation start kept at {old_start}h before impact")

    #e. Area-specific note for the strategy
    if new_problem["area_type"] == "urban" and new_problem["flood_risk"] >= 4:
        sol["evacuation_strategy"] += " + prioritize underpasses and low-lying urban zones"
        log.append("strategy extended for urban flooding")

    return sol, log


def revise(solution, feedback):
    """
    REVISE: fix the proposed solution using feedback from a simulated
    deployment (e.g., what the LGU actually observed on the ground).
    """
    revised = copy.deepcopy(solution)
    log = []
    if feedback.get("shelter_shortfall_pct", 0) > 0:
        pct = feedback["shelter_shortfall_pct"]
        before = revised["evacuees"]
        revised["evacuees"] = round(before * (1 + pct / 100))
        log.append(f"Shelters ran short by {pct}% -> planned evacuees {before:,} -> {revised['evacuees']:,}")
    if feedback.get("boats_insufficient"):
        revised["rescue_boats"] += feedback["boats_insufficient"]
        log.append(f"{feedback['boats_insufficient']} more rescue boats needed -> {revised['rescue_boats']}")
    if not log:
        log.append("No corrections needed.")
    return revised, log


def retain(case_base, name, problem, solution):
    """RETAIN: store the newly solved case so the system can learn from it."""
    new_case = {
        "id": max(c["id"] for c in case_base) + 1,
        "name": name,
        "problem": problem,
        "solution": solution,
    }
    case_base.append(new_case)
    with open(CASE_BASE_FILE, "w") as f:
        json.dump(case_base, f, indent=2)
    return new_case


#4. DISPLAY HELPERS
LINE = "=" * 72


def show_problem(p):
    for k, v in p.items():
        print(f"   {k:<18}: {v:,}" if isinstance(v, int) and v > 999 else f"   {k:<18}: {v}")


def show_solution(s):
    print(f"Strategy: {s['evacuation_strategy']}")
    print(f"Start evacuation: {s['evacuation_start_hours_before']} hour(s) before impact")
    print(f"Evacuees: {s['evacuees']:,}")
    print(f"Relief packs: {s['relief_packs']:,}")
    print(f"Rescue boats: {s['rescue_boats']}")
    print(f"Medical teams: {s['medical_teams']}")


def show_case_base(case_base):
    print(f"   {'ID':<4}{'Case':<44}{'Type':<12}{'Area':<9}{'Pop.':>9}")
    print("   " + "-" * 76)
    for c in case_base:
        p = c["problem"]
        print(f"   {c['id']:<4}{c['name']:<44}{p['disaster_type']:<12}{p['area_type']:<9}{p['population']:>9,}")


#5. MAIN
def main():
    case_base = seed_case_base()

    print(LINE)
    print("DISASTER RESPONSE DSS - CASE-BASED REASONING")
    print(LINE)
    print(f"\nCase base loaded: {len(case_base)} past cases")
    show_case_base(case_base)

    new_problem = {
        "disaster_type": "typhoon",
        "area_type": "urban",
        "flood_risk": 5,
        "severity": 4,
        "population": 350000,
        "lead_time_hours": 24,
    }
    print("\n" + LINE)
    print("[INPUT] NEW PROBLEM: Typhoon with expected flooding in urban areas")
    print(LINE)
    show_problem(new_problem)

    #STEP 1
    print("\n" + LINE)
    print("[STEP 1 - RETRIEVE] Similarity ranking")
    print(LINE)
    ranked = retrieve(new_problem, case_base)
    for rank, (score, case, _) in enumerate(ranked, start=1):
        print(f"   #{rank}  {case['name']:<34} similarity = {score:.2%}")

    best_score, best_case, best_parts = ranked[0]
    second_score, second_case, _ = ranked[1]
    print(f"\n   Most relevant case : {best_case['name']} ({best_score:.2%})")
    print(f"   Runner-up          : {second_case['name']} ({second_score:.2%})")
    print("\n   Attribute breakdown for the best match (weight x match):")
    for attr, val in best_parts.items():
        print(f"      {attr:<18} {WEIGHTS[attr]:.2f} x {val:.2f} = {WEIGHTS[attr] * val:.3f}")
    print("\n   Retrieved solution (before adaptation):")
    show_solution(best_case["solution"])

    #STEP 2
    print("\n" + LINE)
    print("[STEP 2 - REUSE & ADAPT] Fitting the old solution to the new problem")
    print(LINE)
    adapted, adapt_log = reuse_and_adapt(new_problem, best_case)
    for line in adapt_log:
        print("   *", line)
    print("\n   Adapted solution:")
    show_solution(adapted)

    #STEP 3
    print("\n" + LINE)
    print("[STEP 3 - REVISE] Applying simulated field feedback")
    print(LINE)
    feedback = {"shelter_shortfall_pct": 10, "boats_insufficient": 5}
    print(f"   Feedback received: {feedback}")
    final_solution, revise_log = revise(adapted, feedback)
    for line in revise_log:
        print("   *", line)
    print("\n   FINAL SOLUTION:")
    show_solution(final_solution)

    #STEP 4
    print("\n" + LINE)
    print("[STEP 4 - RETAIN] Learning from the new case")
    print(LINE)
    new_case = retain(case_base, "New Typhoon - Urban Flooding (Simulated)",
                      new_problem, final_solution)
    print(f"   New case saved as ID {new_case['id']} -> '{new_case['name']}' (stored in {CASE_BASE_FILE})")
    print(f"\n   Updated case base: {len(case_base)} cases")
    show_case_base(case_base)
    print("\n" + LINE)
    print("End of CBR cycle: Retrieve -> Reuse -> Revise -> Retain")
    print(LINE)


if __name__ == "__main__":
    main()