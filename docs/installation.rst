
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

        .. note::
            We are running the installation in editable mode (-e). When developing or testing, if you make any changes to the code, the server should restart automatically. This will happen if you checkout different tags or branches of the code as well. To see the server restart in action you can see the logs using

            .. code-block:: bash

                docker logs edx.devstack.lms -f

            You can also restart the server manually with

            .. code-block:: bash

                make lms-restart


#. Add the seb_opened middleware to the lms and studio.

    So far we have installed the plugin. You can already see if the installation was successful by navigating to http://localhost:18000/seb-openedx/seb-info after login as a superuser. You will see the exact version of the plugin you have installed along with the git commit ID

    Now, in order for the plugin to function properly, and be able to control the interactions with the Safe Exam Browser, you need to include the middleware.

    We recommend to do that through the ``EXTRA_MIDDLEWARE_CLASSES`` configuration setting.

    In versions up to the open-release/ironwood of the codebase:

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
            make lms-restart

        For studio

        .. code-block:: bash

            make studio-shell
            vi ../cms.env.json
            # edit the file by adding "seb_openedx.middleware.SecureExamBrowserMiddleware"
            # into the EXTRA_MIDDLEWARE_CLASSES array.
            exit
            make studio-restart

    .. note::
        In versions starting from to the open-release/juniper of the codebase the ``lms.env.json`` or ``cms.env.json`` file have been moved to ``/edx/etc/lms.yml`` and ``/edx/etc/studio.yml``

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


Upgrading existing code
-----------------------

To upgrade the current running version of the plugin, you need to obtain the correct version of the source code and then restart the lms. This example is done from the outside of the container but you can work from the container shell as well.


#. Use git to pull the version that you want

    .. code-block:: bash

        cd src/edxapp/seb-openedx
        git fetch origin

        # Checkout tag 1.1.0 on branch 'branch_v1_1_0'
        git checkout -b branch_v1_1_0 tags/v1.1.0

#. Restart the lms

    Since we installed it in the editable mode with the ``-e`` flag, there is no need to re-install. A simple restart will do.

    .. code-block:: bash

        cd ../../devstack

        make lms-restart

As before, you can navigate to http://localhost:18000/seb-openedx/seb-info as a superuser to find the exact version that is running on the platform.


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

#. Restart the services

    .. code-block:: shell

        /edx/bin/supervisorctl restart all

#. Run the database migrations

    .. code-block:: shell

        /edx/bin/edxapp-migrate-lms


Upgrading existing code
-----------------------

Upgrading the existing code on an already running installation is exactly the same as installing from scratch.


For ansible managed installations this means running the installation scripts again, but make sure you have upgraded the version on the ``EDXAPP_EXTRA_REQUIREMENTS`` variable.

.. code-block:: yaml

    EDXAPP_EXTRA_REQUIREMENTS:
          # SEB Plugin
        - name: 'git+https://github.com/edunext/seb-openedx.git@<NEW_VERSION_TAG>#egg=seb-openedx==<NEW_VERSION>'

For manually managed installations install again with the same steps as before and restart the processes.

#. Install the new code

    .. code-block:: shell

        sudo su edxapp -s /bin/bash
        /edx/bin/pip.edxapp install git+https://github.com/edunext/seb-openedx.git@<NEW_VERSION_TAG>#egg=seb-openedx==<NEW_VERSION>

#. Restart the services

    .. code-block:: shell

        /edx/bin/supervisorctl restart all


As before, you can navigate to https://<yourdomain>/seb-openedx/seb-info as a superuser to find the exact version that is running on the platform.

Tutor
=====

`Tutor <https://docs.tutor.overhang.io>`_ is a free, open source, docker-based Open edX distribution, both for production and local development. Tutor makes it easy to deploy, customize, upgrade and scale Open edX platform. It is reliable, fast, extensible, and it is already used by hundreds of Open edX platforms around the world.

#. Configure the tutor environment, if you want to know more about how to run tutor in a productive environment you can review the following article `Local deployment <https://docs.tutor.overhang.io/local.html>`_

#. After creating the configuration file *config.yml* you must add an ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` to install the *seb-openedx* plugin by adding the following code snippet at the end of that file.

    .. code-block:: yaml

        OPENEDX_EXTRA_PIP_REQUIREMENTS:
        - "git+https://github.com/eduNEXT/seb-openedx.git"

#. Once you have added the above configuration you should proceed to build the openedx image again.

    .. code-block:: shell

        tutor images build openedx

#. When the image has finished its construction we can proceed to run the respective migrations.

    .. code-block:: shell

        tutor local init

#. With the migrations done we must proceed to create a tutor yaml plugin, which will be responsible for configuring the ``seb_openedx.middleware.SecureExamBrowserMiddleware`` middleware, for this we can follow the following article `YAML file <https://docs.tutor.overhang.io/plugins/v0/gettingstarted. html#getting-started-with-plugin-development>`_, the plugin structure should go as follows and must be saved in the plugins folder of our installation, to know which is the path to the root folder of our plugins we must type the following command ``$(tutor plugins printroot)``.

    .. code-block:: yaml

        name: seb-backend-plugin
        version: 0.1.0
        patches:
            openedx-common-settings: |
                MIDDLEWARE.append("seb_openedx.middleware.SecureExamBrowserMiddleware")

            common-env-features: |
                ENABLE_OTHER_COURSE_SETTINGS: true

#. To check if the plugin is correctly saved, you can view the list of plugins that have been created.

    .. code-block:: shell

        tutor plugins list

#. Do not forget to run the following commands after saving the plugin in the plugins folder to activate the plguin.

    .. code-block:: shell

        tutor plugins enable seb-backend-plugin
        tutor config save

#. Finally we can proceed to update our services with all the changes we made.

    .. code-block:: shell
    
        tutor local dc down
        tutor local start -d

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

    This is necessary to create the tables that store the user banning. Running the migrations is obligatory. Do so with any available methods from your distribution of Open edX.
