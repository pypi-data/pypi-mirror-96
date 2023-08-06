from typing import Sequence, List
from psycopg2.sql import SQL

from estnltk import logger, Progressbar
from estnltk import Text
from estnltk.converters import serialisation_modules
from estnltk.storage import postgres as pg
from estnltk.converters.layer_dict_converter import layer_converter_collection


class PgSubCollection:
    """
    Wrapper class that provides read-only access to a subset of a collection.

    The subset is specified by a SQL select statement that is determined by
    - the selection criterion
    - the set of selected layers
    - the set of meta attributes

    The main usecase for the class is iteration over its elements. 
    It is possible to iterate several times over the subcollection.

    Depending on the configuration attributes, the iterator returns:
    - text objects with selected layers
    - text objects together with their index
    - text objects together with their index and meta fields


    TODO: Complete the description

    ISSUES: How one specifies layer meta attributes? Do they come automatically
    retrieving layer meta attributes is not implemented
    """

    def __init__(self, collection: pg.PgCollection, selection_criterion: pg.WhereClause = None,
                 selected_layers: Sequence[str] = None, meta_attributes: Sequence[str] = None,
                 progressbar: str = None, return_index: bool = True):
        """
        :param collection: PgCollection
        :param selection_criterion: WhereClause
        :param selected_layers: Sequence[str]
            names of layers attached to the Text object, dependencies are included automatically
        :param meta_attributes: Sequence[str]
            names of collection meta attributes that yield in dict with text object
        :param progressbar: str, default None
            no progressbar by default
            'ascii', 'unicode' or 'notebook'
        :param return_index: bool
            yield collection id with text objects
        """

        #TODO: Make sure that all objects used by the class are independent copies and cannot be 
        #changed form the outside. This might invalidate invariants 


        if not collection.exists():
            raise pg.PgCollectionException('collection {!r} does not exist'.format(collection.name))

        self.collection = collection

        if selection_criterion is None:
            self._selection_criterion = pg.WhereClause(collection=self.collection)
        elif isinstance(selection_criterion, pg.WhereClause):
            self._selection_criterion = selection_criterion
        else:
            raise TypeError('unexpected type of selection_criterion: {!r}'.format(type(selection_criterion)))

        #TODO: Why different default values? Unify
        self.selected_layers = selected_layers or []
        self.meta_attributes = meta_attributes or ()
        self.progressbar = progressbar
        self.return_index = return_index

    @property
    def selected_layers(self):
        return self._selected_layers

    @selected_layers.setter
    def selected_layers(self, layers: list):
        """
        Selects layers together with all layers needed to define them.
        """

        self._selected_layers = self.collection.dependent_layers(layers)
        self._attached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['layer_type'] == 'attached']
        self._detached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['layer_type'] == 'detached']

    @property
    def layers(self):
        return self.collection.get_layer_names()

    @property
    def detached_layers(self):
        return self._detached_layers

    @property
    def fragmented_layers(self):
        # TODO: Complete this
        raise NotImplementedError()

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the subcollection.
        
        BUGS: This function does not handle fragmented layers correctly.
        We need nested sql queries to combine fragments into single object per text_id
        This must be solved by defining a view during creation of fragmented layers
        or some dark magic query composition.

        """
        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layers=self._detached_layers,
                                              collection_meta=self.meta_attributes,
                                              include_layer_ids=False)

        required_layers = sorted(set(self._detached_layers + self._selection_criterion.required_layers))
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)

        # Required layers are part of the main collection
        if required_layers:
            # Build a join clauses to merge required detached layers by text_id
            required_layer_tables = [pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
                                     for layer in required_layers]
            join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(collection_identifier,
                                                                                    layer_table_identifier)
                                               for layer_table_identifier in required_layer_tables)

            required_tables = SQL(', ').join((collection_identifier, *required_layer_tables))
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {} AND {}").format(SQL(', ').join(selected_columns),
                                                                        required_tables,
                                                                        join_condition,
                                                                        self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                 required_tables,
                                                                 join_condition)
        else:
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                 collection_identifier,
                                                                 self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)

        return SQL('{} ORDER BY {}."id"').format(query, collection_identifier)

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    @property
    def sql_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_query)

    @property
    def sql_count_query_text(self):
        return self.sql_count_query.as_string(self.collection.storage.conn)

    def select(self, additional_constraint: pg.WhereClause = None, selected_layers: Sequence[str] = None):
        """
        Returns a new subcollection that satisfies additional constraints.

        TODO: Document its usages
        """

        if selected_layers is None:
            selected_layers = self.selected_layers

        if additional_constraint is None:
            self.selected_layers = selected_layers
            return self

        return PgSubCollection(collection=self.collection,
                               selection_criterion=self._selection_criterion & additional_constraint,
                               selected_layers=selected_layers.copy(),
                               meta_attributes=self.meta_attributes,
                               progressbar=self.progressbar,
                               return_index=self.return_index
                               )

    __read_cursor_counter = 0

    def _dict_to_layer(self, layer_dict: dict, text_object=None):
        # collections with structure versions <2.0 are used same old serialisation module for all layers
        if self.collection.structure.version in {'0.0', '1.0'}:
            return serialisation_modules.legacy_v0.dict_to_layer(layer_dict, text_object)

        serialisation_module = self.collection.structure[layer_dict['name']]['serialisation_module']
        # use default serialisation if specification is missing
        if serialisation_module is None:
            return serialisation_modules.default.dict_to_layer(layer_dict, text_object)

        if serialisation_module in layer_converter_collection:
            return layer_converter_collection[serialisation_module].dict_to_layer(layer_dict, text_object)

        raise ValueError('serialisation module not registered in serialisation map: ' + layer_converter_collection)

    def _dict_to_text(self, text_dict: dict, attached_layers) -> Text:
        text = Text(text_dict['text'])
        text.meta = text_dict['meta']
        for layer_dict in text_dict['layers']:
            if layer_dict['name'] in attached_layers:
                layer = self._dict_to_layer(layer_dict, text)
                text.add_layer(layer)
        return text

    def __iter__(self):
        """
        Yields all subcollection elements ordered by the text_id 

        Depending on self.return_index and self.meta_attributes yields either
        - text
        - text_id, text
        - text, meta
        - text_id, text, meta

        The value of these configuration attributes is fixed before starting the iteration.
        """

        # Check that somebody else has not deleted the collection
        if not self.collection.exists():
            raise pg.PgCollectionException('collection {!r} has been unexpectedly deleted'.format(self.collection.name))

        with self.collection.storage.conn.cursor() as c:
            c.execute(self.sql_count_query)
            logger.debug(c.query.decode())
            total = next(c)[0]

        self.__class__.__read_cursor_counter += 1

        with self.collection.storage.conn.cursor('read_'+str(self.__class__.__read_cursor_counter),
                                                 withhold=True) as c:
            c.execute(self.sql_query)
            logger.debug(c.query.decode())
            data_iterator = Progressbar(iterable=c, total=total, initial=0, progressbar_type=self.progressbar)

            # Cash configuration attributes to protect against unexpected changes during iteration
            return_index = self.return_index
            if self.meta_attributes:
                for row in data_iterator:
                    text_id = row[0]
                    data_iterator.set_description('collection_id: {}'.format(text_id), refresh=False)

                    text_dict = row[1]
                    text = self._dict_to_text(text_dict, self._attached_layers)

                    for layer_dict in row[2 + len(self.meta_attributes):]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    meta_values = row[2:2 + len(self.meta_attributes)]
                    meta = {attr: value for attr, value in zip(self.meta_attributes, meta_values)}
                    if return_index:
                        yield text_id, text, meta
                    else:
                        yield text, meta
            else:
                for row in data_iterator:
                    text_id = row[0]
                    data_iterator.set_description('collection_id: {}'.format(text_id), refresh=False)

                    text_dict = row[1]
                    text = self._dict_to_text(text_dict, self._attached_layers)

                    for layer_dict in row[2:]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    if return_index:
                        yield text_id, text
                    else:
                        yield text

    def head(self, n: int = 5) -> List[Text]:
        return [t for _, t in zip(range(n), self)]

    def tail(self, n: int = 5) -> List[Text]:
        # ineffective implementation:
        # return list(collections.deque(self, n))
        raise NotImplementedError()

    def select_all(self):
        self.selected_layers = self.layers
        return self

    def detached_layer(self, name):
        return pg.PgSubCollectionLayer(self.collection,
                                       detached_layer=name,
                                       selection_criterion=self._selection_criterion,
                                       progressbar=self.progressbar,
                                       return_index=self.return_index)

    def fragmented_layer(self, name):
        return pg.PgSubCollectionFragments(self.collection,
                                           fragmented_layer=name,
                                           selection_criterion=self._selection_criterion,
                                           progressbar=self.progressbar,
                                           return_index=self.return_index)

    def __repr__(self):
        return ('{self.__class__.__name__}('
                'collection: {self.collection.name!r}, '
                'selected_layers={self.selected_layers}, '
                'meta_attributes={self.meta_attributes}, '
                'progressbar={self.progressbar!r}, '
                'return_index={self.return_index})').format(self=self)
