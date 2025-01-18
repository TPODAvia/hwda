import PySimpleGUI as sg
from time import sleep
import requests

# Global variables
delay = 99
# forward=1 => "forward", forward=2 => "backward"
forward = 1
# color is stored as a string like "#RRGGBB"
color = sg.rgb(255, 255, 255)
ip = '192.168.172.222'  # ESP-01 IP address
port = 80               # ESP-01 web server port

################
# GUI LAYOUT
################
layout = [
    [sg.Text('COLOR: None', size=(None, None), key='-currcol-', 
             auto_size_text=True, pad=((5,5),(80,0)), expand_x=True, 
             font=('Calibri', 48), justification='center')],

    [sg.Button('SELECT A COLOR', key='-selcolor-', size=(14,1), 
               pad=((5,5),(0,0)), enable_events=True, expand_x=True, 
               font=('Calibri', 48))],

    [sg.Text('DELAY: 99', size=(None, None), key='-del-', auto_size_text=True, 
             pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), 
             justification='center')],

    [sg.Slider(default_value=99, range=(0,99), size=(None, None), resolution=1, 
               key='-delay-', pad=((5,5),(0,0)), orientation='horizontal', 
               enable_events=True, expand_x=True, font=('Calibri', 48))],

    [sg.Text('DIRECTION:', size=(None, None), key='-dir-', auto_size_text=True, 
             pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), 
             justification='center')],

    [sg.Radio('FRWRD:', group_id=1, size=(None, None), key='-frwrd-', 
              auto_size_text=True, pad=((5,5),(0,0)), enable_events=True, 
              expand_x=True, font=('Calibri', 48)),
     sg.Radio('BKWRD:', group_id=1, size=(None, None), key='-bkwrd-', 
              auto_size_text=True, pad=((5,5),(0,0)), enable_events=True, 
              expand_x=True, font=('Calibri', 48))],

    [sg.Button('CLEAR', key='-clear-', size=(5,1), enable_events=True, 
               expand_x=True, font=('Calibri', 48)),
     sg.Button('SET COLOR', key='-setcol-', size=(9,1), enable_events=True, 
               expand_x=True, font=('Calibri', 48)),
     sg.Button('RAINBOW', key='-rain-', size=(8,1), enable_events=True, 
               expand_x=True, font=('Calibri', 48))]
]

window = sg.Window('RGB LED Strip Controller', layout, size=(1280,800), finalize=True)

################
# COLOR POPUP
################
def ColorPopup():
    """
    Show a small color chooser popup dialog.
    Updates the global color variable with the new color (#RRGGBB).
    """
    global color
    popup_layout = [
        [sg.In("Pick a color", visible=False, enable_events=True, key='set_color'),
         sg.ColorChooserButton("Pick a color", size=(18, 1), target='set_color', 
                               button_color=('#1f77b4', '#1f77b4'), border_width=1, 
                               key='set_color_chooser', font=('Calibri', 24))]
    ]

    popup_window = sg.Window('Press the button to pick a color', popup_layout)

    while True:
        event, values = popup_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'set_color':
            color = values[event]
            if color is None:
                break
            else:
                try:
                    popup_window['set_color_chooser'].update(button_color=(color, color))
                except Exception as E:
                    print(f'** Error {E} **')
                    color = sg.rgb(255, 255, 255)
                    popup_window.close()
                    break
            break

    popup_window.close()

################
# MAIN LOOP
################
try:
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # Color selection
        if event == '-selcolor-':
            ColorPopup()
            # Update the displayed color in the main window
            window['-currcol-'].update('COLOR: ' + str(color), text_color=color)
            window.refresh()

        # Direction radio buttons
        elif event == '-frwrd-':
            forward = 1
            window['-frwrd-'].update(value=True)
            window['-bkwrd-'].update(value=False)
            window.refresh()

        elif event == '-bkwrd-':
            forward = 2
            window['-frwrd-'].update(value=False)
            window['-bkwrd-'].update(value=True)
            window.refresh()

        # Delay slider
        elif event == '-delay-':
            delay = round(values['-delay-'])
            window['-del-'].update('DELAY: ' + str(delay))
            window.refresh()

        # CLEAR the strip
        elif event == '-clear-':
            try:
                # We'll add a dummy "cycle" value of '1' at the end
                # If your Arduino code expects something else, adjust accordingly.
                url = f'http://{ip}:{port}/clear?params={forward}{color[1:]}{delay}1'
                print(f"REQUEST: {url}")
                r = requests.get(url, timeout=3)
                print(f"RESPONSE: {r.status_code}, {r.text}")
            except Exception as E:
                print(f'** Error {E} **')

        # SET COLOR (fill)
        elif event == '-setcol-':
            try:
                # cycle = '0' as an example
                url = f'http://{ip}:{port}/fill?params={forward}{color[1:]}{delay}0'
                print(f"REQUEST: {url}")
                r = requests.get(url, timeout=3)
                print(f"RESPONSE: {r.status_code}, {r.text}")
            except Exception as E:
                print(f'** Error {E} **')

        # RAINBOW
        elif event == '-rain-':
            try:
                # cycle = '2' as an example
                url = f'http://{ip}:{port}/rainbow?params={forward}{color[1:]}{delay}2'
                print(f"REQUEST: {url}")
                r = requests.get(url, timeout=3)
                print(f"RESPONSE: {r.status_code}, {r.text}")
            except Exception as E:
                print(f'** Error {E} **')

        sleep(0.1)

except KeyboardInterrupt:
    pass

window.close()