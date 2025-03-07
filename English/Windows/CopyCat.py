import tkinter as tk
from tkinter import scrolledtext
import os
import subprocess
import re

base_dir = os.path.dirname(__file__)
file_path_template = os.path.join(base_dir, './template.rtf')
file_path_records = os.path.join(base_dir, './records') # change records to the name of the folder you want

# def get_folder_path(folder_name):
#     return os.path.join(base_dir, folder_name)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Copycat")
        self.choosing_action = True
        self.user_input = ""
        self.user_input_list = []  # List to track user-typed characters
        self.content_template_before = []
        self.folder_name = "records"  # Default folder name which you can change by editing this variable : NOT IMPLEMENTED YET - CHANGE file_path_records INSTEAD
        self.create_widgets()
        self.display_initial_messages()

    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=30, font=("Times New Roman", 15))
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(bg='#18191A', fg='#E4E6EB', insertbackground='#E4E6EB')
        self.text_area.bind("<KeyPress>", self.on_key_press)
        self.text_area.mark_set("insert", "end")  # Ensure the cursor is always at the end

    def scroll_to_end(self):
        self.text_area.yview(tk.END)
    
    def display_initial_messages(self):
        messages = [
            "\nVERSION 1.1\n\n",
            "Welcome to the dialog box. \n",
            "Here are some rules to avoid running into problems:\n#1: 2 CATEGORIES IN THE TEMPLATE FILE CANNOT HAVE THE SAME NAME, OTHERWISE THAT WILL MESS UP THE VALUES IN THE RECORDS.\n\n",
            "#2: WHEN ADDING A CATEGORY, BE SURE TO ADD A COLON ':' AFTER THE CATEGORY. DO NOT WRITE MULTIPLE COLONS ON THE SAME LINE.\n\n",
            "#3: FOR THE MODIFICATIONS OF THE TEMPLATE TO TAKE EFFECT ON THE RECORDS, SAVE AND CLOSE THE WINDOW OF THE TEXT EDITOR (Pages, Word...) THAT WAS OPENED BY THE PROGRAM. WHILE THAT WINDOW HASN'T BEEN CLOSED, THE DIALOG BOX WILL BE WAITING. ONCE THE TEXT EDITOR WINDOW IS CLOSED, THE RECORDS THAT HAVE SUCCESSFULLY BEEN MODIFIED WILL BE ANNOUNCED IN THE DIALOG BOX.\n\n",
            "#4: IF FUNCTIONALITY 3 DOES NOT WORK, CHECK THAT THERE ARE NO ACCENTS IN THE FILE NAME, AS THAT MIGHT BE THE ISSUE.\n\n",

            "\nHi, what would you like to do? Type the indicated number and press Enter to proceed...\n",
            "1: Modify the template\n",
            "2: Add a record\n",
            "3: Modify a record\n",
            "4: Display the list of existing records\n"
            # "5: Change the storage folder\n"
        ]
        for message in messages:
            self.display_message(message)

        self.choosing_action = True

    def display_action_messages(self):
        messages = [
            "\n\nHi, what would you like to do? Type the indicated number and press Enter to proceed...\n",
            "1: Modify the template\n",
            "2: Add a record\n",
            "3: Modify a record\n",
            "4: Display the list of existing records\n"
            # "5: Change the storage folder\n"
        ]
        for message in messages:
            self.display_message(message)

        self.choosing_action = True

    def display_message(self, message):
        self.text_area.insert(tk.END, message)
        self.user_input = ""
        # Reset the user_input_list after printing the machine message
        self.user_input_list.clear()
        self.scroll_to_end()

    def on_key_press(self, event):
        if event.keysym not in ['BackSpace', 'Return']:
            self.text_area.insert(tk.END, event.char)
            self.user_input_list.append(event.char) # Track user-typed character
            self.scroll_to_end() # Scroll to the end after each character input
        elif event.keysym == 'BackSpace':
            self.handle_backspace()
        elif event.keysym == 'Return':
            self.handle_enter()

        # Move the cursor to the end of the text after every key press
        self.text_area.mark_set("insert", "end")
        return "break"  # Prevent default behavior so user can't move the cursor

    def handle_backspace(self):
        if self.user_input_list:
            current_pos = self.text_area.index("insert")
            if current_pos != "1.0":  # Prevent deleting at the very beginning
                self.text_area.delete('end-2c', 'end-1c')
                self.user_input_list.pop()  # Remove the last tracked character
                self.scroll_to_end() # Scroll to the end after backspace

    def handle_enter(self):
        user_input = self.text_area.get("end-2c linestart", "end-1c").strip()
        self.user_input = user_input

        if self.choosing_action: # the input corresponds to a number : the action to take
            self.process_action(user_input)

    def process_action(self, user_input):
        user_input_number = 0  # default value
        try:
            user_input_number = float(user_input)
        except ValueError:
            self.display_message("\n\Error: please write the number of the action you wish to perform as a WHOLE NUMBER...")
            self.display_action_messages()
            return
        self.display_message("\n")

        with open(file_path_template, 'r', encoding='latin-1') as template:   # ..., int, encoding=utf_8
            self.content_template_before = template.read().splitlines()

        if user_input_number == 1:          # MODIFY TEMPLATE > UPDATE RECORDS
            self.modify_template()
        
        elif user_input_number == 2:        # CREATE A RECORD
            self.choosing_action = False
            self.ask_for_input("\nWrite the new record's name, then press Enter: \n", self.get_file_name_for_creation)
        
        elif user_input_number == 3:        # MODIFY A RECORD
            self.choosing_action = False
            self.ask_for_input("\nWrite the name of the record to modify: \n", self.get_file_name_for_modification)

        # elif user_input_number == 5:        # MODIFY FOLDER NAME
        #     self.choosing_action = False
        #     self.ask_for_input("\nEWrite the new folder name: \n", self.set_folder_name)

        elif user_input_number == 4:        # PRINT THE LIST OF EXISTING RECORDS
            self.display_message("\n") # self.list_files()
            with os.scandir(file_path_records) as directory:
                for record in directory:
                    self.display_message(record.name + "\n")
            self.display_action_messages()

        else:
            self.display_message("Invalid command: the input has to be 1, 2, 3, or 4") # or 5
            self.display_action_messages()

    def modify_template(self):
        #os.system("start "+"template.rtf")
        p = subprocess.Popen(file_path_template, shell=True, encoding='latin-1')
        p.wait()
        #p.wait(timeout= x) timeout for x seconds if program is left running
        with open(file_path_template, 'r', encoding='latin-1') as template: # ..., int, encoding=utf_8
            content_template_after = template.read().splitlines() # list of lines in model file
            
        if self.content_template_before != content_template_after: # if changes have been made . ADD: MAYBE content_template_after IN SELF
            with os.scandir(file_path_records) as directory:
                for record in directory:

                    content_template_after_2 = []
                    for compteur in range(len(content_template_after)):
                        liste_ligne_cle_valeur0 = content_template_after[compteur].rsplit(":", maxsplit=1)[0] # string - Category given before ":"
                        content_template_after_2.append(liste_ligne_cle_valeur0)
                    
                    # print(content_template_after_2) # all categories without ":" in template, WORKS
                    # print('\n')

                    with open(record, 'r', encoding='latin-1') as fiche_record:   # ..., int, encoding=utf_8
                        content_fiche_record = fiche_record.read().splitlines() # list of all the lines

                    content_fiche_record_2 = [] # list of all the lists, representing lines of record file, with 2 values: Category and Value given after ":"

                    for compteur in range(len(content_fiche_record)):
                        liste_ligne_cle_valeur = content_fiche_record[compteur].rsplit(":", maxsplit=1) # list with 2 values: Category and Value given after ":"
                        content_fiche_record_2.append(liste_ligne_cle_valeur)

                    list_record_keys = []
                    list_record_values = []
                    for compteur_2 in range(len(content_fiche_record_2)):
                        list_record_keys.append(content_fiche_record_2[compteur_2][0])

                        if len(content_fiche_record_2[compteur_2]) == 2:    # so no IndexError on empty lines with no ":"
                            list_record_values.append(content_fiche_record_2[compteur_2][1])
                        else:
                            list_record_values.append(content_fiche_record_2[compteur_2][0])
                    
                    # print(list_record_keys, list_record_values) # works
                    # print('\n')

                    final_record_list = [] # list of lines to rewrite in record file, after all mods
                    index_template = 0
                    index_record = 0
                    assert len(content_template_after) == len(content_template_after_2), "HAY UNO PROBLEMO :("
                    while index_template < len(content_template_after):
                        if content_template_after_2[index_template] in list_record_keys: #if not new line
                            local_record_index = list_record_keys.index(content_template_after_2[index_template]) #getting index of key in list of keys, which should be same as index of line in list of lines
                            final_record_list.append(content_fiche_record[local_record_index])
                            index_template+=1
                        else:
                            final_record_list.append(content_template_after[index_template])
                            index_template+=1
                            
                    # print('\n')                            
                    # print(final_record_list) 
                    # print('\n')
                    with open(record, 'w', encoding='latin-1') as fiche_record:   # ..., int, encoding=utf_8
                        for loop_index in range(len(final_record_list)):
                            fiche_record.write(final_record_list[loop_index] + "\n")

                    self.display_message("Modifications saved for: " + record.name + "\n") #  + " (" + list_record_values[1] + list_record_values[0] + "). "

        else: 
            self.display_message("No modifications saved.")
        
        self.display_action_messages()

    def is_string_unsuitable_for_name(self, string):
        # Regular expression that allows letters (including accented), spaces, hyphens, and apostrophes
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ \-_']+$", string):
            return True
        
        # Ensure the string contains at least one alphabetic character (including accented)
        if not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", string):
            return True
        
        return False
        # return (not (string.__contains__('-') or string.isalpha())) or (string.__contains__(' ')) or (string.__contains__('\"'))

    def get_file_name_for_creation(self):
        name = self.user_input
        if self.is_string_unsuitable_for_name(name):
            self.display_message("\nError: the name must only contain letters, hyphens, spaces, apostrophes. ")
            self.display_action_messages()
            return
        self.create_new_file(name)

    def create_new_file(self, name):
        file_path = os.path.join(base_dir, f"records/{name}.rtf")
        with os.scandir(file_path_records) as directory:
            if any(f.name == f"{name}.rtf" for f in directory):  # type: ignore
                self.display_message(f"\WARNING: a record with that name already exists (records/{name}.rtf). The demand to create a new record with this name has been ignored.\n")
                self.display_action_messages()
                return
                # self.display_message("ATTENTION: UNE FICHE RECORD AVEC CE PRENOM ET CE NOM EXISTE DEJA, PROCEDER VOUDRAIT DIRE PERDRE LES INFOS EXISTANTES DANS CETTE FICHE.\n PROCEDER: TAPEZ oui \n RENONCER: TAPEZ AUTRE CHOSE \n")
        
        with open(file_path, 'w', encoding='latin-1') as new_file:
            for index_ligne, ligne_de_content in enumerate(self.content_template_before):
                # if index_ligne > 1:
                    new_file.write(f"{ligne_de_content}\n")

        p = subprocess.Popen(file_path, shell=True) 
        p.wait()

        self.display_action_messages()

    def get_file_name_for_modification(self):
        name = self.user_input
        if self.is_string_unsuitable_for_name(name):
            self.display_message("\nError: the name must only contain letters, hyphens, spaces, apostrophes. ")
            self.display_action_messages()
            return

        file_exists = False
        with os.scandir(file_path_records) as directory:
            for record in directory:
                if f'{name}.rtf' == record.name:
                    p = subprocess.Popen(os.path.join(base_dir, f'records\\{name}.rtf'), shell=True) 
                    p.wait()
                    file_exists = True

        if not file_exists:
            self.display_message("\n\Warning, typing error or record doesn't exist.\n\n To see existing record names, type 4.\n")

        self.display_action_messages()

    def ask_for_input(self, prompt, callback): # maybe del this function
        self.display_message(prompt)
        self.wait_for_user_input(callback)

    def wait_for_user_input(self, callback, *args):
        if self.user_input: # if input has been returned (Enter called after character input)
            callback(*args)
        else:
            self.root.after(100, self.wait_for_user_input, callback, *args)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
