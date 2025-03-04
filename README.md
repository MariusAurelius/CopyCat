# CopyCat - Dynamic RTF File Manager

A python-based Tkinter application for managing RTF files via modifying a template RTF file.

It allows users to:

- Create and edit files based on a template.
- Store records (RTF files based on the template) in a folder.
- View and modify existing files easily.
- Automatically update all records after modifying the template file.

Perfect for automatically updating files based on the same template!

## Details

The template file is an RTF file in which each line is a 'category' followed by a colon (:). 

When categories are added, deleted, or modified in the template, all records in the 'Records' folder are updated to reflect these changes, ensuring that each record retains its values for pre-existing categories while incorporating the updates.

Each time the program is launched, a message detailing how to use the program is shown.
