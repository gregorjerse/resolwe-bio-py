.. _`migration_guide_11`:

========================================
Migration guide for porting code to 11.x
========================================

Instructions for migrating ``resdk`` code from ``<11.x`` to ``>=11.x``.

Upgrade resdk
=============

First make sure that you have the latest version od ``resdk``::

    pip install --upgrade resdk

Verify that you have the lastest version::

    pip freeze | grep resdk
    # Should display something with version number greater or
    # equal than 11.0.0. For example:
    # resdk==11.0.0

Changes
=======

Resolwe server now enforces that Data can only be in one single Sample
and one single Collection. Sample can only be in one Collection
as well. This implies the changes described below.

Attributes that describe relations have slightly changed their names::

    # Before:
    my_data.samples
    my_data.collections
    my_sample.collections
    # Now
    my_data.sample
    my_data.collection
    my_sample.collection

Methods for adding/removing objects (``add_data``, ``remove_data``,
``add_samples``, ``remove_samples``) are removed::

    # Before (single data):
    my_sample.add_data(my_data)
    # Now (single data):
    my_data.sample = sample
    my_data.save()

    # Before (multiple data)
    my_sample.add_data(*my_data_list)
    # Now (multiple data)
    for my_data in my_data_list:
        my_data.sample = sample
        my_data.save()

    # Same also for remove_data, add_samples and remove_samples.

When running a process, one could specify list of collections into which
created Data is put. Now, only one Collection can be given. The parameter of
the method has also changed from ``collections`` to ``collection``::

    res = resdkResolwe
    # Before
    res.run(slug='my-process-slug', collections=[my_collection])
    # Now:
    res.run(slug='my-process-slug', collection=my_collection)

When method ``delete()`` is called on Sample or Collection all of it's content
is now deleted automatically. Thus ``delete_content`` parameter is therefore
removed::

    # Before (removing only sample but keeping it's data):
    my_sample.delete(delete_content=False)  # Not possible anymore
    # Before (removing sample and all it's data):
    my_sample.delete(delete_content=True)
    # Now (single data:
    my_sample.delete()
    # Same for Collection.delete()

Data resource now has a ``process`` attribute, which is an instance of
``Process`` resource. Therefore some attributes are removed as they can be
acessed through ``Data.process``::

    # Before
    my_data.process_name
    my_data.process_slug
    my_data.process_type
    my_data.process_input_schema
    my_data.process_output_schema
    # Now
    my_data.process.name
    my_data.process.slug
    my_data.process.type
    my_data.process.input_schema
    my_data.process.output_schema
