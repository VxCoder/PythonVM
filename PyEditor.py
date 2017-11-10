# coding=utf-8
import tkFont
from Tkinter import *
from ttk import *
from PIL.ImageOps import expand


# open_file_icon = PhotoImage(file='icons/open_file.gif')
# save_file_icon = PhotoImage(file='icons/save.gif')
# cut_icon = PhotoImage(file='icons/cut.gif')
# copy_icon = PhotoImage(file='icons/copy.gif')
# paste_icon = PhotoImage(file='icons/paste.gif')
# undo_icon = PhotoImage(file='icons/undo.gif')
# redo_icon = PhotoImage(file='icons/redo.gif')


class PyEditor(Frame):

    COLOR_SCHEMES = {
        'Default': '#000000.#FFFFFF',
        'Greygarious': '#83406A.#D1D4D1',
        'Aquamarine': '#5B8340.#D1E7E0',
        'Bold Beige': '#4B4620.#FFF0E1',
        'Cobalt Blue': '#ffffBB.#3333aa',
        'Olive Green': '#D1E7E0.#5B8340',
        'Night Mode': '#FFFFFF.#000000',
    }

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.pack()
        self.init_resource()
        self.init_style()
        self.create_widgets()

    def init_style(self):
        self.background = "#272822"
        self.main_color = "#A7EC21"
        self.font = tkFont.Font(family='Helvetica', size=12, weight='bold')

        Style().configure("Frame", background=self.background, foreground="#52E3F6", font=self.font)

    def init_resource(self):
        self.new_file_icon = PhotoImage(file='icons/new_file.gif')
        self.open_file_icon = PhotoImage(file='icons/open_file.gif')
        self.save_file_icon = PhotoImage(file='icons/save.gif')
        self.cut_icon = PhotoImage(file='icons/cut.gif')
        self.copy_icon = PhotoImage(file='icons/copy.gif')
        self.paste_icon = PhotoImage(file='icons/paste.gif')
        self.undo_icon = PhotoImage(file='icons/undo.gif')
        self.redo_icon = PhotoImage(file='icons/redo.gif')

    def create_widgets(self):
        menu_bar = Menu()

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New',
                              accelerator='Ctrl+N',
                              compound='left',
                              image=self.new_file_icon,
                              underline=0,
                              command=self.new_file)
        file_menu.add_command(label='Open',
                              accelerator='Ctrl+O',
                              compound='left',
                              image=self.open_file_icon,
                              underline=0)
        file_menu.add_command(label='Save',
                              accelerator='Ctrl+S',
                              compound='left',
                              image=self.save_file_icon,
                              underline=0)
        file_menu.add_command(label='Save as', accelerator='Shift+Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4')
        menu_bar.add_cascade(label='File', menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z',
                              compound='left', image=self.undo_icon)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y',
                              compound='left', image=self.redo_icon)
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X',
                              compound='left', image=self.cut_icon)
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C',
                              compound='left', image=self.copy_icon)
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V',
                              compound='left', image=self.paste_icon)
        edit_menu.add_separator()
        edit_menu.add_command(label='Find', underline=0, accelerator='Ctrl+F')
        edit_menu.add_separator()
        edit_menu.add_command(label='Select All', underline=7, accelerator='Ctrl+A')
        menu_bar.add_cascade(label='Edit', menu=edit_menu)

        view_menu = Menu(menu_bar, tearoff=0)
        self.show_line_number = IntVar()
        self.show_line_number.set(1)
        view_menu.add_checkbutton(label='Show Line Number', variable=self.show_line_number)
        self.show_cursor_info = IntVar()
        self. show_cursor_info.set(1)
        view_menu.add_checkbutton(label='Show Cursor Location at Bottom', variable=self.show_cursor_info)
        self.highlight_line = IntVar()
        view_menu.add_checkbutton(label='Highlight Current Line', onvalue=1,
                                  offvalue=0, variable=self.highlight_line)
        themes_menu = Menu(menu_bar, tearoff=0)
        view_menu.add_cascade(label='Themes', menu=themes_menu)
        self.theme_choice = StringVar()
        self.theme_choice.set('Default')
        for k in sorted(self.COLOR_SCHEMES):
            themes_menu.add_radiobutton(label=k, variable=self.theme_choice)
        menu_bar.add_cascade(label='View', menu=view_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label='About')
        about_menu.add_command(label='Help')
        menu_bar.add_cascade(label='About', menu=about_menu)

        self.master.config(menu=menu_bar)

        shortcut_bar = Frame(height=25)
        shortcut_bar.pack(expand=False, fill=X)

        line_number_bar = Text(width=4, padx=3, takefocus=0, border=0,
                               background='khaki', state=DISABLED, wrap=NONE)
        line_number_bar.pack(side=LEFT, fill=Y)

        content_text = Text(wrap=WORD)
        content_text.pack(expand=True, fill=BOTH)

        scroll_bar = Scrollbar(content_text)
        content_text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=content_text.yview)
        scroll_bar.pack(side=RIGHT, fill=Y)

    def new_file(self):
        print "new_file"

    @classmethod
    def run(cls):
        root = Tk()
        root.title("Python Editor")
        root.geometry('400x400')
        root.resizable(width=True, height=True)
        app = cls(master=root)
        app.mainloop()


def main():
    PyEditor.run()

if __name__ == "__main__":
    main()
