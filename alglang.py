from csv import reader as csv_reader
from collections import OrderedDict as odict
from json import load as json_load

# TODO:
# dump_dfa
# NFA
# load_nfa
# dump_nfa
# determ

# ADDITIONAL:
# loads_nfa
# dumps_nfa
# loads_nfa
# dumps_nfa

class FileFormatError(OSError):
    pass

class DFA:
    def __init__(self,alphabet,transition_table,finals):
        column_len = len(transition_table)
        if column_len == 0: 
            raise ValueError('Empty table.')
        if len(alphabet) == 0: 
            raise ValueError('Empty alphabet.')
        if len(finals) == 0: 
            raise ValueError('No finals.')
        if len(set(alphabet)) != len(alphabet): 
            raise ValueError('Repeated characters in alphabet.')
        if len(set(finals)) != len(finals):
            raise ValueError('Repeated values in finals')
        first_row_len = len(transition_table[0])
        if len(alphabet) != first_row_len:
            raise ValueError("Transition table's shape does not corresponde to alphabet.")
        for fin in finals:
            if fin < 0 or fin >= column_len:
                raise ValueError("States in finals are not represented by transition table.")
        for row in transition_table:
            if len(row) != first_row_len:
                raise ValueError("Rows' lengths are not equal.")
            for i in row:
                if i < 0 or i >= column_len:
                    raise ValueError("States in transition table are not represented by it.")
        self._alphamap = odict({ ch:i for i,ch in enumerate(alphabet) })
        self._table = transition_table
        self.finals = set(finals)

    def __eq__(self, other):
        return self.alphabet == other.alphabet and self.finals == other.finals and self._table == other._table 

    def __repr__(self):
        if len(self._alphamap) < 5:
            alph = self.alphabet
        else:
            alph = self.alphabet[:5] + "..."
        if len(self._table[0]) < 4:
            if len(self._table[0]) == 1:
                table = '[' + str(self._table[0]) + ']'
            else:
                table = '[' + str(self._table[0]) + ', ...]'
        else:
            if len(self._table[0]) == 1:
                table = '[[...]]'
            else:
                table = '[[...], ...]'
        if len(self.finals) < 5:
            fins = str(self.finals)
        else:
            fins = '{' + str(list(self.finals)[:5])[1:-1] + ', ...}'
        return f"DFA('{alph}',{table},{fins})"

    def __str__(self):
        maxlen = len(str(len(self._table) - 1))
        pattern = f'%{maxlen}s'
        str_list = ['   ' + (' ' * maxlen) + ' '.join(pattern % ch for ch in self._alphamap)] 
        for i,line in enumerate(self._table):
            str_list.append(('> ' if i in self.finals else '  ') 
                            + pattern % i + '|'
                            + ' '.join(pattern % stt for stt in line))
        return '\n'.join(str_list)

    def __getitem__(self,t):
        i,ch = t
        return self._table[i][self._alphamap[ch]]
    
    @property
    def table(self):
        return [line.copy() for line in self._table]
    
    @property
    def alphabet(self):
        return ''.join(self._alphamap)

    def run(self,string):
        if any(ch not in self._alphamap for ch in string):
            raise ValueError('String contains characters that are not in alphabet')
        cur = 0
        for ch in string:
            cur = self[cur,ch]
        return cur in self.finals

    def minimized(self, get_simulars = False):
        """ 
        Returns minimazed version of DFA\n
        if get_simulars is set, returns tuple of new DFA and list of sets of unified states
        """
        X = 1
        V = 2
        column_len = len(self._table)
        table = { (i,j):(None if i != j else V) for i in range(column_len) for j in range(column_len)[i:] }
        for i,j in table.keys():
            if (i in self.finals and j not in self.finals) or (i not in self.finals and j in self.finals):
                table[(i,j)] = X
        asc = lambda x,y: (x,y) if x <= y else (y,x)
        changes_occurred = True
        while changes_occurred:
            changes_occurred = False
            for i,j in ( t for t,sign in table.items() if sign == None ):
                table2_row = [ asc(self[i,ch],self[j,ch]) for ch in self._alphamap ]
                if any(table[t] == X for t in table2_row):
                    table[(i,j)] = X
                    changes_occurred = True
                    continue
                if all(table[t] == V for t in table2_row):
                    table[(i,j)] = V
                    changes_occurred = True
        for t in (t for t,sign in table.items() if sign == None):
            table[t] = V
        simulars = [ set(t) for t,sign in table.items() if sign == V ]

        # changes_occurred = True
        # while changes_occurred:
        #     changes_occurred = False
        #     for s1 in simulars:
        #         for s2 in simulars:
        #             if s1 is s2:
        #                 continue
        #             if s1.intersection(s2):
        #                 s1.update(s2)
        #                 simulars.remove(s2) 
        #                 changes_occurred = True

        for i,s1 in enumerate(simulars):
            # print(s1)
            changes_occurred = True
            while changes_occurred:
                good_ones =[ s2 for s2 in simulars[(i+1):] if s1.intersection(s2) ]
                changes_occurred = len(good_ones) != 0
                for s2 in good_ones: 
                    s1.update(s2)
                    # print('+',s2,'->',s1)
                for s2 in good_ones:
                    simulars.remove(s2)
                # if changes_occurred: print('again')

        def bucket_index_containing(state):
            for i,buk in enumerate(simulars):
                if state in buk:
                    return i
        def peek(aSet):
            el = aSet.pop()
            aSet.add(el)
            return el

        new_table = [ [ bucket_index_containing(self[peek(buk),ch]) for ch in self._alphamap ] for buk in simulars ]
        new_finals = [ i for i,buk in enumerate(simulars) if peek(buk) in self.finals ]
        new_dfa = DFA(self._alphamap,new_table,new_finals)

        if get_simulars:
            return (new_dfa,simulars)
        else:
            return new_dfa

        # for bucket in simulars:
        #     for ch in self._alphamap:
        #         bucket_iter = iter(bucket)
        #         first_state = next(bucket_iter)
        #         first_state_in_fins = first_state in self.finals
        #         pivot_bucket_index = bucket_index_containing(self[first_state,ch])
        #         for state in bucket_iter:
        #             bucket_index = bucket_index_containing(self[state,ch])
        #             if bucket_index != pivot_bucket_index or first_state_in_fins != state in self.finals:
        #                 raise Exception('Minimizing went wrong!')

        # pattern = '{:>%s}' % len(str(column_len - 1))
        # print(pattern.format(' '), ' '.join(pattern.format(i) for i in range(column_len)))
        # for i in range(column_len):
        #     print(pattern.format(i), end=' ')
        #     for j in range(column_len):
        #         if (i,j) in table:
        #             if table[(i,j)] == 1:
        #                 print(pattern.format('X'), end=' ')
        #             if table[(i,j)] == 2:
        #                 print(pattern.format('V'), end=' ') 
        #         else:
        #             print(pattern.format('*'), end=' ') 
        #     print()

    @staticmethod
    def load(filepath):
        '''
        Loads DFA from file
        '''
        table = []
        with open(filepath, newline='') as csvfile:
            lines_reader = csv_reader(csvfile, delimiter=' ', quotechar="'", skipinitialspace=True)
            try:
                fins = [int(sfin) for sfin in next(lines_reader)]
                alphabet = next(lines_reader)
                table.append([int(s) for s in next(lines_reader)])
            except StopIteration:
                raise FileFormatError('Not enough lines in file.') from None
            if not all(len(ch) == 1 for ch in alphabet):
                raise FileFormatError('All characters in alphabet must be separated.')
            table += [ list(map(int,line)) for line in lines_reader ]
        return DFA(alphabet,table,fins)
    
