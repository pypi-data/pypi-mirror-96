# Ariadne Extended

Ariadne comes with a few contrib modules to support integration with Django. This module acts as an additional Django contrib module to reduce some of the boilerplate when integrating with Django.

It copies and follows some of the conventions defined in Django Rest Framework, effort will be made to provide API compatibility with certain DRF extension modules that are relevant.

The overall goal is to provide often re-used modules and GrpahQL schema, so one doesn't have to re-create them per project.

## Supported DRF modules

* Pagination classes
* Permissions classes
* Serializer classes ( may not removed and made generic )
* Throttling
* django-filters filter backend

## Supported Django versions

**2.2.*, 3.0.\***


### `ariadne_extended.graph_loader`

auto schema, resolver and types loader 

Searches for `types` and `resolvers` modules as well as any `.graphql` files defined within any installed Django application.

Once found they can be used to build the final schema and resolver solution for your ariadne application.

### `ariadne_extended.payload`
Schema, types and resolvers for the graphql `Payload` interface.

Currently the `FieldErrors` are highly coupled to Django rest framework field validation exceptions.

### `ariadne_extended.cursor_pagination`
Rename to relay_pagination maybe?

Contains the `PageInfo` graphql type and `Connection` interface for utilizing cursor based pagination.

TODO: Should we provide a input type for cursor pagination instead of just copying pagination args info paginate-able list fields??

### `ariadne_extended.filters`
Filter backend interface to pass filter arguments to django-filter.

### `ariadne_extended.resolvers`
ABC for Class Based Resolvers and model resolvers that utilize DRF serializers for saving data. This is likely to change in the future.

### `ariadne_extended.uuid`
DRF UUID field scalar for use with models that may use a UUID as their primary key, or other UUID fields.

## Contrib

### `django-waffle` in `ariadne_extended.contrib.waffle_graph`

Adds resolvers, schema and types that can be utilized to query the any waffle flags, samples and switches.


# Checklist
- [ ] Get rid of dependency on DRF?
- [ ] Investigate the need for a serializer ( nested data reliance? )
- [x] Organize code into multiple Django apps to select desired componentry
- [ ] Documentation and examples
- [ ] Better support of lists of enums when used with django-filters ( currently expects comma sep list string, not a list of enums from input field resolver )
- [x] License and make public
- [ ] Deployment automation
- [ ] Mixins are highly coupled to serializers, should they still be?
