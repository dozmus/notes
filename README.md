notes
========

A minimal note-taking web application using Django 2.0.6 licensed under the MIT License.

# Features
* Write notes using Markdown
* Organise notes using notebooks amd tags
* Share links with custom permissions
* Colour code notebooks
* Search notes and notebooks
* User accounts
* Download notes as text files or PDFs
* Download notebooks
* Mass manage notes in notebooks
* Responsive design

# Usage
## Installation
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

## Run
```
python manage.py runserver 127.0.0.1:8000
```

# Credits
* HTML Styling done using [PureCSS](https://purecss.io/) and [PureCSS Email Layout](https://purecss.io/layouts/email/).
* Syntax highlighting stylesheets from [pygments-css](https://github.com/richleland/pygments-css)
* Tags input field constructed using [tagify](https://github.com/yairEO/tagify)

# Samples
## Light theme
![Light theme](light-theme-sample.png)

## Share links
![Share links](share-links-sample.png)
