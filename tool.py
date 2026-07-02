import pandas as pd
import random
from itertools import combinations

# ======================
# CONFIGURATION
# ======================

COURSES_FILE = "courses.xlsx"
RAS_FILE = "ras.xlsx"
SLOT_MAP_FILE = "l_to_slot_map.csv"  # e.g. "L1,A1"

OUTPUT_FILE = "lab_allocation.xlsx"

# Maximum and minimum number of distinct courses per RA
MIN_COURSES = 2
MAX_COURSES = 3


# ======================
# HELPER FUNCTIONS
# ======================

def parse_slots(slot_str):
    """Convert 'L43+L44+L45+L46' -> ['L43','L44','L45','L46']"""
    if pd.isna(slot_str):
        return []
    return [s.strip() for s in slot_str.split('+') if s.strip()]


def group_lab_hours(l_slots):
    """Group consecutive Ls into pairs (2 Ls = 1 hour, 4 Ls = 2 hours)."""
    if not l_slots:
        return []
    grouped = []
    for i in range(0, len(l_slots), 2):
        grouped.append('+'.join(l_slots[i:i+2]))
    return grouped


def get_theory_equivalents(l_slots, l_to_theory_map):
    """Map lab slots (Lxx) -> corresponding theory slots (e.g., A1, F1)."""
    equivalents = set()
    for l in l_slots:
        if l in l_to_theory_map:
            equivalents.add(l_to_theory_map[l])
    return equivalents


def has_clash(l_slots, busy_theory_slots, l_to_theory_map):
    """Check if lab's mapped theory slot overlaps with RA's busy slots."""
    for l in l_slots:
        if l_to_theory_map.get(l) in busy_theory_slots:
            return True
    return False


# ======================
# LOAD DATA
# ======================

print("Loading files...")

courses_df = pd.read_excel(COURSES_FILE)
ras_df = pd.read_excel(RAS_FILE)
slot_map_df = pd.read_csv(SLOT_MAP_FILE, header=None, names=["L", "Theory"])

# Create dict for mapping
l_to_theory = dict(zip(slot_map_df["L"], slot_map_df["Theory"]))

# Filter lab courses only
courses_df = courses_df[courses_df["COURSE TYPE"] == "LO"].copy()

# Expand slot strings into grouped lab hours
courses_df["L_SLOTS"] = courses_df["SLOT"].apply(parse_slots)
courses_df["LAB_GROUPS"] = courses_df["L_SLOTS"].apply(group_lab_hours)

# Flatten all lab groups for assignment
lab_pool = []
for _, row in courses_df.iterrows():
    for group in row["LAB_GROUPS"]:
        lab_pool.append({
            "COURSE CODE": row["COURSE CODE"],
            "COURSE TITLE": row["COURSE TITLE"],
            "COURSE OWNER": row.get("COURSE OWNER"),
            "CLASS ID": row.get("CLASS ID"),
            "ROOM NUMBER": row.get("ROOM NUMBER"),
            "SLOT": group,
            "EMPLOYEE NAME": row.get("EMPLOYEE NAME"),
            "EMPLOYEE SCHOOL": row.get("EMPLOYEE SCHOOL"),
            "COURSE MODE": row.get("COURSE MODE"),
            "COURSE TYPE": row.get("COURSE TYPE"),
        })

print(f"Loaded {len(lab_pool)} available lab hour groups.")

# ======================
# ASSIGNMENT LOGIC
# ======================

allocations = []

for _, ra in ras_df.iterrows():
    ra_name = ra["Name of the Student"]
    emp_id = ra["Emp Id"]
    phd_id = ra.get("Ph.D Registartion Number", "")
    num_labs = int(ra["NUMBER OF LABS"])
    reg_slots = str(ra.get("REGISTERED SLOTS", "")).replace(" ", "")
    busy_theory_slots = set([s for s in reg_slots.split(',') if s])

    # Shuffle lab pool for randomness
    random.shuffle(lab_pool)

    # Collect non-conflicting labs
    assigned = []
    used_courses = set()

    for lab in lab_pool:
        if has_clash(parse_slots(lab["SLOT"]), busy_theory_slots, l_to_theory):
            continue
        if len(used_courses) >= MAX_COURSES and lab["COURSE CODE"] not in used_courses:
            continue
        assigned.append(lab)
        used_courses.add(lab["COURSE CODE"])
        # Each lab group = 1 hour
        if len(assigned) >= num_labs:
            break

    # If less than required labs were found, fill remaining ignoring clashes
    if len(assigned) < num_labs:
        remaining = [x for x in lab_pool if x["COURSE CODE"] not in used_courses]
        random.shuffle(remaining)
        for lab in remaining:
            assigned.append(lab)
            used_courses.add(lab["COURSE CODE"])
            if len(assigned) >= num_labs:
                break

    # If less than min course count, try to adjust
    if len(used_courses) < MIN_COURSES:
        extra_courses = [x for x in lab_pool if x["COURSE CODE"] not in used_courses]
        for lab in extra_courses:
            assigned.append(lab)
            used_courses.add(lab["COURSE CODE"])
            if len(used_courses) >= MIN_COURSES or len(assigned) >= num_labs:
                break

    for lab in assigned:
        allocations.append({
            "RA Name": ra_name,
            "Emp Id": emp_id,
            "PhD Reg No": phd_id,
            "No. of Labs (Req)": num_labs,
            "Registered Slots": reg_slots,
            **lab,
            "Comments": ""
        })

print(f"✅ Assigned labs to {len(ras_df)} RAs.")

# ======================
# OUTPUT
# ======================

alloc_df = pd.DataFrame(allocations)
alloc_df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Allocation saved to {OUTPUT_FILE}")
