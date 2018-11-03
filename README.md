notes
========

A minimal note-taking web application using Django 2.1.3 licensed under the MIT License.

# Features
* Write notes using Markdown
* Syntax highlighting with 18 themes to choose from
* Organise notes using colour-coded notebooks and tags
* Task lists (check boxes)
* Share links with custom permissions
* Download notes and notebooks as TXT or PDFs
* Search notes and notebooks
* Mass manage notes in notebooks
* User accounts
* Trash bin
* RESTful API
* Responsive design

# Usage
## Installation
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

Windows Users: You will also need
[Microsoft Visual C++ 14.0](https://wiki.python.org/moin/WindowsCompilers#Compilers_Installation_and_configuration)
due to the dependency on reportlab.

## Run
```
python manage.py runserver 127.0.0.1:8000
```

# Samples
## Light theme
![Light theme](samples/light-theme-sample.png)

## Dark theme
![Dark theme](samples/dark-theme-sample.png)

## Task list
![Task list](samples/task-list-sample.png)

## Share links
![Share links](samples/share-links-sample.png)

# Credits
* HTML Styling done using [PureCSS](https://purecss.io/) and [PureCSS Email Layout](https://purecss.io/layouts/email/).
* Syntax highlighting stylesheets from [pygments-css](https://github.com/richleland/pygments-css)
* Tags input field constructed using [django-tagify](https://github.com/PureCS/django-tagify)
