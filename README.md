# SEB Open edX

## Installation
- Clone this repo
- Execute `pip install -e .`
- Add middleware into `/edx-platform/lms/envs/common.py` as in: 
    ```python
    # Use MIDDLEWARE.append instead on Django >= 2.0
    MIDDLEWARE_CLASSES.append('seb_openedx.middleware.SecureExamBrowserMiddleware')
    ```

## Configuration

##### SEB Keys
On studio Settings.FEATURES['ENABLE_OTHER_COURSE_SETTINGS'] must be enabled, then on advanced settings "other_course_settings" must contain a key called seb_keys with all the seb_keys this course allows, as in:
```json
{
    "seb_keys": ["EXAMPLEHASHPROVIDEDBYSEB"]
}
```

##### Whitelisting/Blacklisting
You can specify which tabs/parts of the course are always allowed; and if you need to be more specific you can blacklist specific chapters as well.
Example allowing all tabs but denying access to a specific "chapter":
```python
SEB_KEYS = {
    "course-v1:edX+DemoX+Demo_Course": {
        "BROWSER_KEYS": ["EXAMPLEHASHPROVIDEDBYSEB"],
        "WHITELIST_PATHS": ['wiki', 'course-outline', 'courseware', 'progress', 'discussion'],
        "BLACKLIST_CHAPTERS": ['d8a6192ade314473a78242dfeedfbf5b'],
    },
    "course-v1:edX+E2E-101+course": ["ANOTHEREXAMPLEHASHPROVIDEDBYSEB"]
}
```

## Development

When using edx/devstack clone the repo to the `src` folder then run the following commands from the lms container:
```bash
# set 'ENABLE_OTHER_COURSE_SETTINGS': True
sed -i "s/'ENABLE_OTHER_COURSE_SETTINGS': False,/'ENABLE_OTHER_COURSE_SETTINGS': True,/g" /edx/app/edxapp/edx-platform/cms/envs/common.py
# Adding middleware if not added already
grep -q -F "MIDDLEWARE_CLASSES.append('seb_openedx.middleware.SecureExamBrowserMiddleware')" /edx/app/edxapp/edx-platform/lms/envs/common.py || printf "\nMIDDLEWARE_CLASSES.append('seb_openedx.middleware.SecureExamBrowserMiddleware')" >> /edx/app/edxapp/edx-platform/lms/envs/common.py
sudo su edxapp -s /bin/bash
source ../venvs/edxapp/bin/activate
cd /edx/src/seb-open-edx/
pip install -e .
```