class NFA:
    def __init__(self,transition_dictionaries,finals):
        amount_of_states = len(transition_dictionaries)
        for state_dict in transition_dictionaries:
            for ch in state_dict:
                state_dict[ch] = set(state_dict[ch])
                for state in state_dict[ch]:
                    if state < 0 or state >= amount_of_states:
                        raise ValueError('States in transition dictionaries are not represented by them.')
        finals = set(finals)
        if any( fin < 0 or fin >= amount_of_states for fin in finals ):
            raise ValueError("States in finals are not represented by transition dictionaries.")
        self._trans_dicts = transition_dictionaries
        self.finals = finals
        self.start_states = self[0,None] | {0}

    def __eq__(self,other):
        return self._trans_dicts == other._trans_dicts and self.finals == other.finals

    def __getitem__(self,t):
        i,ch = t
        # def get_nones(state):
        #     local_res = self._trans_dicts[i].get(None, set())
            
        #     for state in local_res - res
        # for state in res:
        #     res |= self[state,None]
        states_to_check = self._trans_dicts[i].get(ch, set())
        res = set()
        new_states = set()
        while len(states_to_check) != 0:
            res.update(states_to_check)
            new_states.clear()
            for state in states_to_check:
                new_states.update(self._trans_dicts[state].get(None, set()))
            states_to_check = new_states - res
        return frozenset(res)

    def run(self,string,start=None):
        curs = start if start is not None else self.start_states
        for ch in string:
            new_curs = set()
            for cur in curs:
                new_curs.update(self[cur,ch])
            curs = new_curs
        return bool(curs & self.finals)

    def determinize(self):
        alphabet = self.alphabet
        buckets_to_check = {self.start_states}
        res_buckets = {}
        new_buckets = set()
        while len(buckets_to_check) != 0:
            new_buckets.clear()
            for bucket in buckets_to_check:
                res_buckets[bucket] = []
                for ch in alphabet:
                    new_buk = frozenset()
                    for state in bucket:
                        new_buk |= self[state,ch]
                    res_buckets[bucket].append(new_buk)
                    new_buckets.add(new_buk)
            buckets_to_check = new_buckets - set(res_buckets)
        table = []
        finals = []
        res_buckets_list = list(res_buckets)
        for i,bucket in enumerate(res_buckets_list):
            if bucket & self.finals:
                finals.append(i)
            table.append([])
            for trans_buk in res_buckets[bucket]:
                table[i].append(res_buckets_list.index(trans_buk))
        return DFA(alphabet,table,finals)

    @property
    def alphabet(self):
        alph = set()
        for state_dict in self._trans_dicts:
            alph.update(set(state_dict))
        alph.discard(None)
        return alph

    @staticmethod
    def load(jsonpath):
        '''
        Loads NFA from file
        '''
        with open(jsonpath, newline='') as file:
            loaded_dict = json_load(file)
        if 'finals' not in loaded_dict:
            raise FileFormatError('Json does not contaun key "finals".')
        if 'trans_dicts' not in loaded_dict:
            raise FileFormatError('Json does not contaun key "trans_dicts".')
        for state_dict in loaded_dict['trans_dicts']:
            if "null" in state_dict:
                state_dict[None] = state_dict.pop("null")
        return NFA(loaded_dict['trans_dicts'], loaded_dict['finals'])

# d = DFA.load('nonmin2.txt')
# print(d)
# md,sims = d.minimized(True)
# print(sims)
# print(md)
# print(md == d)
# d2 = DFA.load('nonmin2.txt')
# print(d2 == d)
# print(repr(d))
# print(repr(md))
# print(repr(d2))

n = NFA.load('a..b.json')
print(n.alphabet)
d = n.determinize()
print(d)
norm = d.minimized()
print(norm)