from sys import argv
from os.path import exists, isdir

if __name__  == "__main__":
    ERROR_SUCCESS = 0x0
    ERROR_FILE_NOT_FOUND = 0x2
    ERROR_BAD_ARGUMENTS = 0xA0
    ERROR_BAD_FORMAT = 0xB    
    if '/?' in argv[1:]:
        print("Проверка строчек на соответствие их автомату.")
        print()
        print("DFACHK diagram [count] [/P]")
        print("  diagram      Файл со схемой автомата и алфавитом.")
        print("  /P           Показывать путь через автомат.")
        print("  count        Количество строк что будет проверенно.")
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
    count = 0
    show_path = False
    alphabet = ''
    dfa = []
    fins = []
    #Chekeing for incorrect input
    if len(argv) < 2:
        print('Не указан файл со схемой автомата.')
        quit(ERROR_BAD_ARGUMENTS)
    if len(argv) > 2:
        if len(argv) == 3: #Two arguments
            if argv[2] == '/p' or argv[2] == '/P':
                show_path = True
            else:
                try:
                    count = int(argv[2])
                    if count <= 0:
                        print('Параметр count меньше или равен нулю.')
                        quit(ERROR_BAD_ARGUMENTS)
                except ValueError:
                    print('Вторым параметром идет несуществющий флаг или целое число неверного формата.')
                    quit(ERROR_BAD_ARGUMENTS)
        elif len(argv) == 4: #Three arguments
            try:
                count = int(argv[2])
                if count <= 0:
                    print('Параметр count меньше или равен нулю.')
                    quit(ERROR_BAD_ARGUMENTS)
            except ValueError:
                print('Неверный формат параметра count.')
                quit(ERROR_BAD_ARGUMENTS)
            if argv[3] != '/p' and argv[3] != '/P': 
                print('Третьим параметром идет несуществющий флаг.')
                quit(ERROR_BAD_ARGUMENTS)
            show_path = True
        else:
            print('Колличество парметров превышает требуемое.')
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
    # Main process of state-jumping
    if count == 0:
        if show_path:
            while True:
                string = input()
                if any(ch not in alphabet for ch in string):
                    print('Символы строки не входят в алфавит.')
                    count -= 1
                    continue
                cur = 0
                print('   ->(q0)',end = '')
                for ch in string:
                    cur = dfa[cur][alphabet.index(ch)]
                    print(f'->\n[{ch}]->(q{cur})', end = '')
                print()
                print(cur in fins)
        else:
            while True:
                string = input()
                if any(ch not in alphabet for ch in string):
                    print('Символы строки не входят в алфавит.')
                    count -= 1
                    continue
                cur = 0
                for ch in string:
                    cur = dfa[cur][alphabet.index(ch)]
                print(cur in fins)
    else:
        if show_path:
            while count != 0:
                string = input()
                if any(ch not in alphabet for ch in string):
                    print('Символы строки не входят в алфавит.')
                    count -= 1
                    continue
                cur = 0
                print('   ->(q0)',end = '')
                for ch in string:
                    cur = dfa[cur][alphabet.index(ch)]
                    print(f'->\n[{ch}]->(q{cur})', end = '')
                print() 
                print(cur in fins)
                count -= 1
        else:
            while count != 0:
                string = input()
                if any(ch not in alphabet for ch in string):
                    print('Символы строки не входят в алфавит.')
                    count -= 1
                    continue
                cur = 0
                for ch in string:
                    cur = dfa[cur][alphabet.index(ch)]
                print(cur in fins)
                count -= 1 
                
                


