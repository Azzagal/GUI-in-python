import customtkinter
import os
from PIL import Image
from datetime import date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Tension():
    def __init__(self, sys, dias, date):
        self.sys = sys
        self.dias = dias
        self.date = date

    def toString(self):
        return "Systolique: " + self.sys + "\n Diastolique: " + self.dias + "\n Date: " + self.date

class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, buttonDisable=False ,**kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = self.remove_item
        self.buttonDisable = buttonDisable
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []
        self.show_list = []

    def add_item(self, item, image=None):
        label_text = item.toString()
        label = customtkinter.CTkLabel(self, text=label_text, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Supprimer", width=100, height=24, fg_color="red", hover_color="#A62F2F")
        
        if self.buttonDisable:
            button.configure(state="disabled")
        
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        

        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)
        self.show_list.append(item)

    def remove_item(self, item):
        for label, button, tension in zip(self.label_list, self.button_list, self.show_list):
            if item.sys == tension.sys and item.dias == tension.dias and item.date == tension.date:
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                self.show_list.remove(tension)

                with open("tension.txt","w") as file:
                    for tension in self.show_list:
                        file.write(tension.sys + " " + tension.dias + " " + tension.date + "\n")

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, utility ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(f"{1100}x{580}")
        
        self.focus() #focus the window
        
        if(utility == "add"):
            self.title("Ajout de tension")
            self.Scroll = ScrollableLabelButtonFrame(self,buttonDisable=True,width=400)
            self.Scroll.pack()

            self.sys = customtkinter.CTkEntry(self, placeholder_text="Systolique")
            self.sys.pack(padx=20, pady=10, anchor="center")

            self.dias = customtkinter.CTkEntry(self, placeholder_text="Diastolique")
            self.dias.pack(padx=20, pady=10, anchor="center")

            self.diasButton = customtkinter.CTkButton(self, command=self.add, text="OK")
            self.diasButton.pack(padx=20, pady=10, anchor="center")

        if(utility == "show"):
            self.title("Historique de tension")
            self.Scroll = ScrollableLabelButtonFrame(self,width=400)
            self.Scroll.pack()
            tensions = []
            with open("tension.txt") as file:
                lines = file.readlines()
            for line in lines:
                self.Scroll.show_label = line
                lineData = line.split()
                tensions.append(Tension(lineData[0],lineData[1],lineData[2]))
                self.Scroll.add_item(tensions[-1])

    def add(self):

        today = date.today()

        # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y") 

        with open("tension.txt") as file:
            lines = file.readlines()
    
        newValue = self.sys.get() +" "+ self.dias.get() +" "+ d1 + "\n"
        tension = Tension(self.sys.get(),self.dias.get(),d1)
        lines.append(newValue)

        with open("tension.txt","w") as file:
            for line in lines:
                file.write(line)
        self.Scroll.add_item(tension)
        self.sys.delete(0, 'end')
        self.dias.delete(0, 'end')

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Historique de tension")
        self.geometry(f"{1100}x{580}")
        self.theme = "dark"

        # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # load all the images 
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.icon_dark_theme = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "dark_theme.png")), size=(40, 40))
        self.icon_light_theme = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "light_theme.png")), size=(40, 40))
    
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, height=1 ,corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Actions", font=customtkinter.CTkFont(size=40, weight="bold", family="Roboto" ))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_add = customtkinter.CTkButton(self.sidebar_frame, command=self.add, text="Ajouter")
        self.sidebar_button_add.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_show = customtkinter.CTkButton(self.sidebar_frame, command=self.show, text="Afficher / Modifier")
        self.sidebar_button_show.grid(row=2, column=0, padx=20, pady=10)
        self.appearance_mode_button = customtkinter.CTkButton(self.sidebar_frame,text="" ,fg_color="transparent" ,command=self.change_appearance_mode_event , image=self.icon_light_theme, hover_color="none")
        self.appearance_mode_button.grid(row=5, column=0, padx=20, pady=(10, 0))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250,command=self.update_graph)
        self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Diastolique")
        self.tabview.add("Systolique")
        self.tabview.tab("Systolique").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Diastolique").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        # create the graph
        self.update_graph()

        self.sysGraph = customtkinter.CTkLabel(self.tabview.tab("Systolique"), image=self.sys_image,text="")
        self.sysGraph.grid(row=0, column=0, padx=20, pady=20)
        self.diasGraph = customtkinter.CTkLabel(self.tabview.tab("Diastolique"), image=self.dias_image,text="")
        self.diasGraph.grid(row=0, column=0, padx=20, pady=20) 

        self.toplevel_window = None

    def change_appearance_mode_event(self):
        if(self.theme == "dark"):
            self.theme = "light"
            self.appearance_mode_button.configure(image=self.icon_dark_theme)
        else:
            self.theme = "dark"
            self.appearance_mode_button.configure(image=self.icon_light_theme)
        customtkinter.set_appearance_mode(self.theme)

    def get_appearance_mode(self):
        if(self._get_appearance_mode == "dark"):
            return self.icon_dark_theme
        else:
            return self.icon_light_theme

    def add(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(utility="add") # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
    
    def show(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(utility="show") # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
    #All the function to create the plots
    
    def construct_graph(self,Sys,Dia, input,refSys,refDia):

        # open the file
        file = open(input,'r')
    
        list_sys = []
        list_Dia = []
        date =[]
        cnt = 0
        prevdate = ""

        # reading each line
        for line in file:
            # reading each word and save each in an element of the list 
            lineData = line.split()

            # If there is an empty line, We do the mean and we add the appropriate list
            if (prevdate == "" or prevdate == lineData[2]):
                list_sys.append(int(lineData[0]))
                list_Dia.append(int(lineData[1]))
                prevdate = lineData[2]
                cnt += 1

            # take maximum 3 values of the same date and do the mean
            if(prevdate != lineData[2] or cnt > 3):
                #create the mean of the list
                Sys.append(self.mean(list_sys))
                Dia.append(self.mean(list_Dia))
                date.append(prevdate)
                refSys.append(135)
                refDia.append(85)
                list_sys = []
                list_Dia = []
                #append the value of the new date
                list_sys.append(int(lineData[0]))
                list_Dia.append(int(lineData[1]))
                prevdate = lineData[2] #update the previous date
                cnt = 1 #reset the counter

        #create the mean of the list
        # To don't forget the last value
        Sys.append(self.mean(list_sys))
        Dia.append(self.mean(list_Dia))
        refSys.append(135)
        refDia.append(85)
        date.append(lineData[2])

        #close the file
        file.close()
        return date
                
    def mean(self,List):
        if(len(List)==0):
            return
        mean = 0
        for element in List:
            mean += element

        return mean / len(List) 

    def save_graph(self,graph,date,ref,filename):
        plt.figure()
        plt.plot(date,graph,ref,marker='o')
        plt.savefig(filename)
    
    def update_graph(self):
        #construct the plots
        Sys = []
        Dia = []
        refSys = []
        refDia = []
        date = self.construct_graph(Sys,Dia,"tension.txt",refSys,refDia)
        self.save_graph(Dia,date,refDia,"images\\Diastolique.png")
        self.save_graph(Sys,date,refSys,"images\\Systolique.png")
        self.sys_image = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "Systolique.png")), size=(800, 500))
        self.dias_image = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "Diastolique.png")), size=(800, 500))

        self.sysGraph = customtkinter.CTkLabel(self.tabview.tab("Systolique"), image=self.sys_image,text="")
        self.sysGraph.grid(row=0, column=0, padx=20, pady=20)
        self.diasGraph = customtkinter.CTkLabel(self.tabview.tab("Diastolique"), image=self.dias_image,text="")
        self.diasGraph.grid(row=0, column=0, padx=20, pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()