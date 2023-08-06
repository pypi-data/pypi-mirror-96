import multiprocessing
from math import ceil
from sqlalchemy.orm import Query
from tornado.concurrent import Future, chain_future
from concurrent.futures import Executor, ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from typing import Callable, Optional, Any

class MissingFactoryError(Exception):
    pass


class MissingDatabaseSettingError(Exception):
    pass


class _AsyncExecution:
    """Tiny wrapper around ThreadPoolExecutor. This class is not meant to be
    instantiated externally, but internally we just use it as a wrapper around
    ThreadPoolExecutor so we can control the pool size and make the
    `as_future` function public.
    """

    def __init__(self, max_workers: Optional[int] = None):
        self._max_workers = (
            max_workers or multiprocessing.cpu_count()
        )  # type: int
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)  # type: Optional[Executor]

    def set_max_workers(self, count: int):
        if self._pool:
            self._pool.shutdown(wait=True)

        self._max_workers = count
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    @run_on_executor(executor='_pool')
    def as_future(self, query: Callable, *args: Any, **kwargs: Any) -> Future:
        # concurrent.futures.Future is not compatible with the "new style"
        # asyncio Future, and awaiting on such "old-style" futures does not
        # work.
        #
        # tornado includes a `run_in_executor` function to help with this
        # problem, but it's only included in version 5+. Hence, we copy a
        # little bit of code here to handle this incompatibility.

        if not self._pool:
            self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

        # old_future = self._pool.submit(query, *args, **kwargs)
        # new_future = Future()  # type: Future
        
        # IOLoop.current().add_future(
        #     old_future, lambda f: chain_future(f, new_future)
        # )

        return query


_async_exec = _AsyncExecution()

as_future = _async_exec.as_future

max_workers = _async_exec._max_workers

set_max_workers = _async_exec.set_max_workers

class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.per_page)

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        .. sourcecode:: html+jinja
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def paginate(self, page=None, per_page=None, max_per_page=None, count=True):
        """Returns ``per_page`` items from page ``page``.
        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively. If ``count`` is ``False``,
        no query to help determine total page count will be run.
        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:
        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.
        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.
        Returns a :class:`Pagination` object.
        """

        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1: page = 1

        if per_page < 0: per_page = 20

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not count:
            total = None
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


Query.paginate = paginate


__all__ = ('as_future', 'SessionMixin', 'set_max_workers', 'SQLAlchemy', 'RedisMixin', 'Redis')
