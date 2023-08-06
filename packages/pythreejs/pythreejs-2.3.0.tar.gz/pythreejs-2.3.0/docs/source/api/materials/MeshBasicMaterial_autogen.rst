
.. py:currentmodule:: pythreejs

MeshBasicMaterial
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: MeshBasicMaterial()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Material`.

    Three.js docs: https://threejs.org/docs/#api/materials/MeshBasicMaterial


    .. py:attribute:: alphaMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: aoMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: aoMapIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: color


        .. sourcecode:: python

            Color("#ffffff", allow_none=False).tag(sync=True)

    .. py:attribute:: combine


        .. sourcecode:: python

            Enum(Operations, "MultiplyOperation", allow_none=False).tag(sync=True)

    .. py:attribute:: envMap


        .. sourcecode:: python

            Instance(CubeTexture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: lightMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: lightMapIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: lights


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: map


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: morphTargets


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: reflectivity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: refractionRatio


        .. sourcecode:: python

            CFloat(0.98, allow_none=False).tag(sync=True)

    .. py:attribute:: skinning


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: specularMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: wireframe


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinewidth


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinecap


        .. sourcecode:: python

            Unicode("round", allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinejoin


        .. sourcecode:: python

            Unicode("round", allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("MeshBasicMaterial", allow_none=False).tag(sync=True)

