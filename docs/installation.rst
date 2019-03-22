
============
Installation
============


To install the SEB Open edX plugin in an Open edX instance you need to complete 3 steps.

* Use pip to install the plugin into the same virtualenv that has all the dependencies for edxapp (edx-platform)
* Include ``seb_openedx.middleware.SecureExamBrowserMiddleware`` into the list of *Middleware Classes* for the django application.
* Run the database migrations needed for the User Banning feature

We will go into detail on how to achieve this for the two more common ways of running Open edX.


Docker Devstack
===============

The `devstack <https://github.com/edx/devstack>`_ install based on docker is a very popular way of launching a development environment of the Open edX services. If you are running this environment then follow this steps.


#. First step is to get the code and install it.

    In the directory where you created your `devstack` you also have now a `src` directory. You can download the code there.

    .. code-block:: bash

        cd src
        sudo mkdir edxapp
        sudo chown $USER edxapp/
        cd edxapp
        git clone https://github.com/eduNEXT/seb-openedx.git

    Now we need to install it in the virtualenv.

    .. code-block:: bash

        cd ../../devstack
        docker-compose exec lms bash -c 'source /edx/app/edxapp/edxapp_env && cd /edx/src/edxapp/seb-openedx && pip install -e .'
        docker-compose exec studio bash -c 'source /edx/app/edxapp/edxapp_env && cd /edx/src/edxapp/seb-openedx && pip install -e .'
        make lms-restart && make studio-restart

    Or more interactively if you prefer

        .. note::
            If you already ran the previous instructions you can skip ahead to the second step.

        .. code-block:: bash

            cd ../../devstack
            make lms-shell
            cd /edx/src/edxapp/seb-openedx/
            pip install -e .
            exit
            make lms-restart

        .. note::
            It is not required for development but we do recommended to install in studio as well.

        .. code-block:: bash

            make studio-shell
            cd /edx/src/edxapp/seb-openedx/
            pip install -e .
            exit
            make studio-restart


#. Add the seb_opened middleware to the lms and studio.

    So far we have installed the plugin. You can already see if the installation was successful by navigating to http://localhost:18000/seb-openedx/seb-info after login as a superuser. You will see the exact version of the plugin you have installed along with the git commit ID

    Now, in order for the plugin to function properly, and be able to control the interactions with the Safe Exam Browser, you need to include the middleware.

    We recommend to do that through the ``EXTRA_MIDDLEWARE_CLASSES`` configuration setting.

        .. code-block:: bash

            docker-compose exec lms bash -c "sed -i -e 's/\"EXTRA_MIDDLEWARE_CLASSES\": \[\]/\"EXTRA_MIDDLEWARE_CLASSES\": \[\"seb_openedx.middleware.SecureExamBrowserMiddleware\"\]/g' /edx/app/edxapp/lms.env.json"
            docker-compose exec studio bash -c "sed -i -e 's/\"EXTRA_MIDDLEWARE_CLASSES\": \[\]/\"EXTRA_MIDDLEWARE_CLASSES\": \[\"seb_openedx.middleware.SecureExamBrowserMiddleware\"\]/g' /edx/app/edxapp/cms.env.json"
            make lms-restart && make studio-restart

    Or as always, you can do it interactively

        For the lms

        .. code-block:: bash

            make lms-shell
            vi ../lms.env.json
            # edit the file by adding "seb_openedx.middleware.SecureExamBrowserMiddleware"
            # into the EXTRA_MIDDLEWARE_CLASSES array.
            exit
            make studio-restart

        For studio

        .. code-block:: bash

            make studio-shell
            vi ../cms.env.json
            # edit the file by adding "seb_openedx.middleware.SecureExamBrowserMiddleware"
            # into the EXTRA_MIDDLEWARE_CLASSES array.
            exit
            make studio-restart


#. Run the database migrations

    To run the database migration in the devstack environment

    .. code-block:: bash

        make lms-update-db

    You should see this on your console.

    .. code-block:: bash

        Running migrations:
          Applying seb_openedx.0001_initial... OK

    .. note::
        The database is shared between lms and studio so you only need to migrate once for both applications.


