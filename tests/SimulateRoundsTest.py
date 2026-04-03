import unittest
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from SimulateRounds import run_simulation


class TestRunSimulation(unittest.TestCase):

    def setUp(self):
        self.students = [
            'max', 'james', 'billy', 'sam', 'zeus',
            'hamlet', 'thadeus', 'laquintes', 'lebron', 'kobe',
            'saint nick', 'hermes', 'lincoln log', 'perry', 'danny',
            'poseidon', 'achilles', 'maxwell', 'victor', 'marcy'
        ]
        self.groups_to_sizes = [
            ('Dramatic Play', 2),
            ('Library', 10),
            ('Word Work', 10),
            ('Writing Center', 10),
            ('iStation', 10),
            ('Play Station', 4),
            ('Play Time', 10)
        ]
        self.invalid_student_pairs = [
            ('james', 'poseidon'),
            ('maxwell', 'james'),
            ('kobe', 'marcy'),
            ('max', 'hermes'),
            ('zeus', 'hamlet'),
            ('perry', 'danny')
        ]
        self.round_sit_outs = [ ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'],
                               ['thadeus', 'laquintes', 'lebron'],
                               ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny'],
                               ['max', 'james', 'billy', 'sam', 'zeus', 'hamlet'],
                               ['poseidon', 'achilles', 'maxwell'],
                               ['kobe', 'saint nick', 'hermes', 'lincoln log', 'perry', 'danny'],
                               ['victor', 'marcy'],
                               ['thadeus', 'laquintes', 'lebron'],
                               ['poseidon', 'achilles', 'maxwell'],
                               [],
                               ['victor', 'marcy'],
                               [] ]

    def test_for_unknown_failures(self):
        for i in range(100):
            print(f'starting test: {i}')

            s = self.students[:]
            random.shuffle(s)

            g_to_s = self.groups_to_sizes[:]
            random.shuffle(g_to_s)

            i_s_p = self.invalid_student_pairs[:]
            random.shuffle(i_s_p)

            r_s_o = self.round_sit_outs[:]
            random.shuffle(r_s_o)

            num_students = random.randint(1, len(self.students)-1)
            s = s[:num_students]

            num_groups_to_sizes = random.randint(4, len(self.groups_to_sizes))
            g_to_s = g_to_s[:num_groups_to_sizes]

            num_invalid_student_pairs = random.randint(0, len(self.invalid_student_pairs))
            i_s_p = i_s_p[:num_invalid_student_pairs]

            res = run_simulation(s, g_to_s, i_s_p, 12, r_s_o, debug_mode=False)

            assert(len(res) == 12)




if __name__ == '__main__':
    unittest.main()
