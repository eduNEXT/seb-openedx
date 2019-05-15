
==============================
Connection with the SEB Server
==============================


Summary
=======

The SEB Server is a web application that is external both to the Safe Exam Browser and the Open edX server.
It's purpose is to make operation of courses restricted by the Safe Exam Browser easier.


API
===

The API for manipulating the Browser Keys (BEK) and Config Keys (CK) is a RESTful API over http.
It uses Json as the payload format.

The API has one resource, namely the Course SEB Configuration. This resource is located at:

``https://courses.yourdomain.com/seb-openedx/api/v1/course/<COURSE_ID>/configuration/``

Methods
-------

The API has the usual available methods to read, update, create and delete SEB Configurations.

GET
---
Issuing a GET request to ``https://courses.yourdomain.com/seb-openedx/api/v1/course/<COURSE_ID>/configuration/`` should return a json representation of the configuration.

For example:

.. code-block:: json

    {
        "BROWSER_KEYS":[
        "cd8827e4555e4eef82........5088a4bd5c9887f32e590"
        ],
        "CONFIG_KEYS":[
        "9887f32e590cd8827e........5088a4bd5c4555e4eef82"
        ],
        "WHITELIST_PATHS": ["wiki", "about"]
    }

If the internal representation of the configuration uses the simple format (list of mixed SEB and CK keys), the API will render the detailed representation.

It the course_id does not have a SEB configuration then a 404 error will be returned.


POST
----
Issuing a POST request to ``https://courses.yourdomain.com/seb-openedx/api/v1/course/<COURSE_ID>/configuration/`` will create a new configuration for the give COURSE_ID. If the resource already exists the API will return a 422 'unable to process request' error.

The payload data must be a json object that contains a valid configuration as detailed on the `usage <usage>`_ section. Otherwise a http 400 error will be returned.

The list of keys for the json object must include either a BEK or CK list, but may also include optionally:

- BROWSER_KEYS: List of valid BEK.
- CONFIG_KEYS: List of valid CK.
- WHITELIST_PATHS: List of whitelisted course paths that do not require SEB for access.
- BLACKLIST_CHAPTERS: List of chapters that do require a valid SEB for access when ``courseware`` was whitelisted.
- SEB_PERMISSION_COMPONENTS: Ordered list of permission components.
- USER_BANNING_ENABLED: Boolean that determines the state of the user banning feature for the course.


PUT
---
Issuing a PUT request is very similar to a POST request, but in this case the object will be updated. If the object does not exist, then an it will be created. Calling put is an idempotent operation.


PATCH
-----
The API allows the use of the PATCH request to issue a partial update. This case is similar to a PUT request, but with all the fields being optional


DELETE
------
Sending a DELETE request to ``https://courses.yourdomain.com/seb-openedx/api/v1/course/<COURSE_ID>/configuration/`` will delete the SEB configuration for the course in question.

.. note::
    The API can alter the information stored at the ``site configuration`` and ``other_course_settings`` in studio. However the information stored in the ``global_settings`` is out of reach for the python process serving the API and therefore not deletable. Editing is valid since the configuration stored in the other sources will override the ``global_settings``.



Authentication
--------------
The API uses the standard mechanisms for authenticating APIs in the Open edX platform. This means that both OAuth2 or Session-based authentication are available.
In any mechanism of authentication, the permissions will be given only for global staff users. This means that the session or the user-account linked to the Oauth2 token must have the is_staff flag set.


Storage internals
-----------------
When available, the API will try to store the configuration in the ``other_course_settings`` field that is available in Studio. When this is not possible, then it will defer to use the ``site_configuration`` object.
