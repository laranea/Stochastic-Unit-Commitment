# -*- coding: utf-8 -*-
# instance.py
# authors: Antoine Passemiers, Cedric Simar

import numpy as np


class SUPInstance:

    def __init__(self, Gs, Gf, n_scenarios, n_periods, n_lines, n_nodes, n_import_groups):
        self.Gs = Gs
        self.Gf = Gf
        self.n_generators = len(Gs) + len(Gf)
        self.n_scenarios = n_scenarios
        self.n_periods = n_periods
        self.n_buses = n_nodes
        self.n_lines = n_lines
        self.n_nodes = n_nodes
        self.n_import_groups = n_import_groups

        self.Gn = None
        self.LIn = None
        self.LOn = None
        self.IG = None
    
        # PI[s] = Probability of scenario s
        self.PI = np.empty(self.n_scenarios, dtype=np.float)

        # K[g] = Minimum load cost of generator g
        self.K = np.empty(self.n_generators, dtype=np.float)

        # S[g] = Startup cost of generator g
        self.S = np.empty(self.n_generators, dtype=np.float)
        
        # C[g] = Marginal cost of generator g
        self.C = np.empty(self.n_generators, dtype=np.float)

        # D[n, s, t] = Demand in bus n, scenario s, period t
        self.D = np.empty((self.n_buses, self.n_scenarios, self.n_periods), dtype=np.float)

        # P_plus[g, s] = Maximum capacity of generator g in scenario s
        self.P_plus = np.empty((self.n_generators, self.n_scenarios), dtype=np.float)

        # P_minus[g, s] = Minimum capacity of generator g in scenario s
        self.P_minus = np.empty((self.n_generators, self.n_scenarios), dtype=np.float)

        # R_plus[g] = Maximum ramping of generator g
        self.R_plus = np.empty(self.n_generators, dtype=np.float)

        # R_minus[g] = Minimum ramping of generator g
        self.R_minus = np.empty(self.n_generators, dtype=np.float)

        # UT[g] = Minimum up time of generator g
        self.UT = np.empty(self.n_generators, dtype=np.float)

        # DT[g] = Minimum down time of generator g
        self.DT = np.empty(self.n_generators, dtype=np.float)

        # T_req[t] = Total reserve requirement in period t
        self.T_req = np.empty(self.n_periods, dtype=np.float)

        # F_req[t] = Fast reserve requirement in period t
        self.F_req = np.empty(self.n_periods, dtype=np.float)

        # B[l, s] = Susceptance of line l in scenario s
        self.B = np.empty((self.n_lines, self.n_scenarios), dtype=np.float)

        # TC[l] = Maximum capacity of line l
        self.TC = np.empty(self.n_lines, dtype=np.float)

        # FR[g] = Fast reserve limit of generator g
        self.FR = np.empty(self.n_generators, dtype=np.float)

        # IC[j] = Maximum capacity of import group j
        self.IC = np.empty(self.n_import_groups, dtype=np.float)

        # GAMMA[j, l] = Polarity of line l in import group j
        self.GAMMA = np.empty((self.n_import_groups, self.n_lines), dtype=np.float)

    def get_sizes(self):
        return (self.n_generators, self.n_scenarios, self.n_periods,
            self.n_lines, self.n_nodes, self.n_import_groups)

    def get_indices(self):
        return (self.Gs, self.Gf, self.Gn, self.LIn, self.LOn, self.IG)

    def get_constants(self):
        return (self.PI, self.K, self.S, self.C, self.D, self.P_plus, self.P_minus,
            self.R_plus, self.R_minus, self.UT, self.DT, self.T_req, self.F_req, 
            self.B, self.TC, self.FR, self.IC, self.GAMMA)

    @staticmethod
    def parse_n_data_lines(f, n_lines, is_index=False):
        i = 0
        data = list()
        while i < n_lines:
            line = f.readline().replace("\n", "").rstrip()
            if line.strip()[0] != '#':
                words = line.split(' ')
                elements = list()
                for word in words:
                    if '-' in word:
                        pair = word.split('-')
                        if is_index:
                            elements.append((int(pair[0])-1, int(pair[1])-1))
                        else:
                            elements.append((int(pair[0]), int(pair[1])))
                    elif word.isdigit():
                        elements.append(int(word)-1 if is_index else int(word))
                    else:
                        elements.append(float(word))
                data.append(elements if len(elements) > 1 else elements[0])
                i += 1
        return data

    @staticmethod
    def check_if_provided(f):
        line = f.readline().replace("\n", "").rstrip()
        assert(line.strip()[0] == '#')
        return not ("#no" in line.replace(" ", "").lower())

    @staticmethod
    def from_file(filepath):
        with open(filepath) as f:
            n_generators = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            Gs = np.asarray(SUPInstance.parse_n_data_lines(f, 1)[0],
                dtype=np.int)-1
            Gf = np.asarray(SUPInstance.parse_n_data_lines(f, 1)[0],
                dtype=np.int)-1
            assert(n_generators == len(Gs) + len(Gf))
            S = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            T = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            L = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            N = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            Gn = SUPInstance.parse_n_data_lines(f, N, is_index=True)
            LIn = SUPInstance.parse_n_data_lines(f, N, is_index=True)
            LOn = SUPInstance.parse_n_data_lines(f, N, is_index=True)
            if SUPInstance.check_if_provided(f):
                n_import_groups = int(SUPInstance.parse_n_data_lines(f, 1)[0])
            else:
                n_import_groups = 0

            instance = SUPInstance(Gs, Gf, S, T, L, N, n_import_groups)
            instance.Gn, instance.LIn, instance.LOn = Gn, LIn, LOn
            if SUPInstance.check_if_provided(f):
                instance.IG = SUPInstance.parse_n_data_lines(f, 1)

            instance.PI[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.K[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.S[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.C[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.D[:] = np.asarray(
                SUPInstance.parse_n_data_lines(f, N*S)).reshape(N, S, T)
            instance.P_plus[:] = np.asarray(
                SUPInstance.parse_n_data_lines(f, n_generators)).reshape(n_generators, S)
            instance.P_minus[:] = np.asarray(
                SUPInstance.parse_n_data_lines(f, n_generators)).reshape(n_generators, S)
            instance.R_plus[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.R_minus[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.UT[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.DT[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.T_req[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.F_req[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.B[:] = np.asarray(
                SUPInstance.parse_n_data_lines(f, L)).reshape(L, S)
            instance.TC[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
            instance.FR[:] = SUPInstance.parse_n_data_lines(f, 1)[0]

            if SUPInstance.check_if_provided(f):
                instance.IC[:] = SUPInstance.parse_n_data_lines(f, 1)[0]
                instance.GAMMA[:] = SUPInstance.parse_n_data_lines(f, 1)[0]

            return instance