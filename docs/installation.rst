
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

    Optionally, if you want to preserve your changes across installations, then you need to commit your docker image.

    .. code-block:: bash

        # TODO: This is not enough to prevent make down from removing the plugin
        docker commit edx.devstack.lms
        docker commit edx.devstack.studio


Native Installation
===================



Other Distributions
===================

