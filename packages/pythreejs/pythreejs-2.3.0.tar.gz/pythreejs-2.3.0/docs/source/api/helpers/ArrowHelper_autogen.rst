
.. py:currentmodule:: pythreejs

ArrowHelper
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: ArrowHelper(dir=[0, 0, 1], origin=[0, 0, 0], length=1, color="#ffff00", headLength=None, headWidth=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Blackbox`.

    Three.js docs: https://threejs.org/docs/#api/helpers/ArrowHelper


    .. py:attribute:: dir


        .. sourcecode:: python

            Vector3(default_value=[0, 0, 1]).tag(sync=True)

    .. py:attribute:: origin


        .. sourcecode:: python

            Vector3(default_value=[0, 0, 0]).tag(sync=True)

    .. py:attribute:: length


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: color


        .. sourcecode:: python

            Color("#ffff00", allow_none=False).tag(sync=True)

    .. py:attribute:: headLength


        .. sourcecode:: python

            CFloat(None, allow_none=True).tag(sync=True)

    .. py:attribute:: headWidth


        .. sourcecode:: python

            CFloat(None, allow_none=True).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("ArrowHelper", allow_none=False).tag(sync=True)

