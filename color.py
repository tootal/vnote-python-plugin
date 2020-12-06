#-*- coding:utf-8 -*-#

#filename: prt_cmd_color.py

import ctypes,sys

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
front_color={
    'blue': 0x09,
    'green': 0x0a,
    'red': 0x0c,
    'yellow': 0x0e,
    'white': 0x0f
}
back_color={
    'yellow': 0xe0
} 
 
# get handle
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
 
def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool
 
#reset white
def resetColor():
    set_cmd_text_color(front_color['white'])

def print(s,color='white',end='\n'):
    set_cmd_text_color(front_color[color])
    sys.stdout.write(s+end)
    resetColor()
 
if __name__ == '__main__':
    printGreen('printGreen:Gree Color Text')
    printRed('printRed:Red Color Text')
    printYellow('printYellow:Yellow Color Text')