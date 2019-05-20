from sys import argv
from os.path import exists, isdir

def indexes(l): return range(len(l))
def asc(a,b):
    if a > b:
        return (b,a)
    return (a,b)


if __name__  == "__main__":
    ERROR_SUCCESS = 0x0
    ERROR_FILE_NOT_FOUND = 0x2
    ERROR_BAD_ARGUMENTS = 0xA0
    ERROR_BAD_FORMAT = 0xB    
    if '/?' in argv[1:]:
        print("Минимизация алфавита.")
        print()
        print("DFAMIN diagram")
        print("  diagram      Файл со схемой автомата и алфавитом.")
        print()
        print("Содержание файла:")
        print("<номера финальных состояний, разделенные пробелами>")
        print("<символы алфавита, разделенные пробелами и расставленные в соответствии со схемой>")
        print("<разделенные пробелами номера сотояний, к которым перейдет автомат по соответствующему символу из состояния №0>")
        print("<разделенные пробелами номера сотояний, к которым перейдет автомат по соответствующему символу из состояния №1>")
        print("  .")
        print("  .")
        print("  .")
        print("<разделенные пробелами номера сотояний, к которым перейдет автомат по соответствующему символу из состояния №K>")
        print()
        print("Пример:")
        print("0")
        print("0 1")
        print("0 1")
        print("1 0")
        print("Этот автомат принимает только строчки с четным количеством едениц")
        
        quit(ERROR_SUCCESS)
    alphabet = ''
    dfa = []
    fins = []
    #Chekeing for incorrect input
    if len(argv) < 2:
        print('Не указан файл со схемой автомата.')
        quit(ERROR_BAD_ARGUMENTS)
    if not exists(argv[1]):
        print('Файл не найден.')
        quit(ERROR_FILE_NOT_FOUND)
    if isdir(argv[1]):
        print('Вместо файла указан каталог.')
        quit(ERROR_FILE_NOT_FOUND)
    with open(argv[1]) as file: filelines = file.readlines()
    if len(filelines) < 3:
        print('Неверный формат файла: недостаточное количество строк.')
        quit(ERROR_BAD_FORMAT)
    alphabet = filelines[1].replace(' ','')[:-1]
    if len(alphabet) != len(set(alphabet)):
        print('Неверный формат файла: повторяющиеся символы в алфавите.') 
        quit(ERROR_BAD_FORMAT)
    try:
        fins = [int(sfin) for sfin in filelines[0].split()]
        for fline in filelines[2:]:
            dfa.append([int(s) for s in fline.split()])    
    except ValueError:
        print('Неверный формат файла: неверный формат целочисленных значений.') 
        quit(ERROR_BAD_FORMAT)
    if len(fins) != len(set(fins)):
        print('Неверный формат файла: повторяющиеся номера состояний.') 
        quit(ERROR_BAD_FORMAT)
    first_row_len = len(dfa[0])
    column_len = len(dfa)
    if len(alphabet) != first_row_len:
        print('Неверный формат файла: размер алфавита не соответствует схеме.')
        quit(ERROR_BAD_FORMAT)
    for fin in fins:
        if fin < 0 or fin >= column_len:
            print('Неверный формат файла: финальные состояния не соответствуют схеме.') 
            quit(ERROR_BAD_FORMAT)
    for row in dfa:
        if len(row) != first_row_len:
            print('Неверный формат файла: разные длины строк схемы.')
            quit(ERROR_BAD_FORMAT)
        for i in row:
            if i < 0 or i >= column_len:
                print('Неверный формат файла: содержимое схемы указывает за ее пределы.')
                quit(ERROR_BAD_FORMAT)
    # Main process of dfa minimizing
    X = 1
    V = 2
    table = { (i,j):(None if i != j else V) for i in range(column_len) for j in range(column_len)[i:] }
    for i,j in table.keys():
        if (i in fins and j not in fins) or (i not in fins and j in fins):
            table[(i,j)] = X
    changes_occurred = True
    while changes_occurred:
        changes_occurred = False
        for i,j in ( t for t,sign in table.items() if sign == None ):
            table2_row = [ asc(dfa[i][indx],dfa[j][indx]) for indx in range(first_row_len) ]
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
    
    print(simulars)
    
    changes_occurred = True
    while changes_occurred:
        changes_occurred = False
        for s1 in simulars:
            for s2 in simulars:
                if s1 == s2:
                    continue
                if s1.intersection(s2):
                    s1.update(s2)
                    changes_occurred = True
                    del simulars[simulars.index(s2)]
                    
    print(simulars)
    
    def index_of_a_bucket_that_contains(state):
        for i in indexes(simulars):
            if state in simulars[i]:
                return i
        raise Exception
        
    new_dfa = [ [ ] for _ in simulars]
    for bucket in simulars:
        print(f'{bucket}:')
        for letter_index in range(first_row_len):# aka indexes(alphabet)
            print('  ' + alphabet[letter_index] + ':')
            bucket_iter = iter(bucket)
            first_state = next(bucket_iter)
            pivot_bucket_index = index_of_a_bucket_that_contains(dfa[first_state][letter_index])
            print(f'    {simulars[pivot_bucket_index]}:')
            for state in bucket_iter:
                bucket_index = index_of_a_bucket_that_contains(dfa[state][letter_index])
                print(f'    {simulars[bucket_index]}:')
    
    pattern = '{:>%s}' % len(str(column_len - 1))
    print(pattern.format(' '), ' '.join(pattern.format(i) for i in range(column_len)))
    for i in range(column_len):
        print(pattern.format(i), end=' ')
        for j in range(column_len):
            if (i,j) in table:
                if table[(i,j)] == 1:
                    print(pattern.format('X'), end=' ')
                if table[(i,j)] == 2:
                    print(pattern.format('V'), end=' ') 
            else:
                print(pattern.format('*'), end=' ') 
        print()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
