# Copyright (C) 2023 Greg Landrum
# All rights reserved
# This file is part of lwreg.
# The contents are covered by the terms of the MIT license
# which is included in the file LICENSE,

from rdkit import Chem

import warnings

# MolStandardize generates a pile of deprecation warnings in the 2024.03 release
# of RDKit. We aren't using any of the deprecated code and can ignore the
# warnings here
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem import rdMolTransforms


class Standardization:
    '''
    a Standardization should have a __call__ method which returns either the 
      standardized molecule (on success) or None (on failure)
    '''
    __slots__ = ["name", "explanation"]

    def __call__(self, mol):
        return mol


class NoStandardization(Standardization):
    name = "no_standardization"
    explanation = "does not modify the molecule"

    def __call__(self, mol):
        return mol


class RemoveHs(Standardization):
    name = "remove_hs"
    explanation = "removes hydrogens from the molecule"

    def __call__(self, mol):
        return Chem.RemoveHs(mol)


class CanonicalizeOrientation(Standardization):
    name = "canonicalize_orientation"
    explanation = "canonicalizes the orientation of the molecule's 3D conformers (if present)"

    def __call__(self, mol):
        for conf in mol.GetConformers():
            if conf.Is3D():
                rdMolTransforms.CanonicalizeConformer(conf)
        return mol


class OverlappingAtomsCheck(Standardization):
    name = "has_overlapping_atoms"
    explanation = "fails if molecule has at least two atoms which are closer than a threshold distance to each other"
    threshold = 0.0001

    def __call__(self, mol):
        if mol.GetNumConformers():
            t2 = self.threshold * self.threshold
            conf = mol.GetConformer()
            pts = [conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms())]
            for i, pti in enumerate(pts):
                for j in range(i):
                    d = pti - pts[j]
                    if d.LengthSq() < t2:
                        return None
        return mol


class PolymerCheck(Standardization):
    name = "has_polymer_info"
    explanation = "fails if molecule has an SGroup associated with polymers"
    polymerTypes = ['SRU', 'COP', 'MON', 'CRO', 'GRA']

    def __call__(self, mol):
        for sg in Chem.GetMolSubstanceGroups(mol):
            typ = sg.GetProp('TYPE')
            if typ in self.polymerTypes:
                return None

        return mol


class RDKitSanitize(Standardization):
    name = "rdkit_sanitize"
    explanation = "runs the standard RDKit sanitization on the molecule"

    def __call__(self, mol):
        try:
            Chem.SanitizeMol(mol)
        except:
            return None
        return mol


class FragmentParent(Standardization):
    name = "fragment_parent"
    explanation = "generates the fragment parent of the molecule"

    def __call__(self, mol):
        try:
            res = rdMolStandardize.FragmentParent(mol)
        except:
            return None
        return res


class ChargeParent(Standardization):
    name = "charge_parent"
    explanation = "generates the charge parent of the molecule"

    def __call__(self, mol):
        try:
            res = rdMolStandardize.ChargeParent(mol)
        except:
            return None
        return res


class TautomerParent(Standardization):
    name = "tautomer_parent"
    explanation = "generates the tautomer parent of the molecule"

    def __call__(self, mol):
        try:
            res = rdMolStandardize.TautomerParent(mol)
        except:
            return None
        return res


class SuperParent(Standardization):
    name = "super_parent"
    explanation = "generates the super parent of the molecule"

    def __call__(self, mol):
        try:
            res = rdMolStandardize.SuperParent(mol)
        except:
            return None
        return res
