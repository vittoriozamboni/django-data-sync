from distutils.core import setup
from django_data_sync import VERSION

setup(
    name='django_data_sync',
    version=VERSION,
    description="Sync data from a remote API endpoint to local model",
    author='Vittorio Zamboni',
    author_email='vittorio.zamboni@gmail.com',
    license='MIT',
    url='https://github.com/vittoriozamboni/django-data-sync.git',
    packages=[
        'django_data_sync',
    ],
    dependency_links=[
        'https://github.com/yigor/django-jsonfield/archive/master.zip',
        'https://bitbucket.org/zamboni/django-helper-forms/get/tip.zip#egg=django_helper_forms',
        'https://bitbucket.org/zamboni/django-utils/get/tip.zip#egg=django_utils',
    ],
    install_requires=[
        'django>=1.7',
    ],
)
