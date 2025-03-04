import tkinter as tk
from tkinter import scrolledtext
import os
import subprocess
import re

base_dir = os.path.dirname(__file__)
file_path_fiche_modele = os.path.join(base_dir, './fiche_modele.rtf')
file_path_exemplaires = os.path.join(base_dir, './exemplaires')

# def get_folder_path(folder_name):
#     return os.path.join(base_dir, folder_name)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Copycat")
        self.choosing_action = True
        self.user_input = ""
        self.user_input_list = []  # List to track user-typed characters
        self.contenu_fiche_modele_avant = []
        self.folder_name = "exemplaires"  # Default folder name which you can change by editing this variable
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
            "Bienvenue dans la boite de dialogue. \n",
            "Voici les règles à suivre pour éviter des problèmes:\n#1: 2 COMPETENCES DE LA FICHE MODELE NE DOIVENT PAS AVOIR LE MEME NOM, SINON CELA CHANGERA LA VALEUR ASSOCIEE DANS LA FICHE EXEMPLAIRE.\n\n",
            "#2: LORS DE L'AJOUT D'UNE COMPETENCE, BIEN METTRE UN DOUBLE-POINT : APRES LA COMPETENCE. NE PAS EN AVOIR PLUSIEURS DANS LA MEME LIGNE.\n\n",
            "#3: POUR QUE LES MODIFICATIONS DE LA FICHE MODELE PRENNENT EFFET SUR LES FICHES EXEMPLAIRE, SAUVEGARDER ET FERMER LA FENETRE DE CELLE-CI DANS L'EDITEUR DE TEXTE (Pages, Word...). TANT QUE L'EDITEUR DE TEXTE N'A PAS ETE FERME, LA BOITE DE DIALOGUE SERA FIGEE. UNE FOIS L'EDITEUR FERME, LES FICHES EXEMPLAIRE MODIFIEES SERONT ANNONCEES DANS LA BOITE DE DIALOGUE.\n\n",
            "#4: SI TU CHANGES LE NOM OU PRENOM D'UN EXEMPLAIRE, BIEN CHANGER AUSSI SON NOM DE FICHIER prenom_nom, POUR POUVOIR UTILISER LA FONCTIONNALITE 3 (Modifier une fiche exemplaire).\n\n",
            "#5: SI LA FONCTIONNALITE 3 NE MARCHE PAS, VERIFIE QU'IL N'Y A PAS D'ACCENTS DANS LE NOM DU FICHIER, CELA POURRAIT PEUT-ETRE ETRE LE PROBLEME.\n\n",

            "\nBonjour, que voulez-vous faire ? Tapez le nombre indiqué puis Entrée pour procéder ...\n",
            "1: Modifier la Fiche Modèle\n",
            "2: Ajouter une fiche exemplaire\n",
            "3: Modifier une fiche exemplaire\n",
            "4: Afficher la liste des fiches exemplaire existantes\n"
            # "5: Changer le dossier de stockage\n"
        ]
        for message in messages:
            self.display_message(message)

        self.choosing_action = True

    def display_action_messages(self):
        messages = [
            "\n\nBonjour, que voulez-vous faire ? Tapez le nombre indiqué puis Entrée pour procéder ...\n",
            "1: Modifier la Fiche Modèle\n",
            "2: Ajouter une fiche exemplaire\n",
            "3: Modifier une fiche exemplaire\n",
            "4: Afficher la liste des fiches exemplaire existantes\n"
            # "5: Changer le dossier de stockage\n"
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
            self.display_message("\n\nErreur: attention, ecris bien le nombre de l'action en CHIFFRE ENTIER...")
            self.display_action_messages()
            return
        self.display_message("\n")

        with open(file_path_fiche_modele, 'r', encoding='latin-1') as fiche_modele:   # ..., int, encoding=utf_8
            self.contenu_fiche_modele_avant = fiche_modele.read().splitlines()

        if user_input_number == 1:          # MODIF FICHE MODELE > UPDATE FICHES EXEMPLAIRES
            self.modify_fiche_modele()
        
        elif user_input_number == 2:        # CREE UNE FICHE EXEMPLAIRE
            self.choosing_action = False
            self.ask_for_input("\nEntrez un nom pour la fiche exemplaire: \n", self.get_file_name_for_creation)
        
        elif user_input_number == 3:        # MODIF UNE FICHE EXEMPLAIRE
            self.choosing_action = False
            self.ask_for_input("\nEntrez le nom de la fiche à modifier: \n", self.get_file_name_for_modification)

        # elif user_input_number == 5:        # MODIF NOM DE DOSSIER
        #     self.choosing_action = False
        #     self.ask_for_input("\nEntrez le nom du nouveau dossier: \n", self.set_folder_name)

        elif user_input_number == 4:        # AFFICHER LA LISTE DES FICHES EXEMPLAIRES
            self.display_message("\n") # self.list_files()
            with os.scandir(file_path_exemplaires) as directory:
                for exemplaire in directory:
                    self.display_message(exemplaire.name + "\n")
            self.display_action_messages()

        else:
            self.display_message("Commande invalide: attention, le nombre de l'action doit etre 1, 2, 3, ou 4") # ou 5
            self.display_action_messages()

    def modify_fiche_modele(self):
        #os.system("start "+"fiche_modele.rtf")
        p = subprocess.Popen(file_path_fiche_modele, shell=True, encoding='latin-1')
        p.wait()
        #p.wait(timeout= x) timeout for x seconds if program is left running
        with open(file_path_fiche_modele, 'r', encoding='latin-1') as fiche_modele: # ..., int, encoding=utf_8
            contenu_fiche_modele_apres = fiche_modele.read().splitlines() # list of lines in model file
            
        if self.contenu_fiche_modele_avant != contenu_fiche_modele_apres: # if changes have been made . ADD: MAYBE contenu_fiche_modele_apres IN SELF
            with os.scandir(file_path_exemplaires) as directory:
                for student in directory:

                    contenu_fiche_modele_apres_2 = []
                    for compteur in range(len(contenu_fiche_modele_apres)):
                        liste_ligne_cle_valeur0 = contenu_fiche_modele_apres[compteur].rsplit(":", maxsplit=1)[0] # string - Category given before ":"
                        contenu_fiche_modele_apres_2.append(liste_ligne_cle_valeur0)
                    
                    # print(contenu_fiche_modele_apres_2) # all categories without ":" in fiche modele, WORKS
                    # print('\n')

                    with open(student, 'r', encoding='latin-1') as fiche_exemplaire:   # ..., int, encoding=utf_8
                        contenu_fiche_exemplaire = fiche_exemplaire.read().splitlines() # list of all the lines

                    contenu_fiche_exemplaire_2 = [] # list of all the lists, representing lines of student file, with 2 values: Category and Value given after ":"

                    for compteur in range(len(contenu_fiche_exemplaire)):
                        liste_ligne_cle_valeur = contenu_fiche_exemplaire[compteur].rsplit(":", maxsplit=1) # list with 2 values: Category and Value given after ":"
                        contenu_fiche_exemplaire_2.append(liste_ligne_cle_valeur)

                    list_student_keys = []
                    list_student_values = []
                    for compteur_2 in range(len(contenu_fiche_exemplaire_2)):
                        list_student_keys.append(contenu_fiche_exemplaire_2[compteur_2][0])

                        if len(contenu_fiche_exemplaire_2[compteur_2]) == 2:    # so no IndexError on empty lines with no ":"
                            list_student_values.append(contenu_fiche_exemplaire_2[compteur_2][1])
                        else:
                            list_student_values.append(contenu_fiche_exemplaire_2[compteur_2][0])
                    
                    # print(list_student_keys, list_student_values) # works
                    # print('\n')

                    final_student_list = [] # list of lines to rewrite in student file, after all mods
                    index_fiche_modele = 0
                    index_student = 0
                    assert len(contenu_fiche_modele_apres) == len(contenu_fiche_modele_apres_2), "HAY UNO PROBLEMO :("
                    while index_fiche_modele < len(contenu_fiche_modele_apres):
                        if contenu_fiche_modele_apres_2[index_fiche_modele] in list_student_keys: #if not new line
                            local_student_index = list_student_keys.index(contenu_fiche_modele_apres_2[index_fiche_modele]) #getting index of key in list of keys, which should be same as index of line in list of lines
                            final_student_list.append(contenu_fiche_exemplaire[local_student_index])
                            index_fiche_modele+=1
                        else:
                            final_student_list.append(contenu_fiche_modele_apres[index_fiche_modele])
                            index_fiche_modele+=1
                            
                    # print('\n')                            
                    # print(final_student_list) 
                    # print('\n')
                    with open(student, 'w', encoding='latin-1') as fiche_exemplaire:   # ..., int, encoding=utf_8
                        for loop_index in range(len(final_student_list)):
                            fiche_exemplaire.write(final_student_list[loop_index] + "\n")

                    self.display_message("Modifications enregistrées pour: " + student.name + "\n") #  + " (" + list_student_values[1] + list_student_values[0] + "). "

        else: 
            self.display_message("Pas de modifications enregistrées.")
        
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
        nom = self.user_input
        if self.is_string_unsuitable_for_name(nom):
            self.display_message("\nErreur: le nom ne doit contenir que des lettres ou des tirets / espaces / apostrophes. ")
            self.display_action_messages()
            return
        self.create_new_file(nom)

    def create_new_file(self, nom):
        file_path = os.path.join(base_dir, f"exemplaires/{nom}.rtf")
        with os.scandir(file_path_exemplaires) as directory:
            if any(f.name == f"{nom}.rtf" for f in directory):  # type: ignore
                self.display_message(f"\nATTENTION: une fiche exemplaire avec ce nom existe déjà (exemplaires/{nom}.rtf). La demande de création de nouvelle fiche à ce nom a été ignorée.\n")
                self.display_action_messages()
                return
                # self.display_message("ATTENTION: UNE FICHE EXEMPLAIRE AVEC CE PRENOM ET CE NOM EXISTE DEJA, PROCEDER VOUDRAIT DIRE PERDRE LES INFOS EXISTANTES DANS CETTE FICHE.\n PROCEDER: TAPEZ oui \n RENONCER: TAPEZ AUTRE CHOSE \n")
        
        with open(file_path, 'w', encoding='latin-1') as new_file:
            for index_ligne, ligne_de_contenu in enumerate(self.contenu_fiche_modele_avant):
                # if index_ligne > 1:
                    new_file.write(f"{ligne_de_contenu}\n")

        p = subprocess.Popen(file_path, shell=True) 
        p.wait()

        self.display_action_messages()

    def get_file_name_for_modification(self):
        nom = self.user_input
        if self.is_string_unsuitable_for_name(nom):
            self.display_message("\nErreur: le nom ne doit contenir que des lettres ou des tirets / espaces / apostrophes. ")
            self.display_action_messages()
            return

        file_exists = False
        with os.scandir(file_path_exemplaires) as directory:
            for exemplaire in directory:
                if f'{nom}.rtf' == exemplaire.name:
                    p = subprocess.Popen(os.path.join(base_dir, f'exemplaires\\{nom}.rtf'), shell=True) 
                    p.wait()
                    file_exists = True

        if not file_exists:
            self.display_message("\n\nAttention, erreur de frappe ou bien la fiche exemplaire n'existe pas.\n\n Pour voir les noms des fiches exemplaire existantes, tapez 4.\n")

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