#. Commit the docker image

    Since this is a docker based environment, once you run ``make down``, all your temporary changes will be gone. This includes the installation we just made.

    If you want to preserve your changes across installations, then you need to commit your docker image.

    #. Make lms image work for studio. We will use a single image to start both the lms and studio containers. This means we need to add the seb_openedx middleware to the ``cms.env.json`` as well.

    .. code-block:: bash

            docker-compose exec lms bash -c "sed -i -e 's/\"EXTRA_MIDDLEWARE_CLASSES\": \[\]/\"EXTRA_MIDDLEWARE_CLASSES\": \[\"seb_openedx.middleware.SecureExamBrowserMiddleware\"\]/g' /edx/app/edxapp/cms.env.json"

    #. Now we want to commit the current container to an docker image.

    .. code-block:: bash

        docker container ls | grep edx.devstack.lms

    The result will be a line describing the current container filtered by the name ``edx.devstack.lms``. Something similar to:

    .. code-block:: bash

        <CONTAINER_ID>   edxops/edxapp:master   "bash -c 'source /ed…"   5 minutes ago   Up 5 minutes       0.0.0.0:18000->18000/tcp, 0.0.0.0:19876->19876/tcp, 18010/tcp   edx.devstack.lms

    Then we use that container ID to commit the container into a named image.

    .. code-block:: bash

        docker commit <CONTAINER_ID> edxops/edxapp_seb

    Finally, we need to edit the ``docker-compose.yml`` file to use the new image. This is out of the container, so use your favorite editor to modify it.

    Where it normally says:

    .. code-block:: yaml

          lms:
            ...
              NO_PYTHON_UNINSTALL: 1
            image: edxops/edxapp:${OPENEDX_RELEASE:-latest}
            ports:
              - "18000:18000"
            ...

          studio:
            ...
              NO_PYTHON_UNINSTALL: 1
            image: edxops/edxapp:${OPENEDX_RELEASE:-latest}
            ports:
              - "18000:18000"
            ...


    Change it to:

    .. code-block:: yaml

          lms:
            ...
              NO_PYTHON_UNINSTALL: 1
            image: edxops/edxapp_seb
            ports:
              - "18000:18000"
            ...

          studio:
            ...
              NO_PYTHON_UNINSTALL: 1
            image: edxops/edxapp_seb
            ports:
              - "18000:18000"
            ...

    .. note::
        If you want to go back to a version of the platform that does not have the openedx_seb plugin installed, you only need to remove the changes to ``docker-compose.yml`` and restart the environment.

        You can also commit the changes into the ``edxops/edxapp:latest`` image. This will however affect all your environments.


Native Installation
===================

The native environment is regarded as a base ubuntu 16.04 server where the ansible playbooks from the `configuration <https://github.com/edx/configuration>`_ repository where run.

Using ansible
-------------

If you use ansible to create or update your instance of the Open edX project, then most likely you have a ``serve-vars.yml`` directory or you have some form of *secure data* repository.

To install the SEB Open edX plugin in there you need to change some ansible variables and re-run your installation playbooks.

.. code-block:: yaml

    EDXAPP_EXTRA_REQUIREMENTS:
          # SEB Plugin
        - name: 'git+https://github.com/edunext/seb-openedx.git@v1.0.0#egg=seb-openedx==1.0.0'

    EDXAPP_EXTRA_MIDDLEWARE_CLASSES:
        - 'seb_openedx.middleware.SecureExamBrowserMiddleware

If you want to check that your installation was successful you need to verify:

- The ``/edx/app/edxapp/lms.env.json`` file must include the seb_openedx middleware in ``EXTRA_MIDDLEWARE_CLASSES``.
- The ``/edx/app/edxapp/cms.env.json`` file must include the seb_openedx middleware in ``EXTRA_MIDDLEWARE_CLASSES``.
- ``/edx/bin/pip.edxapp list| grep seb`` must return the correct version of seb.

Or you can:

Navigate to https://<yourdomain>/seb-openedx/seb-info as a superuser and you will see the info on your browser.


.. note::

    Some site operators prefer not to run database migration during the playbook runs. If this is you, then please run the migrations manually.

    .. code-block:: shell

        /edx/bin/edxapp-migrate-lms


Installing manually
-------------------

To run the installation without the help of any script you still need to run the same basic steps.

#. Install the code

    .. code-block:: shell

        sudo su edxapp -s /bin/bash
        /edx/bin/pip.edxapp install git+https://github.com/edunext/seb-openedx.git@v1.0.0#egg=seb-openedx==1.0.0

#. Activate the middleware

    .. code-block:: shell

        sudo su edxapp -s /bin/bash
        nano /edx/app/edxapp/lms.env.json
        # edit the file by adding "seb_openedx.middleware.SecureExamBrowserMiddleware"
        # into the EXTRA_MIDDLEWARE_CLASSES array.

    .. code-block:: shell

        sudo su edxapp -s /bin/bash
        nano /edx/app/edxapp/cms.env.json
        # edit the file by adding "seb_openedx.middleware.SecureExamBrowserMiddleware"
        # into the EXTRA_MIDDLEWARE_CLASSES array.

# Restart the services


    .. code-block:: shell

        /edx/bin/supervisorctl restart all

#. Run the database migrations

    .. code-block:: shell

        /edx/bin/edxapp-migrate-lms



Other Distributions
===================

Being open source, there are a lot of ways of installing the Open edX platform. This document will not pretend to list them all.
We do want to give you the information you need to install this plugin in your environment.


#. Install the code

    Run ``pip install git+https://github.com/edunext/seb-openedx.git@v1.0.0#egg=seb-openedx==1.0.0`` in the same virtualenv, or with the same user and permissions you used when installing all the dependencies of the edx-platform repository.

#. Activate the middleware

    You need to make sure that ``seb_openedx.middleware.SecureExamBrowserMiddleware`` is listed into the Django middleware classes.

    You can do so by altering the ``EXTRA_MIDDLEWARE_CLASSES`` setting.

    You can also add it directly into the ``MIDDLEWARE_CLASSES`` key in the ``lms.envs.common.py`` & ``cms.envs.common.py`` module. Whichever method works best for your use case.

#. Restart the services

    After installing the SEB Open edX plugin and adding the middleware you always need to restart your processes.

#. Run the database migrations

    This is necessary to create the tables that store the user banning. Running the migrations obligatory. Do so with any available methods from your distribution of Open edX.
