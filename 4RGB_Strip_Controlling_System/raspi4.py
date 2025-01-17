import PySimpleGUI as sg
from time import sleep
import requests

delay = 99
forward = 1
color = sg.rgb(255,255,255)
ip = '192.168.1.69' #some_ip_address
port = 80

layout = [[sg.Text('COLOR: None', size=(None, None), key='-currcol-', auto_size_text=True, pad=((5,5),(80,0)), expand_x=True, font=('Calibri', 48), justification='center')],
         [sg.Button('SELECT A COLOR', key='-selcolor-', size=(14,1), pad=((5,5),(0,0)), enable_events=True, expand_x=True, font=('Calibri', 48))], 
         [sg.Text('DELAY: 99', size=(None, None), key='-del-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), justification='center')],
         [sg.Slider(default_value = 99, range=(0,99), size=(None, None), resolution = 1, key='-delay-', pad=((5,5),(0,0)), orientation = 'horizontal', enable_events=True, expand_x=True, font=('Calibri', 48))],
         [sg.Text('DIRECTION:', size=(None, None), key='-dir-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), justification='center')],
         [sg.Radio('FRWRD:', group_id=1, size=(None, None), key='-frwrd-', auto_size_text=True, pad=((5,5),(0,0)), enable_events=True, expand_x=True, font=('Calibri', 48)),
         sg.Radio('BKWRD:', group_id=1, size=(None, None), key='-bkwrd-', auto_size_text=True, pad=((5,5),(0,0)), enable_events=True, expand_x=True, font=('Calibri', 48))],
         [sg.Button('CLEAR', key='-clear-', size=(5,1), enable_events=True, expand_x=True, font=('Calibri', 48)),
         sg.Button('SET COLOR', key='-setcol-', size=(9,1), enable_events=True, expand_x=True, font=('Calibri', 48)),
         sg.Button('RAINBOW', key='-rain-', size=(8,1), enable_events=True, expand_x=True, font=('Calibri', 48))]]

window = sg.Window('RGB LED Strip Controller', layout, size=(1280,800), finalize=True)



def ColorPopup():
    global color
    layout = [[sg.In("Pick a color", visible=False, enable_events=True, key='set_color'),
           sg.ColorChooserButton("Pick a color", size=(18, 1), target='set_color', button_color=('#1f77b4', '#1f77b4'),border_width=1, key='set_color_chooser', font=('Calibri', 24))]]

    window = sg.Window('Press the button to pick a color', layout)

    while True:
        event, values = window.read()
        if event is None or event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'set_color':
            color=values[event]
            if color == None:
                break
            else:
                try:
                    window['set_color_chooser'].update(button_color=(color, color))
                except Exception as E:
                    print(f'** Error {E} **')
                    color=sg.rgb(255,255,255)
                    window.close()
                    pass    
            break
            
    window.close()
    


try:
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # на всякий случай
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == '-selcolor-':
            #открываем диалог выбора цвета
            print(ColorPopup())
            window['-currcol-'].update('COLOR: '+str(color), text_color=color)
            window.refresh()
            print(color)            
        elif event == '-frwrd-':
            forward = 1
            window['-frwrd-'].update()
            window['-bkwrd-'].update()
            window.refresh()
        elif event == '-bkwrd-':
            forward = 2
            window['-frwrd-'].update()
            window['-bkwrd-'].update()
            window.refresh()
        elif event == '-delay-':
            delay = round(values['-delay-'])
            window['-delay-'].update()  
            window['-del-'].update('DELAY: '+str(delay))
            window.refresh()
        elif event == '-clear-':
            #гасим ленту
            try:
                string = 'http://'+ip+'/clear?params='+str(forward)+str(color[1:])+str(delay)+'1'
                requests.post(string)
                print(string)
            except Exception as E:
                print(f'** Error {E} **')
                   
        elif event == '-setcol-':
            #выполняем заливку ленты выбранным цветом
            try:
                string = 'http://'+ip+'/fill?params='+str(forward)+str(color[1:])+str(delay)+'0'
                requests.post(string)
                print(string)
            except Exception as E:
                print(f'** Error {E} **')
                
        elif event == '-rain-':
            #показываем радугу
            try:                              
                string = 'http://'+ip+'/rainbow?params='+str(forward)+str(color[1:])+str(delay)+'2'
                requests.post(string)
                print(string)
            except Exception as E:
                print(f'** Error {E} **')
                  
        sleep(0.1)

except KeyboardInterrupt:
    window.close()
    
    
    
# закрываем окно и освобождаем используемые ресурсы
window.close()
