# import pretty_errors

import PySimpleGUI as sg
import tabulate

import random, math
from pprint import pprint
import webbrowser

sg.theme('Reddit')

window_title = 'Распределитель билетов'
bilet_count = 30
students_count = 5
student_names = list()
student_numbers = list()
printout_data = dict()
bilets_width = 10
all_valid = False
colors = [
    '#DFFF00', '#FFBF00', '#FF7F50', '#DE3163',
    '#9FE2BF', '#40E0D0', '#89CFF0', '#6495ED',
    '#CCCCFF', '#E0B0FF'
]

def new_student_row(i, name, number):
    return [
        sg.Text(i+1, size=(2, 1), justification='left'),
        sg.Input(name, size=(20, 1), key=f'_table_name_{i}', justification='left'),
        sg.Input(number, size=(7, 1), key=f'_table_num_{i}', justification='left', tooltip=f'Целое число от 1 до {bilet_count}'),
        sg.Text('', size=(6, 1), key=f'_table_b_{i}', justification='left')
    ]

def generate_layout(generate_bilets=False):
    layout = [
        [
            sg.Text('#', size=(2, 1), justification='left'),
            sg.Text('Фамилия', size=(20, 1), justification='left'),
            sg.Text('Загадал', size=(7, 1), justification='left', tooltip='Загаданный студентом номер'),
            sg.Text('Билет', size=(6, 1), justification='left', tooltip='Здесь появится номер вытащенного билета')
        ],
        *[new_student_row(i, '', i+1) for i in range(students_count)],
        [
            sg.Button('Добавить студента', key='add'),
            sg.Button('Распределить билеты', key='distribute')
        ],
        [
            sg.Text('Число билетов'),
            sg.Input(bilet_count, key='bilet_count', size=(4, 1), tooltip='Число билетов'),
            sg.Text('', size=(15,1)),
            sg.Button('@', key='github', pad=(0,0), tooltip='Перейти на веб-страницу программы')
        ],
        [
            sg.Text('', text_color="#ff0000", key='_error', size=(40,1)),
        ]
    ]

    if generate_bilets:
        grid = list()
        pool = list()
        row_num = math.ceil(bilet_count // bilets_width) + 1

        for h in range(row_num):
            row = list()
            for w in range(bilets_width):
                bilet_num = h * bilets_width + w
                if bilet_num < bilet_count:
                    row.append(sg.Text(bilet_num+1, size=(3,1), key=f'_bilet_{bilet_num+1}', justification='right'))
                else:
                    break
            grid.append(row)

        for h in range(row_num):
            row = list()
            for w in range(bilets_width):
                bilet_num = h * bilets_width + w
                if bilet_num < bilet_count:
                    row.append(sg.Text('', size=(3,1), key=f'_pool_{bilet_num+1}', justification='right'))
                else:
                    break
            pool.append(row)

        layout += [
            [sg.HorizontalSeparator()],
            [sg.Text('Перемешанные билеты')],
            *pool,
            [sg.HorizontalSeparator()],
            [sg.Text('Совпадения с загаданным номером')],
            *grid,
            [sg.Button('Распечатать', key='printout')]
        ]

    return layout

layout = generate_layout()
window = sg.Window(window_title, generate_layout())
window.Finalize()

while True:  # Event Loop
    event, values = window.read()
    print(values)

    if values is not None:
        bilet_count = int(values['bilet_count'])
        student_names = [values[f'_table_name_{i}'] for i in range(students_count)] + ['']
        student_numbers = [values[f'_table_num_{i}'] for i in range(students_count)] + ['']
        loc = window.CurrentLocation()

        all_valid = True
        for i in range(students_count):
            key = f'_table_num_{i}'
            window[key].update(background_color=sg.theme_input_background_color())
            if not values[key].isdigit():
                window[key].update(background_color='#ffaaaa')
                window['_error'].update('Загаданный номер - не число!')
                all_valid = False
                continue

            if not (0 < int(values[key]) <= int(values['bilet_count'])):
                window[key].update(background_color='#ffaaaa')
                window['_error'].update(f'Загаданный номер < 1 или > {bilet_count}')
                all_valid = False
                continue

    if event is None or event == 'Exit':
        break


    elif event == 'add':
        students_count += 1

        window.Close()
        window = sg.Window(window_title, location=loc).Layout(generate_layout())
        window.Finalize()

        for i in range(students_count):
            window[f'_table_name_{i}'].update(student_names[i])
            window[f'_table_num_{i}'].update(student_numbers[i])
        window[f'_table_num_{students_count-1}'].update(students_count)


    elif event == 'distribute':
        if all_valid:
            window.Close()
            window = sg.Window(window_title, location=loc).Layout(generate_layout(generate_bilets=True))
            window.Finalize()

            for i in range(students_count):
                window[f'_table_name_{i}'].update(student_names[i])
                window[f'_table_num_{i}'].update(student_numbers[i])

            # ensure numbers are unique
            if not len(set(student_numbers)) == len(student_numbers):
                print('Not unique')
                print(student_numbers)

                used_numbers = list()
                for i, vv in enumerate(student_numbers[:-1]):
                    v = int(vv)
                    if v not in used_numbers:
                        used_numbers.append(v)
                    else:
                        v2 = v
                        while True:
                            v2 += 1
                            v2 = v2 % bilet_count
                            print(v2)
                            if v2 not in used_numbers:
                                used_numbers.append(v2)
                                student_numbers[i] = v2
                                window[f'_table_num_{i}'].update(v2)
                                break

            bilets = list(range(1, int(values['bilet_count']) + 1))
            random.shuffle(bilets)

            for i, v in enumerate(bilets):
                window[f'_pool_{i+1}'].update(v)

            printout_data['Фамилия'] = list()
            printout_data['Билет'] = list()

            for i in range(students_count):
                window[f'_table_b_{i}'].update(bilets[int(student_numbers[i]) - 1], background_color=colors[i % len(colors)])

                window[f'_pool_{int(student_numbers[i])}'].update(background_color=colors[i % len(colors)])
                window[f'_bilet_{bilets[int(student_numbers[i]) - 1]}'].update(background_color=colors[i % len(colors)])

                printout_data['Фамилия'].append(values[f'_table_name_{i}'])
                printout_data['Билет'].append(bilets[int(student_numbers[i]) - 1])


    elif event == 'printout':
        layout = [[sg.Multiline(tabulate.tabulate(printout_data, headers='keys'), size=(40, students_count+4))]]
        window2 = sg.Window('Список', layout, modal=True)
        window2.Finalize()

    elif event == 'github':
        webbrowser.open('https://github.com/xtotdam/exam-tickets-distributor')
