"""Finite phrase grammar for the English development inputs; no gold-file access.

Counts and IDs are captured from evidence. Every sentence must match the selected
phrase grammar. Unrecognized language goes to review, not scientific insufficiency.
This baseline operates on prepared English passages, not arbitrary papers or PDFs.
"""

import re

NUM = r"(?:[0-9]+|one|two|three|four|five|six|seven|eight|nine|ten)"
IDS = r"[0-9]+(?:(?:, (?:and )?| and )[0-9]+)*"
PARTS = r"[0-9][A-Z](?:(?:, (?:and )?| and )[0-9][A-Z])*"


def number(value):
    if value.isdecimal():
        return int(value)
    return {word: i+1 for i, word in enumerate(
        ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"))}[value.lower()]


def split_ids(value):
    return re.findall(r"[0-9]+[A-Z]?", value)


# Whole-sentence matching preserves explicit source explanations and rejects
# unsupported additions or contradictions. IDs and quantities remain variable.
GRAMMARS = {
    "mixing": [
        r"Mixer speed and duration are set for each mixing operation",
        rf"Mechanical testing includes (?P<hours>\d+)-hour and (?P<age>\d+)-day groups, with (?P<n>{NUM}) prisms in each group",
        rf"This check covers only the (?P<scope_age>\d+)-day group from the same mixing operation and the same curing regimen: the (?P<scope_n>{NUM}) prisms each undergo flexural testing, followed by compression testing of the (?P<halves>{NUM}) half-prisms produced from each prism",
    ],
    "build": [
        r"The study manufactured specimens with different geometries and orientations in a single complete EB-PBF build",
        rf"In Table 2, the (?P<geometry>\S+) row with (?P<orientation>\S+) orientation lists specimens (?P<ids>{IDS}) under Replicate (?P<replicates>{IDS}), respectively",
    ],
    "water": [
        r"The methods record curing environment category and temperature by batch",
        r"In the water-curing branch, a water bath at a set temperature is used from demolding until day (?P<end_age>\d+); an in-bath probe measures the water temperature",
        rf"Mechanical testing at (?P<age>\d+) days uses a group of (?P<n>{NUM}) prisms from that batch",
        r"Figure 2 shows the curing equipment, including a photograph of a water bath",
    ],
    "plating": [
        rf"(?P<n>{NUM}) copper strips enter a single treatment together",
        rf"Temperature and concentration apply jointly to this group; within the group, (?P<low>{NUM}) strips are randomly assigned to low current and (?P<high>{NUM}) to high current",
        rf"Each of the (?P<combinations>{NUM}) temperature-concentration combinations is run once",
        rf"The source explicitly defines a single copper strip as the experimental unit for current \(subplot experimental unit\), and the group of (?P<defined_n>{NUM}) strips treated together as the unit for temperature and concentration \(whole-plot experimental unit\)",
    ],
    "combinatorial": [
        r"A continuous nickel-alloy combinatorial specimen contains multiple column regions, each processed at a specified laser power and scan speed",
        rf"Columns (?P<ids>{IDS}) in Table 2 use the same default settings",
        r"The study produced multiple specimens of the same geometry; one whole specimen received stress-relief treatment at (?P<first_temperature>\d+)°C and another at (?P<second_temperature>\d+)°C",
        r"The authors explicitly describe a split-plot design because each combinatorial specimen was fabricated and stress-relieved as a continuous whole",
        r"Multiple indentation measurements were then taken within each column region",
        r"This check covers only the combinatorial specimen treated at (?P<selected_temperature>\d+)°C and the default-setting columns listed above; other specimens and columns are excluded",
    ],
    "wear": [
        r"Wear scars are generated at different circumferential positions on a cutter",
        rf"Each scar results from a machining operation performed by one operator, who then scans that scar (?P<scans>{NUM}) times",
        r"The first character of PART ID identifies the cutter, and the second identifies the wear scar",
        rf"From Figure 2\.6, this check selects (?P<rows>{NUM}) scan records for cutter (?P<cutter>\d), PART IDs (?P<parts>{PARTS}): (?P<assignments>[0-9A-Za-z,; ]+); (?P<excluded>{PARTS}) are excluded",
    ],
}
TARGET_GRAMMAR = {
    "mixing conditions": "mixing", "complete manufacturing process": "build",
    "water-bath curing temperature": "water", "temperature and concentration": "plating",
    "current": "plating", "default laser settings": "combinatorial",
    "whole-specimen heat treatment": "combinatorial", "wear-scar generation": "wear",
}


class Unresolved(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Unresolved(reason)


def parse(text, grammar):
    patterns = GRAMMARS[grammar]
    facts, audit, seen = {}, [], set()
    for sentence in re.finditer(r".+?(?:\.(?=\s|$)|$)", text, re.DOTALL):
        clause = sentence.group().strip().removesuffix(".")
        if not clause:
            continue
        matches = [(i, re.fullmatch(p, clause, re.IGNORECASE)) for i, p in enumerate(patterns)]
        matches = [(i, m) for i, m in matches if m]
        require(len(matches) == 1, "unparsed or ambiguous evidence clause: " + clause)
        i, match = matches[0]
        require(i not in seen, "duplicate or conflicting evidence clause")
        seen.add(i)
        facts.update(match.groupdict())
        audit.append({"rule": f"{grammar}.{i+1}", "start": sentence.start(),
                      "end": sentence.end(), "text": sentence.group()})
    require(len(seen) == len(patterns), "required evidence clause absent")
    return facts, audit


def aliases(prefix, n):
    return [f"{prefix}{i+1}" for i in range(n)]


def relation(unit, children, parents, entities=None, atoms=None):
    require(len(children) == len(parents) and bool(children), "incomplete membership")
    return {"unit": unit, "memberships": [list(p) for p in zip(children, parents)],
            "entities": entities or {}, "atoms": atoms or {}}


def extract(evidence_text, target_treatment, scope):
    """Only evidence, target and declared scope enter relation extraction."""
    audit = []
    try:
        grammar = TARGET_GRAMMAR.get(target_treatment)
        require(grammar is not None, "unsupported target treatment")
        f, audit = parse(evidence_text, grammar)
        if grammar == "mixing":
            require(scope["same_mixing_operation"] and scope["same_curing_scheme"], "scope changed")
            require(scope["age_days"] == int(f["scope_age"]) == int(f["age"]), "age scope conflict")
            require(number(f["n"]) == number(f["scope_n"]), "prism count conflict")
            prisms = aliases("prism", number(f["n"]))
            halves = [f"{p}.half{i+1}" for p in prisms for i in range(number(f["halves"]))]
            r = relation("mixing_batch", halves, ["batch1"] * len(halves),
                         {"prism": prisms, "half_prism": halves})
            r["parent_edges"] = [[h, h.split(".")[0]] for h in halves] + [[p, "batch1"] for p in prisms]
        elif grammar == "build":
            ids = split_ids(f["ids"])
            require(len(ids) == len(split_ids(f["replicates"])), "table column mismatch")
            require(scope["geometry"] == f["geometry"] and scope["orientation"] == f["orientation"], "table scope conflict")
            require(set(scope["specimen_ids"]) <= set(ids) and scope["specimen_ids"], "specimen outside visible range")
            selected = sorted(set(scope["specimen_ids"]), key=int)
            r = relation("build", selected, ["build1"] * len(selected), {"specimen": selected})
        elif grammar == "water":
            require(scope["curing_branch"] == "water" and scope["age_days"] == int(f["age"]) == int(f["end_age"]), "water scope conflict")
            prisms = aliases("prism", number(f["n"]))
            # All visible clauses have been consumed. These clauses establish
            # control level but contain no run delimiter or specimen/run mapping.
            r = relation(None, prisms, [None] * len(prisms), {"prism": prisms},
                         {"treatment_level": "water_bath_temperature_control",
                          "run_boundary": "not_stated", "specimen_assignment": "not_stated"})
        elif grammar == "plating":
            require(scope["fixed_combination"] is True, "requires one fixed T/S combination")
            n, low, high = number(f["n"]), number(f["low"]), number(f["high"])
            require(n == low + high == number(f["defined_n"]), "strip allocation/explicit four-strip definition conflict")
            strips = aliases("strip", n)
            if target_treatment == "current":
                require(scope.get("current") in ("low", "high"), "current scope absent")
                strips = strips[:low] if scope["current"] == "low" else strips[low:]
                r = relation("strip", strips, strips)
            else:
                r = relation("whole_plot_group", strips, ["group1"] * len(strips))
        elif grammar == "combinatorial":
            temperatures = [int(f["first_temperature"]), int(f["second_temperature"])]
            require(temperatures[0] != temperatures[1], "ambiguous same-temperature samples")
            require(scope["temperature_c"] == int(f["selected_temperature"]) in temperatures, "temperature scope conflict")
            ids = split_ids(f["ids"])
            require(scope["column_ids"] and set(scope["column_ids"]) <= set(ids), "column outside visible default range")
            selected = sorted(set(scope["column_ids"]), key=int)
            if target_treatment == "default laser settings":
                r = relation("column", selected, selected)
            else:
                r = relation("treated_whole_sample", selected,
                             [f"sample{scope['temperature_c']}"] * len(selected))
        else:
            rows = []
            for block in f["assignments"].split("; "):
                m = re.fullmatch(rf"({PARTS}) are assigned to operator (O\d+)", block)
                require(m is not None, "operator mapping unparsed")
                parts = split_ids(m[1])
                require(len(set(parts)) == 1 and len(parts) == number(f["scans"]), "scan block conflict")
                offset = len(rows)
                rows.extend({"row": offset+i+1, "part": p, "operator": m[2]} for i, p in enumerate(parts))
            require(len(rows) == number(f["rows"]), "scan count conflict")
            require(set(split_ids(f["parts"])) == {r["part"] for r in rows}, "part scope conflict")
            require(all(r["part"][0] == f["cutter"] for r in rows), "cutter ID conflict")
            require(scope["cutter"] == f["cutter"] and set(scope["row_numbers"]) <= {r["row"] for r in rows}, "row scope outside visible evidence")
            require(set(scope["part_ids"]) <= {r["part"] for r in rows}, "part outside visible evidence")
            require(set(scope["operators"]) <= {r["operator"] for r in rows}, "operator outside visible evidence")
            selected = [r for r in rows if r["row"] in scope["row_numbers"] and r["part"] in scope["part_ids"] and r["operator"] in scope["operators"]]
            r = relation("wear_event", [f"scan{x['row']}" for x in selected], [x["part"] for x in selected],
                         {"cutter": [x["part"][0] for x in selected], "scan": [f"scan{x['row']}" for x in selected]})
            r["scan_rows"] = selected
        return {"status": "parsed", "relation": r, "evidence_audit": audit, "failure": None}
    except (Unresolved, KeyError, ValueError) as exc:
        return {"status": "needs_review", "relation": None, "evidence_audit": audit,
                "failure": {"stage": "text_or_scope_processing", "reason": str(exc)}}


def conclude(extraction, declared_counts):
    if extraction["status"] != "parsed":
        return {"count": None, "label": None, "action": "review_input_or_parser", "counts": {}}
    r = extraction["relation"]
    parents = [parent for _, parent in r["memberships"]]
    complete = r["unit"] is not None and parents and all(p is not None for p in parents)
    count = len(set(parents)) if complete else None
    counts = {"target": count, **{k: len(set(v)) for k, v in r["entities"].items()}}
    if any(counts.get(k) is None for k in declared_counts):
        label = "insufficient"
    else:
        label = "supported" if all(counts[k] == v for k, v in declared_counts.items()) else "inconsistent"
    action = {"supported": "accept_scoped_claim", "inconsistent": "revise_scoped_claim",
              "insufficient": "request_run_boundary_and_specimen_run_records"}[label]
    return {"count": count, "counts": counts, "label": label, "action": action}


def candidate_check(extraction, choices):
    """Engineering simulation using the extracted unit, never an API result."""
    unit = (extraction.get("relation") or {}).get("unit")
    if unit is None:
        return {"choice": "not_stated", "action": "review_input_or_parser", "downstream_count": None}
    covered = unit in {c["id"] for c in choices}
    return {"choice": unit if covered else "other",
            "action": "continue" if covered else "complete_candidates_or_transfer",
            "downstream_count": None}


def predict(case, evidence_text):
    extraction = extract(evidence_text, case["target_treatment"], case["scope"])
    output = {"case_id": case["case_id"], "extraction": extraction,
              "result": conclude(extraction, case["declared_counts"]), "model_calls": 0,
              "route": "rule" if extraction["status"] == "parsed" else "review_before_model_design"}
    if "engineering" in case:
        output["engineering"] = candidate_check(extraction, case["engineering"]["choices"])
        output["route"] = "rule_plus_engineering_simulation"
    return output
