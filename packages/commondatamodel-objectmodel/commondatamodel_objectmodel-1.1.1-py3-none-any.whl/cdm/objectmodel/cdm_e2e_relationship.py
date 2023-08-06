﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from typing import Optional, TYPE_CHECKING

from cdm.enums import CdmObjectType
from cdm.utilities import ResolveOptions, logger, Errors

from .cdm_object_def import CdmObjectDefinition

if TYPE_CHECKING:
    from cdm.objectmodel import CdmCorpusContext
    from cdm.utilities import FriendlyFormatNode, VisitCallback


class CdmE2ERelationship(CdmObjectDefinition):
    def __init__(self, ctx: 'CdmCorpusContext', name: str) -> None:
        super().__init__(ctx)

        self.relationship_name = name  # type: str
        self.from_entity = None  # type: Optional[str]
        self.from_entity_attribute = None  # type: Optional[str]
        self.to_entity = None  # type: Optional[str]
        self.to_entity_attribute = None  # type: Optional[str]

        self._TAG = CdmE2ERelationship.__name__

    @property
    def object_type(self) -> 'CdmObjectType':
        return CdmObjectType.E2E_RELATIONSHIP_DEF

    def copy(self, res_opt: Optional['ResolveOptions'] = None, host: Optional['CdmE2ERelationship'] = None) -> 'CdmE2ERelationship':
        if not res_opt:
            res_opt = ResolveOptions(wrt_doc=self, directives=self.ctx.corpus.default_resolution_directives)

        if not host:
            copy = CdmE2ERelationship(self.ctx, self.get_name())
        else:
            copy = host
            copy.ctx = self.ctx
            copy.relationship_name = self.get_name()

        copy.from_entity = self.from_entity
        copy.from_entity_attribute = self.from_entity_attribute
        copy.to_entity = self.to_entity
        copy.to_entity_attribute = self.to_entity_attribute
        self._copy_def(res_opt, copy)

        return copy

    def get_name(self) -> str:
        return self.relationship_name

    def is_derived_from(self, base: str, res_opt: Optional['ResolveOptions'] = None) -> bool:
        return False

    def validate(self) -> bool:
        missing_fields = []
        if not bool(self.from_entity):
            missing_fields.append('from_entity')
        if not bool(self.from_entity_attribute):
            missing_fields.append('from_entity_attribute')
        if not bool(self.to_entity):
            missing_fields.append('to_entity')
        if not bool(self.to_entity_attribute):
            missing_fields.append('to_entity_attribute')

        if missing_fields:
            logger.error(self._TAG, self.ctx, Errors.validate_error_string(self.at_corpus_path, missing_fields))
            return False
        return True

    def visit(self, path_from: str, pre_children: 'VisitCallback', post_children: 'VisitCallback') -> bool:
        path = ''
        if self.ctx.corpus._block_declared_path_changes is False:
            if not self._declared_path:
                self._declared_path = '{}{}'.format(path_from, self.get_name())

            path = self._declared_path

        if pre_children and pre_children(self, path):
            return False

        if self._visit_def(path, pre_children, post_children):
            return True

        if post_children and post_children(self, path):
            return True

        return False
