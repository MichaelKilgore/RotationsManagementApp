from collections import defaultdict
from SimulateRounds import run_simulation


class RoundsPresentation:
    def build_replacements(self, rounds: list) -> dict:
        replacements = {}
        for round_idx, round_assignments in enumerate(rounds):
            g_to_students = defaultdict(list)
            for assignment in round_assignments:
                g_to_students[assignment.group_name].append(assignment.student_name)

            for group_name, students in g_to_students.items():
                key = f'{{{{{group_name.upper().replace(" ", "_")}_ROUND_{round_idx + 1}}}}}'
                replacements[key] = ', '.join(students)

        return replacements


if __name__ == '__main__':
    students = ['alice', 'bob', 'charlie', 'diana', 'evan', 'fiona', 'george', 'hannah',
                'ivan', 'julia', 'kevin', 'laura', 'mike', 'nina', 'oscar', 'paula',
                'quinn', 'rachel', 'steve', 'tina']

    groups_to_sizes = [('Play Station', 4), ('Word Work', 6), ('Dramatic Play', 4), ('Writing Center', 6)]

    rounds = run_simulation(students, groups_to_sizes, [], num_rounds=12)

    replacements = RoundsPresentation().build_replacements(rounds)
    for key, value in replacements.items():
        print(f'{key}: {value}')
