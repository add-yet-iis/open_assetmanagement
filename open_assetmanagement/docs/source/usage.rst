Usage
=====

.. _installation:

Installation
------------

.. _Kali: https://www.kali.org/get-kali/#kali-virtual-machines

The purpose of this tutorial is, to assisst the
installation of the open-assetmanagemt Web-Server

It ist based on the `Kali Virtual Machine  <https://www.kali.org/get-kali/#kali-virtual-machines>`_. in VirtualBox, but should work for VMWare or others as well.

#. Step:
    Download and Extract (7zip) the `Kali Virtual Machine  <https://www.kali.org/get-kali/#kali-virtual-machines>`_.

    If you want to use another Operating System, be aware,
    that you might have to install Python, Pip, NMAP,
    Netdiscover, CrackMapExec or others

    You can also use the `Kali ISO <https://www.kali.org/get-kali/#kali-installer-images>`_.


    Add the Kali VM and start it

    If you want to use the Test Network, you will have to make changes on the network
    adapter settings of the vm
    Add a second adapter and set it to internal network
    Then set the static ip of the kali VM to one in the Range (10.0.0.0/24)
    of the testing network


#. Step:
    Get the latest version of  `open-assetmanagement <https://github.com/lucapoehler/open_assetmanagement>`_ from the git-repository.
    You can use your favorite IDE or just the default Kali Text Editor.
    The folder should look like this:

    .. code-block:: console

        $ tree -L 2
        .
        ├── open_assetmanagement
        │   ├── db.sqlite3
        │   ├── docs
        │   ├── inventory
        │   ├── manage.py
        │   ├── open_assetmanagement
        │   ├── __pycache__
        │   └── templates
        ├── README.rst
        ├── requirements.txt
        ├── testdata
        │   ├── csv_test.CSV
        │   ├── csv_test_no_supplier.CSV
        │   └── xlsx_test.xlsx
        └── Walktrough.txt


#. Step :
    Use the default kali Account. Dont use sudo unless specified

    Create a python virtual environment (optional) and install the requirements

    .. code-block:: console

        $ python -m venv venv


        You may need to install some packages using the command provided
        $ sudo apt install python3.10-venv

    Then activate the virtual environment

    .. code-block:: console

        $ source venv/bin/activate(venv)

    Navigate to the Folder containing the requirements.txt and from within the venv

    .. code-block:: console

        (venv)$  pip install -r requirements.txt

    You can check if the django installation worked:

    .. code-block:: console

        (venv)$ python


    .. code-block::

        Python 3.10.7 (main, Oct  1 2022, 04:31:04) [GCC 12.2.0] on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import django
        >>> django.get_version()
        '4.1.2'

    Now you are ready to start!

    BE CAREFUL THE APP IS UNDER ACTIVE DEVELOPMENT.
    BUGS MAY OCCUR
#. Step:
    Generate a private key and add it to the .env file (see .env)
    
    In Python:
    
    .. code-block::
    
        >>> from django.core.management.utils import get_random_secret_key
        >>> print(get_random_secret_key())
    
#. Step:
    To use the Networkdiscovery Function you need NMAP, Netdiscover and CrackMapExec
    (Preinstalled on Kali)

    Netdiscover and NMAP need Sudo Privileges to run correctly because the have to
    access system ports

    There are several ways to make this possible:

    #. Run the Server as Sudo oder Root (NOT RECOMMENDED! Very Unsafe)

    #. Give python or nmap passwordless sudo access (Also not recommended and very Unsafe, possible PrivEsc)

    #. Give the specific script passwordless sudo access, and make it only writable by the root user, so ther cant be changes (version used)
        Add the following line to the /etc/sudoers File:
        .. code-block::

            ALL  ALL=(ALL) NOPASSWD: <full_path_to_folder>/open_assetmanagement/open_assetmanagement/inventory/network_discovery_module.py

        This lets any user, run the networkdiscovery script as sudo without a password

    #. Install NMAP with capabilities (https://secwiki.org/w/Running_nmap_as_an_unprivileged_user)

    #. Somehow ask for the sudo password in the webinterface and pass it to the backend


.. _developmentserver:

Working with the Development Server
-----------------------------------

Migrate the Database (if there are changes to the models)

.. code-block:: console

    (venv)$ python manage.py makemigrations
    (venv)$ python manage.py migrate

To start the development server

.. code-block:: console

    (venv)$ python manage.py runserver
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    November 02, 2022 - 11:52:28
    Django version 4.1.3, using settings 'open_assetmanagement.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.


Now you should be able to access the Server under the address stated.
To login, create a new user or use the admin account for access to the admin panel

:Username: admin
:PW: Vsc&fbce4WzHQv

