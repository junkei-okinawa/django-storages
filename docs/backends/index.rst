Vercel Storage
==============

This backend implements the Django File Storage API for Vercel's storage solution.

Installation
------------

To use the Vercel storage backend, add the following to your settings.py file::

    DEFAULT_FILE_STORAGE = 'storages.backends.vercel_storage.VercelStorage'

Configuration & Settings
------------------------

The Vercel storage backend requires the following settings:

- `VERCEL_ACCESS_KEY`: Your Vercel access key.
- `VERCEL_SECRET_KEY`: Your Vercel secret key.
- `VERCEL_BUCKET_NAME`: The name of your Vercel storage bucket.

Authentication Settings
~~~~~~~~~~~~~~~~~~~~~~~

The Vercel storage backend uses the access key and secret key for authentication. These keys can be obtained from your Vercel account.

Settings
~~~~~~~~

``VERCEL_ACCESS_KEY`` or ``VERCEL_ACCESS_KEY``

  **Required**

  Your Vercel access key.

``VERCEL_SECRET_KEY`` or ``VERCEL_SECRET_KEY``

  **Required**

  Your Vercel secret key.

``VERCEL_BUCKET_NAME`` or ``VERCEL_BUCKET_NAME``

  **Required**

  The name of your Vercel storage bucket.

