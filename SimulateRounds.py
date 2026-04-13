
from GenerateSchedule import Group, GroupAssignment, InvalidStudentPair, Student, generate_schedule
from collections import defaultdict


def run_simulation(students: list[str], group_to_size: list[tuple[str, int]],
                   invalid_student_pairs: list[tuple[str,str]], num_rounds: int = 12,
                   round_sit_outs: list[list[str]] = [],
                   debug_mode: bool = False) -> list[list[GroupAssignment]]:
    # validate student and group names are all unique
    if not students:
        raise Exception('student names cant be empty')
    if not group_to_size:
        raise Exception('groups cant be empty')
    if sum([g[1] for g in group_to_size]) < len(students):
        raise Exception('there are not enough slots in the groups specified to run simulation')
    if len(students) != len(set(students)):
        raise Exception('student names must all be unique')
    g_names = [g[0] for g in group_to_size]
    if len(g_names) != len(set(g_names)):
        raise Exception('group names must all be unique')


    # instantiating objs
    _students = {}
    for s in students:
        _students[s] = Student(name=s)
    _groups = {}
    for g in group_to_size:
        _groups[g[0]] = Group(name=g[0], max_size=g[1])

    _invalid_student_pairs = []
    for p in invalid_student_pairs:
        _invalid_student_pairs.append(InvalidStudentPair(student_a=p[0], student_b=p[1]))


    res = []
    for r in range(num_rounds):
        _students_in_this_round = list(_students.values())
        if len(round_sit_outs) > r:
            _students_in_this_round = [s for s in _students_in_this_round if s.name not in round_sit_outs[r]]

        round_assignments = generate_schedule(list(_students_in_this_round), list(_groups.values()), _invalid_student_pairs)
        res.append(round_assignments)

        g_to_s = defaultdict(list)
        for assignment in round_assignments:
            _students[assignment.student_name].visits[assignment.group_name] += 1
            g_to_s[assignment.group_name].append(assignment.student_name)

        # print(f'round {r+1}:')
        # for key,val in sorted(g_to_s.items()):
        #     print(f'  {key}: {val}')

    if debug_mode:
        print('')
        for s in _students.values():
            visits = sorted([ (key,value) for key,value in s.visits.items() ], key=lambda x: x[1])
            print(f'{s.name}: {visits}')

    return res


if __name__ == '__main__':
    students = ['marcy', 'perry', 'hamlet', 'saint nick', 'thadeus', 'maxwell', 'zeus', 'james', 'victor', 'kobe', 'danny', 'laquintes', 'max', 'sam', 'achilles', 'lincoln log', 'hermes', 'poseidon']

    groups_to_sizes = [('Play Station', 4), ('Word Work', 10), ('Dramatic Play', 2), ('Writing Center', 10)]

    invalid_student_pairs = [('kobe', 'marcy'), ('max', 'hermes'), ('maxwell', 'james'), ('james', 'poseidon'), ('perry', 'danny')]

    round_sit_outs = [[], ['thadeus', 'laquintes', 'lebron'], ['thadeus', 'laquintes', 'lebron'], ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny'], [], ['victor', 'marcy'], ['poseidon', 'achilles', 'maxwell'], ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'], ['poseidon', 'achilles', 'maxwell'], ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'], ['victor', 'marcy'], ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny']]



    run_simulation(students, groups_to_sizes, invalid_student_pairs,
                   round_sit_outs=round_sit_outs,
                   debug_mode=False)



