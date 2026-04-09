from dataclasses import dataclass, field
from collections import defaultdict
from typing import Sequence, cast
from ortools.linear_solver import pywraplp
import math

# TODO: Could potentially add max_visits_allowed, limiting number of times a user can be part of a group
@dataclass
class Group:
    name: str
    max_size: int

@dataclass
class Student:
    name: str
    visits: dict = field(default_factory=lambda: defaultdict(int))

@dataclass
class GroupAssignment:
    group_name: str
    student_name: str

@dataclass
class InvalidStudentPair:
    student_a: str
    student_b: str

def generate_schedule(students: list[Student], groups: list[Group], invalid_student_pairs: list[InvalidStudentPair] = []) -> list[GroupAssignment]:
    solver = pywraplp.Solver.CreateSolver("SCIP")

    x = {}
    for s in students:
        for g in groups:
            x[(s.name, g.name)] = solver.IntVar(0, 1, f"x_{s.name}_{g.name}")

    # restrict students to only be assigned to one group
    for s in students:
        solver.Add(sum(x[(s.name, g.name)] for g in groups) == 1)

    # restrict max students assigned to each group
    for g in groups:
        solver.Add(sum(x[(s.name, g.name)] for s in students) <= g.max_size)

    # prevent not allowed pairing of students into the same group
    for p in invalid_student_pairs:
        for g in groups:
            if (p.student_a, g.name) in x and (p.student_b, g.name) in x:
                solver.Add(x[(p.student_a, g.name)] + x[(p.student_b, g.name)] <= 1)


    # evenly distribute students between groups
    students_remaining = len(students)
    remaining_groups = groups[:]
    while remaining_groups:
        avg = students_remaining / len(remaining_groups)
        small_groups = [g for g in remaining_groups if g.max_size < avg]
        large_groups = [g for g in remaining_groups if g.max_size >= avg]

        if not small_groups:
            min_group_size = math.floor(avg)
            for g in large_groups:
                solver.Add(sum(x[(s.name, g.name)] for s in students) >= min_group_size)
                solver.Add(sum(x[(s.name, g.name)] for s in students) <= min_group_size + 1)
            break

        for g in small_groups:
            solver.Add(sum(x[(s.name, g.name)] for s in students) == g.max_size)

        students_remaining -= sum(g.max_size for g in small_groups)
        remaining_groups = large_groups


    preferences = _generate_student_preferences(students, groups)
    solver.Maximize(
        sum(preferences[(s.name, g.name)] * x[(s.name, g.name)] for s in students for g in groups)
    )

    status = solver.Solve()

    res = []
    if status == pywraplp.Solver.OPTIMAL:
        for s in students:
            for g in groups:
                if x[(s.name, g.name)].solution_value() == 1:
                    res.append(GroupAssignment(g.name, s.name))
    else:
        raise Exception('unexpected error, no solution found')

    return res

def _generate_student_preferences(students: list[Student], groups: list[Group]) -> dict:
    preferences = { }
    for student in students:
        for i, g in enumerate(groups):
            preferences[(student.name, g.name)] = ( student.visits[g.name] * -1 ) - (i * 0.001)

    return preferences



if __name__ == '__main__':
    students = [Student(name='max', visits = defaultdict(int, { 'Dramatic Play': 1 })),
                Student(name='james', visits = defaultdict(int, { 'Dramatic Play': 1 })),
                Student(name='billy', visits = defaultdict(int, { 'Dramatic Play': 1 })),
                Student(name='sam', visits = defaultdict(int, { 'Dramatic Play': 1 })),
                Student(name='zeus', visits = defaultdict(int, { 'Dramatic Play': 1 })),

                Student(name='hamlet', visits = defaultdict(int, { 'Library': 2 })),
                Student(name='thadeus', visits = defaultdict(int, { 'Library': 2 })),
                Student(name='laquintes', visits = defaultdict(int, { 'Library': 2 })),
                Student(name='lebron', visits = defaultdict(int, { 'Library': 2 })),
                Student(name='kobe', visits = defaultdict(int, { 'Library': 2 })),

                Student(name='saint nick', visits = defaultdict(int, { 'Word Work': 1 })),
                Student(name='hermes', visits = defaultdict(int, { 'Word Work': 1 })),
                Student(name='lincoln log', visits = defaultdict(int, { 'Word Work': 1 })),
                Student(name='perry', visits = defaultdict(int, { 'Word Work': 1 })),
                Student(name='danny', visits = defaultdict(int, { 'Word Work': 1 })),

                Student(name='poseidon', visits = defaultdict(int, { 'iStation': 3 })),
                Student(name='achilles', visits = defaultdict(int, { 'iStation': 3 })),
                Student(name='maxwell', visits = defaultdict(int, { 'iStation': 3 })),
                Student(name='victor', visits = defaultdict(int, { 'iStation': 3 })),
                Student(name='marcy', visits = defaultdict(int, { 'iStation': 3 })),
                ]


    groups = [Group('Dramatic Play', 2), Group('Library', 10), Group('Word Work', 10), Group('Writing Center', 10), Group('iStation', 10)]

    res = generate_schedule(students, groups)

    print(res)

