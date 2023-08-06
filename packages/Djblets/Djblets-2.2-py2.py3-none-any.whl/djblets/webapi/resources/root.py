"""A flexible resource for the root of your API resource tree."""

from __future__ import unicode_literals

from collections import namedtuple

from django.conf.urls import url
from django.http import HttpResponseNotModified
from django.utils import six

from djblets.urls.patterns import never_cache_patterns
from djblets.webapi.errors import DOES_NOT_EXIST
from djblets.webapi.resources.base import WebAPIResource
from djblets.webapi.responses import WebAPIResponseError


class RootResource(WebAPIResource):
    """The root of a resource tree.

    This is meant to be instantiated with a list of immediate child
    resources. The result of :py:meth:`get_url_patterns` should be included in
    a project's :file:`urls.py`.
    """

    name = 'root'
    singleton = True

    #: A resource entry returned from :py:meth:`RootResource.walk_resources`.
    #:
    #: Attributes:
    #:      name (unicode):
    #:          The name of current resource being explored.
    #:
    #       list_href (unicode):
    #:          The list_href associated with this resource.
    #:
    #       resource (djblets.webapi.resources.base.WebAPIResource):
    #:          The resource object being explored.
    #:
    #       is_list (bool):
    #:          Whether or not the resource is a list resource.
    ResourceEntry = namedtuple('ResourceEntry',
                               ('name', 'list_href', 'resource', 'is_list'))

    def __init__(self, child_resources=[], include_uri_templates=True):
        super(RootResource, self).__init__()
        self.list_child_resources = child_resources
        self._uri_templates = {}
        self._registered_uri_templates = {}
        self._include_uri_templates = include_uri_templates

    def get_etag(self, request, obj, *args, **kwargs):
        return self.encode_etag(request, repr(obj))

    def get(self, request, *args, **kwargs):
        """Retrieve the list of top-level resources and URL templates."""
        data = self.serialize_root(request, *args, **kwargs)
        etag = self.get_etag(request, data)

        if self.are_cache_headers_current(request, etag=etag):
            return HttpResponseNotModified()

        return 200, data, {
            'ETag': etag,
        }

    def serialize_root(self, request, *args, **kwargs):
        """Serialize the contents of the root resource.

        By default, this just provides links and URI templates. Subclasses
        can override this to provide additional data, or to otherwise
        change the structure of the root resource.
        """
        data = {
            'links': self.get_links(self.list_child_resources,
                                    request=request, *args, **kwargs),
        }

        if self._include_uri_templates:
            data['uri_templates'] = self.get_uri_templates(request, *args,
                                                           **kwargs)

        return data

    def get_uri_templates(self, request, *args, **kwargs):
        """Return all URI templates in the resource tree.

        REST APIs can be very chatty if a client wants to be well-behaved
        and crawl the resource tree asking for the links, instead of
        hard-coding the paths. The benefit is that they can keep from
        breaking when paths change. The downside is that it can take many
        HTTP requests to get the right resource.

        This list of all URI templates allows clients who know the resource
        name and the data they care about to simply plug them into the
        URI template instead of trying to crawl over the whole tree. This
        can make things far more efficient.
        """
        if not self._uri_templates:
            self._uri_templates = {}

        base_href = request.build_absolute_uri()

        if base_href not in self._uri_templates:
            templates = {}
            unassigned_templates = self._registered_uri_templates.get(
                None, {})

            for name, href in six.iteritems(unassigned_templates):
                templates[name] = href

            for entry in self.walk_resources(self, base_href):
                templates[entry.name] = entry.list_href

                if entry.is_list:
                    list_templates = self._registered_uri_templates.get(
                        entry.resource, {})

                    for name, href in six.iteritems(list_templates):
                        templates[name] = '%s%s' % (entry.list_href, href)

            self._uri_templates[base_href] = templates

        return self._uri_templates[base_href]

    @classmethod
    def walk_resources(cls, resource, list_href):
        """Yield all URI endpoints associated with a specified resource.

        Args:
            resource djblets.webapi.resources.WebAPIResource:
                The starting point for searching the resource tree.

            list_href (unicode):
                The path to the list resource, relative to the WebAPIResource
                provided. Used as a component of the URL in the API.

        Yields:
            RootResource.ResourceEntry:
            Resource entries for all sub-resources.
        """
        yield cls.ResourceEntry(name=resource.name_plural,
                                list_href=list_href,
                                resource=resource,
                                is_list=True)

        for child in resource.list_child_resources:
            child_href = '%s%s/' % (list_href, child.uri_name)

            for entry in cls.walk_resources(child, child_href):
                yield entry

        if resource.uri_object_key:
            object_href = '%s{%s}/' % (list_href, resource.uri_object_key)

            yield cls.ResourceEntry(name=resource.name,
                                    list_href=object_href,
                                    resource=resource,
                                    is_list=False)

            for child in resource.item_child_resources:
                child_href = '%s%s/' % (object_href, child.uri_name)

                for entry in cls.walk_resources(child, child_href):
                    yield entry

    def api_404_handler(self, request, api_format=None, *args, **kwargs):
        """Default handler at the end of the URL patterns.

        This returns an API 404, instead of a normal django 404.
        """
        return WebAPIResponseError(request,
                                   err=DOES_NOT_EXIST,
                                   api_format=api_format)

    def get_url_patterns(self):
        """Return the Django URL patterns for this object and its children.

        This returns the same list as
        :py:meth:`WebAPIResource.get_url_patterns`, but also introduces a
        generic catch-all 404 handler which returns API errors instead of HTML.
        """
        urlpatterns = super(RootResource, self).get_url_patterns()
        urlpatterns += never_cache_patterns(url(r'.*', self.api_404_handler))

        return urlpatterns

    def register_uri_template(self, name, relative_path,
                              relative_resource=None):
        """Register the specified resource for URI template serialization.

        This adds the specified name and relative resource to the Root
        Resource's URI templates.

        Args:
            name (unicode):
                The name of the associated resource being added to templates.

            relative_path (unicode):
                The path of the API resource relative to its parent resources.

            relative_resource (djblets.extensions.resources.ExtensionResource,
                               optional):
                The resource instance associated with this URI template.
        """
        # Clear the cache so that new lookups can detect newly added templates.
        self._uri_templates = {}

        templates = self._registered_uri_templates.setdefault(
            relative_resource, {})
        templates[name] = relative_path

    def unregister_uri_template(self, name, relative_resource=None):
        """Unregister the specified resource for URI template serialization.

        This removes the specified name and relative resource to the Root
        Resource's URI templates.

        Args:
            name (unicode):
                The name of the resource being removed from templates.

            relative_resource (djblets.extensions.resources.ExtensionResource,
                               optional):
                The resource instance associated with this URI template.
        """
        # Clear the cache so that new lookups can detect newly added templates.
        self._uri_templates = {}

        try:
            del self._registered_uri_templates[relative_resource][name]
        except KeyError:
            pass
