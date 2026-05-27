"""
Vendored helpers from PXDesign that we cannot import directly.

The released `pxdesign/utils/design.py` and `pxdesign/data/ccd.py` both
import `from protenix.data import ccd` (and `from protenix.data.ccd import ...`)
— but the Protenix in this workspace exposes the same symbols at
`protenix.data.core.ccd`, so any import of those PXDesign modules raises
`ImportError`.

Rather than monkey-patch PXDesign's import path, we vendor verbatim copies of
the three small pure-Python functions we need, calling
`protenix.data.core.ccd.get_one_letter_code` directly. Behavior is unchanged.

Sources (all under Apache 2.0):
  - cano_seq_resname_with_mask:  pxdesign/utils/design.py
  - restype_onehot_encoded:      pxdesign/utils/design.py
  - get_condition_template_feature: pxdesign/data/featurizer.py (DesignFeaturizer)
"""
import biotite.structure as struc
import numpy as np
import torch

from pxdesign.data.constants import (
    DNA_STD_RESIDUES,
    PROT_STD_RESIDUES_ONE_TO_THREE,
    RNA_STD_RESIDUES,
    STD_RESIDUES_WITH_GAP,
    mmcif_restype_3to1,
)


def _get_one_letter_code(resname: str):
    """Resolve a 3-letter residue name to its one-letter code.

    Standard residues hit the in-module table from `mmcif_restype_3to1`. For
    non-standard residues (e.g. modified amino acids, glycans), fall back to
    Protenix's CCD lookup — which requires the CCD components.cif database
    (downloaded by `PXDesign/download_tool_weights.sh`). Tests that use only
    standard residues never need the CCD.
    """
    if resname in mmcif_restype_3to1:
        return mmcif_restype_3to1[resname]
    # Lazy import — only loaded when we actually need it.
    from protenix.data.core import ccd
    return ccd.get_one_letter_code(resname)


def _encoder(encode_def_list, input_list):
    onehot_dict = {}
    num_keys = len(encode_def_list)
    for index, key in enumerate(encode_def_list):
        onehot = [0] * num_keys
        onehot[index] = 1
        onehot_dict[key] = onehot
    return torch.Tensor([onehot_dict[item] for item in input_list])


def restype_onehot_encoded(restype_list):
    return _encoder(list(STD_RESIDUES_WITH_GAP.keys()), restype_list)


def cano_seq_resname_with_mask(atom_array):
    """Per-atom canonical residue name; xpb residues map to one-letter 'j'."""
    cano_seq_resname = []
    starts = struc.get_residue_starts(atom_array, add_exclusive_stop=True)
    for start, stop in zip(starts[:-1], starts[1:]):
        res_atom_nums = stop - start
        mol_type = atom_array.mol_type[start]
        resname = atom_array.res_name[start]

        if resname == "xpb":
            one_letter_code = "j"
        else:
            one_letter_code = _get_one_letter_code(resname)

        if one_letter_code is None or len(one_letter_code) != 1:
            one_letter_code = "X" if mol_type == "protein" else "N"

        if mol_type == "protein":
            res_name_in_cano_seq = PROT_STD_RESIDUES_ONE_TO_THREE.get(one_letter_code, "UNK")
        elif mol_type == "dna":
            res_name_in_cano_seq = "D" + one_letter_code
            if res_name_in_cano_seq not in DNA_STD_RESIDUES:
                res_name_in_cano_seq = "DN"
        elif mol_type == "rna":
            res_name_in_cano_seq = one_letter_code
            if res_name_in_cano_seq not in RNA_STD_RESIDUES:
                res_name_in_cano_seq = "N"
        else:
            res_name_in_cano_seq = "UNK"

        cano_seq_resname.extend([res_name_in_cano_seq] * res_atom_nums)
    return cano_seq_resname


def get_condition_template_feature(
    atom_array,
    coordinate_attribute: str = "coord",
    ignore_ligand_only_condition: bool = True,
    templ_token_mask: np.ndarray = None,
    no_bins: int = 64,
    min_bin: float = 2.0,
    max_bin: float = 22.0,
):
    """Build `conditional_templ` (binned target pair distances) + mask.

    Matches `pxdesign.data.featurizer.DesignFeaturizer.get_condition_template_feature`
    byte-for-byte, except parameterised on bin range. The released defaults
    (no_bins=64, min=2.0, max=22.0) give 63 boundaries: bin i means
    distance in [boundary_{i-1}, boundary_i). Bin 0 is the "no distance" slot
    when used with `c_templ_in = no_bins + 1` (see `ConditionTemplateEmbedder`
    which does `pair_mask * (1 + conditional_templ)` — masked pairs read bin 0).
    """
    distogram_atom = atom_array[atom_array.distogram_rep_atom_mask.astype(bool)]
    N_token = len(distogram_atom)
    conditional_templ = torch.zeros(size=(N_token, N_token), dtype=torch.long)
    conditional_templ_mask = torch.zeros(size=(N_token, N_token), dtype=torch.bool)

    feature_dict = {
        "conditional_templ": conditional_templ,
        "conditional_templ_mask": conditional_templ_mask.long(),
    }

    if ignore_ligand_only_condition:
        is_ligand_condition = (distogram_atom.res_name != "xpb") * (
            distogram_atom.mol_type == "ligand"
        )
        if is_ligand_condition.all():
            return feature_dict

    condi_token_rslv_mask = (
        distogram_atom.res_name != "xpb"
    ) * distogram_atom.is_resolved.astype(bool)
    if templ_token_mask is not None:
        condi_token_rslv_mask = condi_token_rslv_mask * templ_token_mask.astype(bool)
    if not condi_token_rslv_mask.any():
        return feature_dict

    condi_rslv_disto_atom = distogram_atom[condi_token_rslv_mask]
    if coordinate_attribute == "coord":
        condi_token_coord = torch.tensor(condi_rslv_disto_atom.coord)
    else:
        condi_token_coord = torch.tensor(
            condi_rslv_disto_atom.get_annotation(coordinate_attribute)
        )

    condi_token_dist = torch.cdist(condi_token_coord, condi_token_coord)
    boundaries = torch.linspace(start=min_bin, end=max_bin, steps=no_bins - 1)
    condi_templ_bins = torch.sum(condi_token_dist.unsqueeze(-1) > boundaries, dim=-1)

    idx = torch.nonzero(torch.tensor(condi_token_rslv_mask).long(), as_tuple=True)[0]
    ii, jj = torch.meshgrid(idx, idx, indexing="ij")
    conditional_templ[ii, jj] = condi_templ_bins
    conditional_templ_mask[ii, jj] = True
    feature_dict["conditional_templ"] = conditional_templ
    feature_dict["conditional_templ_mask"] = conditional_templ_mask.long()
    return feature_dict
