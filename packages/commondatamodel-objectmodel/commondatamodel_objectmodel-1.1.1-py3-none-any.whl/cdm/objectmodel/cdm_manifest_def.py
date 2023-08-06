﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from datetime import datetime, timezone
from typing import cast, Dict, Iterable, Optional, Union, TYPE_CHECKING

from cdm.enums import CdmObjectType, CdmRelationshipDiscoveryStyle
from cdm.utilities import AttributeResolutionDirectiveSet, logger, ResolveOptions, time_utils

from .cdm_collection import CdmCollection
from .cdm_entity_collection import CdmEntityCollection
from .cdm_document_def import CdmDocumentDefinition
from .cdm_file_status import CdmFileStatus
from .cdm_object_def import CdmObjectDefinition
from .cdm_referenced_entity_declaration_def import CdmReferencedEntityDeclarationDefinition
from .cdm_trait_collection import CdmTraitCollection

if TYPE_CHECKING:
    from cdm.objectmodel import CdmCorpusContext, CdmCorpusDefinition, CdmE2ERelationship, CdmEntityDefinition, CdmEntityDeclarationDefinition, \
        CdmFolderDefinition, CdmLocalEntityDeclarationDefinition, CdmManifestDeclarationDefinition, CdmObject, CdmTraitDefinition, CdmTraitReference
    from cdm.utilities import CopyOptions, VisitCallback


def rel2_cache_key(rel: 'CdmE2ERelationship') -> str:
    """"standardized way of turning a relationship object into a key for caching
    without using the object itself as a key (could be duplicate relationship objects)"""
    name_and_pipe = ''
    if rel.relationship_name:
        name_and_pipe = '{}|'.format(rel.relationship_name)
    return '{}{}|{}|{}|{}'.format(name_and_pipe, rel.to_entity, rel.to_entity_attribute, rel.from_entity, rel.from_entity_attribute)


