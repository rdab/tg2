
class RendererFactory(object):
    # Here specify the list of engine names for which this factory
    # will create a rendering engine.
    engines = []

    # Here specify if turbogears variables have to be injected
    # in the template context before using any of the declared engines.
    # Usually True unless engines are protocols (ie JSON).
    with_tg_vars = True

    @classmethod
    def create(cls, config, app_globals):  # pragma: no cover
        """
        Given the TurboGears configuration and application globals
        it must create a rendering engine for each one specified
        into the ``engines`` list.

        It must return a dictionary in the form::

            {'engine_name': rendering_engine_callable,
             'other_engine': other_rendering_callable}

        Rendering engine callables are callables in the form:

            func(template_name, template_vars, cache_key=None,
                 cache_type=None, cache_expire=None, **kwargs)

        """
        raise NotImplementedError()