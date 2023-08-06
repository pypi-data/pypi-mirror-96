# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from typing import Optional, TYPE_CHECKING

from cdm.enums import CdmAttributeContextType, CdmObjectType, CdmOperationType
from cdm.objectmodel import CdmAttributeContext
from cdm.resolvedmodel.projections.projection_attribute_state import ProjectionAttributeState
from cdm.utilities import logger, Errors, AttributeContextParameters

from .cdm_operation_base import CdmOperationBase

if TYPE_CHECKING:
    from cdm.objectmodel import CdmCorpusContext, CdmTypeAttributeDefinition
    from cdm.resolvedmodel.projections.projection_attribute_state_set import ProjectionAttributeStateSet
    from cdm.resolvedmodel.projections.projection_context import ProjectionContext
    from cdm.utilities import VisitCallback, ResolveOptions


class CdmOperationAddSupportingAttribute(CdmOperationBase):
    """Class to handle AddSupportingAttribute operations"""

    def __init__(self, ctx: 'CdmCorpusContext') -> None:
        super().__init__(ctx)

        self.supporting_attribute = None  # type: Optional[CdmTypeAttributeDefinition]
        self.type = CdmOperationType.ADD_SUPPORTING_ATTRIBUTE  # type: CdmOperationType

        # --- internal ---
        self._TAG = CdmOperationAddSupportingAttribute.__name__

    def copy(self, res_opt: Optional['ResolveOptions'] = None, host: Optional['CdmOperationAddSupportingAttribute'] = None) -> 'CdmOperationAddSupportingAttribute':
        copy = CdmOperationAddSupportingAttribute(self.ctx)
        if self.supporting_attribute:
            copy.supporting_attribute = self.supporting_attribute.copy()
        return copy

    def get_name(self) -> str:
        return 'operationAddSupportingAttribute'

    @property
    def object_type(self) -> 'CdmObjectType':
        return CdmObjectType.OPERATION_ADD_SUPPORTING_ATTRIBUTE_DEF

    def validate(self) -> bool:
        missing_fields = []

        if not bool(self.supporting_attribute):
            missing_fields.append('supporting_attribute')

        if len(missing_fields) > 0:
            logger.error(self._TAG, self.ctx, Errors.validate_error_string(self.at_corpus_path, missing_fields))
            return False

        return True

    def visit(self, path_from: str, pre_children: 'VisitCallback', post_children: 'VisitCallback') -> bool:
        path = ''
        if not self.ctx.corpus._block_declared_path_changes:
            path = self._declared_path
            if not path:
                path = path_from + 'operationAddSupportingAttribute'
                self._declared_path = path

        if pre_children and pre_children(self, path):
            return False

        if post_children and post_children(self, path):
            return True

        return False

    def _append_projection_attribute_state(self, proj_ctx: 'ProjectionContext', proj_output_set: 'ProjectionAttributeStateSet', attr_ctx: 'CdmAttributeContext') -> 'ProjectionAttributeStateSet':
        # Pass through all the input projection attribute states if there are any
        for current_PAS in proj_ctx._current_attribute_state_set._states:
            proj_output_set._add(current_PAS)

        # Create a new attribute context for the operation
        attr_ctx_op_add_supporting_attr_param = AttributeContextParameters()
        attr_ctx_op_add_supporting_attr_param._under = attr_ctx
        attr_ctx_op_add_supporting_attr_param._type = CdmAttributeContextType.OPERATION_ADD_SUPPORTING_ATTRIBUTE
        attr_ctx_op_add_supporting_attr_param._name = 'operation/index{}/{}'.format(self._index, self.get_name())
        attr_ctx_op_add_supporting_attr = CdmAttributeContext._create_child_under(proj_ctx._projection_directive._res_opt, attr_ctx_op_add_supporting_attr_param)

        # Create a new attribute context for the supporting attribute we will create
        attr_ctx_supporting_attr_param = AttributeContextParameters()
        attr_ctx_supporting_attr_param._under = attr_ctx_op_add_supporting_attr
        attr_ctx_supporting_attr_param._type = CdmAttributeContextType.ADDED_ATTRIBUTE_SUPPORTING
        attr_ctx_supporting_attr_param._name = self.supporting_attribute.name
        attr_ctx_supporting_attr = CdmAttributeContext._create_child_under(proj_ctx._projection_directive._res_opt, attr_ctx_supporting_attr_param)
        
        # TODO: this if statement keeps the functionality the same way it works currently in resolution guidance.
        # This should be changed to point to the foreign key attribute instead. 
        # There has to be some design decisions about how this will work and will be done in the next release.
        if len(proj_ctx._current_attribute_state_set._states) > 0:
            last_state = proj_ctx._current_attribute_state_set._states[-1]  # type: ProjectionAttributeState
            in_support_of_trait = self.supporting_attribute.applied_traits.append('is.addedInSupportOf')  # type: CdmTraitReference
            in_support_of_trait.arguments.append('inSupportOf', last_state._current_resolved_attribute.resolved_name)

        # Create the supporting attribute with the specified 'SupportingAttribute' property as its target and apply the trait 'is.virtual.attribute' to it
        add_trait = ['is.virtual.attribute']
        new_res_attr = self._create_new_resolved_attribute(proj_ctx, attr_ctx_supporting_attr, self.supporting_attribute, added_simple_ref_traits=add_trait)

        # Create a new projection attribute state for the new supporting attribute and add it to the output set
        # There is no previous state for the newly created supporting attribute
        new_PAS = ProjectionAttributeState(proj_output_set._ctx)
        new_PAS._current_resolved_attribute = new_res_attr

        proj_output_set._add(new_PAS)

        return proj_output_set