class CdmManifestDefinition(CdmDocumentDefinition, CdmObjectDefinition, CdmFileStatus):
    def __init__(self, ctx: 'CdmCorpusContext', name: str) -> None:
        super().__init__(ctx, '{}.manifest.cdm.json'.format(name))
        # The name of the manifest
        self.manifest_name = name

        self.explanation = None  # type: Optional[str]

        self.last_child_file_modified_time = None  # type: Optional[datetime]

        self.last_file_modified_time = None  # type: Optional[datetime]

        self.last_file_status_check_time = None  # type: Optional[datetime]

        # --- internal ---
        self._file_system_modified_time = None  # type: Optional[datetime]
        self._TAG = CdmManifestDefinition.__name__

    @property
    def object_type(self) -> CdmObjectType:
        return CdmObjectType.MANIFEST_DEF

    @property
    def entities(self) -> 'CdmCollection[CdmEntityDeclarationDefinition]':
        if not hasattr(self, '_entities'):
            self._entities = CdmEntityCollection(self.ctx, self)  # type: CdmCollection[CdmEntityDeclarationDefinition]
        return self._entities

    @property
    def exhibits_traits(self) -> 'CdmTraitCollection':
        if not hasattr(self, '_exhibits_traits'):
            self._exhibits_traits = CdmTraitCollection(self.ctx, self)  # type: CdmTraitCollection
        return self._exhibits_traits

    @property
    def relationships(self) -> 'CdmCollection[CdmE2ERelationship]':
        if not hasattr(self, '_relationships'):
            self._relationships = CdmCollection(self.ctx, self, CdmObjectType.E2E_RELATIONSHIP_DEF)  # type: CdmCollection[CdmE2ERelationship]
        return self._relationships

    @property
    def sub_manifests(self) -> 'CdmCollection[CdmManifestDeclarationDefinition]':
        if not hasattr(self, '_sub_manifests'):
            self._sub_manifests = CdmCollection(self.ctx, self, CdmObjectType.MANIFEST_DECLARATION_DEF)  # type: CdmCollection[CdmManifestDeclarationDefinition]
        return self._sub_manifests

    def copy(self, res_opt: Optional['ResolveOptions'] = None, host: Optional['CdmManifestDefinition'] = None) -> 'CdmManifestDefinition':
        # since we need to call the base copy which will only return a document when there is no host, make a fake host here
        if not host:
            host = CdmManifestDefinition(self.ctx, self.manifest_name)

        copy = super().copy(res_opt, host)  # type: CdmManifestDefinition
        copy.manifest_name = self.manifest_name
        copy.explanation = self.explanation
        copy.last_file_status_check_time = self.last_file_status_check_time
        copy.last_file_modified_time = self.last_file_modified_time
        copy.last_child_file_modified_time = self.last_child_file_modified_time

        copy.entities.clear()
        for ent in self.entities:
            copy.entities.append(ent)

        copy.relationships.clear()
        for rel in self.relationships:
            copy.relationships.append(rel)

        copy.sub_manifests.clear()
        for man in self.sub_manifests:
            copy.sub_manifests.append(man)

        copy.exhibits_traits.clear()
        for et in self.exhibits_traits:
            copy.exhibits_traits.append(et)

        return copy

    async def create_resolved_manifest_async(self, new_manifest_name: str, new_entity_document_name_format: str, directives: Optional[AttributeResolutionDirectiveSet] = None) -> Optional['CdmManifestDefinition']:
        """Creates a resolved copy of the manifest.
        new_entity_document_name_format specifies a pattern to use when creating documents for resolved entities.
        The default is "resolved/{n}.cdm.json" to avoid a document name conflict with documents in the same folder as
        the manifest. Every instance of the string {n} is replaced with the entity name from the source manifest. Any
        sub-folders described by the pattern should exist in the corpus prior to calling this function.
        """
        with logger._enter_scope(self._TAG, self.ctx, self.create_resolved_manifest_async.__name__):
            if self.entities is None:
                return None

            if not self.folder:
                logger.error(
                    self._TAG,
                    self.ctx,
                    'Cannot resolve the manifest \'{}\' because it has not been added to a folder'.format(self.manifest_name),
                    self.create_resolved_manifest_async.__name__
                )
                return None

            if new_entity_document_name_format is None:
                new_entity_document_name_format = '{f}resolved/{n}.cdm.json'
            elif new_entity_document_name_format == '':  # for back compat
                new_entity_document_name_format = '{n}.cdm.json'
            elif '{n}' not in new_entity_document_name_format:  # for back compat
                new_entity_document_name_format = new_entity_document_name_format + '/{n}.cdm.json'

            source_manifest_path = self.ctx.corpus.storage.create_absolute_corpus_path(self.at_corpus_path, self)
            source_manifest_folder_path = self.ctx.corpus.storage.create_absolute_corpus_path(self.folder.at_corpus_path, self)

            resolved_manifest_path_split = new_manifest_name.rfind('/') + 1
            resolved_manifest_folder = None
            if resolved_manifest_path_split > 0:
                resolved_manifest_path = new_manifest_name[0:resolved_manifest_path_split]
                new_folder_path = self.ctx.corpus.storage.create_absolute_corpus_path(resolved_manifest_path, self)
                resolved_manifest_folder = await self.ctx.corpus.fetch_object_async(new_folder_path)  # type: CdmFolderDefinition
                if resolved_manifest_folder is None:
                    logger.error(self._TAG, self.ctx, 'New folder for manifest not found {}'.format(new_folder_path), self.create_resolved_manifest_async.__name__)
                    return None
                new_manifest_name = new_manifest_name[resolved_manifest_path_split:]
            else:
                resolved_manifest_folder = self.owner

            logger.debug(self._TAG, self.ctx, 'resolving manifest {}'.format(source_manifest_path), self.create_resolved_manifest_async.__name__)

            # using the references present in the resolved entities, get an entity
            # create an imports doc with all the necessary resolved entity references and then resolve it
            # sometimes they might send the docname, that makes sense a bit, don't include the suffix in the name
            if new_manifest_name.lower().endswith('.manifest.cdm.json'):
                new_manifest_name = new_manifest_name[0: (len(new_manifest_name) - len('.manifest.cdm.json'))]
            resolved_manifest = CdmManifestDefinition(self.ctx, new_manifest_name)

            # bring over any imports in this document or other bobbles
            resolved_manifest.schema = self.schema
            resolved_manifest.explanation = self.explanation
            resolved_manifest.document_version = self.document_version
            for imp in self.imports:
                resolved_manifest.imports.append(imp.copy())

            # add the new document to the folder
            if resolved_manifest_folder.documents.append(resolved_manifest) is None:
                # when would this happen?
                return None

            for entity in self.entities:
                ent_def = await self._get_entity_from_reference(entity, self)

                if not ent_def:
                    logger.error(self._TAG, self.ctx, 'Unable to get entity from reference', self.create_resolved_manifest_async.__name__)
                    return None

                if not ent_def.in_document.folder:
                    logger.error(self._TAG, self.ctx, 'The document containing the entity \'{}\' is not in a folder'.format(
                        ent_def.entity_name), self.create_resolved_manifest_async.__name__)
                    return None

                # get the path from this manifest to the source entity. this will be the {f} replacement value
                source_entity_full_path = self.ctx.corpus.storage.create_absolute_corpus_path(ent_def.in_document.folder.at_corpus_path, self)
                f = ''
                if source_entity_full_path.startswith(source_manifest_folder_path):
                    f = source_entity_full_path[len(source_manifest_folder_path):]

                new_document_full_path = new_entity_document_name_format.replace('{n}', ent_def.entity_name).replace('{f}', f)
                new_document_full_path = self.ctx.corpus.storage.create_absolute_corpus_path(new_document_full_path, self)

                new_document_path_split = new_document_full_path.rfind('/') + 1
                new_document_path = new_document_full_path[0:new_document_path_split]
                new_document_name = new_document_full_path[new_document_path_split:]

                # make sure the new folder exists
                folder = await self.ctx.corpus.fetch_object_async(new_document_path)  # type: CdmFolderDefinition
                if not folder:
                    logger.error(self._TAG, self.ctx, 'New folder not found {}'.format(new_document_path), self.create_resolved_manifest_async.__name__)
                    return None

                # next create the resolved entity.
                with_directives = directives if directives is not None else self.ctx.corpus.default_resolution_directives
                res_opt = ResolveOptions(ent_def.in_document, with_directives.copy())

                logger.debug(self._TAG, self.ctx, '    resolving entity {} to document {}'.format(source_entity_full_path, new_document_full_path),
                            self.create_resolved_manifest_async.__name__)

                resolved_entity = await ent_def.create_resolved_entity_async(ent_def.entity_name, res_opt, folder, new_document_name)
                if not resolved_entity:
                    # fail all resolution, if any one entity resolution fails
                    return None

                result = entity.copy(res_opt)
                if result.object_type == CdmObjectType.LOCAL_ENTITY_DECLARATION_DEF:
                    relative_entity_path = self.ctx.corpus.storage.create_relative_corpus_path(resolved_entity.at_corpus_path, resolved_manifest)
                    result.entity_path = relative_entity_path or result.at_corpus_path

                resolved_manifest.entities.append(result)

            logger.debug(self._TAG, self.ctx, '    calculating relationships', self.create_resolved_manifest_async.__name__)
            # Calculate the entity graph for just this manifest.
            await self.ctx.corpus.calculate_entity_graph_async(resolved_manifest)
            # Stick results into the relationships list for the manifest.
            await resolved_manifest.populate_manifest_relationships_async(CdmRelationshipDiscoveryStyle.EXCLUSIVE)

            # needed until Matt's changes with collections where I can propigate
            resolved_manifest._is_dirty = True
            return resolved_manifest

    async def file_status_check_async(self) -> None:
        """Check the modified time for this object and any children."""
        with logger._enter_scope(self._TAG, self.ctx, self.file_status_check_async.__name__):
            adapter = self.ctx.corpus.storage.fetch_adapter(self.in_document.namespace)
            if adapter:
                context = adapter.create_file_query_cache_context()
                try:
                    modified_time = await self.ctx.corpus._fetch_last_modified_time_from_object_async(self)

                    self.last_file_status_check_time = datetime.now(timezone.utc)
                    if not self.last_file_modified_time:
                        self.last_file_modified_time = self._file_system_modified_time

                    # Reload the manifest if it has been updated in the file system.
                    if modified_time and self._file_system_modified_time and modified_time != self._file_system_modified_time:
                        await self._reload_async()
                        self.last_file_modified_time = time_utils._max_time(modified_time, self.last_file_modified_time)
                        self._file_system_modified_time = self.last_file_modified_time
                    
                    for entity in self.entities:
                        await entity.file_status_check_async()

                    for sub_manifest in self.sub_manifests:
                        await sub_manifest.file_status_check_async()
                        
                finally:
                    context.dispose()

    async def _get_entity_from_reference(self, entity: 'CdmEntityDeclarationDefinition', manifest: 'CdmManifestDefinition') -> 'CdmEntityDefinition':
        entity_path = await self._get_entity_path_from_declaration(entity, cast('CdmObject', manifest))
        result = await self.ctx.corpus.fetch_object_async(entity_path)  # type: CdmEntityDefinition

        if result is None:
            logger.error(self._TAG, self.ctx, 'failed to resolve entity {}'.format(entity_path), self._get_entity_from_reference.__name__)

        return result

    async def _get_entity_path_from_declaration(self, entity_dec: 'CdmEntityDeclarationDefinition', obj: Optional['CdmObject'] = None):
        while isinstance(entity_dec, CdmReferencedEntityDeclarationDefinition):
            entity_dec = await self.ctx.corpus.fetch_object_async(entity_dec.entity_path, obj)
            if not entity_dec:
                return None
            obj = entity_dec.in_document

        return self.ctx.corpus.storage.create_absolute_corpus_path(entity_dec.entity_path, obj)

    def is_derived_from(self, base: str, res_opt: Optional['ResolveOptions'] = None) -> bool:
        return False

    def _is_rel_allowed(self, rel: 'CdmE2ERelationship', option: 'CdmRelationshipDiscoveryStyle') -> bool:
        if option == CdmRelationshipDiscoveryStyle.NONE:
            return False
        if option == CdmRelationshipDiscoveryStyle.EXCLUSIVE:
            absolute_from_ent_string = self.ctx.corpus.storage.create_absolute_corpus_path(rel.from_entity, self)

            #  only true if from and to entities are both found in the entities list of self folio
            from_ent_in_manifest = bool(list(filter(lambda x: self.ctx.corpus.storage.create_absolute_corpus_path(x.entity_path, self) == absolute_from_ent_string,
                                                    self.entities)))

            absolute_to_ent_string = self.ctx.corpus.storage.create_absolute_corpus_path(rel.to_entity, self)
            to_ent_in_manifest = bool(list(filter(lambda x: self.ctx.corpus.storage.create_absolute_corpus_path(x.entity_path, self) == absolute_to_ent_string,
                                                  self.entities)))

            return bool(from_ent_in_manifest and to_ent_in_manifest)
        return True

    def _localize_rel_to_manifest(self, rel: 'CdmE2ERelationship') -> 'CdmE2ERelationship':
        rel_copy = self.ctx.corpus.make_object(CdmObjectType.E2E_RELATIONSHIP_DEF, rel.relationship_name)  # type: CdmE2ERelationship
        rel_copy.to_entity = self.ctx.corpus.storage.create_relative_corpus_path(rel.to_entity, self)
        rel_copy.from_entity = self.ctx.corpus.storage.create_relative_corpus_path(rel.from_entity, self)
        rel_copy.to_entity_attribute = rel.to_entity_attribute
        rel_copy.from_entity_attribute = rel.from_entity_attribute
        return rel_copy

    async def populate_manifest_relationships_async(self, option: CdmRelationshipDiscoveryStyle = CdmRelationshipDiscoveryStyle.ALL) -> None:
        """Populate the relationships that the entities in the current manifest are involved in."""
        self.relationships.clear()
        rel_cache = set()  # Set[str]

        for ent_dec in self.entities:
            ent_path = await self._get_entity_path_from_declaration(ent_dec, self)
            curr_entity = await self.ctx.corpus.fetch_object_async(ent_path)  # type: CdmEntityDefinition

            if curr_entity is None:
                continue

            # handle the outgoing relationships
            outgoing_rels = self.ctx.corpus.fetch_outgoing_relationships(curr_entity)  # List[CdmE2ERelationship]
            if outgoing_rels:
                for rel in outgoing_rels:
                    cache_key = rel2_cache_key(rel)
                    if cache_key not in rel_cache and self._is_rel_allowed(rel, option):
                        self.relationships.append(self._localize_rel_to_manifest(rel))
                        rel_cache.add(cache_key)

            incoming_rels = self.ctx.corpus.fetch_incoming_relationships(curr_entity)  # type: List[CdmE2ERelationship]

            if incoming_rels:
                for in_rel in incoming_rels:
                    # get entity object for current toEntity
                    current_in_base = await self.ctx.corpus.fetch_object_async(in_rel.to_entity, self)  # type: CdmEntityDefinition

                    if not current_in_base:
                        continue

                    # create graph of inheritance for to current_in_base
                    # graph represented by an array where entity at i extends entity at i+1
                    to_inheritance_graph = []  # type: List[CdmEntityDefinition]
                    while current_in_base:
                        res_opt = ResolveOptions(wrt_doc=current_in_base.in_document)
                        current_in_base = current_in_base.extends_entity.fetch_object_definition(res_opt) if current_in_base.extends_entity else None
                        if current_in_base:
                            to_inheritance_graph.append(current_in_base)

                    # add current incoming relationship
                    cache_key = rel2_cache_key(in_rel)
                    if cache_key not in rel_cache and self._is_rel_allowed(in_rel, option):
                        self.relationships.append(self._localize_rel_to_manifest(in_rel))
                        rel_cache.add(cache_key)

                    # if A points at B, A's base classes must point at B as well
                    for base_entity in to_inheritance_graph:
                        incoming_rels_for_base = self.ctx.corpus.fetch_incoming_relationships(base_entity)  # type: List[CdmE2ERelationship]

                        if incoming_rels_for_base:
                            for in_rel_base in incoming_rels_for_base:
                                new_rel = self.ctx.corpus.make_object(CdmObjectType.E2E_RELATIONSHIP_DEF, '')
                                new_rel.from_entity = in_rel_base.from_entity
                                new_rel.from_entity_attribute = in_rel_base.from_entity_attribute
                                new_rel.to_entity = in_rel.to_entity
                                new_rel.to_entity_attribute = in_rel.to_entity_attribute

                                base_rel_cache_key = rel2_cache_key(new_rel)
                                if base_rel_cache_key not in rel_cache and self._is_rel_allowed(new_rel, option):
                                    self.relationships.append(self._localize_rel_to_manifest(new_rel))
                                    rel_cache.add(base_rel_cache_key)
        if self.sub_manifests:
            for sub_manifest_def in self.sub_manifests:
                corpus_path = self.ctx.corpus.storage.create_absolute_corpus_path(sub_manifest_def.definition, self)
                sub_manifest = await self.ctx.corpus.fetch_object_async(corpus_path)  # type: CdmManifestDefinition
                await sub_manifest.populate_manifest_relationships_async(option)

    async def report_most_recent_time_async(self, child_time: datetime) -> None:
        """Report most recent modified time (of current or children objects) to the parent object."""
        if child_time:
            self.last_child_file_modified_time = time_utils._max_time(child_time, self.last_child_file_modified_time)

    async def _query_on_traits_async(self, query_spec: Union[str, object]) -> Iterable[object]:
        """Query the manifest for a set of entities that match an input query
        query_spec = a JSON object (or a string that can be parsed into one) of the form
        {"entityName":"", "attributes":[{see QueryOnTraits for CdmEntityDefinition for details}]}
        returns null for 0 results or an array of json objects, each matching the shape of
        the input query, with entity and attribute names filled in"""
        return None

    async def _save_dirty_link(self, relative: str, options: 'CopyOptions') -> None:
        """helper that fixes a path from local to absolute, gets the object from that path
        then looks at the document where the object is found.
        if dirty, the document is saved with the original name"""

        # get the document object from the import
        doc_path = self.ctx.corpus.storage.create_absolute_corpus_path(relative, self)
        if doc_path is None:
            logger.error(self._TAG, self.ctx, 'Invalid corpus path {}'.format(relative), self._save_dirty_link.__name__)
            return False

        obj_at = await self.ctx.corpus.fetch_object_async(doc_path)
        if obj_at is None:
            logger.error(self._TAG, self.ctx, 'Couldn\'t get object from path {}'.format(doc_path), self._save_dirty_link.__name__)
            return False

        doc_imp = cast('CdmDocumentDefinition', obj_at.in_document)
        if doc_imp:
            if doc_imp._is_dirty:
                # save it with the same name
                if not await doc_imp.save_as_async(doc_imp.name, True, options):
                    logger.error(self._TAG, self.ctx, 'failed saving document {}'.format(doc_imp.name), self._save_dirty_link.__name__)
                    return False
        return True

    async def _save_linked_documents_async(self, options: 'CopyOptions') -> bool:
        if self.imports:
            for imp in self.imports:
                if not await self._save_dirty_link(imp.corpus_path, options):
                    logger.error(self._TAG, self.ctx, 'failed saving imported document {}'.format(
                        imp.at_corpus_path), self._save_linked_documents_async.__name__)
                    return False

        # only the local entity declarations please
        for entity_def in self.entities:
            if entity_def.object_type == CdmObjectType.LOCAL_ENTITY_DECLARATION_DEF:
                if not await self._save_dirty_link(entity_def.entity_path, options):
                    logger.error(self._TAG, self.ctx, 'failed saving local entity schema document {}'.format(entity_def.entity_path),
                                 self._save_linked_documents_async.__name__)
                    return False

                # also, partitions can have their own schemas
                if entity_def.data_partitions:
                    for partition in entity_def.data_partitions:
                        if partition.specialized_schema:
                            if not await self._save_dirty_link(entity_def.entity_path, options):
                                logger.error(self._TAG, self.ctx, 'failed saving partition schema document {}'.format(
                                    entity_def.entity_path), self._save_linked_documents_async.__name__)
                                return False

                # so can patterns
                if entity_def.data_partition_patterns:
                    for pattern in entity_def.data_partition_patterns:
                        if pattern.specialized_schema:
                            if not await self._save_dirty_link(pattern.specialized_schema, options):
                                logger.error(self._TAG, self.ctx, 'failed saving partition schema document {}'.format(
                                    pattern.specialized_schema), self._save_linked_documents_async.__name__)
                                return False

        if self.sub_manifests:
            for sub in self.sub_manifests:
                if not await self._save_dirty_link(sub.definition, options):
                    logger.error(self._TAG, self.ctx, 'failed saving sub-manifest document {}'.format(sub.definition),
                                 self._save_linked_documents_async.__name__)
                    return False

        return True

    def visit(self, path_from: str, pre_children: 'VisitCallback', post_children: 'VisitCallback') -> bool:
        if pre_children and pre_children(self, path_from):
            return False

        if self.definitions and self.definitions._visit_array(path_from, pre_children, post_children):
            return True

        if self.entities and self.entities._visit_array(path_from, pre_children, post_children):
            return True

        if self.relationships and self.relationships._visit_array('{}/relationships/'.format(path_from), pre_children, post_children):
            return True

        if self.sub_manifests and self.sub_manifests._visit_array('{}/subManifests/'.format(path_from), pre_children, post_children):
            return True

        if post_children and post_children(self, path_from):
            return True

        return False
