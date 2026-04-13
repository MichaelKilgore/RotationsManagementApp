from SimulateRounds import run_simulation
from RoundsPresentation import RoundsPresentation
from CreateGoogleSlides import create_google_slides
import random

students = ['marcy', 'perry', 'hamlet', 'saint nick', 'thadeus', 'maxwell', 'zeus', 'james', 'victor', 'kobe', 'danny', 'laquintes', 'max', 'sam', 'achilles', 'lincoln log', 'hermes', 'poseidon']
random.shuffle(students)

groups_to_sizes = [('Play Station', 4), ('Word Work', 10), ('Dramatic Play', 2), ('Writing Center', 10)]

invalid_student_pairs = [('kobe', 'marcy'), ('max', 'hermes'), ('maxwell', 'james'), ('james', 'poseidon'), ('perry', 'danny')]

round_sit_outs = [[], ['thadeus', 'laquintes', 'lebron'], ['thadeus', 'laquintes', 'lebron'], ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny'], [], ['victor', 'marcy'], ['poseidon', 'achilles', 'maxwell'], ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'], ['poseidon', 'achilles', 'maxwell'], ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'], ['victor', 'marcy'], ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny']]



rounds = run_simulation(students, groups_to_sizes, invalid_student_pairs,
                        round_sit_outs=round_sit_outs,
                        debug_mode=False)

replacements = RoundsPresentation().build_replacements(rounds)
create_google_slides('1oQ8zrRGx5s-LbDCpxb8FOg0e62y_bsJ_OOQo1np555Y', replacements)



